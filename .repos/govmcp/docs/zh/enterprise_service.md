# tools.government.enterprise_service

```include ../govmcp/tools/government/enterprise_service.py
```

## 模块文档

govmcp.tools.government.enterprise_service — 企业服务工具模块

提供工商登记、税务、许可证、知识产权、政府采购等企业常用政务服务的工具函数。

### 参数

| 行号 | 复杂度 | 装饰器 |
|:---|:---|:---|
| 17 | 低 | govmcp_tool(name='query_business_registration', description='查询企业工商登记信息') |
| 51 | 低 | govmcp_tool(name='apply_business_license', description='办理营业执照') |
| 91 | 低 | govmcp_tool(name='query_tax_registration', description='查询税务登记信息') |
| 123 | 低 | govmcp_tool(name='apply_invoice', description='申领发票') |
| 159 | 低 | govmcp_tool(name='apply_social_security_account', description='办理社保开户') |
| 196 | 低 | govmcp_tool(name='apply_housing_fund_account_enterprise', description='办理公积金开户') |
| 231 | 低 | govmcp_tool(name='query_environmental_impact_approval', description='查询环评审批进度') |
| 262 | 低 | govmcp_tool(name='query_fire_approval', description='查询消防审批进度') |
| 293 | 低 | govmcp_tool(name='query_building_permit', description='查询建筑许可审批进度') |
| 324 | 低 | govmcp_tool(name='apply_food_business_license', description='申请食品经营许可证') |
| 359 | 低 | govmcp_tool(name='apply_drug_operation_license', description='申请药品经营许可证') |
| 394 | 低 | govmcp_tool(name='apply_medical_device_license', description='申请医疗器械经营许可证') |
| 427 | 低 | govmcp_tool(name='apply_intellectual_property', description='申请知识产权保护') |
| 463 | 低 | govmcp_tool(name='query_trademark_registration', description='查询商标注册进度') |
| 496 | 低 | govmcp_tool(name='query_patent_application', description='查询专利申请进度') |
| 529 | 低 | govmcp_tool(name='apply_high_tech_enterprise', description='申请高新技术企业认定') |
| 565 | 低 | govmcp_tool(name='apply_tech_project', description='申报科技项目') |
| 601 | 低 | govmcp_tool(name='query_government_procurement', description='查询政府采购招标信息') |
| 638 | 低 | govmcp_tool(name='query_enterprise_credit_report', description='查询企业信用报告') |
| 673 | 低 | govmcp_tool(name='query_listing_guidance_progress', description='查询上市辅导进度') |

## 导出函数

### `query_business_registration(company_name: str, unified_social_credit_code: str) -> Dict[str, Any]`

`行号:17` `复杂度:低`

查询企业工商登记注册信息。

Args:

    company_name: 企业名称

    unified_social_credit_code: 统一社会信用代码

Returns:

    工商登记信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `unified_social_credit_code` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_business_license(company_name: str, company_type: str, registered_capital: float, business_scope: str, address: str, legal_person: str, id_number: str) -> Dict[str, Any]`

`行号:51` `复杂度:低`

申请办理营业执照。

Args:

    company_name: 企业名称

    company_type: 企业类型

    registered_capital: 注册资本

    business_scope: 经营范围

    address: 注册地址

    legal_person: 法定代表人

    id_number: 法定代表人身份证号

Returns:

    申请结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `company_type` | `str` | `-` |
| `registered_capital` | `float` | `-` |
| `business_scope` | `str` | `-` |
| `address` | `str` | `-` |
| `legal_person` | `str` | `-` |
| `id_number` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_tax_registration(company_name: str, tax_id: str) -> Dict[str, Any]`

`行号:91` `复杂度:低`

查询企业税务登记信息。

Args:

    company_name: 企业名称

    tax_id: 纳税人识别号

Returns:

    税务登记信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `tax_id` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_invoice(company_name: str, tax_id: str, invoice_type: str, quantity: int) -> Dict[str, Any]`

`行号:123` `复杂度:低`

申领增值税发票。

Args:

    company_name: 企业名称

    tax_id: 纳税人识别号

    invoice_type: 发票类型 (增值税专用发票/普通发票)

    quantity: 申领数量

Returns:

    申领结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `tax_id` | `str` | `-` |
| `invoice_type` | `str` | `-` |
| `quantity` | `int` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_social_security_account(company_name: str, credit_code: str, legal_person: str, employee_count: int, address: str) -> Dict[str, Any]`

`行号:159` `复杂度:低`

办理企业社会保险开户。

Args:

    company_name: 企业名称

    credit_code: 统一社会信用代码

    legal_person: 法定代表人

    employee_count: 员工人数

    address: 经营地址

Returns:

    开户结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `credit_code` | `str` | `-` |
| `legal_person` | `str` | `-` |
| `employee_count` | `int` | `-` |
| `address` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_housing_fund_account_enterprise(company_name: str, credit_code: str, employee_count: int, monthly_deposit_base: float) -> Dict[str, Any]`

`行号:196` `复杂度:低`

办理企业住房公积金开户。

Args:

    company_name: 企业名称

    credit_code: 统一社会信用代码

    employee_count: 员工人数

    monthly_deposit_base: 月缴存基数

Returns:

    开户结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `credit_code` | `str` | `-` |
| `employee_count` | `int` | `-` |
| `monthly_deposit_base` | `float` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_environmental_impact_approval(project_name: str, approval_no: str) -> Dict[str, Any]`

`行号:231` `复杂度:低`

查询环境影响评价审批进度。

Args:

    project_name: 项目名称

    approval_no: 审批编号

