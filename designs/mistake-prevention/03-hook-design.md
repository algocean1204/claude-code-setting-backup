# Hook 설계 — 실시간 예방 엔진

## 설계 원칙

1. **PreToolUse가 예방의 핵심** — `PostToolUse`는 이미 실행된 뒤다. 공식 Claude Code docs에서 `PreToolUse`만 실행 전 차단(deny) 가능.
2. **Latency budget**: `PreToolUse` 50-200ms, 최대 500ms. 이를 초과하면 UX 훼손.
3. **Shell entrypoint → Python runner**: shell script가 `python3` 호출. M4 Pro 기준 cold start 포함 50-180ms.
4. **P0만 hard deny, P1은 ask, P2 이하는 context/warn**. Hard deny가 많으면 모델이 hook 우회를 시도한다.
5. **Hook이 해야 할 것/하지 말아야 할 것**: 좁고 정밀한 패턴만. 전체 테스트, lint, repo-wide grep 금지.

## Hook 구성 (7종)

### Hook 1: PreToolUse:Bash — Destructive Command Guard

```json
{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/mistake-pretool.sh",
    "timeout": 2
  }]
}
```

탐지 대상:
- `rm -rf` / `rm -r` (broad deletion)
- `git reset --hard` / `git checkout .` / `git clean -f`
- `git push --force` / `git push -f`
- `kill -9` (broad process kill)
- `chmod 777` / `chmod -R`
- `DROP TABLE` / `DROP DATABASE` / `TRUNCATE`
- pytest 프로세스 3개 이상 존재 시 추가 pytest 실행 차단

처리: P0 deny (즉시 차단, 사용자 확인 요구)

---

### Hook 2: PreToolUse:Edit|Write — Code Quality Guard

```json
{
  "matcher": "Edit|MultiEdit|Write",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/mistake-pretool.sh",
    "timeout": 2
  }]
}
```

탐지 대상:
- 보호 파일 직접 수정 (`settings.json`을 agent가 직접 수정 시도 등)
- `stub` / `TODO` / `NotImplemented` / `FIXME` 삽입
- workaround 키워드: `@ts-ignore`, `@ts-expect-error`, `eslint-disable`, `noqa`, `!important`, `any` type
- generated 파일 직접 수정 (lockfile, compiled output)
- 200줄 초과 파일 생성

처리: P1 ask (경고 + 사유 설명 요구)

---

### Hook 3: PreToolUse:Agent|Task — Delegation Protocol Guard

```json
{
  "matcher": "Agent|Task",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/mistake-pretool.sh",
    "timeout": 2
  }]
}
```

탐지 대상:
- `NoThinkingAgent` 단독 스폰 (monitor 없이)
- Phase 2에서 guardian 없이 구현 에이전트 스폰
- 이미 활성화된 동일 에이전트 중복 스폰

처리: P0 deny (필수 pairing 위반)

---

### Hook 4: PostToolUse — Event Recorder

```json
{
  "matcher": "Bash|Edit|MultiEdit|Write|Agent|Task",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/mistake-posttool.sh",
    "timeout": 2
  }]
}
```

역할:
- 실행 결과에서 evidence 수집 (diff summary, 변경 파일 목록)
- `PreToolUse`에서 탐지된 이벤트의 해결 여부 기록
- lightweight diff scan으로 비정상 패턴 후속 감지
- `events/*.jsonl`에 append

처리: warn only (차단 없음, 기록 전용)

---

### Hook 5: UserPromptSubmit — Context Injection

```json
{
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/mistake-prompt-context.sh",
    "timeout": 2
  }]
}
```

역할:
- 현재 프로젝트에서 active pattern 중 상위 3개를 context로 주입
- severity 높은 순 정렬
- 300-600 tokens 이내로 제한
- `additionalContext` 형태로 반환

출력 형식:

