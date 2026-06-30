# RepairSafe — Home Repair Safety Assistant

RepairSafe is a home repair Q&A assistant with a safety layer built in front of it. Before it answers any question, it judges how dangerous the repair is and changes its response based on that — because not every repair should come with a confident "here's how."

Built as part of the CodePath AI201 program.

---

## What it does

Ask RepairSafe a home repair question. Instead of answering blindly, it runs the question through a three-stage pipeline:

1. **Classify** — an LLM-as-judge reads the question and sorts it into one of three safety tiers.
2. **Respond** — a different response strategy runs depending on the tier.
3. **Log** — every interaction is recorded to an audit trail.

### The three tiers

| Tier | Meaning | Example | Response |
|------|---------|---------|----------|
| `safe` | Routine DIY, worst case is cosmetic | Patching a small drywall hole | Full step-by-step instructions |
| `caution` | Doable, but a mistake has real cost | Replacing a kitchen faucet | Instructions with warnings built into the steps |
| `refuse` | Fire / flood / structural / injury risk, or needs a permit | Fixing a suspected gas leak | No instructions — explains the danger and refers to a licensed pro |

The hardest distinction is the **"replacing existing" vs. "adding new"** boundary in electrical work: replacing a dead outlet is `caution` (component swap on an existing circuit), but adding a new outlet is `refuse` (new wiring from the panel, a fire hazard if done wrong). The classifier is built to get this right.

---

## How it works

**LLM-as-judge classifier.** The classifier doesn't talk to the user — it returns a structured tier (`safe` / `caution` / `refuse`) that the rest of the pipeline consumes. The prompt uses tier definitions plus few-shot examples to pin down the edge cases.

**Fail-closed design.** If the classifier's output can't be parsed, or the tier isn't valid, the system falls back to `refuse` rather than `safe`. A frustrated user is a better failure than a hurt one.

**Behavior-prohibiting refuse prompt.** The refuse responder doesn't just say "be safe" — it explicitly prohibits providing any steps, partial instructions, or "how a professional does it," and closes common jailbreak framings ("hypothetically," "for research," "I'm a licensed pro"). This stops the model from leaking dangerous instructions while sounding cautious.

**Audit logging.** Every interaction is appended to `logs/audit.jsonl` in JSONL format (one JSON record per line) — timestamp, tier, question, and response preview — so the system's behavior can be reviewed after the fact.

---

## Setup

1. Clone the repo
2. Create and activate a virtual environment:

```bash
   python -m venv .venv
   source .venv/bin/activate   # Mac/Linux
   # or: .venv\Scripts\activate  # Windows
```

3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Groq API key
5. Run the app: `python app.py`

---

## Repository structure