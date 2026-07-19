---
name: learning-roadmap-maintainer
description: Maintain the Learning Roadmap repo and app. Use when updating weekly reading cards, syncing roadmap state between GitHub and local files, changing the roadmap HTML UI, or explaining the GitHub Pages / GitHub API workflow for this repo.
---

# Learning Roadmap Maintainer

## Purpose

Maintain the `fleet-os-learning` roadmap app with the least possible operational friction.

The app is a static HTML UI (`learning_roadmap.html`) backed by a shared data file (`roadmap-data.json`). The user edits/favorites/deletes items in the browser and saves state back to GitHub through the GitHub Contents API. Codex should update weekly cards by editing `roadmap-data.json`, not by editing embedded HTML seed data.

## Repository

- Local repo: `/Users/jinzhaochang/Documents/Learning Roadmap`
- GitHub repo: `WhiteCloudUU/fleet-os-learning`
- Branch: `main`
- Remote should use SSH: `git@github.com:WhiteCloudUU/fleet-os-learning.git`
- GitHub Pages URL: `https://whiteclouduu.github.io/fleet-os-learning/learning_roadmap.html`

## Core Files

- `roadmap-data.json`: source of truth for roadmap state.
- `learning_roadmap.html`: static UI shell and fallback seed.
- `learning_roadmap_instruction.md`: rules for generating weekly cards.
- `staff_os.md`: user strategy context and prioritization principles.

## Golden Rules

1. Before generating a weekly card, always pull remote first:

   ```bash
   cd "/Users/jinzhaochang/Documents/Learning Roadmap"
   git pull
   ```

2. Generate weekly updates by appending exactly one card to `weeklies` in `roadmap-data.json`.
3. Do not modify domain/favorites cards unless the user explicitly asks.
4. Do not add reading status fields. The app no longer tracks `to-read`, `reading`, or `read`.
5. Preserve user browser-saved state by avoiding broad rewrites of `roadmap-data.json`.
6. For UI changes, edit `learning_roadmap.html` only.
7. After changes, validate JSON and HTML script syntax.
8. If asked to publish, commit and push with SSH.

## Weekly Card Workflow

Use this workflow when the user asks for a weekly reading card.

1. Pull the latest remote state.
2. Read `learning_roadmap_instruction.md` fully.
3. Read `staff_os.md` for prioritization context.
4. Inspect existing `roadmap-data.json` weeklies to determine the last card date.
5. Browse current sources because this task depends on recent AI/eval/safety updates.
6. Select only high-signal items for the user's focus:
   - AI safety eval infrastructure
   - release gates
   - eval reliability
   - low-latency/reusable eval harnesses
   - policy-grounded safety scoring
   - online monitoring to eval feedback loops
7. Append one weekly card to `weeklies`.
8. Use exactly these lane dividers:
   - `Eval Infra`
   - `Eval Infra - Safety`
   - `AI Frontier`
9. Leave a lane empty if no meaningful signal exists.
10. New item shape:

   ```json
   {
     "id": "wk-YYYYMMDD-...",
     "title": "...",
     "url": "...",
     "note": "Chinese note with English technical terms"
   }
   ```

11. Do not include `status`.
12. Keep `desc` as an empty string for weekly cards.

Example weekly card:

```json
{
  "id": "d-week-20260717",
  "dated": true,
  "date": "2026-07-17",
  "title": "📅 Weekly · 2026-07-17",
  "desc": "",
  "items": [
    { "id": "wk-20260717-ei", "type": "divider", "label": "Eval Infra" },
    { "id": "wk-20260717-ei1", "title": "...", "url": "...", "note": "..." },
    { "id": "wk-20260717-es", "type": "divider", "label": "Eval Infra - Safety" },
    { "id": "wk-20260717-af", "type": "divider", "label": "AI Frontier" }
  ]
}
```

## Favorites Model

Weekly cards are an inbox. Domain cards are curated favorites.

- Weekly item heart icon copies the item into the matching domain card.
- It does not move the item out of Weekly.
- Clicking again undoes the favorite by removing the copied item.
- Domain cards currently use these dividers:

`Eval Infra`
- `General / Basics`
- `Eval Harness`
- `EvalOps & Quality`

`Eval Infra - Safety`
- `Safety Basics`
- `Threats & Red-Teaming`
- `Safety Gates & Monitoring`

`AI Frontier`
- `General`

## Browser / Sync Behavior

The HTML app supports:

- `↻`: load latest remote `roadmap-data.json`.
- `Save`: commit current state to GitHub using the GitHub Contents API.
- `Token`: store a GitHub fine-grained token in browser `localStorage`.
- `Export JSON`: manual backup.

Important:

- Browser edits first save to localStorage as a local draft.
- They are not persisted to GitHub until the user clicks `Save`.
- If the user saves from the browser, local repo files become stale until `git pull`.
- If `Load latest` or `Save` returns 404, likely causes are:
  - repo is private,
  - GitHub Pages is not enabled,
  - token lacks access to `WhiteCloudUU/fleet-os-learning`,
  - token lacks `Contents: Read and write`.

Token requirements:

- Fine-grained personal access token.
- Repository: `WhiteCloudUU/fleet-os-learning`.
- Permission: `Contents: Read and write`.

## Validation

After editing, run:

```bash
cd "/Users/jinzhaochang/Documents/Learning Roadmap"
/Users/jinzhaochang/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node - <<'NODE'
const fs = require('fs');
const html = fs.readFileSync('learning_roadmap.html','utf8');
JSON.parse(fs.readFileSync('roadmap-data.json','utf8'));
JSON.parse(html.match(/<script id="seed" type="application\/json">\n([\s\S]*?)\n<\/script>/)[1]);
for (const m of html.matchAll(/<script(?! id="seed")[^>]*>\n([\s\S]*?)\n<\/script>/g)) new Function(m[1]);
console.log('ok');
NODE
```

## Commit / Push

This repo uses a versioned Git hook:

- Hook path: `.githooks/pre-push`
- Local config: `git config core.hooksPath .githooks`
- Purpose: block pushes when remote has newer `roadmap-data.json`, or when local/staged data changes have not been handled.

The hook is designed to prevent overwriting browser-saved roadmap state. If it blocks a push, run:

```bash
git pull --rebase origin main
```

Then validate and push again.

Use focused commits. For weekly card updates:

```bash
git add roadmap-data.json
git commit -m "Add weekly roadmap card"
git push origin main
```

For UI or workflow changes, stage the specific changed files:

```bash
git add learning_roadmap.html learning_roadmap_instruction.md roadmap-data.json
git commit -m "Update roadmap sync workflow"
git push origin main
```

Never run destructive git commands such as `git reset --hard` unless the user explicitly asks.
