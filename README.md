# Tectonic Briefing

A daily structural analysis platform identifying deep forces transforming the world.

## Architecture

```
tectonic-briefing/
├── index.html              # Archive page (GitHub Pages entry point)
├── briefings/              # Daily briefing HTML files
│   └── 2026-04-05.html     # Briefing No. 001
├── threads/                # Cross-briefing structural thread tracking (future)
├── assets/                 # Shared assets if needed
├── scripts/                # Workflow automation scripts
│   └── publish.sh          # One-command publish script
└── README.md
```

## Eight Analytical Lenses

1. **Geopolitical** — Power dynamics, conflict, alliance structures
2. **Technological** — AI, compute, infrastructure, architectural shifts
3. **Economic** — Markets, trade, energy, financial system structure
4. **Scientific** — Paradigm shifts, foundational transitions, discovery
5. **Social & Cultural** — Demographics, labor, inequality, cultural dynamics
6. **Environmental & Ecological** — Climate tipping points, biophysical constraints
7. **Institutional & Governance** — Regulatory architecture, constitutional dynamics, legitimacy
8. **Liminal Signals** — Forces that resist categorization; held contemplatively

## Integrated Systems

- **Inference Engine** — Conditional chains mapping how forces interact
- **Force Interaction Matrix** — Amplification/dampening between structural forces
- **Wise Action** — Entrepreneurship, global markets, investment positioning
- **Structural Vocabulary** — Named patterns accumulating across briefings
- **Anomaly Detection** — What should be happening but isn't
- **Source Archive** — Annotated reading list with Thinker Registry and Serendipity Queue
- **Deep Dive Markers** — Signals for topics warranting extended conversation
- **Research Program Relevance** — Connections to active research projects

## Workflow

### Daily briefing generation
Briefings are generated through conversation with Claude, then published:

```bash
# From the repo root:
./scripts/build.sh --check   # read-only reproducibility + structural check
./scripts/publish.sh
```

The build is deterministic and runs `scripts/validate.py` before publish. New
briefing numbers are allocated from the highest canonical issue number, not the
number of files in the archive. Historical duplicate/gap warnings are retained
for visibility and do not silently renumber already-published issues.

`publish.sh` stages an explicit public-site allowlist; it refuses unrelated
tracked or untracked files rather than sweeping them into a public commit.

### Automated morning candidate

The parent workflow control plane can generate a private candidate each morning:

```bash
workflowctl run tectonic.morning --dry-run  # capability check only
workflowctl status tectonic.morning
```

The scheduled job runs in a disposable repository copy, researches and writes
there through the locally authenticated Claude Code subscription (never a
separate Anthropic API-key call), and requires both the build and structural
validator to pass. It aborts
if briefing inputs changed during generation. Only the validated daily HTML may
cross into this repository; all other provider edits are discarded. The job
stops at `awaiting_review` and never commits, pushes, or publishes. A human must
inspect the candidate and then invoke the normal `publish.sh` workflow.

## Deployment

Served via GitHub Pages from the `main` branch root.

**Access URL:** `https://[username].github.io/tectonic-briefing/`

## Setup (One-Time)

```bash
# 1. Clone or initialize
cd ~/workflow
git clone git@github.com:[username]/tectonic-briefing.git
# OR if starting fresh:
mkdir tectonic-briefing && cd tectonic-briefing && git init

# 2. Enable GitHub Pages
# Go to repo Settings → Pages → Source: Deploy from branch → main → / (root)

# 3. Set up the publish script
chmod +x scripts/publish.sh
```

---

*"We soon observe that little or nothing is really fixed but all is a perpetual flux."* — Frank Knight (1913)
