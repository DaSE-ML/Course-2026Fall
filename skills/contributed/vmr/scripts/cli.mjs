import process from 'node:process';
import { createMeetingPlan, renderPlanSummary } from './lib/plan.mjs';
import { MeetingPlanError } from './lib/request.mjs';
import { saveSsoCredentials, readSsoCredentials } from './lib/credentials.mjs';
import { withMeetingPage } from './lib/browser.mjs';
import { ensureAuthenticated, SsoError } from './lib/sso.mjs';
import { bookMeetings, listMeetings, deleteMeetingById } from './lib/vmr-submit.mjs';
import { openCalendarDraft } from './lib/calendar.mjs';

const USAGE = `用法：
  npm run new-meeting -- init --username <学工号> --password <密码>   # 存入系统安全存储（一次性）
  npm run new-meeting -- login [--headed]                            # 检查/自动完成 SSO 登录
  npm run new-meeting -- book --subject <主题> --start <ISO+08:00> --end <ISO+08:00> [--headed]
  npm run new-meeting -- status                                       # 列出我的会议申请
  npm run new-meeting -- delete --id <申请编号>                        # 删除指定申请
  npm run new-meeting -- plan --subject <主题> --start <ISO+08:00> --end <ISO+08:00>   # 干跑，无副作用
  npm run new-meeting -- calendar-draft --meeting-url <详情页URL> --subject <主题> --start <ISO+08:00> --end <ISO+08:00>

说明：
  - SSO 凭据保存在平台安全存储：macOS Keychain / Windows DPAPI / 其他平台为 0600 本地文件（服务名 new-meeting-ecnu-sso），仅在自动登录时由本进程临时读取；也可改用环境变量 ECNU_SSO_USER / ECNU_SSO_PASS（优先级最高，不落盘）。
  - 浏览器使用专用持久化实例（~/.new-meeting/profile），不影响日常浏览器；登录态持久保存。
  - 时间必须是 Asia/Shanghai 的 ISO-8601 并带 +08:00 偏移，例如 2026-08-26T14:00:00+08:00。
  - book 为一键预约：自动登录 → 提交 → 一次核验，全程无人工确认；提交后等待管理员审批。
  - 若 SSO 触发验证码导致自动登录失败，运行 login --headed 人工完成一次即可。`;

function parseArguments(argv) {
  const [command, ...tokens] = argv;
  const options = {};
  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index];
    if (!token.startsWith('--')) {
      throw new MeetingPlanError(`无法识别参数：${token}`);
    }
    const key = token.slice(2);
    if (key === 'headed') {
      options.headless = false;
      continue;
    }
    const value = tokens[index + 1];
    if (!value || value.startsWith('--')) {
      throw new MeetingPlanError(`参数 --${key} 缺少值。`);
    }
    options[key.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = value;
    index += 1;
  }
  return { command, options };
}

function planInput(options) {
  return {
    subject: options.subject,
    start: options.start,
    end: options.end,
    timeZone: 'Asia/Shanghai',
  };
}

function printMeetingRecords(records) {
  if (!records.length) {
    console.log('（会议列表为空）');
    return;
  }
  for (const record of records) {
    console.log(`申请 ${record.applicationId} | ${record.startTime} | ${record.durationText} | ${record.subject} | 状态：${record.approveStatus || '未知'}`);
  }
}

async function main() {
  const { command, options } = parseArguments(process.argv.slice(2));
  if (!command || command === '--help' || command === 'help') {
    console.log(USAGE);
    return;
  }

  if (command === 'init') {
    const username = options.username ?? process.env.ECNU_SSO_USER;
    const password = options.password ?? process.env.ECNU_SSO_PASS;
    const saved = saveSsoCredentials(username, password);
    console.log(`SSO 凭据已存入系统安全存储（${saved.store}，服务名 ${saved.service}，账号 ${saved.username}）。`);
    return;
  }

  if (command === 'login') {
    await withMeetingPage(async (page) => {
      await ensureAuthenticated(page, { onEvent: (msg) => console.log(msg) });
    }, { headless: options.headless !== false });
    console.log('登录检查完成：可以使用 book/status/delete。');
    return;
  }

  if (command === 'plan') {
    const plan = createMeetingPlan(planInput(options));
    console.log(renderPlanSummary(plan));
    console.log(`\nJSON：\n${JSON.stringify(plan, null, 2)}`);
    return;
  }

  if (command === 'book') {
    const plan = createMeetingPlan(planInput(options));
    console.log(renderPlanSummary(plan));
    const results = await bookMeetings(plan, { headless: options.headless !== false });
    if (!results.length || results.some((r) => r.status !== 'submitted_pending_approval')) {
      process.exitCode = 1;
    }
    return;
  }

  if (command === 'status') {
    const records = await listMeetings({ headless: options.headless !== false });
    printMeetingRecords(records);
    return;
  }

  if (command === 'delete') {
    await deleteMeetingById(options.id, { headless: options.headless !== false });
    return;
  }

  if (command === 'calendar-draft') {
    await openCalendarDraft(options);
    return;
  }

  if (command === 'whoami') {
    const creds = readSsoCredentials();
    console.log(`SSO 凭据账号：${creds.username}`);
    return;
  }

  throw new MeetingPlanError(`未知子命令：${command}`);
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`错误：${message}`);
  process.exitCode = error instanceof MeetingPlanError || error instanceof SsoError ? 2 : 1;
});
