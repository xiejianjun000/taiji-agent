# tools.government.environmental

```include ../govmcp/tools/government/environmental.py
```

## Module Documentation

govmcp.tools.government.environmental — 环保监测工具模块

提供空气质量、水质、土壤、噪声、固废等环境监测和环保监管服务的工具函数。

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 17 | Low | govmcp_tool(name='query_air_quality', description='查询空气质量监测数据') |
| 56 | Low | govmcp_tool(name='query_water_quality', description='查询水质监测数据') |
| 94 | Low | govmcp_tool(name='detect_soil_pollution', description='土壤污染检测') |
| 133 | Low | govmcp_tool(name='query_noise_monitoring', description='查询噪声监测数据') |
| 168 | Low | govmcp_tool(name='query_solid_waste_disposal', description='查询固废处理监管信息') |
| 202 | Low | govmcp_tool(name='query_hazardous_waste_transfer', description='查询危险废物转移联单') |
| 234 | Low | govmcp_tool(name='query_radiation_monitoring', description='查询辐射环境监测数据') |
| 269 | Low | govmcp_tool(name='query_pollution_discharge_permit', description='查询排污许可证信息') |
| 307 | Low | govmcp_tool(name='query_environmental_impact_assessment', description='查询环境影响评价信息') |
| 340 | Low | govmcp_tool(name='query_environmental_penalty', description='查询环保处罚记录') |
| 370 | Low | govmcp_tool(name='apply_cleaner_production_audit', description='申请清洁生产审核') |
| 405 | Low | govmcp_tool(name='query_environmental_acceptance', description='查询环保竣工验收信息') |
| 438 | Low | govmcp_tool(name='query_environmental_facility_operation', description='查询环保设施运行数据') |
| 473 | Low | govmcp_tool(name='query_ecological_red_line', description='查询生态红线保护区信息') |
| 507 | Low | govmcp_tool(name='query_environmental_emergency_response', description='查询环境应急响应信息') |

## Exported Functions

### `query_air_quality(region: str, monitoring_station: str, date: str) -> Dict[str, Any]`

`Line:17` `Complexity:Low`

查询空气质量监测数据。

Args:

    region: 地区名称

    monitoring_station: 监测站点

    date: 查询日期 (YYYY-MM-DD)

Returns:

    空气质量数据

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `region` | `str` | `-` |
| `monitoring_station` | `str` | `-` |
| `date` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_water_quality(river_name: str, section_name: str, date: str) -> Dict[str, Any]`

`Line:56` `Complexity:Low`

查询水质监测数据。

Args:

    river_name: 河流名称

    section_name: 断面名称

    date: 查询日期

Returns:

    水质监测数据

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `river_name` | `str` | `-` |
| `section_name` | `str` | `-` |
| `date` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `detect_soil_pollution(location: str, land_use: str, sampling_date: str) -> Dict[str, Any]`

`Line:94` `Complexity:Low`

土壤污染状况检测查询。

Args:

    location: 地块位置

    land_use: 土地利用类型

    sampling_date: 采样日期

Returns:

    土壤污染检测结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `location` | `str` | `-` |
| `land_use` | `str` | `-` |
| `sampling_date` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_noise_monitoring(monitoring_point: str, date: str, time_period: str) -> Dict[str, Any]`

`Line:133` `Complexity:Low`

查询环境噪声监测数据。

Args:

    monitoring_point: 监测点位

    date: 查询日期

    time_period: 时段 (昼间/夜间)

Returns:

    噪声监测数据

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `monitoring_point` | `str` | `-` |
| `date` | `str` | `-` |
| `time_period` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_solid_waste_disposal(company_name: str, waste_type: str) -> Dict[str, Any]`

`Line:168` `Complexity:Low`

查询固体废物处理处置监管信息。

Args:

    company_name: 企业名称

    waste_type: 废物类型 (一般固废/危险废物)

Returns:

    固废处理监管信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `waste_type` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_hazardous_waste_transfer(manifest_no: str) -> Dict[str, Any]`

`Line:202` `Complexity:Low`

查询危险废物转移联单信息。

Args:

    manifest_no: 转移联单编号

Returns:

    危废转移联单信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `manifest_no` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_radiation_monitoring(monitoring_location: str, monitoring_type: str, date: str) -> Dict[str, Any]`

`Line:234` `Complexity:Low`

查询辐射环境监测数据。

Args:

    monitoring_location: 监测地点

    monitoring_type: 监测类型 (γ辐射/氡/电磁辐射)

    date: 监测日期

Returns:

    辐射监测数据

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `monitoring_location` | `str` | `-` |
| `monitoring_type` | `str` | `-` |
| `date` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_pollution_discharge_permit(company_name: str, permit_no: str) -> Dict[str, Any]`

`Line:269` `Complexity:Low`

查询企业排污许可证信息。

Args:

    company_name: 企业名称

    permit_no: 许可证编号

Returns:

    排污许可证信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `permit_no` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_environmental_impact_assessment(project_name: str, eia_document_no: str) -> Dict[str, Any]`

`Line:307` `Complexity:Low`

查询环境影响评价信息。

Args:

    project_name: 项目名称

    eia_document_no: 环评批复文号

Returns:

    环评信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `project_name` | `str` | `-` |
| `eia_document_no` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_environmental_penalty(company_name: str, region: str) -> Dict[str, Any]`

`Line:340` `Complexity:Low`

查询企业环保行政处罚记录。

Args:

    company_name: 企业名称

    region: 地区

Returns:

    处罚记录列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `region` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `apply_cleaner_production_audit(company_name: str, industry: str, production_scale: str) -> Dict[str, Any]`

`Line:370` `Complexity:Low`

申请清洁生产审核。

Args:

    company_name: 企业名称

    industry: 行业类型

    production_scale: 生产规模

Returns:

    审核申请结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `industry` | `str` | `-` |
| `production_scale` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_environmental_acceptance(project_name: str, acceptance_no: str) -> Dict[str, Any]`

`Line:405` `Complexity:Low`

查询建设项目竣工环境保护验收信息。

Args:

    project_name: 项目名称

    acceptance_no: 验收备案号

Returns:

    环保竣工验收信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `project_name` | `str` | `-` |
| `acceptance_no` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_environmental_facility_operation(company_name: str, facility_type: str) -> Dict[str, Any]`

`Line:438` `Complexity:Low`

查询企业环保设施运行数据。

Args:

    company_name: 企业名称

    facility_type: 设施类型 (废气处理/废水处理/噪声控制)

Returns:

    环保设施运行数据

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `facility_type` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_ecological_red_line(location: str) -> Dict[str, Any]`

`Line:473` `Complexity:Low`

查询区域生态红线保护信息。

Args:

    location: 地理位置

Returns:

    生态红线信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `location` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_environmental_emergency_response(company_name: str) -> Dict[str, Any]`

`Line:507` `Complexity:Low`

查询企业环境应急响应相关信息。

Args:

    company_name: 企业名称

Returns:

    环境应急响应信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

## Test Coverage

*No specific tests found for this module.*
