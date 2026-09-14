#!/usr/bin/env bash
# 组队报名机器人（issue 版）：自动为报名 issue 分配组号（ML26-01 ~ ML26-25）并维护一条确认评论。
# 幂等：同一 issue 多次触发（opened/edited）时复用已分配的组号，只更新确认评论。
set -euo pipefail

TAG='<!-- signup-bot-confirm -->'
MAX_GROUP=25
num="${ISSUE_NUMBER:?}"
repo="$GITHUB_REPOSITORY"

ISSUE=$(gh api "repos/$repo/issues/$num")
body=$(jq -r '.body // ""' <<<"$ISSUE")
title=$(jq -r '.title' <<<"$ISSUE")
[[ $(jq -r '.state' <<<"$ISSUE") == "closed" ]] && exit 0

# ---------- 解析成员 ----------
members=$(jq -r '.body // ""' <<<"$ISSUE" \
  | grep -oE '@[A-Za-z0-9][A-Za-z0-9-]{0,38}' | sed 's/-*$//' | sort -fu)
count=$(grep -c . <<<"$members" || true)

# ---------- 校验 ----------
errors=()
warnings=()
if (( count == 0 )); then
  errors+=("没有识别到任何成员：请在「全体成员名单」中按 \`姓名 @github用户名\` 每行一位填写。")
else
  while IFS= read -r u; do
    u=${u#@}
    t=$(gh api -q .type "users/$u" 2>/dev/null || echo "")
    if [[ -z "$t" ]]; then
      errors+=("GitHub 用户名 \`@$u\` 不存在，请逐字核对（含大小写）。")
    elif [[ "$t" != "User" ]]; then
      errors+=("\`@$u\` 不是个人账号（类型为 $t），请填写同学本人的 GitHub 个人账号。")
    fi
  done <<<"$members"
fi
if (( count > 5 )); then
  errors+=("识别到 ${count} 位成员，超过每组 5 人上限。")
elif (( count > 0 && count < 4 )); then
  warnings+=("目前识别到 ${count} 位成员（每组需 4–5 人）。可以先提交占号，凑齐后**编辑本 issue** 更新名单，机器人会自动重新确认。")
fi

# ---------- 分配组号（已有则沿用） ----------
group=''
if [[ "$title" =~ ML26-([0-9]{2}) ]]; then
  group=${BASH_REMATCH[1]}
else
  used=$(gh api "repos/$repo/issues?state=all&per_page=100" --paginate -q '.[].title' 2>/dev/null \
    | grep -oE 'ML26-[0-9]{2}' | grep -oE '[0-9]{2}' | sort -u || true)
  for i in $(seq -w 1 "$MAX_GROUP"); do
    if ! grep -qx "$i" <<<"$used"; then group=$i; break; fi
  done
  if [[ -z "$group" ]]; then
    errors+=("25 个组号已全部用完，请联系老师增开仓库。")
  else
    gh api -X PATCH "repos/$repo/issues/$num" -f title="ML26-$group · 组队报名" >/dev/null
    gh issue edit "$num" --repo "$repo" --add-label "ML26-$group" >/dev/null 2>&1 || true
  fi
fi

# ---------- 生成确认评论（幂等 upsert） ----------
if (( ${#errors[@]} )); then
  out=("$TAG" "### ❌ 报名未通过，请修改后重新提交" "")
  for e in "${errors[@]}"; do out+=("- $e"); done
  out+=("" "修改方法：编辑本 issue 的描述（右上角 ⋯ → Edit），机器人会自动重新检查。")
else
  out=("$TAG" "### ✅ 已登记：ML26-$group" "" "| # | GitHub 用户名 |" "| - | - |")
  i=1
  while IFS= read -r u; do
    out+=("| $i | $u |"); i=$((i+1))
  done <<<"$members"
  out+=("" "共 ${count} 人。组仓库权限将在报名截止后由老师统一开通。" "")
  for w in "${warnings[@]:-}"; do [[ -n "$w" ]] && out+=("> ℹ️ $w"); done
  out+=("名单有变动时请**编辑本 issue**，机器人会自动更新本确认。")
fi
cbody=$(printf '%s\n' "${out[@]}")

cid=$(gh api "repos/$repo/issues/$num/comments?per_page=100" \
  -q '.[] | select(.body | contains("<!-- signup-bot-confirm -->")) | .id' 2>/dev/null | head -1 || true)

if [[ -n "${cid:-}" ]]; then
  gh api -X PATCH "repos/$repo/issues/$num/comments/$cid" -F body="$cbody" >/dev/null
else
  gh api -X POST "repos/$repo/issues/$num/comments" -F body="$cbody" >/dev/null
fi

echo "issue #$num: group=${group:-none} members=$count errors=${#errors[@]}"
