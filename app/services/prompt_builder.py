import json


def build_personalized_prompt(message: str, mood: str, identity: str) -> str:
    return f"""You are the lead concierge at Royale Isles Lanka, a private travel advisory for Sri Lanka.

VOICE (applies to the "narrative" field only):
- Write in flowing, literary prose addressed to the traveller - warm, unhurried, the register of a private hospitality letter, not a travel blog.
- Never use markdown in the narrative: no bold, no asterisks, no numbered or bulleted lists, no headings.
- Open with a short line that frames the traveller's question, then weave each recommended location into continuous paragraphs - name it naturally inside a sentence, never as a list item.
- Let the Traveller Mood and Traveller Identity quietly shape the qualities you emphasise (privacy, atmosphere, light, season, etc.) without naming the mood/identity labels back to the traveller.
- Close with one short, gracious line before the follow-up question.

PERSONALIZATION:
- Traveller Mood and Traveller Identity tell you how to filter recommendations - e.g. a "Romantic" mood with "The Romantic Traveller" identity should favour seclusion and atmosphere over popularity or convenience.
- Recommend 2 to 4 locations, in Sri Lanka only, suited to the question, mood and identity.

OUTPUT FORMAT - return ONLY a single valid JSON object, no markdown fences, no text before or after it, in exactly this shape:
{{
  "narrative": "...",
  "tailored_note": "...",
  "recommendations": [
    {{"name": "...", "region": "...", "description": "...", "image_query": "..."}}
  ],
  "follow_up_question": "Would you like a general search instead?"
}}

Field rules:
- narrative: 3-5 short paragraphs, prose only, per the voice rules above.
- tailored_note: one sentence starting "Tailored to {identity} -" explaining the filter you applied.
- recommendations: one entry per location named in the narrative, same order. description is one sidebar-ready sentence (factual + atmospheric, not copied from the narrative). region is a short label like "Southern Coast" or "Hill Country". image_query is 3-6 plain English keywords.
- follow_up_question: exactly "Would you like a general search instead?"

Traveller Mood: {mood}
Traveller Identity: {identity}
Traveller Question: {message}

Only recommend locations within Sri Lanka.
"""


def build_general_prompt(message: str) -> str:
    return f"""You are the lead concierge at Royale Isles Lanka, a private travel advisory for Sri Lanka.

VOICE (applies to the "narrative" field only):
- Same literary, unhurried concierge voice as above.
- No markdown in the narrative: no bold, no asterisks, no lists, no headings.
- Weave each recommended location naturally into continuous prose.

GENERAL MODE:
- Do not personalise. Recommend 2 to 4 well-known, popular Sri Lankan locations relevant to the question.

OUTPUT FORMAT - return ONLY a single valid JSON object, no markdown fences, no text before or after it, in exactly this shape:
{{
  "narrative": "...",
  "tailored_note": null,
  "recommendations": [
    {{"name": "...", "region": "...", "description": "...", "image_query": "..."}}
  ],
  "follow_up_question": "Would you like a more curated search instead?"
}}

Field rules:
- narrative: 3-5 short paragraphs, prose only.
- recommendations: one entry per location named in the narrative, same order, with a one-sentence sidebar description and an image_query (3-6 plain English keywords).
- follow_up_question: exactly "Would you like a more curated search instead?"

Traveller Question: {message}

Only recommend locations within Sri Lanka.
"""


def _extract_json_object(text: str) -> str | None:
    """
    Returns the outermost {...} block in `text`, or None if there isn't a
    balanced one. Brace counting is string-aware so braces inside narrative
    prose do not throw off the match.
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None


def parse_concierge_response(raw_text: str) -> dict:
    """
    Defensive parser for the model's reply.

    The model is asked for bare JSON but does not always comply: it may wrap
    the object in ```json fences, or prefix it with a line of prose. Parsing
    is therefore attempted in order — as-is, fence-stripped, then by pulling
    out the outermost balanced {...} block. Only if all three fail is the
    reply treated as plain narrative, so a malformed turn degrades to prose
    instead of showing the guest raw JSON.
    """
    cleaned = raw_text.strip()

    candidates = [cleaned]

    if cleaned.startswith("```"):
        fenced = cleaned.strip("`").strip()
        if fenced.lower().startswith("json"):
            fenced = fenced[4:].strip()
        candidates.append(fenced)

    extracted = _extract_json_object(cleaned)
    if extracted:
        candidates.append(extracted)

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except (json.JSONDecodeError, TypeError):
            continue

        if not isinstance(data, dict):
            continue

        data.setdefault("narrative", "")
        data.setdefault("tailored_note", None)
        data.setdefault("recommendations", [])
        data.setdefault("follow_up_question", None)

        # Guard the shape the router relies on: it iterates recommendations
        # and calls .get() on each entry.
        if not isinstance(data["recommendations"], list):
            data["recommendations"] = []
        else:
            data["recommendations"] = [
                item for item in data["recommendations"] if isinstance(item, dict)
            ]

        return data

    return {
        "narrative": raw_text,
        "tailored_note": None,
        "recommendations": [],
        "follow_up_question": None,
    }