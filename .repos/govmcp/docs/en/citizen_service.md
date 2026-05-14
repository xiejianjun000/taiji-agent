# tools.government.citizen_service

```include ../govmcp/tools/government/citizen_service.py
```

## Module Documentation

govmcp.tools.government.citizen_service — 市民服务工具模块

提供身份证、户籍、社保、医保、公积金、交通、不动产等市民常用政务服务的工具函数。

### Parameters

| Line | Complexity | Decorators |
|:---|:---|:---|
| 17 | Low | govmcp_tool(name='query_id_card_progress', description='查询身份证办理进度') |
| 49 | Low | govmcp_tool(name='query_household_registration', description='查询户籍信息') |
| 79 | Low | govmcp_tool(name='query_social_security_account', description='查询社保账户信息') |
| 111 | Low | govmcp_tool(name='query_social_security_payment', description='查询社保缴费记录') |
| 146 | Low | govmcp_tool(name='query_medical_insurance_account', description='查询医保账户') |
| 178 | Low | govmcp_tool(name='query_medical_settlement', description='查询医保结算记录') |
| 226 | Low | govmcp_tool(name='query_housing_fund_account', description='查询公积金账户') |
| 259 | Low | govmcp_tool(name='apply_housing_fund_withdrawal', description='申请公积金提取') |
| 299 | Low | govmcp_tool(name='query_housing_fund_loan', description='查询公积金贷款进度') |
| 331 | Low | govmcp_tool(name='query_residence_permit', description='查询居住证办理进度') |
| 364 | Low | govmcp_tool(name='query_driver_license', description='查询驾驶证信息') |
| 397 | Low | govmcp_tool(name='query_vehicle_info', description='查询车辆信息') |
| 431 | Low | govmcp_tool(name='query_traffic_violation', description='查询交通违章记录') |
| 471 | Low | govmcp_tool(name='query_property_registration', description='查询不动产登记信息') |
| 504 | Low | govmcp_tool(name='query_utility_bill', description='查询水电气缴费记录') |
| 536 | Low | govmcp_tool(name='apply_low_income_assistance', description='申请低保救助') |
| 572 | Low | govmcp_tool(name='apply_disability_subsidy', description='申请残疾人补贴') |
| 608 | Low | govmcp_tool(name='apply_elderly_benefit_card', description='申请老年人优待证') |
| 642 | Low | govmcp_tool(name='book_marriage_registration', description='预约婚姻登记') |
| 683 | Low | govmcp_tool(name='register_fertility_service', description='生育服务登记') |

## Exported Functions

### `query_id_card_progress(name: str, id_number: str, phone: str) -> Dict[str, Any]`

`Line:17` `Complexity:Low`

查询身份证办理进度。

Args:

    name: 申请人姓名

    id_number: 身份证号码

    phone: 联系电话

Returns:

    办理进度信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `id_number` | `str` | `-` |
| `phone` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_household_registration(id_number: str, name: str) -> Dict[str, Any]`

`Line:49` `Complexity:Low`

查询户籍基本信息。

Args:

    id_number: 身份证号码

    name: 姓名

Returns:

    户籍信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `name` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_social_security_account(id_number: str, name: str) -> Dict[str, Any]`

`Line:79` `Complexity:Low`

查询社保账户余额和基本信息。

Args:

    id_number: 身份证号码

    name: 姓名

Returns:

    社保账户信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `name` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_social_security_payment(id_number: str, year: int, month: int) -> Dict[str, Any]`

`Line:111` `Complexity:Low`

查询社保缴费明细记录。

Args:

    id_number: 身份证号码

    year: 查询年份

    month: 查询月份

Returns:

    缴费记录详情

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `year` | `int` | `-` |
| `month` | `int` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_medical_insurance_account(id_number: str, name: str) -> Dict[str, Any]`

`Line:146` `Complexity:Low`

查询医保个人账户余额和消费记录。

Args:

    id_number: 身份证号码

    name: 姓名

Returns:

    医保账户信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `name` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_medical_settlement(id_number: str, start_date: str, end_date: str) -> Dict[str, Any]`

`Line:178` `Complexity:Low`

查询医保结算明细。

Args:

    id_number: 身份证号码

    start_date: 开始日期 (YYYY-MM-DD)

    end_date: 结束日期 (YYYY-MM-DD)

Returns:

    结算记录列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `start_date` | `str` | `-` |
| `end_date` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_housing_fund_account(id_number: str, name: str) -> Dict[str, Any]`

`Line:226` `Complexity:Low`

查询公积金账户余额。

Args:

    id_number: 身份证号码

    name: 姓名

Returns:

    公积金账户信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `name` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `apply_housing_fund_withdrawal(id_number: str, name: str, withdrawal_type: str, amount: float, bank_name: str, bank_account: str) -> Dict[str, Any]`

`Line:259` `Complexity:Low`

申请公积金提取。

Args:

    id_number: 身份证号码

    name: 姓名

    withdrawal_type: 提取类型 (租房/购房/还贷/离职等)

    amount: 提取金额

    bank_name: 银行名称

    bank_account: 银行账号

Returns:

    申请结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `name` | `str` | `-` |
