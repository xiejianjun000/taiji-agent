# tools.government.smart_city

```include ../govmcp/tools/government/smart_city.py
```

## 模块文档

govmcp.tools.government.smart_city — 智慧城市工具模块

提供智慧交通、智慧水务、智慧社区、智慧养老、应急指挥等智慧城市服务的工具函数。

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| 17 | 低 | govmcp_tool(name='control_smart_traffic_light', description='智慧交通信号灯控制') |
| 51 | 低 | govmcp_tool(name='query_public_parking', description='查询公共停车位') |
| 90 | 低 | govmcp_tool(name='manage_smart_streetlight', description='智慧路灯管理') |
| 123 | 低 | govmcp_tool(name='monitor_smart_water', description='智慧水务监控') |
| 161 | 低 | govmcp_tool(name='supervise_smart_gas', description='智慧燃气监管') |
| 196 | 低 | govmcp_tool(name='manage_smart_heating', description='智慧供热管理') |
| 231 | 低 | govmcp_tool(name='query_smart_community', description='智慧社区服务查询') |
| 263 | 低 | govmcp_tool(name='query_smart_city_enforcement', description='智慧城管执法查询') |
| 302 | 低 | govmcp_tool(name='query_public_bicycle', description='查询公共自行车') |
| 343 | 低 | govmcp_tool(name='query_smart_elderly_care', description='智慧养老服务查询') |
| 379 | 低 | govmcp_tool(name='query_smart_education', description='智慧教育服务查询') |
| 419 | 低 | govmcp_tool(name='book_smart_medical', description='智慧医疗预约') |
| 462 | 低 | govmcp_tool(name='dispatch_emergency_command', description='应急指挥调度') |
| 503 | 低 | govmcp_tool(name='query_grid_management', description='网格化管理查询') |
| 544 | 低 | govmcp_tool(name='query_snow亮的视频', description='雪亮工程视频监控查询') |

## 导出函数

### `control_smart_traffic_light(intersection_id: str, action: str, duration: int) -> Dict[str, Any]`

`行号:17` `复杂度:低`

智慧交通信号灯控制。

Args:

    intersection_id: 路口编号

    action: 控制动作 (绿灯/黄灯/红灯/自适应)

    duration: 持续时间(秒)

Returns:

    控制结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `intersection_id` | `str` | `-` |
| `action` | `str` | `-` |
| `duration` | `int` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_public_parking(district: str, street: str) -> Dict[str, Any]`

`行号:51` `复杂度:低`

查询附近公共停车位信息。

Args:

    district: 行政区

    street: 街道

Returns:

    停车位信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `district` | `str` | `-` |
| `street` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `manage_smart_streetlight(streetlight_id: str, action: str, brightness: Optional[int] = None) -> Dict[str, Any]`

`行号:90` `复杂度:低`

智慧路灯管理控制。

Args:

    streetlight_id: 路灯编号

    action: 控制动作 (开灯/关灯/调光/故障上报)

    brightness: 亮度等级 (0-100)

Returns:

    控制结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `streetlight_id` | `str` | `-` |
| `action` | `str` | `-` |
| `brightness` (可选) | `Optional[int]` | `None` |

#### 返回

`Dict[str, Any]`

---

### `monitor_smart_water(area: str, meter_id: str) -> Dict[str, Any]`

`行号:123` `复杂度:低`

智慧水务监控系统。

Args:

    area: 区域名称

    meter_id: 水表编号

Returns:

    水务监控数据

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `area` | `str` | `-` |
| `meter_id` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `supervise_smart_gas(area: str, meter_id: str) -> Dict[str, Any]`

`行号:161` `复杂度:低`

智慧燃气监管系统。

Args:

    area: 区域名称

    meter_id: 燃气表编号

Returns:

    燃气监管数据

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `area` | `str` | `-` |
| `meter_id` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `manage_smart_heating(building_id: str, action: str, target_temperature: Optional[float] = None) -> Dict[str, Any]`

`行号:196` `复杂度:低`

智慧供热管理系统。

Args:

    building_id: 建筑编号

    action: 控制动作 (升温/降温/保温/关闭)

    target_temperature: 目标温度

Returns:

    供热管理数据

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `building_id` | `str` | `-` |
| `action` | `str` | `-` |
| `target_temperature` (可选) | `Optional[float]` | `None` |

#### 返回

`Dict[str, Any]`

---

### `query_smart_community(community_name: str, service_type: str) -> Dict[str, Any]`

`行号:231` `复杂度:低`

智慧社区服务查询。

Args:

    community_name: 社区名称

    service_type: 服务类型 (物业/安防/便民/养老)

Returns:

    社区服务信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `community_name` | `str` | `-` |
| `service_type` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_smart_city_enforcement(area: str, violation_type: Optional[str] = None) -> Dict[str, Any]`

