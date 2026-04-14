# Claude Code 설정 백업

개인 Claude Code 환경(agents / rules / skills / CLAUDE.md / settings)을 백업한 레포. 다른 PC에서 동일한 환경으로 복원할 수 있음.

**Repo URL**: `https://github.com/algocean1204/claude-code-setting-backup.git`

---

## 🤖 Claude에게 — 새 PC에서 복원 시 아래 순서대로 실행할 것

사용자가 이 레포 링크만 주고 "복원해줘"라고 했다면, 다음 단계를 그대로 실행해. 중간에 멈추지 말고 끝까지 진행. 사용자 개입이 필요한 부분은 명시함.

### 사전 요구사항 확인

다음 도구가 설치되어 있는지 먼저 확인해:

```bash
# macOS 기준
command -v claude || echo "❌ Claude Code 미설치"
command -v git || echo "❌ git 미설치"
command -v bun || echo "❌ Bun 미설치 (gstack 빌드에 필요)"
command -v npx || echo "❌ Node.js/npx 미설치 (ClaudeTalkToFigma MCP에 필요)"
command -v rsync || echo "❌ rsync 미설치"
```

없는 도구는 사용자에게 설치 안내:
- **Claude Code**: https://docs.anthropic.com/en/docs/claude-code
- **Bun**: `curl -fsSL https://bun.sh/install | bash`
- **Node.js**: https://nodejs.org/ (LTS)
- **git, rsync**: macOS는 Xcode Command Line Tools (`xcode-select --install`)

### Step 1. 레포 클론

```bash
cd ~
git clone https://github.com/algocean1204/claude-code-setting-backup.git
cd claude-code-setting-backup
```

### Step 2. `~/.claude/`로 복사

기존 `~/.claude/`가 있으면 **덮어쓰기**됨. 사용자에게 한 번 확인받을 것.

```bash
mkdir -p ~/.claude
rsync -av \
  --exclude='.git' \
  --exclude='README.md' \
  --exclude='.gitignore' \
  --exclude='.DS_Store' \
  ./ ~/.claude/
```

### Step 3. gstack 재빌드 (필수)

gstack은 컴파일된 바이너리(`browse/dist/`, `design/dist/`, `bin/gstack-global-discover`)와 `node_modules/`를 git에서 제외하므로 복원 후 **반드시** 재빌드해야 함.

```bash
cd ~/.claude/skills/gstack
./setup
```

`./setup`이 하는 일:
- Bun 설치 여부 확인 (없으면 에러 → 사용자가 설치 후 재실행)
- `bun install`로 의존성 설치
- browse/design 바이너리 컴파일
- Claude Code / Codex에 skill 등록

### Step 4. Claude Code 재시작

```bash
# 실행 중인 Claude Code 세션이 있다면 종료 후 재실행
# 플러그인은 settings.json의 enabledPlugins 기반으로 첫 실행 시 자동 설치됨
```

### Step 5. MCP 연결 상태 확인

```bash
claude mcp list
```

기대 결과:
- `ClaudeTalkToFigma` — `✓ Connected`
- `plugin:context7:context7` — `✓ Connected`
- `claude.ai Context7 / Hugging Face / Notion` — `✓ Connected` (claude.ai 계정 로그인 후 자동)
- `claude.ai Gmail / Google Calendar` — `! Needs authentication` (사용 안 하면 무시)

### Step 6. 사용자에게 수동 작업 안내

다음은 자동화 불가 — 사용자가 직접 처리:

1. **claude.ai 계정 로그인** — Hugging Face / Notion / Context7 MCP 인증용
2. **ClaudeTalkToFigma 사용하려면** — Figma Desktop에 플러그인 수동 설치:
   - Figma Desktop 실행 → Menu → Plugins → Development → Import plugin from manifest
   - 경로: `~/.claude/skills/claude-talk-to-figma-mcp/src/claude_mcp_plugin/manifest.json` (레포에 포함 안 됨, npm 설치 위치 확인 필요)
   - 또는 레포 참조: https://github.com/sonnylazuardi/claude-talk-to-figma-mcp
3. **메모리 초기화 확인** — `~/.claude/projects/-Users-kimtaekyu/memory/`는 의도적으로 백업 제외됨. 새 PC에서 본인 컨텍스트로 처음부터 쌓아감.
4. **`settings.local.json` 재생성** — 로컬 전용 권한 허용 목록. 필요 시 사용자가 직접 작성.

