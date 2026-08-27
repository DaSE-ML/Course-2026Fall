# ECNU VMR Skill — 华东师大云视频会议自动预约

一个 [Agent Skill](https://agentskills.io) 标准的技能包：让 AI 编码助手（Claude Code / opencode / OpenAI Codex 等）一句话完成华东师大云视频（腾讯会议）会议室的**预约、查询、删除**，全程无人工干预，并可联动 Google Calendar 自动建提醒。

> 纯 CLI 工具 + 使用说明书的结构：`scripts/cli.mjs` 是功能本体，`SKILL.md` 教 agent 如何调用它。不装 agent 也能直接当命令行工具用。

## 功能

| 命令 | 说明 |
|------|------|
| `init` | 配置 SSO 凭据（一次性） |
| `login --headed` | 登录检查 / 处理偶发验证码 |
| `book` | 一键预约会议室，输出申请编号 |
| `status` | 列出我的会议申请与审批状态 |
| `delete --id <申请编号>` | 删除指定申请 |
| `plan` | 干跑校验时间，无副作用 |
| `calendar-draft` | 打开 Google Calendar 预填草稿 |

## 环境要求

- Node.js ≥ 22（建议 LTS）
- 平台：macOS / Windows / Linux 均可

## 安装

### 第 1 步：放入 agent 工具的 skills 目录

将整个 `vmr/` 文件夹复制到你所用工具的技能目录（以下均为常见默认路径，具体以你的工具文档为准）：

| 工具 | 默认路径（用户级） |
|------|-------------------|
| Claude Code | `~/.claude/skills/vmr/` |
| opencode | `~/.config/opencode/skills/vmr/` |
| Codex CLI | `~/.codex/skills/vmr/` |
| 其他（仅当 CLI 用） | 任意位置，直接调用 `node scripts/cli.mjs` |

Windows 下路径同理：如 `%USERPROFILE%\.claude\skills\vmr\`。

未原生支持 Agent Skills 标准的工具，也可以在你的全局指令文件（AGENTS.md 等）中加一句：

```markdown
## 云视频会议（vmr）
预约/修改/删除华东师大云视频 → 阅读 ~/.codex/skills/vmr/SKILL.md 并按其执行。
```

### 第 2 步：安装依赖

```bash
cd <skill目录>/scripts
npm install        # 会同时提示安装 Playwright 浏览器内核
npx playwright install chromium   # 首次需要
```

### 第 3 步：配置凭据（二选一）

**方式 A · 环境变量（推荐，跨平台一致且不落盘）：**

```bash
export ECNU_SSO_USER=<学工号>
export ECNU_SSO_PASS=<统一身份认证密码>
```

Windows PowerShell：

```powershell
setx ECNU_SSO_USER "<学工号>"
setx ECNU_SSO_PASS "<密码>"
```

**方式 B · 存入平台安全存储：**

```bash
node cli.mjs init --username <学工号> --password <密码>
```

存储位置按平台自动选择：

| 平台 | 存储方式 |
|------|----------|
| macOS | Keychain（服务名 `new-meeting-ecnu-sso`） |
| Windows | DPAPI 当前用户加密（`~/.new-meeting/credentials.bin`） |
| Linux | `~/.new-meeting/credentials.json`（0600 权限明文，详见下方安全说明） |

环境变量优先于落盘存储；两者都配了则读取环境变量。

### 第 4 步：验证

```bash
node cli.mjs login          # 应输出"登录检查完成"
node cli.mjs plan --subject 测试 --start 2026-09-01T14:00:00+08:00 --end 2026-09-01T15:00:00+08:00
```

## 使用示例（对 agent 说的话）

- 「帮我订下周二下午两点到三点 ECNU 云视频开组会」→ agent 调 `book`，成功后建议联动建日历
- 「看看我最近的云视频审批状态」→ `status`
- 「把刚才订的会删掉」→ `delete --id <申请编号>`

偶发网易易盾验证码导致无头登录失败时，运行 `node cli.mjs login --headed` 人工滑一次验证码即可恢复全自动。修改密码后需重新 `init`。

## 可选：Google Calendar 联动

若你的 agent 环境配置了 `google-calendar` MCP，`book` 成功后会自动在 primary 日历创建事件（**固定提前 60 分钟 popup 提醒**），`delete` 成功后同步删事件。没有该 MCP 则跳过，不影响预约。

## 安全与隐私

- 本包**不含也不收集**任何真实账号、密码、Cookie、浏览器登录态；打包前已经过个人信息扫描。
- 凭据只进你本机的 Keychain / DPAPI / 权限受限文件或你自己设置的环境变量；CLI 不打印密码，不写入日志。
- Playwright 使用独立持久化 profile（`~/.new-meeting/profile`），绝不触碰日常浏览器的 Cookie。
- Linux 平台的降级方案是 0600 权限明文 JSON，安全性弱于系统钥匙串；介意者请使用方式 A 环境变量。
- 请勿将 `credentials.json`、`credentials.bin`、`.env` 提交到任何仓库。

## 已知边界

- 需要校园网环境下可访问 `vmr.ecnu.edu.cn` 与 `sso.ecnu.edu.cn`。
- 内部 API 为站点私有实现，若学校改版可能失效；欢迎提 Issue 反馈。
- 申请提交后仍需管理员审批，`status` 可查进度。

## 许可证

MIT