Returns:

    环评审批进度

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `project_name` | `str` | `-` |
| `approval_no` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_fire_approval(project_name: str, application_no: str) -> Dict[str, Any]`

`行号:262` `复杂度:低`

查询建设工程消防设计审核/验收审批进度。

Args:

    project_name: 项目名称

    application_no: 申请编号

Returns:

    消防审批进度

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `project_name` | `str` | `-` |
| `application_no` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_building_permit(project_name: str, permit_no: str) -> Dict[str, Any]`

`行号:293` `复杂度:低`

查询建筑工程施工许可审批进度。

Args:

    project_name: 项目名称

    permit_no: 许可证编号

Returns:

    建筑许可审批进度

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `project_name` | `str` | `-` |
| `permit_no` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_food_business_license(company_name: str, business_address: str, business_type: str, food_category: str) -> Dict[str, Any]`

`行号:324` `复杂度:低`

申请食品经营许可证。

Args:

    company_name: 企业名称

    business_address: 经营地址

    business_type: 经营类型 (食品销售/餐饮服务)

    food_category: 食品类别

Returns:

    申请结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `business_address` | `str` | `-` |
| `business_type` | `str` | `-` |
| `food_category` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_drug_operation_license(company_name: str, warehouse_address: str, business_scope: str, storage_capacity: float) -> Dict[str, Any]`

`行号:359` `复杂度:低`

申请药品经营许可证。

Args:

    company_name: 企业名称

    warehouse_address: 仓库地址

    business_scope: 经营范围

    storage_capacity: 仓储容量(立方米)

Returns:

    申请结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `warehouse_address` | `str` | `-` |
| `business_scope` | `str` | `-` |
| `storage_capacity` | `float` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_medical_device_license(company_name: str, product_category: str, business_scope: str) -> Dict[str, Any]`

`行号:394` `复杂度:低`

申请医疗器械经营许可证。

Args:

    company_name: 企业名称

    product_category: 产品类别 (I/II/III类)

    business_scope: 经营范围

Returns:

    申请结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `product_category` | `str` | `-` |
| `business_scope` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_intellectual_property(company_name: str, ip_type: str, ip_name: str, application_type: str) -> Dict[str, Any]`

`行号:427` `复杂度:低`

申请知识产权（著作权、软件著作权等）保护。

Args:

    company_name: 企业名称

    ip_type: 知识产权类型 (著作权/软件著作权/集成电路布图设计)

    ip_name: 知识产权名称

    application_type: 申请类型 (登记/转让/变更)

Returns:

    申请结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `ip_type` | `str` | `-` |
| `ip_name` | `str` | `-` |
| `application_type` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_trademark_registration(company_name: str, trademark_name: str, application_no: str) -> Dict[str, Any]`

`行号:463` `复杂度:低`

查询商标注册申请进度。

Args:

    company_name: 企业名称

    trademark_name: 商标名称

    application_no: 申请编号

Returns:

    商标注册进度

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `trademark_name` | `str` | `-` |
| `application_no` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_patent_application(applicant: str, patent_type: str, application_no: str) -> Dict[str, Any]`

`行号:496` `复杂度:低`

查询专利申请进度。

Args:

    applicant: 申请人

    patent_type: 专利类型 (发明/实用新型/外观设计)

    application_no: 申请编号

Returns:

    专利申请进度

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `applicant` | `str` | `-` |
| `patent_type` | `str` | `-` |
| `application_no` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_high_tech_enterprise(company_name: str, industry: str, rd_expense_ratio: float, patent_count: int) -> Dict[str, Any]`

`行号:529` `复杂度:低`

申请高新技术企业认定。

Args:

    company_name: 企业名称

    industry: 技术领域

    rd_expense_ratio: 研发费用占收入比例

    patent_count: 有效专利数量

Returns:

    申请结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `industry` | `str` | `-` |
| `rd_expense_ratio` | `float` | `-` |
| `patent_count` | `int` | `-` |

#### 返回

`Dict[str, Any]`

---

### `apply_tech_project(company_name: str, project_name: str, project_type: str, budget: float) -> Dict[str, Any]`

`行号:565` `复杂度:低`

申报科技计划项目。

Args:

    company_name: 企业名称

    project_name: 项目名称

    project_type: 项目类型 (重点研发/技术创新/成果转化)

    budget: 申报预算

Returns:

    申报结果

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `project_name` | `str` | `-` |
| `project_type` | `str` | `-` |
| `budget` | `float` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_government_procurement(keyword: str, region: str) -> Dict[str, Any]`

`行号:601` `复杂度:低`

查询政府采购招标公告信息。

Args:

    keyword: 关键词

    region: 地区

Returns:

    招标信息列表

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `keyword` | `str` | `-` |
| `region` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_enterprise_credit_report(company_name: str, credit_code: str) -> Dict[str, Any]`

`行号:638` `复杂度:低`

查询企业信用报告。

Args:

    company_name: 企业名称

    credit_code: 统一社会信用代码

Returns:

    企业信用报告

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `credit_code` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

### `query_listing_guidance_progress(company_name: str, stock_code: str) -> Dict[str, Any]`

`行号:673` `复杂度:低`

查询企业上市辅导进度。

Args:

    company_name: 企业名称

    stock_code: 辅导备案号/股票代码

Returns:

    辅导进度信息

#### 参数

| Name | Type | Default |
|:---|:---|:---|
| `company_name` | `str` | `-` |
| `stock_code` | `str` | `-` |

#### 返回

`Dict[str, Any]`

---

## Test Coverage

*No specific tests found for this module.*
