# 站点调研记录

## 登录跳转链（2026-08-24 实测验证）

1. `https://vmr.ecnu.edu.cn/my-meeting` 为 Vue SPA；vmr 会话缺失时跳 `/sign-in?_t=%252Fmy-meeting`。
2. `/sign-in` 页点击"统一身份认证平台"文字 → `sso.ecnu.edu.cn/login?service=...api.ecnu.edu.cn/user/authorize`（CAS）。
3. **重要分支**：
   - SSO 会话已失效 → 停在 CAS 表单页（`#nameInput` 学工号输入框 + `input[type=password]`；**页面无任何 `<button>`，填完凭据后在密码框按 Enter 提交**）。
   - SSO 会话仍有效 → 自动授权 302 直跳 `vmr.ecnu.edu.cn/calendar`，不停留 CAS 页。
4. CAS 登录成功后落地 `vmr.ecnu.edu.cn/calendar`（非 my-meeting），需再次导航到 `/my-meeting`。
5. 已登录页面特征：body 文本含 `您好,<姓名>`；会议列表页另含 `会议列表`。
6. CAS 接入网易易盾验证码（表单含 `NECaptchaValidate` 隐藏域）。无头模式通常不触发；触发时需 `login --headed` 人工滑块一次。

## 内部 API（2026-07-24 授权验证，2026-08-24 重构后复验）

- `POST /api/v1/meeting/list`、`POST /api/v1/meeting/edit`（创建）、`POST /api/v1/meeting/delete`，`application/x-www-form-urlencoded`。
- `user_token` 从会议列表页自身发起的 list 请求 POST body 中监听捕获，仅存于进程内存。
- 创建成功标志：响应 `success: true`；列表核验按 `id`/`topic`/`start_time` 匹配（结构化字段，非页面文本）。
- 审批可能即时完成（实测某次申请提交后状态即为"批准"）。

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
| `size` | 容量 | 前端下拉 `100/200/300/500/1000/2000`，按会议室组权限可见子集 |
| `group_id` | 云会议室组（下拉"请选择会议室组"） | 数字；默认硬编码 `'2'`；空闲查询接口可查各组占用 |
| `usage` | 用途 | 下拉由后端下发，默认 `"办公"` |
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

### 其他接口能力（未封装，记档备用）

- 会议室空闲查询：创建页按 `group + date + time + duration` 触发占用检查（`handleFreeChange`）。
- 批量创建：页面提供 Excel 导入入口（未调研格式）。
- 路由带参：创建页支持从路由 params 读 start/end。

## 架构决策记录

- 旧方案（复用日常浏览器 CDP + 人工 SSO）已废弃：依赖用户重启浏览器、人工登录，流程易卡死。
- 现方案：Playwright `launchPersistentContext` 专用 profile（`~/.new-meeting/profile`）+ Keychain 凭据 + Enter 提交 CAS 表单，`book` 全程零人工。
