# 站点调研记录

## 登录跳转链（2026-08-24 实测验证）

1. `https://vmr.ecnu.edu.cn/my-meeting` 为 Vue SPA；vmr 会话缺失时跳 `/sign-in?_t=%252Fmy-meeting`。
2. `/sign-in` 页点击"统一身份认证平台"文字 → `sso.ecnu.edu.cn/login?service=...api.ecnu.edu.cn/user/authorize`（CAS）。
3. **重要分支**：
   - SSO 会话已失效 → 停在 CAS 表单页（`#nameInput` 教工号输入框 + `input[type=password]`；**页面无任何 `<button>`，填完凭据后在密码框按 Enter 提交**）。
   - SSO 会话仍有效 → 自动授权 302 直跳 `vmr.ecnu.edu.cn/calendar`，不停留 CAS 页。
4. CAS 登录成功后落地 `vmr.ecnu.edu.cn/calendar`（非 my-meeting），需再次导航到 `/my-meeting`。
5. 已登录页面特征：body 文本含 `您好,<姓名>`；会议列表页另含 `会议列表`。
6. CAS 接入网易易盾验证码（表单含 `NECaptchaValidate` 隐藏域）。无头模式通常不触发；触发时需 `login --headed` 人工滑块一次。

## 内部 API（2026-07-24 授权验证，2026-08-24 重构后复验）

- `POST /api/v1/meeting/list`、`POST /api/v1/meeting/edit`（创建）、`POST /api/v1/meeting/delete`、`POST /api/v1/meeting/get`（详情），`application/x-www-form-urlencoded`。
- **list 必须带分页/范围参数**（`search=&page_size=200&page=1&date_range[0..1]=宽范围&use_date_range=0`，见 `buildListMeetingsForm`）。只传 `user_token` 时服务端返回默认首屏快照，超出部分的申请不可见——曾导致"创建成功但核验 unknown"的误判（2026-08-28 实测：带参请求返回全量，裸请求仅返回旧数据首屏）。
- `user_token` 从会议列表页自身发起的 list 请求 POST body 中监听捕获，仅存于进程内存。
- 创建成功标志：响应 `success: true`；列表核验按 `id`/`topic`/`start_time` 匹配（结构化字段，非页面文本）。
- **审批为系统自动且即时**（2026-08-28 实测：提交接口返回后 1 秒内首次 list 核验，状态已是"批准"；`wait` 的 500ms 首轮轮询通常即命中）。
- 列表行 `zoom_info` 字段（批准后）格式：`会议号:987654321<br>密码:135790`（示例为虚构数据），由 `parseZoomInfo` 解析；参会完整链接需走 `/meeting/get`（`details --id`）。

## 审批详情页（未完全复验）

`calendar-draft` 依赖从详情页文本提取参会链接/会议号/密码，正则较宽松，遇格式不符会报 `DETAILS_UNAVAILABLE` 安全停止。拿到真实批准详情页样本后应复验。

## API 参数参考（2026-08-27 从站点前端 chunk 全量分析提取）

`POST /api/v1/meeting/edit` 的完整字段面。skill 默认只用保守子集；以下均可经 CLI 显式参数或 `--field 键=值` 透传（受控键除外）。

### 基础

| 字段 | 说明 | 取值 |
|------|------|------|
| `topic` | 会议主题 | 文本（= CLI `--subject`，受控） |
| `meeting_date` / `meeting_time` / `duration` | 开始日期/时刻/时长分钟 | 受控，由 `--start/--end` 推导 |
| `password` | 入会密码 | 6 位数字；或 8 位且同时含大写字母+小写字母+数字；缺省自动生成 6 位 |
| `size` | 容量 | 前端下拉 `100/200/300/500/1000/2000`，按会议室组权限可见子集；校方政策教职工上限 300 人 |
| `group_id` | 云会议室组（下拉"请选择会议室组"） | 数字；默认硬编码 `'2'`；空闲查询接口可查各组占用 |
| `usage` | 用途 | 下拉由后端下发，默认 `"办公"` |

> 政策来源（ECNU 信息化治理办公室「视频会议」服务页）：系统面向全校教职员工，自助预约企业版腾讯会议最长 **6 小时**、**300 参会人**以内——与 skill 的单场 6 小时拆分策略一致。
| `attendees` | 指定参会人 | JSON 数组字符串，默认 `'[]'` |
| `assistant(s)` / `meeting_guests` / `description`（表单层） | 助手 / 宾客 / 会议描述 | 文本类 |

### 安全开关（'1'/'0' 字符串）

`waiting_room` 等候室 · `option_sso_only` 仅内部用户可参会 · `option_water_mark` 水印 · `option_enroll` 报名入会（配套 `enroll_attendees` 报名人员 ID/手机号列表、`enroll_questions[]` 报名问题）

### 功能开关（'1'/'0' 字符串）

`option_mute` 成员入会静音（默认开）· `option_jbh` 允许成员在主持人前入会（默认开）· `auto_record` 自动录制 · `option_live` 直播 · `option_interpreter` 传译 · `option_h323` H.323 设备入会

### 周期会议

| 字段 | 说明 |
|------|------|
| `is_recurrent` | '1' 开启周期 |
| `repeat_type` | 1=每日循环，2=每周循环，3=每月循环（前端 `repeat_options` 确认） |
| `end_meeting_date` | 周期截止日期 YYYY-MM-DD |
| `end_meeting_times` | 总场次次数（默认 '2'） |
| `recurrent_id` | 编辑周期实例时的标识（新建固定 '0'） |

### 受控字段（CLI `--field` 禁止覆盖）

`user_token, id, quite, duration, meeting_date, meeting_time, topic, password`

### 其他接口能力

- `POST /api/v1/meeting/get`（2026-08-27 实测验证）：单条申请详情，body 为 `user_token + id + review:'true'`。响应 `data` 含 `join_url`（参会链接）、`meeting_id`/`meeting_code`（会议号）、`password`（入会密码）、`host_url`（主持人链接，含会话 hash 勿外传）、`approve`/`is_approved`（审批状态）、`start_time/end_time/auto_record/waiting_room/usage` 等。skill 的 `details` 命令即基于此接口。
- 会议室空闲查询：创建页按 `group + date + time + duration` 触发占用检查（`handleFreeChange`）。
- 批量创建：页面提供 Excel 导入入口（未调研格式）。
- 路由带参：创建页支持从路由 params 读 start/end。

## 架构决策记录

- 旧方案（复用日常浏览器 CDP + 人工 SSO）已废弃：依赖用户重启浏览器、人工登录，流程易卡死。
- 现方案：Playwright `launchPersistentContext` 专用 profile（`~/.new-meeting/profile`）+ Keychain 凭据 + Enter 提交 CAS 表单，`book` 全程零人工。
