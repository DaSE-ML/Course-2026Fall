import { withMeetingPage, bodyText } from './browser.mjs';
import { VmrPageError } from './vmr-read.mjs';

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
