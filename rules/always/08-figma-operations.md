# FIGMA OPERATIONS — Leader Rules (Non-negotiable)

This plugin has a 30-second timeout per command. Large responses or Figma main-thread contention cause silent disconnects. "No global scans, ID-targeted small reads only" is the only safe path.

## Pre-flight Before Spawning figma-agent (mandatory)

1. Leader calls `get_document_info` ONCE and caches the result (page list + top-level metadata)
2. Identify or create target page, obtain its `pageId`
3. Determine root node IDs for the scope of work
4. Prepare a tool whitelist (only tools needed for the specific task)
5. Pass to figma-agent: `{ channelId, pageId, rootNodeIds[], toolWhitelist[], cachedDocumentInfo }`
6. Sub-agents MUST NOT call `get_document_info` again — use the cached version from leader

## Concurrency Limit

- Max **2** figma sub-agents active on the same Figma file simultaneously
- If more work is needed, queue tasks and redistribute after a slot opens
- Pipelining allowed: while figma-inspector checks page N, figma-agent may start page N+1

## On Failure from figma-agent

- **NEVER** retry the same scope — redistribute with a NARROWER scope (fewer nodes, smaller area)
- If agent reports UNCERTAIN, inspect the result (spawn figma-inspector) before deciding next step
- After **2 consecutive timeout escalations** from any agent, STOP all Figma work and report to user
- Do NOT instruct an agent to use a "similar alternative tool" to work around a failure — leader decides the workaround

## Post-Page Inspection Protocol (mandatory)

After figma-agent completes each page/screen, leader MUST spawn `figma-inspector`:

```
figma-agent completes page
       |
       v
Spawn figma-inspector { channelId, pageId, createdNodeIds[] }
       |
       v
PASS --> proceed to next page
FAIL --> spawn figma-agent with fix-only instructions (narrower scope)
       --> re-run figma-inspector
       --> max 2 fix cycles per page
       --> still FAIL --> escalate to user with issue details
```

Do NOT proceed to the next page until the current page passes inspection.

## Text Creation Rules (enforced by figma-agent + figma-inspector)

Every `create_text` call executed by figma-agent MUST follow these rules (defined in full in `~/.claude/agents/figma-agent.md` → "create_text Call Rules"):

1. `load_font_async(family, style)` BEFORE `create_text` — never set characters on an unloaded font
2. `textAutoResize: "WIDTH_AND_HEIGHT"` by default — let content size the node
3. NEVER pass `width`/`height` of `0` — omit `resize_node` entirely if no real size is required
4. Inside auto-layout parents: call `set_layout_sizing` with `layoutSizingHorizontal: "HUG"` (labels) or `"FILL"` (paragraphs). Never `"FIXED"` unless wrapping is intentional.

figma-inspector's Check 6 enforces all 4 rules on the produced nodes. Violations are P0 and trigger a fix cycle.

## Layout Structure Rules

All Figma designs MUST follow this spatial arrangement:

### Vertical: Main Pages
- Main pages (Home, Profile, Search, etc.) stack **vertically** (increasing Y, consistent X)
- Gap between page sections: **100px** vertical spacing

### Horizontal: Sub-Features
- Sub-features of a page (modals, side panels, detail views, tabs) are arranged **horizontally** next to their parent main page
- Same Y position as the main page, increasing X offset
- Gap between main page and first sub-feature: **40px** horizontal
- Gap between sub-features: **40px** horizontal

### Sections: Page Groups
- Each page group (main page + its sub-features) is wrapped in a Figma **Section** (`create_section`)
- Section named: `"Section - [PageName]"`
- Sections themselves stack vertically with 100px gap

```
[Section - Home]
  Main(0,0)  Modal(+1480,0)  SidePanel(+2960,0)
                                                    ← 100px gap
[Section - Profile]
  Main(0,0)  EditModal(+1480,0)  Settings(+2960,0)
                                                    ← 100px gap
[Section - Search]
  Main(0,0)  FilterPanel(+1480,0)  Results(+2960,0)
```
