# TALIMNA Trade Translation Engine
# Multi-backend: deep-translator (free APIs) with NLLB-200 swap path
#
# BRICS+ language map with ISO 639-1 codes
# For NLLB-200 swap: use facebook/nllb-200-distilled-600M later

from deep_translator import GoogleTranslator
import re

# ─── BRICS+ Language Map ──────────────────────────────────────────────
# Google Translate uses uppercase codes for Chinese
GOOGLE_LANG_MAP = {
    "zh-cn": "zh-CN",
    "zh-tw": "zh-TW",
}

LANGUAGES = {
    "en": "English",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "hi": "Hindi",
    "ar": "Arabic",
    "ru": "Russian",
    "pt": "Portuguese",
    "ms": "Malay",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ur": "Urdu",
    "fa": "Farsi",
    "tr": "Turkish",
    "bn": "Bengali",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "ko": "Korean",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "sw": "Swahili",
    "am": "Amharic",
    "ps": "Pashto",
    "sd": "Sindhi",
    "si": "Sinhala",
    "km": "Khmer",
    "lo": "Lao",
    "my": "Burmese",
    "mn": "Mongolian",
    "kk": "Kazakh",
    "uz": "Uzbek",
}

# Document types with field extraction hints
DOC_TYPES = {
    "bill_of_lading": ["shipper", "consignee", "vessel", "port_of_loading",
                        "port_of_discharge", "container_no", "seal_no",
                        "gross_weight", "measurement", "description_of_goods"],
    "invoice": ["seller", "buyer", "invoice_no", "date", "item_description",
                 "quantity", "unit_price", "total_amount", "currency", "terms"],
    "customs_declaration": ["declarant", "customs_office", "tariff_code",
                            "country_of_origin", "declared_value", "hs_code"],
    "cert_of_origin": ["exporter", "consignee", "country_of_origin",
                        "product_description", "cert_no", "issuing_body"],
    "contract": ["parties", "effective_date", "term", "governing_law",
                  "payment_terms", "delivery_terms", "arbitration"],
}


def translate(text: str, source: str, target: str) -> dict:
    """Translate text between BRICS+ languages using available backend."""
    if source not in LANGUAGES or target not in LANGUAGES:
        return {"error": f"Unsupported language pair: {source}→{target}",
                "supported": list(LANGUAGES.keys())}

    # Map codes for Google Translate
    google_source = GOOGLE_LANG_MAP.get(source, source)
    google_target = GOOGLE_LANG_MAP.get(target, target)
    try:
        result = GoogleTranslator(source=google_source, target=google_target).translate(text)
        return {
            "translated_text": result,
            "source_language": source,
            "target_language": target,
            "source_language_name": LANGUAGES[source],
            "target_language_name": LANGUAGES[target],
            "backend": "google_translate",
            "word_count_original": len(text.split()),
            "word_count_translated": len(result.split()),
        }
    except Exception as e:
        return {"error": str(e), "source": source, "target": target}


def detect_language(text: str) -> dict:
    """Detect language of input text."""
    try:
        detected = GoogleTranslator(source="auto", target="en").translate(text)
        # Note: deep-translator doesn't natively return detection info
        # We use a best-effort approach
        return {"text_preview": text[:100], "note": "Auto-detected by Google",
                "backend": "google_translate"}
    except Exception as e:
        return {"error": str(e)}


def batch_translate(entries: list) -> list:
    """Translate multiple text entries in one call.
    
    entries: [{"text": "...", "source": "en", "target": "ms"}, ...]
    """
    results = []
    for entry in entries:
        res = translate(
            text=entry.get("text", ""),
            source=entry.get("source", "auto"),
            target=entry.get("target", "en"),
        )
        results.append(res)
    return results


def extract_trade_terms(text: str, doc_type: str = None) -> dict:
    """Extract key trade document fields from translated text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if doc_type and doc_type in DOC_TYPES:
        expected_fields = DOC_TYPES[doc_type]
    else:
        expected_fields = []

    extracted = {
        "doc_type": doc_type,
        "line_count": len(lines),
        "word_count": len(text.split()),
        "extracted_fields": {},
    }

    # Simple field extraction: look for patterns
    for line in lines[:50]:
        for field in expected_fields:
            pattern = rf"(?i){field.replace('_', ' ')}[:\s]+(.+)"
            match = re.search(pattern, line)
            if match:
                extracted["extracted_fields"][field] = match.group(1).strip()

    return extracted


def translate_trade_doc(text: str, source: str, target: str,
                        doc_type: str = None) -> dict:
    """Full trade document translation pipeline."""
    translation = translate(text, source, target)
    if "error" in translation:
        return translation

    extracted = extract_trade_terms(text, doc_type)

    return {
        **translation,
        "doc_type": doc_type,
        "extracted_fields": extracted["extracted_fields"],
    }


def list_languages() -> dict:
    """List all supported languages."""
    return {"languages": LANGUAGES}


def list_doc_types() -> dict:
    """List supported trade document types."""
    return {"doc_types": DOC_TYPES}