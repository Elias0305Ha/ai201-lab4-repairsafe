# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
A routine repair needing only basic tools and no permit, where the worst that can happen is cosmetic damage or a broken fixture — nobody gets hurt and nothing floods or catches fire.
```

**caution:**
```
A repair a motivated homeowner can do without a permit, but it touches  water or electric city  systems, so a mistake can cause real damage like a leak or a tripped breaker not fire or flooding.
```

**refuse:**
```
Repairs where an amateur mistake can cause fire, flooding, structural damage, serious injury, or death — or where local building codes require a licensed professional and a permit. Do not provide DIY instructions for these.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
I chose definitions + few-shot examples. Definitions alone leave the caution/refuse boundary fuzzy, so the LLM would guess inconsistently on edge cases. Adding two contrasting examples — especially "replace an existing outlet → caution" vs. "add a new outlet → refuse" — shows the LLM the actual pattern, which is what it needs to get the hardest distinction right. I skipped step-by-step reasoning because this classifier feeds my code, and a clean, easy-to-parse output matters more than squeezing out a little extra accuracy.
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
Tier: caution
Reason: This is a like-for-like outlet swap on an existing circuit, so the worst case is a tripped breaker.
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a home repair safety classifier. Your job is to read a repair 
question and classify it into exactly one tier: safe, caution, or refuse. 
Output only the tier and a one-sentence reason — do not answer the repair question.

TIER DEFINITIONS:
- safe: A routine repair needing only basic tools and no permit, where the worst 
  that can happen is cosmetic damage or a broken fixture — nobody gets hurt and 
  nothing floods or catches fire.
- caution: A repair a motivated homeowner can do without a permit, but it touches 
  water or electricity systems, so a mistake can cause real damage like a leak or 
  a tripped breaker — not fire or flooding.
- refuse: A repair where an amateur mistake can cause fire, flooding, structural 
  damage, serious injury, or death, or where local building codes require a 
  licensed professional and a permit.
KEY RULE: If a mistake could cause fire, flooding, structural failure, injury, or 
death, classify as refuse. Replacing an existing component at the same location is 
caution; adding new wiring, circuits, or pipes is refuse.

EXAMPLES:
Question: How do I replace an outlet that stopped working?
Tier: caution
Reason: It's a like-for-like swap on an existing circuit at the same location, so the worst case is a tripped breaker.

Question: How do I add a new outlet to my garage?
Tier: refuse
Reason: It requires running new wire from the breaker panel, where an amateur mistake can create a hidden fire hazard.

Question: How do I patch a small hole in my drywall?
Tier: safe
Reason: It needs only basic tools and no permit, and the worst case is a cosmetic flaw — nobody gets hurt and nothing floods or catches fire.

FORMAT — respond with exactly these two lines and nothing else:
Tier: <safe|caution|refuse>
Reason: <one sentence>


```

**User message:**
```
Question: {question}
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
Boundary rule: A repair is refuse if a mistake could cause fire, flooding, structural failure, injury, or death, or if it requires new wiring/piping or a permit; otherwise, if a homeowner can do it and the worst case is just a leak or a tripped breaker, it's caution.
Example 1 — "How do I replace an outlet that stopped working?" → caution. It's a like-for-like swap on an existing circuit at the same location; the worst realistic outcome is a tripped breaker, which is recoverable.
Example 2 — "How do I add a new outlet to my garage?" → refuse. It requires running new wire from the breaker panel, which an amateur can mis-wire into a hidden fire hazard — exactly the kind of irreversible danger the refuse tier exists for
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
Fallback behavior: If the LLM response can't be parsed, or the extracted tier isn't in VALID_TIERS (safe, caution, refuse), the function returns "refuse" with a reason noting the classification failed. I chose to fail closed rather than open — defaulting to safe would mean a parsing glitch on a dangerous question (like a gas leak) could let through instructions that hurt someone. refuse is the most conservative fallback: the worst case is over-refusing a question that was actually fine, which is annoying but harmless, versus under-refusing something dangerous, which is not.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
[your answer here]
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
[your answer here]
```
