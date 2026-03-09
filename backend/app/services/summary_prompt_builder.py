import json


def build_summary_prompt(summary_input: dict) -> str:
    structured_block = json.dumps(summary_input, indent=2, sort_keys=True)
    return (
        "System instruction:\n"
        "You are summarizing structured predictive microbiology simulation outputs.\n"
        "Do not invent numbers.\n"
        "Do not invent biological claims not present in the input.\n"
        "Do not claim regulatory validation.\n"
        "Keep tone concise, professional, and plain-English.\n"
        "Mention the output is simulation-based.\n"
        "Mention primary drivers if present.\n"
        "Mention challenge test recommendation if present.\n\n"
        "Rules:\n"
        "- Use only the structured data below.\n"
        "- Keep the response to 2 to 5 sentences.\n"
        "- One short paragraph only.\n"
        "- No bullet points.\n"
        "- No markdown tables.\n"
        "- Mention uncertainty when present.\n\n"
        "Structured data:\n"
        f"{structured_block}\n\n"
        "Write the summary now."
    )
