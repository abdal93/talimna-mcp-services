# TALIMNA MCP Services — Pricing & Monetization
# All prices in USD. Fixed pricing (Ijara/Bai'). No riba, no gharar.

PRICING = {
    "trade_translation": {
        "port": 8001,
        "service": "Trade Translation MCP",
        "description": "Translate trade documents across 34 BRICS+ languages",
        "plans": [
            {"tier": "pay_per_word", "price": "0.10/word", "min": 10, "best_for": "Occasional translations"},
            {"tier": "per_document", "price": "$5-25/doc", "details": "Based on length (100-500 words)", "best_for": "Bills of lading, invoices"},
            {"tier": "volume_monthly", "price": "$200/mo", "words_included": 5000, "best_for": "Trading companies"},
            {"tier": "enterprise", "price": "$500/mo", "words_included": 20000, "best_for": "Logistics firms, customs brokers"},
        ],
        "payment": "Stripe / Crypto USDT / Bank transfer",
        "halal_gate": "Ijara (service lease). Transparent per-unit pricing. No gharar.",
    },
    "sharia_compliance": {
        "port": 8002,
        "service": "Sharia Compliance MCP",
        "description": "Transaction screening, zakat calculation, riba detection",
        "plans": [
            {"tier": "pay_per_screen", "price": "$0.50/screen", "min": 10, "best_for": "Occasional checks"},
            {"tier": "starter_monthly", "price": "$99/mo", "screens_included": 500, "best_for": "Small halal businesses"},
            {"tier": "business_monthly", "price": "$299/mo", "screens_included": 2500, "best_for": "Islamic finance startups"},
            {"tier": "enterprise", "price": "$999/mo", "screens_included": 10000, "best_for": "Banks, halal cert bodies"},
        ],
        "payment": "Stripe / Crypto USDT / Bank transfer",
        "halal_gate": "Ijara. Fixed monthly fee. No commission on transaction value (no riba).",
    },
    "trade_intelligence": {
        "port": 8003,
        "service": "Trade Intelligence MCP",
        "description": "BRICS+ trade data, market intel, supplier verification",
        "plans": [
            {"tier": "per_dataset", "price": "$300-$1,500/dataset", "details": "7 datasets available", "best_for": "One-time research"},
            {"tier": "data_monthly", "price": "$199/mo", "includes": "All datasets + weekly updates", "best_for": "Trading companies, analysts"},
            {"tier": "api_access", "price": "$499/mo", "includes": "Real-time API queries, unlimited", "best_for": "Platforms, integrators"},
        ],
        "payment": "Stripe / Crypto USDT / Bank transfer",
        "halal_gate": "Bai' (sale of data). Fixed price per dataset. Delivered immediately. No gharar.",
    },
    "trade_matchmaking": {
        "port": 8004,
        "service": "Trade Matchmaking MCP",
        "description": "B2B buyer-supplier matching for BRICS+ corridors",
        "plans": [
            {"tier": "per_match", "price": "$50/match", "includes": "AI-scored match + intro", "best_for": "Occasional sourcing"},
            {"tier": "starter_monthly", "price": "$99/mo", "matches_included": 10, "best_for": "Small exporters"},
            {"tier": "business_monthly", "price": "$299/mo", "matches_included": 50, "best_for": "Trading companies"},
            {"tier": "enterprise", "price": "$999/mo", "matches_included": "Unlimited", "best_for": "Import/export firms"},
        ],
        "payment": "Stripe / Crypto USDT / Bank transfer",
        "halal_gate": "Ju'ala (commission for service). Fixed fee per successful match. Disclosed upfront.",
    },
    "industrial_content": {
        "port": 8005,
        "service": "Industrial Content MCP",
        "description": "Trade docs, compliance manuals, NDB proposal templates",
        "plans": [
            {"tier": "per_document", "price": "$149-$399/doc", "details": "6 catalog items", "best_for": "One-time needs"},
            {"tier": "content_monthly", "price": "$199/mo", "includes": "5 custom documents/mo", "best_for": "Consultants, project managers"},
        ],
        "payment": "Stripe / Crypto USDT / Bank transfer",
        "halal_gate": "Bai'. Fixed price per document. No ongoing royalty. Clear scope.",
    },
    "digital_commerce": {
        "port": 8006,
        "service": "Digital Commerce MCP",
        "description": "Trade tools, templates, AI prompts, Islamic content",
        "plans": [
            {"tier": "per_product", "price": "$12-$79/product", "details": "8 products", "best_for": "Individual buyers"},
            {"tier": "commercial_license", "price": "5x product price", "includes": "Unlimited distribution rights", "best_for": "Businesses, educators"},
        ],
        "payment": "Stripe / Crypto USDT / Bank transfer",
        "halal_gate": "Bai'. Fixed price. Immediate digital delivery. No subscription trickery.",
    },
    "logistics_dispatch": {
        "port": 8000,
        "service": "Logistics Dispatch MCP",
        "description": "SEA route optimization, dispatching, tracking",
        "plans": [
            {"tier": "per_dispatch", "price": "$2/dispatch", "min": 50, "best_for": "Small logistics operators"},
            {"tier": "starter_monthly", "price": "$99/mo", "dispatches_included": 100, "best_for": "Local couriers"},
            {"tier": "business_monthly", "price": "$299/mo", "dispatches_included": 500, "best_for": "Mid-size logistics"},
            {"tier": "enterprise", "price": "$999/mo", "dispatches_included": "Unlimited", "best_for": "Freight forwarders"},
        ],
        "payment": "Stripe / Crypto USDT / Bank transfer",
        "halal_gate": "Ijara. Fixed fee per dispatch. No percentage of goods value. Transparent.",
    },
}

# Revenue projections (conservative, first 6 months)
REVENUE_PROJECTIONS = {
    "month_1": {"target": "$500-1,000", "strategy": "Per-use pricing. Focus on translation + compliance."},
    "month_2": {"target": "$1,000-2,500", "strategy": "Convert first 5 monthly subscribers."},
    "month_3": {"target": "$2,500-5,000", "strategy": "Expand to 15 subscribers + dataset sales."},
    "month_6": {"target": "$5,000-12,000", "strategy": "30+ subscribers. Enterprise accounts."},
}


def get_pricing(service: str = "") -> dict:
    """Get pricing for a specific service or all services."""
    if service:
        s = service.lower().replace(" ", "_").replace("-", "_")
        if s in PRICING:
            return PRICING[s]
        return {"error": f"Service not found: {service}",
                "available": list(PRICING.keys())}
    return {"services": PRICING, "total_services": len(PRICING)}


def get_revenue_projections(month: int = 1) -> dict:
    """Get revenue projections."""
    key = f"month_{month}"
    if key in REVENUE_PROJECTIONS:
        return {"month": month, **REVENUE_PROJECTIONS[key]}
    # Find nearest
    for m in range(month, 0, -1):
        key = f"month_{m}"
        if key in REVENUE_PROJECTIONS:
            return {"month": month, "note": "Projection for closest defined month",
                    **REVENUE_PROJECTIONS[key]}
    return {"error": "No projections available"}