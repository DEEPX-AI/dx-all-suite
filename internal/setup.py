from setuptools import find_packages, setup

setup(
    name="dx-as-internal-automation",
    version="0.1.0",
    author="DeepX",
    author_email="dhyang@deepx.ai",
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["*"]),
    python_requires=">=3.8",
    entry_points={"console_scripts": ["dx-aws-s3=aws_s3_manager.main:main"]},
    install_requires=[
        "requests",
        "boto3"
    ],
    extras_require={
        "test": [
            "pytest",
        ],
    },
)
