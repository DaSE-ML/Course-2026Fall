import { withMeetingPage, bodyText, VMR_ORIGIN } from './browser.mjs';
import { VmrPageError } from './vmr-read.mjs';

export async function fetchMeetingDetailsViaPage(page, applicationId) {
  const id = String(applicationId ?? '').trim();
  if (!/^\d+$/.test(id)) {
    throw new VmrPageError('details 需要数字申请编号：--id <applicationId>（可用 status 查看）。', 'DETAILS_ID_REQUIRED');
  }

  await page.goto(`${VMR_ORIGIN}/my-meeting`, { waitUntil: 'domcontentloaded', timeout: 30_000 });
  await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => undefined);

  const candidates = [];
  const href = await page.evaluate((meetingId) => {
    const anchors = [...document.querySelectorAll('a[href]')];
    return anchors
      .map((anchor) => anchor.getAttribute('href'))
      .find((url) => url && url.includes(meetingId)) ?? null;
  }, id).catch(() => null);
  if (href) candidates.push(new URL(href, VMR_ORIGIN).toString());
  candidates.push(`${VMR_ORIGIN}/my-meeting/${id}`);
  candidates.push(`${VMR_ORIGIN}/my-meeting#/detail/${id}`);

  let lastFailure = '';
  for (const url of [...new Set(candidates)]) {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30_000 }).catch(() => undefined);
    await page.waitForLoadState('networkidle', { timeout: 10_000 }).catch(() => undefined);
    await page.waitForTimeout(800);
    const content = await bodyText(page);
    if (/待审批|审批中/.test(content)) {
      throw new VmrPageError(`申请 ${id} 尚未批准，无入会详情。`, 'PENDING_APPROVAL');
    }
    if (!content.includes('会议号') && !content.includes('会议链接')) {
      lastFailure = url;
      continue;
    }
    try {
      const details = readApprovedMeetingDetails(content);
      return { ...details, applicationId: id, detailUrl: url };
    } catch (error) {
      if (error instanceof VmrPageError && error.code === 'PENDING_APPROVAL') throw error;
      lastFailure = url;
    }
  }
  throw new VmrPageError(
    `未能从审批详情页提取完整入会信息（最近尝试：${lastFailure || '未知页面'}）。可人工打开页面后运行 calendar-draft。`,
    'DETAILS_UNAVAILABLE',
  );
}

export async function openCalendarDraft(options = {}) {
  const { meetingUrl, subject, start, end } = options;
  if (!meetingUrl || !subject || !start || !end) {
    throw new VmrPageError('calendar-draft 需要 --meeting-url、--subject、--start 和 --end。', 'CALENDAR_ARGS_REQUIRED');
  }
  return withMeetingPage(async (page) => {
    await page.goto(meetingUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 });
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => undefined);
    await page.waitForTimeout(1_000);

    const content = await bodyText(page);
    const details = readApprovedMeetingDetails(content);
    const calendarUrl = buildCalendarUrl({ subject, ...details, start, end });
    await page.goto(calendarUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 });
    console.log('已打开 Google Calendar 预填活动页；脚本不会保存或创建日历活动。');
  }, { ...options, headless: false });
}

export function readApprovedMeetingDetails(content) {
  if (/待审批|审批中/.test(content)) {
    throw new VmrPageError('该会议仍待审批，未打开日历草稿。', 'PENDING_APPROVAL');
  }

  const link = content.match(/https?:\/\/[^\s]+/u)?.[0];
  const meetingId = content.match(/会议号[：:]?\s*([\d\s-]+)/u)?.[1]?.trim();
  const password = content.match(/(?:入会)?密码[：:]?\s*([^\s]+)/u)?.[1]?.trim();
  if (!link || !meetingId || !password) {
    throw new VmrPageError('审批详情页未完整显示普通参会链接、会议号和入会密码，未打开日历草稿。', 'DETAILS_UNAVAILABLE');
  }
  return { link, meetingId, password };
}

export function buildCalendarUrl({ subject, link, meetingId, password, start, end }) {
  const calendarStart = new Date(new Date(start).getTime() - 15 * 60 * 1000);
  const calendarEnd = new Date(end);
  const format = (date) => date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
  const params = new URLSearchParams({
    action: 'TEMPLATE',
    text: subject,
    dates: `${format(calendarStart)}/${format(calendarEnd)}`,
    location: link,
    details: `会议链接：${link}\n会议号：${meetingId}\n入会密码：${password}`,
  });
  return `https://calendar.google.com/calendar/render?${params.toString()}`;
}
