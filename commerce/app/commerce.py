# TALIMNA Digital Commerce MCP — replaces Digital Products & POD
# API-based delivery of trade tools, templates, and digital products

PRODUCTS = [
    {"id": "dp-001", "name": "30-Day Quran Reflection Journal",
     "type": "PDF Journal", "price_usd": 19, "format": "PDF (36 pages)",
     "category": "islamic_content"},
    {"id": "dp-002", "name": "BRICS+ Trade Contract Templates Bundle",
     "type": "Template Bundle", "price_usd": 49, "format": "DOCX + PDF (8 templates)",
     "category": "trade_tools"},
    {"id": "dp-003", "name": "Halal Export Readiness Checklist",
     "type": "Checklist", "price_usd": 15, "format": "PDF + XLSX",
     "category": "trade_compliance"},
    {"id": "dp-004", "name": "MAS Agent Configuration Pack - 60 prompts",
     "type": "AI Prompt Bundle", "price_usd": 39, "format": "JSON (60 prompts)",
     "category": "ai_tools"},
    {"id": "dp-005", "name": "SEA Customs Declaration Field Guide",
     "type": "Reference PDF", "price_usd": 25, "format": "PDF (120 pages)",
     "category": "trade_compliance"},
    {"id": "dp-006", "name": "Zakat Calculator + Business Tracker Spreadsheet",
     "type": "Spreadsheet", "price_usd": 12, "format": "XLSX with macros",
     "category": "islamic_finance"},
    {"id": "dp-007", "name": "Master Supply Agreement (Common Law + Sharia)",
     "type": "Legal Template", "price_usd": 79, "format": "DOCX (dual jurisdiction)",
     "category": "trade_tools"},
    {"id": "dp-008", "name": "NDB Project Proposal Narrative Template",
     "type": "Template", "price_usd": 59, "format": "DOCX + PDF",
     "category": "project_finance"},
]


DELIVERY_METHODS = {
    "PDF": "Immediate download link via email",
    "DOCX": "Immediate download link",
    "JSON": "API response + download link",
    "XLSX": "Immediate download link",
}


def list_products(category: str = "") -> dict:
    """List digital products available for purchase."""
    results = []
    for p in PRODUCTS:
        if category and category != p["category"]:
            continue
        results.append(p)
    return {"count": len(results), "products": results}


def process_order(product_id: str, buyer_email: str = "", payment_method: str = "stripe") -> dict:
    """Process a digital product order."""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return {"error": f"Product not found: {product_id}",
                "available": [p["id"] for p in PRODUCTS]}

    delivery_info = DELIVERY_METHODS.get(product["format"].split()[0], "Email delivery")
    return {
        "order": {
            "product": product["name"],
            "price_usd": product["price_usd"],
            "format": product["format"],
        },
        "payment": {
            "method": payment_method,
            "status": "pending",
            "payment_link": f"https://talimna.com/#digital?product={product_id}",
        },
        "delivery": delivery_info,
        "halal_status": "compliant - Bai' (sale), fixed price, immediate delivery, no gharar"
            if product["category"] in ("islamic_content", "islamic_finance", "trade_tools", "trade_compliance")
            else "compliant",
    }


def manage_license(product_id: str, action: str = "info", licensee: str = "") -> dict:
    """Manage product licenses for commercial use."""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return {"error": f"Product not found: {product_id}"}
    return {
        "product": product["name"],
        "license_action": action,
        "standard_terms": "Personal use. Redistribution prohibited.",
        "commercial_license": f"Available for ${product['price_usd'] * 5:.0f} (unlimited distribution)",
    }