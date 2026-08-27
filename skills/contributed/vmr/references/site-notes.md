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

## 架构决策记录

- 旧方案（复用日常浏览器 CDP + 人工 SSO）已废弃：依赖用户重启浏览器、人工登录，流程易卡死。
- 现方案：Playwright `launchPersistentContext` 专用 profile（`~/.new-meeting/profile`）+ Keychain 凭据 + Enter 提交 CAS 表单，`book` 全程零人工。
