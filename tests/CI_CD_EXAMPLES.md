# CI/CD Integration Examples

This document provides guidance on integrating the Docker Build Test Suite with various CI/CD platforms.

## Table of Contents

- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Jenkins](#jenkins)
- [General Guidelines](#general-guidelines)

## GitHub Actions

### Basic Workflow

`.github/workflows/docker-build-test.yml`:

```yaml
name: Docker Build Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  sanity-check:
    name: Sanity Check
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Run sanity tests
        run: |
          cd tests
          ./test.sh sanity

  docker-build-runtime:
    name: Build dx-runtime
    needs: sanity-check
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-24.04, ubuntu-22.04, ubuntu-20.04, ubuntu-18.04, debian-12, debian-13]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Test dx-runtime build
        run: |
          OS="${{ matrix.os }}" 
          OS_DISTRO="${OS%%-*}"
          OS_VERSION="${OS##*-}"

          cd tests
          ./run_docker_build_tests.sh -v -k "runtime and ${OS_DISTRO} and ${OS_VERSION}"
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-runtime-${{ matrix.os }}
          path: tests/reports/

  docker-build-modelzoo:
    name: Build dx-modelzoo
    needs: sanity-check
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-24.04, ubuntu-22.04, ubuntu-20.04, ubuntu-18.04, debian-12, debian-13]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Test dx-modelzoo build
        run: |
          OS="${{ matrix.os }}" 
          OS_DISTRO="${OS%%-*}"
          OS_VERSION="${OS##*-}"

          cd tests
          ./run_docker_build_tests.sh -v -k "modelzoo and ${OS_DISTRO} and ${OS_VERSION}"
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-modelzoo-${{ matrix.os }}
          path: tests/reports/

  docker-build-compiler:
    name: Build dx-compiler
    needs: sanity-check
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-24.04, ubuntu-22.04, ubuntu-20.04]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Test dx-compiler build
        run: |
          OS="${{ matrix.os }}" 
          OS_DISTRO="${OS%%-*}"
          OS_VERSION="${OS##*-}"

          cd tests
          ./run_docker_build_tests.sh -v -k "compiler and ${OS_DISTRO} and ${OS_VERSION}"
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-compiler-${{ matrix.os }}
          path: tests/reports/

  generate-report:
    name: Generate Test Report
    needs: [docker-build-runtime, docker-build-modelzoo, docker-build-compiler]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v3
        with:
          path: test-results
      
      - name: Display structure of downloaded files
        run: ls -R test-results
```

### Simplified Workflow (Quick Validation)

```yaml
name: Quick Docker Build Check

on:
  pull_request:
    branches: [ main ]

jobs:
  quick-test:
    name: Quick Build Test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Run sanity tests
        run: |
          cd tests
          ./test.sh sanity
      
      - name: Test one configuration per target
        run: |
          cd tests
          ./run_docker_build_tests.sh -v -k "ubuntu and 24.04"
```

## GitLab CI

### Basic Pipeline

`.gitlab-ci.yml`:

```yaml
stages:
  - sanity
  - build-runtime
  - build-modelzoo
  - build-compiler
  - report

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

before_script:
  - python3 --version
  - docker --version
  - docker compose version

# Sanity tests
sanity-check:
  stage: sanity
  image: ubuntu:24.04
  services:
    - docker:24-dind
  script:
    - apt-get update && apt-get install -y python3 python3-venv docker.io
    - cd tests
    - ./test.sh sanity
  tags:
    - docker

# dx-runtime build tests
.runtime-template: &runtime-template
  stage: build-runtime
  image: ubuntu:24.04
  services:
    - docker:24-dind
  script:
    - apt-get update && apt-get install -y python3 python3-venv docker.io docker-compose-v2
    - cd tests
    - ./run_docker_build_tests.sh -v -k "runtime and ${OS_DISTRO} and ${OS_VERSION}"
  artifacts:
    when: always
    paths:
      - tests/reports/
    expire_in: 7 days
  tags:
    - docker

runtime-ubuntu-24.04:
  <<: *runtime-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "24.04"

runtime-ubuntu-22.04:
  <<: *runtime-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "22.04"

runtime-ubuntu-20.04:
  <<: *runtime-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "20.04"

runtime-ubuntu-18.04:
  <<: *runtime-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "18.04"

runtime-debian-12:
  <<: *runtime-template
  variables:
    OS_DISTRO: "debian"
    OS_VERSION: "12"

runtime-debian-13:
  <<: *runtime-template
  variables:
    OS_DISTRO: "debian"
    OS_VERSION: "13"
  script:
    - apt-get update && apt-get install -y python3 python3-venv docker.io docker-compose-v2
    - cd tests
    - ./run_docker_build_tests.sh -v -k "runtime and debian and 13"

# dx-modelzoo build tests
.modelzoo-template: &modelzoo-template
  stage: build-modelzoo
  image: ubuntu:24.04
  services:
    - docker:24-dind
  script:
    - apt-get update && apt-get install -y python3 python3-venv docker.io docker-compose-v2
    - cd tests
    - ./run_docker_build_tests.sh -v -k "modelzoo and ${OS_DISTRO} and ${OS_VERSION}"
  artifacts:
    when: always
    paths:
      - tests/reports/
    expire_in: 7 days
  tags:
    - docker

modelzoo-ubuntu-24.04:
  <<: *modelzoo-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "24.04"

modelzoo-ubuntu-22.04:
  <<: *modelzoo-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "22.04"

modelzoo-ubuntu-20.04:
  <<: *modelzoo-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "20.04"

modelzoo-ubuntu-18.04:
  <<: *modelzoo-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "18.04"

modelzoo-debian-12:
  <<: *modelzoo-template
  variables:
    OS_DISTRO: "debian"
    OS_VERSION: "12"

modelzoo-debian-13:
  <<: *modelzoo-template
  variables:
    OS_DISTRO: "debian"
    OS_VERSION: "13"
  script:
    - apt-get update && apt-get install -y python3 python3-venv docker.io docker-compose-v2
    - cd tests
    - ./run_docker_build_tests.sh -v -k "modelzoo and debian and 13"

# dx-compiler build tests
.compiler-template: &compiler-template
  stage: build-compiler
  image: ubuntu:24.04
  services:
    - docker:24-dind
  script:
    - apt-get update && apt-get install -y python3 python3-venv docker.io docker-compose-v2
    - cd tests
    - ./run_docker_build_tests.sh -v -k "compiler and ${OS_DISTRO} and ${OS_VERSION}"
  artifacts:
    when: always
    paths:
      - tests/reports/
    expire_in: 7 days
  tags:
    - docker

compiler-ubuntu-24.04:
  <<: *compiler-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "24.04"

compiler-ubuntu-22.04:
  <<: *compiler-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "22.04"

compiler-ubuntu-20.04:
  <<: *compiler-template
  variables:
    OS_DISTRO: "ubuntu"
    OS_VERSION: "20.04"

# Generate test report
generate-report:
  stage: report
  image: ubuntu:24.04
  script:
    - echo "All tests completed"
    - ls -R tests/reports/ || true
  artifacts:
    paths:
      - tests/reports/
    expire_in: 30 days
  tags:
    - docker
```

### Simplified Pipeline (MR Validation)

```yaml
stages:
  - quick-test

quick-build-check:
  stage: quick-test
  image: ubuntu:24.04
  services:
    - docker:24-dind
  script:
    - apt-get update && apt-get install -y python3 python3-venv docker.io docker-compose-v2
    - cd tests
    - ./test.sh sanity
    - ./run_docker_build_tests.sh -v -k "ubuntu and 24.04"
  only:
    - merge_requests
  tags:
    - docker
```

## Jenkins

### Declarative Pipeline

`Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.10'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git submodule update --init --recursive'
            }
        }
        
        stage('Sanity Check') {
            steps {
                dir('tests') {
                    sh './test.sh sanity'
                }
            }
        }
        
        stage('Build Tests') {
            parallel {
                stage('dx-runtime') {
                    stages {
                        stage('Ubuntu 24.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "runtime and ubuntu and 24.04"'
                                }
                            }
                        }
                        stage('Ubuntu 22.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "runtime and ubuntu and 22.04"'
                                }
                            }
                        }
                        stage('Ubuntu 20.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "runtime and ubuntu and 20.04"'
                                }
                            }
                        }
                        stage('Ubuntu 18.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "runtime and ubuntu and 18.04"'
                                }
                            }
                        }
                        stage('Debian 12') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "runtime and debian and 12"'
                                }
                            }
                        }
                        stage('Debian 13') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "runtime and debian and 13"'
                                }
                            }
                        }
                    }
                }
                
                stage('dx-modelzoo') {
                    stages {
                        stage('Ubuntu 24.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "modelzoo and ubuntu and 24.04"'
                                }
                            }
                        }
                        stage('Ubuntu 22.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "modelzoo and ubuntu and 22.04"'
                                }
                            }
                        }
                        stage('Ubuntu 20.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "modelzoo and ubuntu and 20.04"'
                                }
                            }
                        }
                        stage('Ubuntu 18.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "modelzoo and ubuntu and 18.04"'
                                }
                            }
                        }
                        stage('Debian 12') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "modelzoo and debian and 12"'
                                }
                            }
                        }
                        stage('Debian 13') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "modelzoo and debian and 13"'
                                }
                            }
                        }
                    }
                }
                
                stage('dx-compiler') {
                    stages {
                        stage('Ubuntu 24.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "compiler and ubuntu and 24.04"'
                                }
                            }
                        }
                        stage('Ubuntu 22.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "compiler and ubuntu and 22.04"'
                                }
                            }
                        }
                        stage('Ubuntu 20.04') {
                            steps {
                                dir('tests') {
                                    sh './run_docker_build_tests.sh -v -k "compiler and ubuntu and 20.04"'
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stage('Generate Report') {
            steps {
                dir('tests') {
                    sh './test.sh report'
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'tests/reports/**/*', allowEmptyArchive: true
            
            // Publish HTML reports if using HTML Publisher plugin
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'tests/reports',
                reportFiles: '*.html',
                reportName: 'Docker Build Test Report'
            ])
        }
        
        success {
            echo 'All Docker build tests passed!'
        }
        
        failure {
            echo 'Some Docker build tests failed!'
        }
    }
}
```

### Scripted Pipeline (Simplified Version)

```groovy
node {
    stage('Checkout') {
        checkout scm
        sh 'git submodule update --init --recursive'
    }
    
    stage('Sanity Check') {
        dir('tests') {
            sh './test.sh sanity'
        }
    }
    
    stage('Quick Build Test') {
        dir('tests') {
            sh './run_docker_build_tests.sh -v -k "ubuntu and 24.04"'
        }
    }
    
    stage('Archive Results') {
        archiveArtifacts artifacts: 'tests/reports/**/*', allowEmptyArchive: true
    }
}
```

## General Guidelines

### 1. Parallel Execution Optimization

Parallel execution is recommended to reduce build time:

- **Strategy**: Run tests in parallel by OS version
- **Job Separation**: Separate runtime, modelzoo, and compiler into different jobs
- **Execution Order**: Sanity tests → Parallel build tests → Report generation

### 2. Caching Strategy

Leverage Docker layer caching to reduce build time:

```yaml
# GitHub Actions example
- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-
```

### 3. Timeout Settings

Set appropriate timeouts for each build:

```yaml
# GitHub Actions
timeout-minutes: 45

# GitLab CI
timeout: 45m

# Jenkins
timeout(time: 45, unit: 'MINUTES')
```

### 4. Artifact Management

Save test results as artifacts:

- HTML reports
- JSON reports
- Build logs
- **Retention period**: 7-30 days recommended

### 5. Failure Handling

```yaml
# Prevent one build failure from stopping the entire workflow
strategy:
  fail-fast: false  # GitHub Actions
# or
allow_failure: true  # GitLab CI
```

### 6. Notification Setup

Configure notifications for build failures:

- Slack integration
- Email notifications
- GitHub/GitLab comments

### 7. Scheduled Execution

Regular build validation:

```yaml
# GitHub Actions - Run daily at midnight
on:
  schedule:
    - cron: '0 0 * * *'

# GitLab CI - Run daily at midnight
only:
  - schedules
```

### 8. Resource Optimization

Optimize CI resource usage:

- **Sanity First**: Quick validation, fail early if issues detected
- **Selective Execution**: In PRs, test only changed targets
- **Prioritization**: Test frequently-used OS versions first

## Best Practices

### 1. PR Workflow

For Pull Requests:

- ✅ Sanity tests are mandatory
- ✅ Build test for latest OS version (24.04)
- ❌ Skip full test suite (save time)

### 2. Main/Develop Branch

For main branches:

- ✅ Run full test suite
- ✅ Validate all OS versions
- ✅ Generate and archive reports

### 3. Release Workflow

Before releases:

- ✅ Run full test suite
- ✅ Review reports
- ✅ Add manual approval step

### 4. Monitoring

Monitor CI/CD performance:

- Track build times
- Monitor success/failure rates
- Identify bottlenecks

## Additional Resources

- [README_DOCKER_BUILD_TESTS.md](README_DOCKER_BUILD_TESTS.md) - Basic usage
- [REFERENCE.sh](REFERENCE.sh) - Quick command reference
- [SUMMARY.md](SUMMARY.md) - Project overview
