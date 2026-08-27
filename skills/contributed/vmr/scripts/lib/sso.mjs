import { VMR_MEETINGS_URL, bodyText } from './browser.mjs';
import { readSsoCredentials } from './credentials.mjs';

const SSO_TIMEOUT_MS = 30_000;
const POLL_MS = 1_000;

export class SsoError extends Error {
  constructor(message, code = 'SSO_FAILED') {
    super(message);
    this.name = 'SsoError';
    this.code = code;
  }
}

export function classifyVmrPage({ url = '', bodyText: text = '' }) {
  if (url.includes('/sign-in')) return 'sign-in';
  if (/您由于长时间未响应，系统自动登出/u.test(text)) return 'expired-session';
  if (/您好,/.test(text) && text.includes('会议列表')) return 'meeting-list';
  if (/您好,/.test(text)) return 'vmr-authenticated';
  if (/统一身份认证平台|Login Center|Sign In/u.test(text)) return 'auth-or-sso';
  return 'unknown';
}

export async function ensureAuthenticated(page, { onEvent = () => {} } = {}) {
  await gotoMeetingList(page);

  const kind = await currentPageKind(page);
  if (kind === 'meeting-list') {
    onEvent('已使用持久化登录态。');
    return;
  }

  onEvent('登录态缺失或过期，开始自动 SSO 登录…');
  await performSsoLogin(page, onEvent);

  await waitForMeetingList(page, 10_000);
  onEvent('SSO 登录成功，登录态已持久化。');
}

async function waitForMeetingList(page, timeoutMs) {
  const result = await pollUntil(page, timeoutMs, async () => (
    (await currentPageKind(page)) === 'meeting-list' ? 'ok' : null
  ));
  if (result !== 'ok') {
    throw new SsoError('自动登录后未进入会议列表。', 'SSO_DID_NOT_LAND');
  }
}

async function performSsoLogin(page, onEvent) {
  const kind = await currentPageKind(page);
  if (kind !== 'sign-in') {
    await gotoMeetingList(page);
  }
  if ((await currentPageKind(page)) === 'meeting-list') return;

  await page.getByText('统一身份认证平台').first().click();
  onEvent('已点击统一身份认证平台入口，等待跳转…');

  const landed = await pollUntil(page, 20_000, async () => {
    const url = page.url();
    if (url.includes('sso.ecnu.edu.cn')) return 'sso-form';
    if (url.includes('vmr.ecnu.edu.cn') && !url.includes('/sign-in')) {
      await page.waitForTimeout(1_500);
      if ((await currentPageKind(page)) !== 'unknown') return 'vmr-back';
      return 'vmr-back';
    }
    return null;
  });

  if (landed === 'vmr-back') {
    onEvent('SSO 会话仍有效，已自动续期云视频登录态。');
    await gotoMeetingList(page);
    if ((await currentPageKind(page)) === 'meeting-list') return;
    throw new SsoError('SSO 自动续期后仍未进入会议列表。', 'SSO_RENEW_DID_NOT_LAND');
  }
  if (landed !== 'sso-form') {
    throw new SsoError('点击统一身份认证入口后既未进入 SSO 也未跳回云视频平台。', 'SSO_NAV_TIMEOUT');
  }

  onEvent('已进入统一身份认证平台，正在填写凭据…');
  const { username, password } = readSsoCredentials();
  await page.fill('#nameInput', username);
  await page.fill('input[type=password]', password);
  await page.press('input[type=password]', 'Enter');

  const after = await pollUntil(page, SSO_TIMEOUT_MS, async () => {
    const url = page.url();
    const text = await bodyText(page);
    if (/密码错误|用户名或密码|账号或密码|Authentication Failure/u.test(text)) {
      return 'rejected';
    }
    if (/验证码/u.test(text) && url.includes('sso.ecnu.edu.cn')) {
      return 'captcha';
    }
    if (url.includes('vmr.ecnu.edu.cn') && !url.includes('/sign-in')) return 'vmr-back';
    return null;
  });

  if (after === 'rejected') {
    throw new SsoError(
      'SSO 拒绝了登录（密码错误）。请运行 npm run new-meeting -- init --username <教工号> --password <新密码> 更新凭据。',
      'SSO_REJECTED',
    );
  }
  if (after === 'captcha') {
    throw new SsoError(
      'SSO 要求验证码。请运行 npm run new-meeting -- login --headed 人工完成一次验证（登录态会持久保存）。',
      'SSO_CAPTCHA',
    );
  }
  if (after !== 'vmr-back') {
    throw new SsoError('SSO 登录超时（30 秒内未跳回云视频平台）。可尝试 login --headed 人工完成一次。', 'SSO_TIMEOUT');
  }

  await gotoMeetingList(page);
}

async function gotoMeetingList(page) {
  await page.goto(VMR_MEETINGS_URL, { waitUntil: 'domcontentloaded', timeout: 30_000 });
  await settleVmr(page);
}

async function pollUntil(page, timeoutMs, predicate) {
  const started = Date.now();
  let last = null;
  while (Date.now() - started < timeoutMs) {
    last = await predicate().catch(() => null);
    if (last) return last;
    await page.waitForTimeout(POLL_MS);
  }
  return null;
}

async function settleVmr(page) {
  await page.waitForLoadState('domcontentloaded', { timeout: 15_000 }).catch(() => undefined);
  await page.waitForTimeout(1_500);
}

async function currentPageKind(page) {
  return classifyVmrPage({ url: page.url(), bodyText: await bodyText(page) });
}
