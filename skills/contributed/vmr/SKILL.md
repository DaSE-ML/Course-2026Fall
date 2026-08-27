---
name: vmr
description: 预约/管理华东师大云视频（腾讯会议）的默认方式。凡"预约会议、订云会议室、开个会、删会议、改会议时间"等涉及 ECNU 云视频的请求一律使用本 skill；book 全程无人工干预（SSO 凭据存系统安全存储 + Playwright 持久化登录态）；预约与删除会联动 Google Calendar（提醒固定为会议开始前 1 小时，优先级高于全局日程默认值）。
---

# vmr — 华东师大云视频会议管理

CLI 位于本 skill 目录 `scripts/` 下，自包含，不依赖任何项目仓库。

```bash
# 先定位本 SKILL.md 所在目录（下称 <skill_dir>），CLI 即 <skill_dir>/scripts/cli.mjs。
# macOS / Linux 示例：
VMR="<skill_dir>/scripts/cli.mjs"
node "$VMR" <子命令>
```

首次使用前需安装依赖（见仓库 README）：`cd <skill_dir>/scripts && npm install`。

## 命令总览

所有时间必须是 `Asia/Shanghai` 的 ISO-8601 并带 `+08:00` 偏移（如 `2026-08-26T14:00:00+08:00`）。

| 子命令 | 用途 |
|--------|------|
| `init --username <学工号> --password <密码>` | 凭据存入平台安全存储（仅首次；或直接设置环境变量 `ECNU_SSO_USER` / `ECNU_SSO_PASS`，免落盘且优先级最高） |
| `login [--headed]` | 检查/自动完成 SSO 登录；验证码时用 `--headed` 人工滑一次 |
| `book --subject <主题> --start <ISO> --end <ISO>` | 一键预约，输出申请编号 |
| `status` | 列出我的会议申请（编号/时间/主题/审批状态） |
| `delete --id <申请编号>` | 删除指定申请 |
| `plan --subject <主题> --start <ISO> --end <ISO>` | 干跑校验时间（无副作用） |
| `calendar-draft --meeting-url <URL> --subject <主题> --start <ISO> --end <ISO>` | 打开 Google Calendar 预填草稿页 |

架构：SSO 凭据存平台安全存储（macOS Keychain / Windows DPAPI / 其他平台 0600 本地文件；服务名 `new-meeting-ecnu-sso`）；Playwright 专用持久化浏览器 `~/.new-meeting/profile`（不影响日常浏览器）；登录态过期时自动用凭据重登；内部 API 提交后一次核验，状态未知不重试。

## Google Calendar 联动（重要）

**提醒规则：vmr 会议的日历提醒固定为会议开始前 1 小时（60 分钟）。此规则优先于全局配置中"默认前一天上午 10:00"的规定。**

| vmr 操作 | 日历联动 |
|----------|----------|
| `book` 成功（输出申请编号后） | 用 `google-calendar` MCP 在 primary 日历创建事件：标题=会议主题、时间=会议起止、提醒=开始前 60 分钟（popup）、描述含"ECNU 云视频 申请编号 N" |
| 会议批准（status 见"批准"） | 可选：更新日历描述，补充会议号/密码（详情页可读时） |
| `delete` 成功 | 用 `google-calendar` MCP 删除/搜索对应标题+时间的旧事件，保持日历与云视频一致 |

日历事件搜索依据：标题精确匹配 + 开始时间匹配 + 描述含申请编号。
若当前环境无 `google-calendar` MCP，则跳过联动并在回复中说明，不影响预约本身。

## 验证码兜底

无头模式偶发网易易盾验证码 → CLI 报 `SSO_CAPTCHA`。此时运行 `node $VMR login --headed` 人工完成一次，登录态持久保存后恢复全自动。密码变更则重新 `init`。

## 安全边界

- 凭据仅存系统安全存储（Keychain / DPAPI / 0600 文件）或环境变量；不进日志、不进 git、不会出现在任何输出中。
- 浏览器为独立持久化 profile，不触碰日常 Chrome/Edge、不读取其 Cookie 或凭据存储。
- 删除仅按唯一申请编号执行；一次核验，失败不自动重试。

## 站点行为参考

登录跳转链、内部 API、页面分类详见 [站点调研记录](references/site-notes.md)。

## 测试

```bash
cd <skill_dir>/scripts && npm test
```
