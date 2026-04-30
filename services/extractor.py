from openai import OpenAI
import json
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

FIELDS = [
    "full_name",
    "date_of_birth",
    "payer_name",
    "chief_complaint",
    "street",
    "city",
    "state",
    "zip_code",
]

def extract_info(user_input: str, state: dict) -> dict:
    missing = state.get("missing_fields") or []
    current_field = next(iter(missing), None)
    print("asking for:", current_field)

    if not user_input:
        return {}

    prompt = f"""
    You are extracting structured medical intake information.

    Extract the following fields if present in the message.
    Return ONLY valid JSON.

    The assistant is currently asking for: {current_field}
    Prioritize extracting that field.

    Fields:
    - full_name
    - date_of_birth
    - payer_name
    - chief_complaint
    - street
    - city
    - state
    - zip_code

    Rules:
    - Only include fields that are explicitly mentioned
    - If not mentioned, return null
    - Do not guess
    - Normalize capitalization where appropriate

    User message:
    "{user_input}"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content.strip()

    try:
        data = json.loads(text)
    except:
        return {}

    # Remove nulls and already-filled fields
    cleaned = {}
    for k, v in data.items():
        if v and not state.get(k):
            cleaned[k] = v

    print("LLM extracted:", cleaned)
    return cleaned