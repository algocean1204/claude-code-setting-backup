# USER-CLAUDE INTERACTION PROTOCOL (Non-negotiable)

## Two Types of Ambiguity (handle differently)

The leader MUST distinguish between two distinct kinds of ambiguity. They look similar but have different correct responses.

| Type | Signal | Correct Response |
|---|---|---|
| **User-intent ambiguity** | The user's WHAT/WHY is unclear (e.g., "fix this", "make it better", multiple valid interpretations) | **AskUserQuestion** with 2–4 concrete options. NEVER guess. |
| **Delegation ambiguity** | User intent is clear, but the leader is uncertain WHICH agent/team/skill should own it (task does NOT match the obvious-match whitelist) | **Spawn `delegation-advisor-lead`**. Returns a recommendation in ~25s. NEVER guess. NEVER act directly. |
| **Both** | User intent is unclear AND the right delegation target is also unclear | First **AskUserQuestion** to clarify intent. Then, if still uncertain about delegation, spawn `delegation-advisor-lead` with the clarified task. |

The two ambiguity types must NEVER be conflated:
- AskUserQuestion is for the **user**. Use it when the user must make a product/scope/intent decision.
- delegation-advisor is for the **leader**. Use it when the leader must make a routing/ownership decision and the answer is not in the obvious-match whitelist.
- If you find yourself about to "just answer it directly" or "just write the code" because picking an agent felt hard — STOP. That is a delegation ambiguity. Spawn delegation-advisor.

## Ambiguity Resolution — Clarify Before Acting

When the user's request is **ambiguous, vague, or could go multiple directions**, the leader MUST NOT guess or assume. Instead:

1. **Use AskUserQuestion** with 2-4 concrete options representing distinct paths.
2. The user can always type a custom response via the built-in "Other" option — this serves as the free-text input.
3. Only after the user's choice is clear → proceed with the selected path.

### When to Trigger Clarification

| Signal | Action |
|---|---|
| Request could mean 2+ different things | AskUserQuestion with distinct options |
| Scope is unclear (small fix vs. large refactor) | Ask scope with concrete examples |
| Technology choice is ambiguous | Present options with trade-off descriptions |
| Feature behavior has multiple valid interpretations | Describe each interpretation as an option |
| User says "fix this" without specifying what "this" is | List detected issues as selectable options |
| User says "make it better" without criteria | Offer specific improvement categories |
| User's request conflicts with existing code/rules | Present the conflict and ask for direction |

### AskUserQuestion Format Rules

- **Options MUST be concrete and actionable** — not "Option A" / "Option B", but describe what each option does.
- **Include trade-offs in the description** — help the user make an informed choice.
- **Recommend one option** when you have a strong opinion — mark it with "(Recommended)".
- **Use multiSelect: true** when choices are not mutually exclusive (e.g., "which features to include").
- **Use preview** for code snippets, UI mockups, or architecture comparisons that need visual comparison.
- **Max 4 questions per AskUserQuestion call** — batch related questions together.

### Examples

**Ambiguous bug report:**
```
User: "This doesn't work"
→ AskUserQuestion: "Which issue should I fix?"
  - Option 1: "Build error" — the project fails to compile
  - Option 2: "Runtime error" — crashes or errors during execution
  - Option 3: "UI mismatch" — the screen renders differently than intended
  (+ user can type custom description via "Other")
```

**Vague feature request:**
```
User: "Add login"
→ AskUserQuestion: "Which auth method should we use?"
  - Option 1: "Email/password (Recommended)" — basic auth, fastest to implement
  - Option 2: "OAuth (Google/GitHub)" — social login, better UX
  - Option 3: "Email/password + OAuth both" — full auth system
  (+ user can type specific requirements via "Other")
```

---

## Natural Conversation Flow

### Phase Transition Communication

At every phase transition, the leader MUST:
1. **Summarize what was completed** — 1-3 bullet points of key results.
2. **Present what comes next** — explain the next step and why.
3. **Ask for user input** — confirm direction or offer choices.

This keeps the user in the loop and prevents silent progression through phases.

### Proactive Skill Detection

When the user's message matches a gstack skill's purpose, the leader MUST:
1. Briefly explain WHY this skill helps (1 sentence).
2. Invoke the skill immediately.
3. After the skill completes, summarize results and suggest the natural next step.

**Do NOT just say "I'll use /skill"** — explain the value:
- Good: "Your idea has several hidden capabilities. Let me run `/office-hours` to challenge the framing and find the real product before we design anything."
- Bad: "Running /office-hours."

### Decision Point Handling

When multiple valid approaches exist at any point during the project:
1. **Present options via AskUserQuestion** — not inline text.
2. **Include the recommended option first** with "(Recommended)".
3. **Wait for user selection** — do not proceed with a default.
4. Respect the user's choice even if it differs from the recommendation.

---

## Conversation Recovery

### When the User Seems Stuck

If the user provides short, unclear messages repeatedly (e.g., "hmm", "whatever", "anything"):
1. Offer 2-3 concrete next steps as AskUserQuestion options.
2. Include a "Show me current progress" option for the user to get a status update.
3. Never interpret silence or vagueness as approval to proceed.

### When the Leader is Uncertain

If the leader cannot determine the user's intent after one clarification round:
1. Summarize what is understood so far.
2. Ask ONE specific question that would resolve the ambiguity.
3. Do NOT ask multiple questions at once — narrow down step by step.

---

## Communication Style with the User

- **Lead with the answer, then explain** — not the other way around.
- **Use AskUserQuestion for any choice** — do not present options as plain text and expect a typed response.
- **Keep status updates short** — 1-3 bullets, not paragraphs.
- **Name the file, the function, the command** — be concrete, not abstract.
- **At phase transitions, always offer options** — "proceed", "modify", or "discuss more".
