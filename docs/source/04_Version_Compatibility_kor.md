# Version Compatibility

**DEEPX SDK**는 모듈 간의 엄격한 버전 의존성을 유지하므로, 업데이트를 수행할 때 아래의 호환성 매트릭스를 참조하는 것이 필수적입니다. **DX-AllSuite**는 모든 구성 요소가 검증된 최적의 조합으로 통합되고 관리되도록 보장합니다.  

## DXNN SDK Version Compatibility Matrix

<table style="border-collapse: collapse; margin-bottom: 0px; width: 100%; text-align: center;" cellpadding="0" cellspacing="0">
  <thead align="center"> <tr>
      <th rowspan="4">Release Date</th>
      <th colspan="7">DX-AllSuite</th>
    </tr>
    <tr>
      <th colspan="2">DX-Compiler</th>
      <th colspan="5">DX-Runtime</th>
    </tr>
    <tr>
      <th>DX-COM</th>
      <th>DX-TRON</th>
      <th>DX-FW</th>
      <th>NPU Driver</th>
      <th>DX-RT</th>
      <th>DX-Stream</th>
      <th>DX-APP</th>
    </tr>
  </thead>
  <tbody align="center">
    <tr>
      <td rowspan="3">2026-04-10</td>
      <td colspan="7">v2.3.0</td>
    </tr>
    <tr>
      <td colspan="2">v2.3.0</td>
      <td colspan="5">v2.3.0</td>
    </tr>
    <tr>
      <td>v2.3.0</td>
      <td>v2.0.1</td>
      <td>v2.5.6</td>
      <td>v2.4.0</td>
      <td>v3.3.0</td>
      <td>v3.0.0</td>
      <td>v3.1.0</td>
    </tr>
    <tr>
      <td rowspan="3">2026-02-26</td>
      <td colspan="7">v2.2.2</td>
    </tr>
    <tr>
      <td colspan="2">v2.2.1</td>
      <td colspan="5">v2.2.2</td>
    </tr>
    <tr>
      <td>v2.2.1</td>
      <td>v2.0.1</td>
      <td>v2.5.0</td>
      <td>v2.1.0</td>
      <td>v3.2.0</td>
      <td>v2.2.1</td>
      <td>v3.0.2</td>
    </tr>
    <tr>
      <td rowspan="3">2026-02-09</td>
      <td colspan="7">v2.2.1</td>
    </tr>
    <tr>
      <td colspan="2">v2.2.0</td>
      <td colspan="5">v2.2.1</td>
    </tr>
    <tr>
      <td>v2.2.0</td>
      <td>v2.0.1</td>
      <td>v2.5.0</td>
      <td>v2.1.0</td>
      <td>v3.2.0</td>
      <td>v2.2.0</td>
      <td>v3.0.1</td>
    </tr>
    <tr>
      <td rowspan="3">2026-01-16</td>
      <td colspan="7">v2.2.0</td>
    </tr>
    <tr>
      <td colspan="2">v2.2.0</td>
      <td colspan="5">v2.2.0</td>
    </tr>
    <tr>
      <td>v2.2.0</td>
      <td>v2.0.1</td>
      <td>v2.5.0</td>
      <td>v2.1.0</td>
      <td>v3.2.0</td>
      <td>v2.2.0</td>
      <td>v3.0.0</td>
    </tr>
    <tr>
      <td rowspan="3">2025-11-28</td>
      <td colspan="7">v2.1.0</td>
    </tr>
    <tr>
      <td colspan="2">v2.1.0</td>
      <td colspan="5">v2.1.0</td>
    </tr>
    <tr>
      <td>v2.1.0</td>
      <td>v2.0.0</td>
      <td>v2.4.0</td>
      <td>v1.8.0</td>
      <td>v3.1.0</td>
      <td>v2.1.0</td>
      <td>v2.1.0</td>
    </tr>
    <tr>
      <td rowspan="3">2025-09-08</td>
      <td colspan="7">v2.0.0</td>
    </tr>
    <tr>
      <td colspan="2">v2.0.0</td>
      <td colspan="5">v2.0.0</td>
    </tr>
    <tr>
      <td>v2.0.0</td>
      <td>v2.0.0</td>
      <td>v2.1.4</td>
      <td>v1.7.1</td>
      <td>v3.0.0</td>
      <td>v2.0.0</td>
      <td>v2.0.0</td>
    </tr>
    <tr>
      <td rowspan="3">2025-07-23</td>
      <td colspan="7">v1.0.0</td>
    </tr>
    <tr>
      <td colspan="2">v1.0.0</td>
      <td colspan="5">v1.0.0</td>
    </tr>
    <tr>
      <td>v1.60.1</td>
      <td>v0.0.8</td>
      <td>v2.1.0</td>
      <td>v1.5.0</td>
      <td>v2.9.5</td>
      <td>v1.7.0</td>
      <td>v1.11.0</td>
    </tr>
  </tbody>
</table>

---

## How to Check Your System Version

시스템 안정성을 보장하기 위해 현재 설치된 구성 요소의 버전을 확인하고, 위에 제공된 **버전 호환성 매트릭스 (Version Compatibility Matrix)**와 비교하십시오.  

**단계 1. 하드웨어 및 드라이버 (타겟 측)**  
NPU 상태 유틸리티를 사용하여 **펌웨어(FW)** 및 **NPU 드라이버** 버전을 즉시 확인할 수 있습니다.  
```Bash
# Display NPU status and driver information
dxrt-cli -s
```

**단계 2. 컴파일러 (호스트 측)**  
모델 변환 도구(`dxcom`)의 버전을 확인합니다. 명령어를 인식하려면 반드시 가상 환경이 **활성화**되어 있어야 함에 유의하십시오.  
```Bash
# Execute within an activated virtual environment
dxcom -v
```

**대안 방법 (Python 사용 시)**  
컴파일러를 라이브러리로 사용 중인 경우 Python을 통해 버전을 직접 확인할 수도 있습니다.  
```Bash
python3 -c "import dx_com; print(dx_com.__version__)"
```

Copyright © DEEPX. All rights reserved.

---
