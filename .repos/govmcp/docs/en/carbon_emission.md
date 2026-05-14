# tools.government.carbon_emission

```include ../govmcp/tools/government/carbon_emission.py
```

## Module Documentation

govmcp.tools.government.carbon_emission — 碳排放管理工具模块

提供企业碳排放数据录入、碳交易、碳足迹计算、碳中和追踪等碳排放管理服务的工具函数。

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 17 | Low | govmcp_tool(name='input_carbon_emission_data', description='录入企业碳排放数据') |
| 72 | Low | govmcp_tool(name='query_carbon_quota', description='查询碳排放配额') |
| 108 | Low | govmcp_tool(name='trade_carbon_emission_allowance', description='碳排放权交易') |
| 145 | Low | govmcp_tool(name='generate_carbon_emission_report', description='生成碳排放报告') |
| 184 | Low | govmcp_tool(name='calculate_carbon_footprint', description='计算碳足迹') |
| 233 | Low | govmcp_tool(name='set_emission_reduction_target', description='设定减排目标') |
| 275 | Low | govmcp_tool(name='apply_carbon_verification', description='申请碳核查') |
| 311 | Low | govmcp_tool(name='register_ccer_project', description='CCER项目登记') |
| 350 | Low | govmcp_tool(name='query_carbon_asset_account', description='查询碳资产账户') |
| 383 | Low | govmcp_tool(name='query_carbon_monitoring_data', description='查询碳排放监测数据') |
| 424 | Low | govmcp_tool(name='analyze_industrial_carbon_emission', description='工业碳排放分析') |
| 463 | Low | govmcp_tool(name='query_energy_consumption', description='查询能源消耗统计') |
| 503 | Low | govmcp_tool(name='query_green_electricity_trade', description='查询绿电交易') |
| 547 | Low | govmcp_tool(name='track_carbon_neutrality_progress', description='追踪碳中和进度') |
| 583 | Low | govmcp_tool(name='predict_carbon_emission', description='碳排放预测分析') |

## Exported Functions

### `input_carbon_emission_data(company_name: str, credit_code: str, reporting_year: int, reporting_quarter: int, coal_consumption: float, oil_consumption: float, natural_gas_consumption: float, electricity_consumption: float) -> Dict[str, Any]`

`Line:17` `Complexity:Low`

录入企业碳排放活动数据。

Args:

    company_name: 企业名称

    credit_code: 统一社会信用代码

    reporting_year: 报告年度

    reporting_quarter: 报告季度 (1-4)

    coal_consumption: 煤炭消耗量(吨)

    oil_consumption: 石油消耗量(吨)

    natural_gas_consumption: 天然气消耗量(万立方米)

    electricity_consumption: 外购电力消耗量(万千瓦时)

Returns:

    数据录入结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `credit_code` | `str` | `-` |