`行号:263` `复杂度:低`

智慧城管执法系统查询。

Args:

    area: 执法区域

    violation_type: 违规类型 (占道经营/乱停乱放/违章建筑)

Returns:

    城管执法信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `area` | `str` | `-` |
| `violation_type` (可选) | `Optional[str]` | `None` |

#### 返回

`Dict[str, Any]`

---

### `query_public_bicycle(location: str) -> Dict[str, Any]`

`行号:302` `复杂度:低`

查询公共自行车站点信息。

Args:

    location: 当前位置或区域

Returns:

    公共自行车信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `location` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_smart_elderly_care(elderly_name: str, id_number: str, service_type: str) -> Dict[str, Any]`

`行号:343` `复杂度:低`

智慧养老服务查询。

Args:

    elderly_name: 老人姓名

    id_number: 身份证号码

    service_type: 服务类型 (居家/社区/机构)

Returns:

    养老服务信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `elderly_name` | `str` | `-` |
| `id_number` | `str` | `-` |
| `service_type` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_smart_education(student_name: str, student_id: str, service_type: str) -> Dict[str, Any]`

`行号:379` `复杂度:低`

智慧教育服务查询。

Args:

    student_name: 学生姓名

    student_id: 学籍号

    service_type: 服务类型 (学籍/成绩/选课/考勤)

Returns:

    教育服务信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `student_name` | `str` | `-` |
| `student_id` | `str` | `-` |
| `service_type` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `book_smart_medical(patient_name: str, id_number: str, hospital: str, department: str, booking_date: str, doctor: Optional[str] = None) -> Dict[str, Any]`

`行号:419` `复杂度:低`

智慧医疗预约挂号。

Args:

    patient_name: 患者姓名

    id_number: 身份证号码

    hospital: 医院名称

    department: 科室

    booking_date: 预约日期

    doctor: 医生姓名(可选)

Returns:

    预约结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `patient_name` | `str` | `-` |
| `id_number` | `str` | `-` |
| `hospital` | `str` | `-` |
| `department` | `str` | `-` |
| `booking_date` | `str` | `-` |
| `doctor` (可选) | `Optional[str]` | `None` |

#### 返回

`Dict[str, Any]`

---

### `dispatch_emergency_command(incident_type: str, location: str, severity: str, reporter: str, description: str) -> Dict[str, Any]`

`行号:462` `复杂度:低`

应急指挥调度系统。

Args:

    incident_type: 事件类型 (火灾/交通事故/自然灾害/公共卫生)

    location: 事发地点

    severity: 严重程度 (一般/较大/重大/特别重大)

    reporter: 上报人

    description: 事件描述

Returns:

    调度结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `incident_type` | `str` | `-` |
| `location` | `str` | `-` |
| `severity` | `str` | `-` |
| `reporter` | `str` | `-` |
| `description` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_grid_management(grid_id: str, query_type: str) -> Dict[str, Any]`

`行号:503` `复杂度:低`

网格化管理系统查询。

Args:

    grid_id: 网格编号

    query_type: 查询类型 (事件/巡查/人口/设施)

Returns:

    网格管理信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `grid_id` | `str` | `-` |
| `query_type` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_snow亮的视频(camera_id: str, query_type: str, start_time: str, end_time: str) -> Dict[str, Any]`

`行号:544` `复杂度:低`

雪亮工程视频监控系统查询。

Args:

    camera_id: 监控点编号

    query_type: 查询类型 (实时/回放/截图)

    start_time: 开始时间

    end_time: 结束时间

Returns:

    视频监控信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `camera_id` | `str` | `-` |
| `query_type` | `str` | `-` |
| `start_time` | `str` | `-` |
| `end_time` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

## Test Coverage

*No specific tests found for this module.*
