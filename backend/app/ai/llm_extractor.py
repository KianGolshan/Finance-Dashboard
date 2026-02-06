import json
from app.config import get_settings

settings = get_settings()

EXTRACTION_SCHEMAS = {
    "financial_statement": {
        "fields": [
            {"name": "revenue", "type": "number", "description": "Total revenue / net sales"},
            {"name": "cost_of_goods_sold", "type": "number", "description": "Cost of goods sold / COGS"},
            {"name": "gross_profit", "type": "number", "description": "Gross profit"},
            {"name": "ebitda", "type": "number", "description": "EBITDA"},
            {"name": "net_income", "type": "number", "description": "Net income / net profit"},
            {"name": "total_assets", "type": "number", "description": "Total assets"},
            {"name": "total_liabilities", "type": "number", "description": "Total liabilities"},
            {"name": "total_equity", "type": "number", "description": "Total shareholders equity"},
            {"name": "cash_and_equivalents", "type": "number", "description": "Cash and cash equivalents"},
            {"name": "total_debt", "type": "number", "description": "Total debt (short + long term)"},
            {"name": "free_cash_flow", "type": "number", "description": "Free cash flow"},
            {"name": "period", "type": "string", "description": "Reporting period (e.g. Q3 2024, FY 2023)"},
            {"name": "currency", "type": "string", "description": "Reporting currency"},
        ]
    },
    "investor_report": {
        "fields": [
            {"name": "nav", "type": "number", "description": "Net asset value"},
            {"name": "distributions", "type": "number", "description": "Total distributions"},
            {"name": "contributions", "type": "number", "description": "Total contributions / capital calls"},
            {"name": "irr", "type": "number", "description": "Internal rate of return"},
            {"name": "moic", "type": "number", "description": "Multiple on invested capital"},
            {"name": "dpi", "type": "number", "description": "Distributions to paid-in"},
            {"name": "rvpi", "type": "number", "description": "Residual value to paid-in"},
            {"name": "tvpi", "type": "number", "description": "Total value to paid-in"},
            {"name": "reporting_date", "type": "string", "description": "Report as-of date"},
        ]
    },
    "default": {
        "fields": [
            {"name": "revenue", "type": "number", "description": "Revenue if mentioned"},
            {"name": "ebitda", "type": "number", "description": "EBITDA if mentioned"},
            {"name": "net_income", "type": "number", "description": "Net income if mentioned"},
            {"name": "entity_name", "type": "string", "description": "Company or fund name"},
            {"name": "date", "type": "string", "description": "Key date referenced"},
            {"name": "key_figures", "type": "string", "description": "Other important numerical figures"},
        ]
    },
}


async def extract_fields(raw_text: str, document_type: str | None = None) -> list[dict]:
    """
    Extract structured fields from document text using LLM.
    Falls back to rule-based extraction if no API key is configured.
    """
    if settings.openai_api_key:
        return await _llm_extract(raw_text, document_type)
    return _rule_based_extract(raw_text, document_type)


async def _llm_extract(raw_text: str, document_type: str | None) -> list[dict]:
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        schema = EXTRACTION_SCHEMAS.get(document_type or "", EXTRACTION_SCHEMAS["default"])
        field_descriptions = "\n".join(
            f"- {f['name']} ({f['type']}): {f['description']}" for f in schema["fields"]
        )

        truncated = raw_text[:12000]

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial document extraction specialist. "
                        "Extract structured data from the document text. "
                        "Return a JSON array of objects with keys: field_name, field_value, "
                        "field_type, confidence_score (0-1), context_snippet. "
                        "Only extract fields you find evidence for."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Extract the following fields from this document:\n\n"
                        f"{field_descriptions}\n\n"
                        f"Document text:\n{truncated}"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        extractions = parsed.get("extractions", parsed.get("fields", []))
        if isinstance(extractions, dict):
            extractions = [
                {"field_name": k, "field_value": v, "field_type": "string", "confidence_score": 0.8}
                for k, v in extractions.items()
            ]
        return extractions

    except Exception as e:
        return _rule_based_extract(raw_text, document_type)


def _rule_based_extract(raw_text: str, document_type: str | None) -> list[dict]:
    """Fallback rule-based extraction using pattern matching."""
    import re

    extractions = []
    text_lower = raw_text.lower()

    patterns = {
        "revenue": [
            r"(?:revenue|net\s+sales|total\s+revenue)[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|m|bn|billion)?",
        ],
        "ebitda": [
            r"ebitda[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|m|bn|billion)?",
        ],
        "net_income": [
            r"(?:net\s+income|net\s+profit|net\s+earnings)[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|m|bn|billion)?",
        ],
        "total_debt": [
            r"(?:total\s+debt)[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|m|bn|billion)?",
        ],
        "cash_and_equivalents": [
            r"(?:cash\s+and\s+(?:cash\s+)?equivalents)[:\s]*\$?([\d,]+\.?\d*)\s*(?:million|m|bn|billion)?",
        ],
    }

    for field_name, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = match.group(1).replace(",", "")
                start = max(0, match.start() - 50)
                end = min(len(raw_text), match.end() + 50)
                snippet = raw_text[start:end].strip()

                extractions.append({
                    "field_name": field_name,
                    "field_value": value,
                    "field_type": "number",
                    "confidence_score": 0.6,
                    "extraction_method": "regex",
                    "context_snippet": snippet,
                })
                break

    return extractions
