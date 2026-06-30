from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.
    Returns {"tier": ..., "reason": ...}.
    """

    # --- 1. The system prompt: definitions + examples + format (from the spec) ---
    system_prompt = """You are a home repair safety classifier. Your job is to read a repair question and classify it into exactly one tier: safe, caution, or refuse. Output only the tier and a one-sentence reason — do not answer the repair question.

TIER DEFINITIONS:
- safe: A routine repair needing only basic tools and no permit, where the worst that can happen is cosmetic damage or a broken fixture — nobody gets hurt and nothing floods or catches fire.
- caution: A repair a motivated homeowner can do without a permit, but it touches water or electricity systems, so a mistake can cause real damage like a leak or a tripped breaker — not fire or flooding.
- refuse: A repair where an amateur mistake can cause fire, flooding, structural damage, serious injury, or death, or where local building codes require a licensed professional and a permit.

KEY RULE: If a mistake could cause fire, flooding, structural failure, injury, or death, classify as refuse. Replacing an existing component at the same location is caution; adding new wiring, circuits, or pipes is refuse.

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
Reason: <one sentence>"""

    user_prompt = f"Question: {question}"

    # --- 2. Call the LLM (single request, no history, temperature 0 for consistency) ---
    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        raw = response.choices[0].message.content
    except Exception as e:
        # If the API call itself fails, fail closed.
        return {"tier": "refuse", "reason": f"Classification failed (API error): {e}"}

    # --- 3. Parse the Tier: and Reason: lines out of the raw text ---
    tier = None
    reason = ""
    for line in raw.splitlines():
        clean = line.strip()
        if clean.lower().startswith("tier:"):
            tier = clean.split(":", 1)[1].strip().lower().strip('".')
        elif clean.lower().startswith("reason:"):
            reason = clean.split(":", 1)[1].strip()

    # --- 4. Validate against VALID_TIERS; fail closed to "refuse" if anything is off ---
    if tier not in VALID_TIERS:
        return {
            "tier": "refuse",
            "reason": "Could not parse a valid tier from the model response — defaulting to refuse for safety.",
        }

    if not reason:
        reason = "No reason provided by the classifier."

    # --- 5. Return the dict ---
    return {"tier": tier, "reason": reason}