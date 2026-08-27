import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { MeetingPlanError } from './request.mjs';

const SERVICE = 'new-meeting-ecnu-sso';
const STORE_DIR = path.join(os.homedir(), '.new-meeting');
const WIN_BLOB_PATH = path.join(STORE_DIR, 'credentials.bin');
const FILE_STORE_PATH = path.join(STORE_DIR, 'credentials.json');

function shq(value) {
  const text = String(value);
  if (/[\r\n]/.test(text)) throw new MeetingPlanError('凭据包含换行符，已拒绝。');
  return `'${text.replaceAll("'", `'\\''`)}'`;
}

function requireBoth(username, password, action) {
  if (!username || !password) {
    throw new MeetingPlanError(
      `${action} 需要 --username 和 --password（或环境变量 ECNU_SSO_USER / ECNU_SSO_PASS）。`,
    );
  }
}

function ensureStoreDir() {
  fs.mkdirSync(STORE_DIR, { recursive: true });
}

function warnPlaintext() {
  console.error(`[vmr] 注意：当前平台无系统钥匙串可用，凭据将以 0600 权限明文存放在 ${FILE_STORE_PATH}。更安全的替代：设置环境变量 ECNU_SSO_USER / ECNU_SSO_PASS。`);
}

/* ---------- macOS Keychain ---------- */

const keychainBackend = {
  save(username, password) {
    execFileSync('security', [
      'add-generic-password', '-U',
      '-s', SERVICE,
      '-a', String(username),
      '-w', String(password),
    ], { stdio: 'ignore' });
  },
  read() {
    let password;
    let metadata;
    try {
      password = execFileSync('security', ['find-generic-password', '-s', SERVICE, '-w'], {
        encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
      }).trimEnd();
      metadata = execFileSync('security', ['find-generic-password', '-s', SERVICE], {
        encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
      });
    } catch {
      throw missingError();
    }
    const username = metadata.match(/"acct"<blob>="([^"]*)"/)?.[1];
    if (!username || !password) throw new MeetingPlanError('Keychain 凭据不完整，请重新运行 init。', 'CREDENTIALS_INCOMPLETE');
    return { username, password };
  },
  has() {
    try {
      execFileSync('security', ['find-generic-password', '-s', SERVICE], {
        encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
      });
      return true;
    } catch {
      return false;
    }
  },
};

/* ---------- Windows DPAPI（当前用户绑定加密，powershell.exe 系统自带） ---------- */

const dpapiBackend = {
  save(username, password) {
    runPowershell([
      `$in = [Console]::In.ReadToEnd();`,
      `$bytes = [Text.Encoding]::UTF8.GetBytes($in);`,
      `$prot = [Security.Cryptography.ProtectedData]::Protect($bytes, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser);`,
      `[IO.File]::WriteAllBytes('${WIN_BLOB_PATH.replaceAll("'", "''")}', $prot);`,
    ].join(' '), JSON.stringify({ username, password }));
  },
  read() {
    if (!fs.existsSync(WIN_BLOB_PATH)) throw missingError();
    const b64 = runPowershell([
      `$in = [Console]::In.ReadToEnd();`,
      `$bytes = [Convert]::FromBase64String($in.Trim());`,
      `$prot = [Security.Cryptography.ProtectedData]::Unprotect($bytes, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser);`,
      `[Console]::Out.Write([Text.Encoding]::UTF8.GetString($prot));`,
    ].join(' '), fs.readFileSync(WIN_BLOB_PATH).toString('base64'));
    return parseStored(b64);
  },
  has() {
    return fs.existsSync(WIN_BLOB_PATH);
  },
};

function runPowershell(script, input) {
  const args = ['-NoProfile', '-NonInteractive', '-Command',
    "Add-Type -AssemblyName System.Security; " +
    "[Console]::InputEncoding = [Text.Encoding]::UTF8; " +
    "[Console]::OutputEncoding = [Text.Encoding]::UTF8; " + script];
  try {
    return execFileSync('powershell.exe', args, {
      encoding: 'utf8', input: String(input), stdio: ['pipe', 'pipe', 'inherit'],
    });
  } catch (err) {
    if (err?.status === 1 && String(err?.stderr ?? '').includes('missing')) throw missingError();
    throw new MeetingPlanError(`Windows 凭据存储失败：无法通过 PowerShell 访问受保护凭据文件（${WIN_BLOB_PATH}）。`, 'CREDENTIAL_STORE_ERROR');
  }
}

/* ---------- 通用降级：0600 权限本地文件 ---------- */

const fileBackend = {
  save(username, password) {
    ensureStoreDir();
    fs.writeFileSync(FILE_STORE_PATH, JSON.stringify({ username, password }, null, 2), { mode: 0o600 });
    warnPlaintext();
  },
  read() {
    if (!fs.existsSync(FILE_STORE_PATH)) throw missingError();
    try {
      return parseStored(fs.readFileSync(FILE_STORE_PATH, 'utf8'));
    } catch (err) {
      if (err instanceof MeetingPlanError) throw err;
      throw new MeetingPlanError('本地凭据文件损坏或不完整，请重新运行 init。', 'CREDENTIALS_INCOMPLETE');
    }
  },
  has() {
    return fs.existsSync(FILE_STORE_PATH);
  },
};

function parseStored(text) {
  const data = JSON.parse(text);
  if (!data?.username || !data?.password) throw new MeetingPlanError('凭据存储不完整，请重新运行 init。', 'CREDENTIALS_INCOMPLETE');
  return { username: String(data.username), password: String(data.password) };
}

function missingError() {
  return new MeetingPlanError(
    `未找到 SSO 凭据（服务名 ${SERVICE}）。请先运行：init --username <学工号> --password <密码>，或设置环境变量 ECNU_SSO_USER / ECNU_SSO_PASS。`,
    'CREDENTIALS_MISSING',
  );
}

/* ---------- 平台分发 ---------- */

export function detectCredentialBackend() {
  if (process.platform === 'darwin') return { name: 'macOS Keychain', backend: keychainBackend };
  if (process.platform === 'win32') return { name: 'Windows DPAPI', backend: dpapiBackend };
  return { name: 'local file (0600)', backend: fileBackend };
}

function readEnvCredentials() {
  const username = process.env.ECNU_SSO_USER;
  const password = process.env.ECNU_SSO_PASS;
  if (username && password) return { username, password };
  return null;
}

export function saveSsoCredentials(username, password) {
  requireBoth(username, password, 'init');
  const { name, backend } = detectCredentialBackend();
  backend.save(String(username), String(password));
  return { service: SERVICE, store: name, username };
}

export function readSsoCredentials() {
  const fromEnv = readEnvCredentials();
  if (fromEnv) return fromEnv;
  const { backend } = detectCredentialBackend();
  return backend.read();
}

export function hasSsoCredentials() {
  if (readEnvCredentials()) return true;
  const { backend } = detectCredentialBackend();
  return backend.has();
}

export { SERVICE, shq };