### 완료 확인

```bash
# 설정 파일 체크
[ -f ~/.claude/CLAUDE.md ] && echo "✓ CLAUDE.md"
[ -f ~/.claude/settings.json ] && echo "✓ settings.json"
[ -f ~/.claude/.mcp.json ] && echo "✓ .mcp.json"
[ -d ~/.claude/agents ] && echo "✓ agents/ ($(ls ~/.claude/agents | wc -l | tr -d ' ') files)"
[ -d ~/.claude/rules ] && echo "✓ rules/"
[ -d ~/.claude/skills ] && echo "✓ skills/"
[ -x ~/.claude/skills/gstack/browse/dist/browse ] && echo "✓ gstack browse 바이너리 빌드됨" || echo "❌ gstack 재빌드 필요 — cd ~/.claude/skills/gstack && ./setup"
```

모든 항목 체크되면 복원 완료. Claude Code 재시작하고 `/office-hours` 같은 gstack 스킬 하나 실행해서 정상 동작 확인.

---

## 📦 레포에 포함된 것

| 경로 | 내용 |
|---|---|
| `agents/` | 커스텀 서브에이전트 정의 75+ 개 (Phase별 팀, 검증자, 리뷰어) |
| `rules/` | 리더 행동 규칙 (`always/` 필수 로드 + `conditional/` 조건부) + CHANGELOG |
| `skills/` | gstack + 커스텀 스킬 세트 (소스 only, 바이너리 제외) |
| `CLAUDE.md` | 글로벌 리더 지침 (LEADER ABSOLUTE RULE, Phase 실행 순서, 팀 호출 규칙) |
| `settings.json` | 글로벌 설정 (권한 모드 / 훅 / 플러그인 활성화 목록 / `effortLevel`) |
| `.mcp.json` | 로컬 stdio MCP 정의 (ClaudeTalkToFigma) |

## 🚫 제외된 것 (`.gitignore`)

**런타임 / 세션 데이터** — 기기마다 다시 쌓여야 함:
- `history.jsonl`, `sessions/`, `todos/`, `tasks/`, `plans/`
- `shell-snapshots/`, `paste-cache/`, `file-history/`, `session-env/`
- `statsig/`, `telemetry/`, `stats-cache.json`, `backups/`, `cache/`, `debug/`, `ide/`, `downloads/`
- `security_warnings_state_*.json`, `mcp-needs-auth-cache.json`

**의도적 제외** — 기기별로 새로 구성:
- `projects/` — auto memory 포함. 새 PC에서 사용자 맞춤으로 새로 쌓아감
- `settings.local.json` — 로컬 전용 권한 허용 목록 (`Bash(rm ...)` 같은 경로 고정 규칙)
- `plugins/` — 공식 플러그인 캐시. `settings.json`의 `enabledPlugins` 기반으로 Claude Code가 자동 재설치
- `skills/gstack/node_modules`, `skills/gstack/browse/dist/`, `skills/gstack/design/dist/` — `./setup`이 로컬에서 재빌드

## 🌐 claude.ai 호스팅 MCP는 자동 동기화

- `Context7`, `Hugging Face`, `Notion`, `Gmail`, `Google Calendar` — claude.ai 계정에 묶인 connector. 로그인 시 자동 복원. 백업 불필요.

---

## 🔄 원본 PC에서 업데이트 후 재푸시 루틴

```bash
cd ~/Documents/Develop_Fold/Claude-code-agent-backup

# 1. 최신 상태 동기화
rsync -a --delete ~/.claude/agents ./
rsync -a --delete ~/.claude/rules ./
rsync -a --delete \
  --exclude='node_modules' \
  --exclude='browse/dist' \
  --exclude='design/dist' \
  --exclude='.git' \
  ~/.claude/skills ./
cp ~/.claude/CLAUDE.md ./
cp ~/.claude/settings.json ./
cp ~/.claude/.mcp.json ./

# 2. 커밋 + 푸시
git add -A
git commit -m "sync: update settings"
git push
```

## 📝 Commit Rules

- `Co-Authored-By` 포함 금지 (CLAUDE.md 전역 규칙)
- 커밋 메시지는 한국어/영어 자유 — 기존 스타일은 `chore:`, `sync:` 프리픽스 사용
