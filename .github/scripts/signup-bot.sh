#!/usr/bin/env bash
# 组队报名机器人：自动为报名帖分配组号（ML26-01 ~ ML26-25）并维护一条确认评论。
# 幂等：同一帖多次触发（created/edited）时复用已分配的组号，只更新确认评论。
set -euo pipefail

TAG='<!-- signup-bot-confirm -->'
MAX_GROUP=25
BOT_LOGIN='github-actions[bot]'

ghq() { gh api graphql -f query="$1" "${@:2}"; }
jq_field() { jq -r "$1" <<<"$DATA"; }

owner="${GITHUB_REPOSITORY_OWNER:?}"
name="${GITHUB_REPOSITORY_NAME:?}"
num="${DISCUSSION_NUMBER:?}"

DATA=$(ghq 'query($o:String!,$n:String!,$num:Int!){
  repository(owner:$o,name:$n){
    id
    discussion(number:$num){
      id title body closed
      comments(first:50){ nodes{ id author{ login } body } }
    }
    discussionCategories(first:20){ nodes{ id slug } }
    discussions(first:100){ nodes{ number title category{ slug } } }
  }
}' -f o="$owner" -f n="$name" -F num="$num")

repo_id=$(jq_field '.data.repository.id')
d_id=$(jq_field '.data.repository.discussion.id')
d_title=$(jq_field '.data.repository.discussion.title')
d_body=$(jq_field '.data.repository.discussion.body')
closed=$(jq_field '.data.repository.discussion.closed')

# 报名截止（老师关闭帖子）后冻结，不再处理任何编辑
[[ "$closed" == "true" ]] && exit 0

signup_cat_id=$(jq -r '.data.repository.discussionCategories.nodes[] | select(.slug=="signup") | .id' <<<"$DATA")

# ---------- 解析成员 ----------
members=$(jq -r '.data.repository.discussion.body' <<<"$DATA" \
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
    if ! gh api -q .login "users/$u" >/dev/null 2>&1; then
      errors+=("GitHub 用户名 \`@$u\` 不存在，请逐字核对（含大小写）。")
    fi
  done <<<"$members"
fi
if (( count > 5 )); then
  errors+=("识别到 ${count} 位成员，超过每组 5 人上限。")
elif (( count > 0 && count < 4 )); then
  warnings+=("目前识别到 ${count} 位成员（每组需 4–5 人）。可以先提交占号，凑齐后**编辑本帖**更新名单，机器人会自动重新确认。")
fi

# ---------- 分配组号（已有则沿用） ----------
group=''
if [[ "$d_title" =~ ML26-([0-9]{2}) ]]; then
  group=${BASH_REMATCH[1]}
else
  used=$(jq -r --arg cat "$signup_cat_id" \
    '.data.repository.discussions.nodes[] | select(.category.slug=="signup") | .title' <<<"$DATA" \
    | grep -oE 'ML26-[0-9]{2}' | grep -oE '[0-9]{2}' | sort -u)
  for i in $(seq -w 1 "$MAX_GROUP"); do
    if ! grep -qx "$i" <<<"$used"; then group=$i; break; fi
  done
  if [[ -z "$group" ]]; then
    errors+=("25 个组号已全部用完，请联系老师增开仓库。")
  else
    new_title="ML26-$group · ${d_title#*· }"
    ghq 'mutation($id:ID!,$t:String!){ updateDiscussion(input:{discussionId:$id,title:$t}){ discussion { number } } }' \
      -f id="$d_id" -f t="$new_title" >/dev/null
  fi
fi

# ---------- 生成确认评论（幂等 upsert） ----------
if (( ${#errors[@]} )); then
  body_lines=("$TAG" "### ❌ 报名未通过，请修改后重新提交" "")
  for e in "${errors[@]}"; do body_lines+=("- $e"); done
  body_lines+=("" "修改方法：编辑本帖正文（右上角 ⋯ → Edit），机器人会自动重新检查。")
else
  body_lines=("$TAG" "### ✅ 已登记：ML26-$group" "" "| # | GitHub 用户名 |" "| - | - |")
  i=1
  while IFS= read -r u; do
    body_lines+=("| $i | $u |"); i=$((i+1))
  done <<<"$members"
  body_lines+=("" "共 ${count} 人。权限将在报名截止后由老师统一开通。" "")
  for w in "${warnings[@]:-}"; do [[ -n "$w" ]] && body_lines+=("> ℹ️ $w"); done
  body_lines+=("名单有变动时请**编辑本帖**，机器人会自动更新本确认。")
fi
comment_body=$(printf '%s\n' "${body_lines[@]}")

comment_id=$(jq -r --arg tag "$TAG" --arg bot "$BOT_LOGIN" \
  '.data.repository.discussion.comments.nodes[] | select(.author.login==$bot and (.body|contains($tag))) | .id' <<<"$DATA" | head -1)

if [[ -n "$comment_id" ]]; then
  ghq 'mutation($id:ID!,$b:String!){ updateDiscussionComment(input:{commentId:$id,body:$b}){ comment { id } } }' \
    -f id="$comment_id" -F b="$comment_body" >/dev/null
else
  ghq 'mutation($id:ID!,$b:String!){ addDiscussionComment(input:{discussionId:$id,body:$b}){ comment { id } } }' \
    -f id="$d_id" -F b="$comment_body" >/dev/null
fi

echo "discussion #$num: group=${group:-none} members=$count errors=${#errors[@]}"
