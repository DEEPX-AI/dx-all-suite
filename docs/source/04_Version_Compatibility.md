# Version Compatibility

Since the **DEEPX SDK** maintains strict version dependencies between modules, it is essential to consult the compatibility matrix below when performing updates. **DX-AllSuite** ensures that all components are integrated and managed in validated, optimal combinations.  

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
      <td rowspan="3">2026-05-06</td>
      <td colspan="7">v2.3.1</td>
    </tr>
    <tr>
      <td colspan="2"><b>v2.3.1</b></td>
      <td colspan="5">v2.3.1</td>
    </tr>
    <tr>
      <td>v2.3.0</td>
      <td>v2.0.1</td>
      <td><b>v2.6.1</b></td>
      <td><b>v2.4.1</b></td>
      <td><b>v3.3.1</b></td>
      <td><b>v3.0.1</b></td>
      <td><b>v3.1.1</b></td>
    </tr>
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
      <td>v2.4.1</td>
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

To ensure system stability, identify the versions of your currently installed components and compare them with the **Version Compatibility Matrix** provided above.  

**Step 1. Hardware & Drivers (Target Side)**  
You can immediately verify the **Firmware (FW)** and **NPU Driver** versions using the NPU status utility.  
```Bash
# Display NPU status and driver information
dxrt-cli -s
```

**Step 2. Compiler (Host Side)**  
Verify the version of the model conversion tool (`dxcom`). Note that the virtual environment **must** be activated for the command to be recognized.
```Bash
# Execute within an activated virtual environment
dxcom -v
```

**Alternative (via Python)**  
If you are using the compiler as a library, you can also check the version directly via Python.  
```Bash
python3 -c "import dx_com; print(dx_com.__version__)"
```

Copyright © DEEPX. All rights reserved.

---
