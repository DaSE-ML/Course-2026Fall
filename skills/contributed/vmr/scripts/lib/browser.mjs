import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';
import { chromium } from 'playwright';
import { MeetingPlanError } from './request.mjs';

export const PROFILE_DIR = path.join(os.homedir(), '.new-meeting', 'profile');
export const VMR_MEETINGS_URL = 'https://vmr.ecnu.edu.cn/my-meeting';
export const VMR_ORIGIN = 'https://vmr.ecnu.edu.cn';

export async function openMeetingSession(options = {}) {
  fs.mkdirSync(path.dirname(PROFILE_DIR), { recursive: true });
  let context;
  try {
    context = await chromium.launchPersistentContext(PROFILE_DIR, {
      headless: options.headless ?? true,
      viewport: { width: 1366, height: 900 },
      args: ['--disable-blink-features=AutomationControlled'],
    });
  } catch (error) {
    throw new MeetingPlanError(`无法启动专用浏览器实例：${error instanceof Error ? error.message : String(error)}`);
  }
  const rawPage = context.pages()[0] ?? await context.newPage();
  return { context, page: rawPage, ownsContext: true };
}

export async function closeMeetingSession(session) {
  if (!session) return;
  await session.context?.close().catch(() => undefined);
}

export async function withMeetingPage(action, options = {}) {
  const session = await openMeetingSession(options);
  try {
    return await action(session.page, session);
  } finally {
    await closeMeetingSession(session);
  }
}

export function pageUrl(page) {
  return page.url();
}

export async function bodyText(page) {
  return page.evaluate(() => document.body?.innerText ?? '').catch(() => '');
}

export async function waitForTimeout(page, ms) {
  await page.waitForTimeout(ms);
}

export async function postFormInPage(page, url, form) {
  return page.evaluate(async ({ targetUrl, formFields }) => {
    const response = await fetch(targetUrl, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
      body: new URLSearchParams(formFields).toString(),
    });
    return { ok: response.ok, status: response.status, text: await response.text() };
  }, { targetUrl: url, formFields: form });
}