```json
{
  "additionalContext": "[MISTAKE PREVENTION] Active patterns for this project:\n1. [P0] destructive_bash: rm -rf, force push 차단 중\n2. [P1] no_workaround: @ts-ignore, eslint-disable 삽입 시 사유 필요\n3. [P1] pytest_guard: pytest 3개 이상 동시 실행 금지"
}
```

---

### Hook 6: Stop — Session End Gate

```json
{
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/mistake-stop-gate.sh",
    "timeout": 3
  }]
}
```

역할:
- unresolved P0/P1 이벤트 존재 시 종료 차단
- 코드 변경이 있는데 검증 evidence가 없으면 경고
- curation threshold 도달 시 큐레이션 요청 생성
- 세션 이벤트 통계 기록

---

### Hook 7: SubagentStop — Subagent Evidence Gate

```json
{
  "matcher": "*",
  "hooks": [{
    "type": "command",
    "command": "~/.claude/hooks/mistake-subagent-stop.sh",
    "timeout": 3
  }]
}
```

역할:
- subagent가 required evidence 없이 종료하는 것 감지
- 검증/테스트 결과 없이 "완료" 보고하는 패턴 차단

## Hook 구현 구조

```
~/.claude/hooks/mistake-pretool.sh (shell entrypoint)
  → exec python3 ~/.claude/mistakes/bin/hook_runner.py pretool

~/.claude/hooks/mistake-posttool.sh
  → exec python3 ~/.claude/mistakes/bin/hook_runner.py posttool

~/.claude/hooks/mistake-prompt-context.sh
  → exec python3 ~/.claude/mistakes/bin/hook_runner.py prompt

~/.claude/hooks/mistake-stop-gate.sh
  → exec python3 ~/.claude/mistakes/bin/hook_runner.py stop

~/.claude/hooks/mistake-subagent-stop.sh
  → exec python3 ~/.claude/mistakes/bin/hook_runner.py subagent_stop
```

### hook_runner.py 핵심 로직

```python
# Pseudocode
def main(mode):
    input_data = json.load(sys.stdin)
    project_dir = detect_project_dir(input_data)

    # 1. compiled rules 로드 (project overlay → global 순서)
    rules = load_compiled_rules(mode, project_dir)

    # 2. 입력과 룰 매칭
    matches = []
    for rule in rules:
        if matches_scope(rule, input_data) and matches_signals(rule, input_data):
            matches.append(rule)

    # 3. action 결정 (severity 최고값 기준)
    if not matches:
        sys.exit(0)  # allow

    worst = max(matches, key=lambda r: r['severity_rank'])

    # 4. 이벤트 기록
    record_event(matches, input_data, project_dir)

    # 5. 결정 반환
    if worst['action'] == 'deny':
        output = {"decision": "block", "reason": worst['message']}
    elif worst['action'] == 'ask':
        output = {"decision": "block", "reason": worst['message']}
    elif worst['action'] == 'context':
        output = {"additionalContext": worst['message']}

    json.dump(output, sys.stdout)
```

## Latency 벤치마크 목표

| Hook | Target | Max | 측정 방법 |
|---|---|---|---|
| `PreToolUse:Bash` | 80ms | 200ms | Python cold start + rule 로드 + regex 매칭 |
| `PreToolUse:Edit/Write` | 120ms | 300ms | 파일 경로/내용 검사 추가 |
| `PreToolUse:Agent/Task` | 80ms | 200ms | agent name 매칭만 |
| `PostToolUse` | 100ms | 250ms | event append + lightweight diff |
| `UserPromptSubmit` | 100ms | 200ms | top 3 패턴 로드 + format |
| `Stop` | 150ms | 500ms | 전체 세션 이벤트 스캔 |
| `SubagentStop` | 100ms | 300ms | evidence 존재 확인 |

## settings.json Hook 설정 (기존 유지 + 신규 추가)

기존 `PostToolUse Write|Edit` hook (CHANGELOG + backup)은 그대로 유지한다. 신규 hooks는 기존 hook 뒤에 추가한다. 기존 hook과의 실행 순서: 기존이 먼저, mistake hooks가 뒤에.
