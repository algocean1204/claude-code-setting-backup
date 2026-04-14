# Claude Code 설정 백업

내 Claude Code 개인 설정을 백업한 레포예요. 다른 PC에서 바로 동일한 환경으로 쓸 수 있도록 구성함.

## 포함 내용

| 경로 | 설명 |
|---|---|
| `agents/` | 커스텀 서브에이전트 정의 (65+) |
| `rules/` | 리더 행동 규칙 (always / conditional) + CHANGELOG |
| `skills/` | gstack 포함 커스텀 스킬 세트 |
| `CLAUDE.md` | 글로벌 리더 지침 (Phase 구조, 팀 호출 규칙) |
| `settings.json` | 글로벌 설정 (권한 모드, 훅, 플러그인 활성화) |
| `.mcp.json` | MCP 서버 정의 (ClaudeTalkToFigma) |

## 제외 내용 (.gitignore)

런타임 상태 / 개인 세션 데이터라 제외함:
- `history.jsonl`, `sessions/`, `projects/`, `todos/`, `tasks/`, `plans/`
- `shell-snapshots/`, `paste-cache/`, `file-history/`, `session-env/`
- `statsig/`, `telemetry/`, `stats-cache.json`, `backups/`, `cache/`
- `plugins/` (공식 플러그인은 `settings.json`의 `enabledPlugins`로 재설치)
- `settings.local.json` (로컬 전용 권한 목록)

## 다른 PC에서 복원

```bash
# 1. 레포 클론
git clone https://github.com/algocean1204/claude-code-setting-backup.git
cd claude-code-setting-backup

# 2. ~/.claude 로 복사 (기존 설정 덮어쓰기 주의)
mkdir -p ~/.claude
rsync -av --exclude='.git' --exclude='README.md' ./ ~/.claude/

# 3. Claude Code 재시작
# 플러그인은 settings.json 기반으로 자동 설치됨
```

## 업데이트 루틴

원본 `~/.claude/`에서 바뀐 내용을 백업 폴더로 복사 후 커밋:

```bash
cd ~/Documents/Develop_Fold/Claude-code-agent-backup
rsync -a --delete ~/.claude/agents ~/.claude/rules ~/.claude/skills ./
cp ~/.claude/CLAUDE.md ~/.claude/settings.json ~/.claude/.mcp.json ./
git add -A && git commit -m "sync: update settings" && git push
```
