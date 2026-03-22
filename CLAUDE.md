# Feasibility Study Skill — Development Instructions

## Project Structure
- `skills/feasibility-study/SKILL.md` — Core skill file (keep under 500 lines)
- `skills/feasibility-study/references/` — On-demand reference files (one level deep)
- `skills/feasibility-study/scripts/estimate.py` — Deterministic calculations (Python stdlib only)
- `.claude-plugin/plugin.json` — Plugin metadata for distribution

## Rules
- SKILL.md must stay under 500 lines. Move detailed content to reference files.
- Scripts must use Python stdlib only — no pip dependencies.
- Reference files must be one level deep from SKILL.md (no nested references).
- All estimation formulas go in `scripts/estimate.py`, not in SKILL.md or reference files.
- Test changes by running: `/feasibility-study BuiltWith.com --depth standard`

## Testing
- After any change to SKILL.md or reference files, run the skill against a known product
- Verify the estimation script still works: `echo '{"operation": "cocomo", "kloc": 50, "mode": "semi-detached"}' | python3 skills/feasibility-study/scripts/estimate.py`
- Check that the generated report follows the template in `references/report-template.md`