| `withdrawal_type` | `str` | `-` |
| `amount` | `float` | `-` |
| `bank_name` | `str` | `-` |
| `bank_account` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_housing_fund_loan(id_number: str, loan_app_no: str) -> Dict[str, Any]`

`Line:299` `Complexity:Low`

查询公积金贷款申请进度。

Args:

    id_number: 身份证号码

    loan_app_no: 贷款申请编号

Returns:

    贷款进度信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `loan_app_no` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_residence_permit(name: str, id_number: str, phone: str) -> Dict[str, Any]`

`Line:331` `Complexity:Low`

查询居住证办理进度。

Args:

    name: 申请人姓名

    id_number: 身份证号码

    phone: 联系电话

Returns:

    居住证办理进度

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `id_number` | `str` | `-` |
| `phone` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_driver_license(name: str, license_no: str) -> Dict[str, Any]`

`Line:364` `Complexity:Low`

查询驾驶证信息。

Args:

    name: 姓名

    license_no: 驾驶证号码

Returns:

    驾驶证信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `license_no` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_vehicle_info(plate_number: str, id_number: str) -> Dict[str, Any]`

`Line:397` `Complexity:Low`

查询车辆登记信息。

Args:

    plate_number: 车牌号

    id_number: 车主身份证号

Returns:

    车辆信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `plate_number` | `str` | `-` |
| `id_number` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_traffic_violation(plate_number: str, id_number: str) -> Dict[str, Any]`

`Line:431` `Complexity:Low`

查询车辆交通违章记录。

Args:

    plate_number: 车牌号

    id_number: 车主身份证号

Returns:

    违章记录列表

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `plate_number` | `str` | `-` |
| `id_number` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_property_registration(id_number: str, property_address: str) -> Dict[str, Any]`

`Line:471` `Complexity:Low`

查询不动产登记信息。

Args:

    id_number: 身份证号码

    property_address: 不动产地址

Returns:

    登记信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `id_number` | `str` | `-` |
| `property_address` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `query_utility_bill(account_no: str, bill_type: str) -> Dict[str, Any]`

`Line:504` `Complexity:Low`

查询水电气等公用事业缴费情况。

Args:

    account_no: 户号

    bill_type: 缴费类型 (水/电/气)

Returns:

    缴费信息

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `account_no` | `str` | `-` |
| `bill_type` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `apply_low_income_assistance(name: str, id_number: str, address: str, income: float, family_size: int) -> Dict[str, Any]`

`Line:536` `Complexity:Low`

申请最低生活保障救助。

Args:

    name: 申请人姓名

    id_number: 身份证号码

    address: 家庭住址

    income: 家庭月收入

    family_size: 家庭人口数

Returns:

    申请结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `id_number` | `str` | `-` |
| `address` | `str` | `-` |
| `income` | `float` | `-` |
| `family_size` | `int` | `-` |

#### Returns

`Dict[str, Any]`

---

### `apply_disability_subsidy(name: str, id_number: str, disability_level: str, disability_cert_no: str) -> Dict[str, Any]`

`Line:572` `Complexity:Low`

申请残疾人补贴。

Args:

    name: 申请人姓名

    id_number: 身份证号码

    disability_level: 残疾等级 (1-4级)

    disability_cert_no: 残疾证号

Returns:

    申请结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `id_number` | `str` | `-` |
| `disability_level` | `str` | `-` |
| `disability_cert_no` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `apply_elderly_benefit_card(name: str, id_number: str, birth_date: str) -> Dict[str, Any]`

`Line:608` `Complexity:Low`

申请老年人优待证。

Args:

    name: 申请人姓名

    id_number: 身份证号码

    birth_date: 出生日期

Returns:

    申请结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `id_number` | `str` | `-` |
| `birth_date` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `book_marriage_registration(name1: str, id_number1: str, name2: str, id_number2: str, book_date: str, location: str) -> Dict[str, Any]`

`Line:642` `Complexity:Low`

预约婚姻登记。

Args:

    name1: 申请人1姓名

    id_number1: 申请人1身份证号

    name2: 申请人2姓名

    id_number2: 申请人2身份证号

    book_date: 预约日期 (YYYY-MM-DD)

    location: 登记地点

Returns:

    预约结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name1` | `str` | `-` |
| `id_number1` | `str` | `-` |
| `name2` | `str` | `-` |
| `id_number2` | `str` | `-` |
| `book_date` | `str` | `-` |
| `location` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

### `register_fertility_service(name: str, id_number: str, spouse_name: str, spouse_id_number: str, expected_date: str) -> Dict[str, Any]`

`Line:683` `Complexity:Low`

生育服务登记（准生证办理）。

Args:

    name: 女方姓名

    id_number: 女方身份证号

    spouse_name: 男方姓名

    spouse_id_number: 男方身份证号

    expected_date: 预产期

Returns:

    登记结果

#### Parameters

| Name | Type | Default |
|:---|:---|:---|
| `name` | `str` | `-` |
| `id_number` | `str` | `-` |
| `spouse_name` | `str` | `-` |
| `spouse_id_number` | `str` | `-` |
| `expected_date` | `str` | `-` |

#### Returns

`Dict[str, Any]`

---

## Test Coverage

*No specific tests found for this module.*