| `reporting_year` | `int` | `-` |
| `reporting_quarter` | `int` | `-` |
| `coal_consumption` | `float` | `-` |
| `oil_consumption` | `float` | `-` |
| `natural_gas_consumption` | `float` | `-` |
| `electricity_consumption` | `float` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_carbon_quota(company_name: str, credit_code: str, year: int) -> Dict[str, Any]`

`Line:72` `Complexity:Low`

查询企业碳排放配额分配情况。

Args:

    company_name: 企业名称

    credit_code: 统一社会信用代码

    year: 查询年度

Returns:

    碳配额信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `credit_code` | `str` | `-` |
| `year` | `int` | `-` |

#### Returns

`Dict[str, Any]`

---

### `trade_carbon_emission_allowance(company_name: str, trade_type: str, quantity: float, price: float) -> Dict[str, Any]`

`Line:108` `Complexity:Low`

碳排放权交易（买入/卖出配额）。

Args:

    company_name: 企业名称

    trade_type: 交易类型 (买入/卖出)

    quantity: 交易数量(吨CO2)

    price: 交易价格(元/吨)

Returns:

    交易结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `trade_type` | `str` | `-` |
| `quantity` | `float` | `-` |
| `price` | `float` | `-` |

#### Returns

`Dict[str, Any]`

---

### `generate_carbon_emission_report(company_name: str, credit_code: str, year: int, report_type: str) -> Dict[str, Any]`

`Line:145` `Complexity:Low`

生成企业碳排放报告。

Args:

    company_name: 企业名称

    credit_code: 统一社会信用代码

    year: 报告年度

    report_type: 报告类型 (年度/季度/月度)

Returns:

    报告生成结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `credit_code` | `str` | `-` |
| `year` | `int` | `-` |
| `report_type` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `calculate_carbon_footprint(product_name: str, raw_materials: Dict[str, float], manufacturing_energy: float, transportation_distance: float, packaging_weight: float) -> Dict[str, Any]`

`Line:184` `Complexity:Low`

计算产品碳足迹。

Args:

    product_name: 产品名称

    raw_materials: 原材料消耗字典 {材料名: 数量(kg)}

    manufacturing_energy: 制造过程能源消耗(kWh)

    transportation_distance: 运输距离(km)

    packaging_weight: 包装材料重量(kg)

Returns:

    碳足迹计算结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `product_name` | `str` | `-` |
| `raw_materials` | `Dict[str, float]` | `-` |
| `manufacturing_energy` | `float` | `-` |
| `transportation_distance` | `float` | `-` |
| `packaging_weight` | `float` | `-` |

#### Returns

`Dict[str, Any]`

---

### `set_emission_reduction_target(company_name: str, base_year: int, base_emission: float, target_year: int, target_reduction_ratio: float) -> Dict[str, Any]`

`Line:233` `Complexity:Low`

设定企业碳减排目标。

Args:

    company_name: 企业名称

    base_year: 基准年

    base_emission: 基准年排放量(吨)

    target_year: 目标年

    target_reduction_ratio: 目标减排比例

Returns:

    减排目标信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `base_year` | `int` | `-` |
| `base_emission` | `float` | `-` |
| `target_year` | `int` | `-` |
| `target_reduction_ratio` | `float` | `-` |

#### Returns

`Dict[str, Any]`

---

### `apply_carbon_verification(company_name: str, credit_code: str, reporting_year: int, verification_body: str) -> Dict[str, Any]`

`Line:275` `Complexity:Low`

申请碳排放核查。

Args:

    company_name: 企业名称

    credit_code: 统一社会信用代码

    reporting_year: 报告年度

    verification_body: 核查机构

Returns:

    核查申请结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `credit_code` | `str` | `-` |
| `reporting_year` | `int` | `-` |
| `verification_body` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `register_ccer_project(company_name: str, project_type: str, project_capacity: float, start_date: str, location: str) -> Dict[str, Any]`

`Line:311` `Complexity:Low`

登记CCER（中国核证自愿减排量）项目。

Args:

    company_name: 企业名称

    project_type: 项目类型 (风电/光伏/甲烷利用/造林等)

    project_capacity: 项目规模

    start_date: 项目开始日期

    location: 项目所在地

Returns:

    项目登记结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `project_type` | `str` | `-` |
| `project_capacity` | `float` | `-` |
| `start_date` | `str` | `-` |
| `location` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_carbon_asset_account(company_name: str, credit_code: str) -> Dict[str, Any]`

`Line:350` `Complexity:Low`

查询企业碳资产账户信息。

Args:

    company_name: 企业名称

    credit_code: 统一社会信用代码

Returns:

    碳资产账户信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `credit_code` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_carbon_monitoring_data(company_name: str, monitor_point: str, start_date: str, end_date: str) -> Dict[str, Any]`

`Line:383` `Complexity:Low`

查询碳排放连续监测数据。

Args:

    company_name: 企业名称

    monitor_point: 监测点位

    start_date: 开始日期

    end_date: 结束日期

Returns:

    监测数据列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `monitor_point` | `str` | `-` |
| `start_date` | `str` | `-` |
| `end_date` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `analyze_industrial_carbon_emission(industry: str, region: str, year: int) -> Dict[str, Any]`

`Line:424` `Complexity:Low`

工业行业碳排放分析。

Args:

    industry: 行业类型

    region: 地区

    year: 分析年度

Returns:

    碳排放分析报告

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `industry` | `str` | `-` |
| `region` | `str` | `-` |
| `year` | `int` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_energy_consumption(company_name: str, year: int, month: int) -> Dict[str, Any]`

`Line:463` `Complexity:Low`

查询企业能源消耗统计数据。

Args:

    company_name: 企业名称

    year: 年份

    month: 月份

Returns:

    能源消耗统计

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `year` | `int` | `-` |
| `month` | `int` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_green_electricity_trade(company_name: str, year: int) -> Dict[str, Any]`

`Line:503` `Complexity:Low`

查询绿色电力交易信息。

Args:

    company_name: 企业名称

    year: 查询年度

Returns:

    绿电交易信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `year` | `int` | `-` |

#### Returns

`Dict[str, Any]`

---

### `track_carbon_neutrality_progress(company_name: str, target_year: int) -> Dict[str, Any]`

`Line:547` `Complexity:Low`

追踪企业碳中和实施进度。

Args:

    company_name: 企业名称

    target_year: 目标实现年份

Returns:

    碳中和进度追踪

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `target_year` | `int` | `-` |

#### Returns

`Dict[str, Any]`

---

### `predict_carbon_emission(company_name: str, historical_data: List[Dict[str, Any]], forecast_years: int) -> Dict[str, Any]`

`Line:583` `Complexity:Low`

碳排放预测分析。

Args:

    company_name: 企业名称

    historical_data: 历史排放数据列表

    forecast_years: 预测年数

Returns:

    预测分析结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `historical_data` | `List[Dict[str, Any]]` | `-` |
| `forecast_years` | `int` | `-` |

#### Returns

`Dict[str, Any]`

---

## Test Coverage

*No specific tests found for this module.*
