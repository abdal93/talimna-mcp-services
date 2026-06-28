# TALIMNA Trade Intelligence Engine
# BRICS+ trade corridor data, market intel, supplier verification
# Replaces: Data Intelligence Service

# ─── BRICS+ Trade Corridor Data ───────────────────────────────────────

TRADE_DATA = {
    "china_asean_2026_q1": {
        "corridor": "China ↔ ASEAN",
        "period": "Q1 2026 (estimated)",
        "volume_billion_usd": 285,
        "growth_yoy_pct": 13.2,
        "top_commodities": [
            {"name": "Electronics & machinery", "share_pct": 42, "value_b": 119.7},
            {"name": "Textiles & apparel", "share_pct": 15, "value_b": 42.8},
            {"name": "Chemicals & plastics", "share_pct": 11, "value_b": 31.3},
            {"name": "Agricultural goods", "share_pct": 9, "value_b": 25.6},
            {"name": "Base metals", "share_pct": 7, "value_b": 19.9},
        ],
        "top_ports": ["Shanghai → Singapore", "Shenzhen → Jakarta",
                      "Guangzhou → Bangkok", "Ningbo → Ho Chi Minh City",
                      "Qingdao → Manila"],
        "settlement_currency": {"CNY": 42, "USD": 48, "SGD": 5, "Other": 5},
        "ndb_projects_active": 12,
    },
    "india_sea_2026_q1": {
        "corridor": "India ↔ Southeast Asia",
        "period": "Q1 2026 (estimated)",
        "volume_billion_usd": 33,
        "growth_yoy_pct": 16.8,
        "top_commodities": [
            {"name": "Pharmaceuticals", "share_pct": 28, "value_b": 9.2},
            {"name": "Textiles & garments", "share_pct": 22, "value_b": 7.3},
            {"name": "Gems & jewelry", "share_pct": 15, "value_b": 4.9},
            {"name": "Software services", "share_pct": 12, "value_b": 3.9},
            {"name": "Automotive parts", "share_pct": 8, "value_b": 2.6},
        ],
        "settlement_currency": {"INR": 18, "USD": 62, "SGD": 12, "Other": 8},
    },
    "uae_sea_2026_q1": {
        "corridor": "UAE ↔ Southeast Asia",
        "period": "Q1 2026 (estimated)",
        "volume_billion_usd": 22,
        "growth_yoy_pct": 19.5,
        "top_commodities": [
            {"name": "Re-exports (electronics)", "share_pct": 35, "value_b": 7.7},
            {"name": "Petrochemicals", "share_pct": 25, "value_b": 5.5},
            {"name": "Gold & jewelry", "share_pct": 15, "value_b": 3.3},
            {"name": "Halal food & beverages", "share_pct": 10, "value_b": 2.2},
            {"name": "Logistics services", "share_pct": 8, "value_b": 1.8},
        ],
        "settlement_currency": {"AED": 15, "USD": 65, "MYR": 8, "IDR": 5, "Other": 7},
    },
    "china_russia_2026_q1": {
        "corridor": "China ↔ Russia",
        "period": "Q1 2026 (estimated)",
        "volume_billion_usd": 68,
        "growth_yoy_pct": 28.4,
        "top_commodities": [
            {"name": "Energy (oil, gas, coal)", "share_pct": 55, "value_b": 37.4},
            {"name": "Machinery & equipment", "share_pct": 18, "value_b": 12.2},
            {"name": "Electronics", "share_pct": 10, "value_b": 6.8},
            {"name": "Agricultural products", "share_pct": 8, "value_b": 5.4},
            {"name": "Chemicals", "share_pct": 5, "value_b": 3.4},
        ],
        "settlement_currency": {"CNY": 52, "RUB": 38, "USD": 8, "Other": 2},
    },
    "russia_india_2026_q1": {
        "corridor": "Russia ↔ India",
        "period": "Q1 2026 (estimated)",
        "volume_billion_usd": 15,
        "growth_yoy_pct": 42.0,
        "top_commodities": [
            {"name": "Crude oil & petroleum", "share_pct": 60, "value_b": 9.0},
            {"name": "Fertilizers", "share_pct": 15, "value_b": 2.3},
            {"name": "Diamonds & precious stones", "share_pct": 10, "value_b": 1.5},
            {"name": "Pharmaceuticals (India→Russia)", "share_pct": 6, "value_b": 0.9},
            {"name": "Tea & coffee (India→Russia)", "share_pct": 4, "value_b": 0.6},
        ],
        "settlement_currency": {"RUB": 35, "INR": 22, "CNY": 20, "AED": 15, "USD": 8},
    },
    "china_brazil_2026_q1": {
        "corridor": "China ↔ Brazil",
        "period": "Q1 2026 (estimated)",
        "volume_billion_usd": 42,
        "growth_yoy_pct": 9.2,
        "top_commodities": [
            {"name": "Soybeans & grains", "share_pct": 32, "value_b": 13.4},
            {"name": "Iron ore & minerals", "share_pct": 28, "value_b": 11.8},
            {"name": "Crude petroleum", "share_pct": 15, "value_b": 6.3},
            {"name": "Beef & poultry", "share_pct": 8, "value_b": 3.4},
            {"name": "Machinery (China→Brazil)", "share_pct": 7, "value_b": 2.9},
        ],
        "settlement_currency": {"CNY": 35, "BRL": 12, "USD": 45, "Other": 8},
    },
}

# ─── Available Datasets ───────────────────────────────────────────────

DATASETS = [
    {
        "id": "ds-001", "name": "SEA Trade Volume Report Q1 2026",
        "description": "Monthly trade volumes across 5 SEA corridors with commodity breakdown",
        "price_usd": 500, "format": "CSV + JSON",
        "coverage": "Indonesia, Malaysia, Thailand, Vietnam, Philippines",
        "update_frequency": "Monthly",
    },
    {
        "id": "ds-002", "name": "BRICS+ Halal Supply Chain Directory",
        "description": "Verified halal-certified suppliers and buyers across 22 countries",
        "price_usd": 750, "format": "JSON + PDF",
        "coverage": "All BRICS+ members + partner states",
        "update_frequency": "Quarterly",
    },
    {
        "id": "ds-003", "name": "SEA Logistics Rate Benchmark",
        "description": "Real-time freight rates for 50+ SEA shipping routes (FCL/LCL/Reefer)",
        "price_usd": 300, "format": "JSON API",
        "coverage": "All major SEA ports",
        "update_frequency": "Weekly",
    },
    {
        "id": "ds-004", "name": "China-ASEAN Tariff Database 2026",
        "description": "HS code-level tariff rates under RCEP + bilateral FTAs",
        "price_usd": 1000, "format": "CSV (30K+ rows)",
        "coverage": "China, Indonesia, Malaysia, Thailand, Vietnam, Philippines",
        "update_frequency": "Annual",
    },
    {
        "id": "ds-005", "name": "UAE Re-Export Market Intel",
        "description": "Top 50 re-export commodities through Dubai with buyer profiles",
        "price_usd": 600, "format": "PDF + XLSX",
        "coverage": "Dubai, Abu Dhabi, Sharjah",
        "update_frequency": "Quarterly",
    },
    {
        "id": "ds-006", "name": "NDB Infrastructure Project Pipeline 2026",
        "description": "Active NDB-funded projects across BRICS+ with tender deadlines",
        "price_usd": 1500, "format": "JSON + PDF",
        "coverage": "All NDB member countries",
        "update_frequency": "Monthly (updated 2 days ago)",
    },
    {
        "id": "ds-007", "name": "BRICS+ SME Export Readiness Index",
        "description": "Country-by-country assessment of SME export capacity, digital readiness, and halal compliance",
        "price_usd": 400, "format": "PDF",
        "coverage": "11 BRICS+ nations",
        "update_frequency": "Annual",
    },
]


def query_trade_volume(corridor_id: str = "", period: str = "latest") -> dict:
    """Get trade volume data for a BRICS+ corridor."""
    if corridor_id:
        data = TRADE_DATA.get(corridor_id)
        if data:
            return {"corridor": corridor_id, "data": data, "status": "available"}
        return {"error": f"Corridor not found: {corridor_id}",
                "available": list(TRADE_DATA.keys())}

    # Return all corridors summary
    summary = []
    for cid, data in TRADE_DATA.items():
        summary.append({
            "corridor_id": cid,
            "corridor_name": data["corridor"],
            "volume_billion_usd": data["volume_billion_usd"],
            "growth_yoy_pct": data["growth_yoy_pct"],
            "top_commodity": data["top_commodities"][0]["name"],
        })
    return {"count": len(summary), "corridors": summary}


def get_market_intel(corridor: str = "", industry: str = "",
                     country: str = "") -> dict:
    """Get AI-synthesized market intelligence."""
    if corridor and corridor in TRADE_DATA:
        data = TRADE_DATA[corridor]
        commodities = [c for c in data["top_commodities"]
                       if not industry or industry.lower() in c["name"].lower()]

        return {
            "corridor": data["corridor"],
            "volume_billion_usd": data["volume_billion_usd"],
            "growth_pct": data["growth_yoy_pct"],
            "top_opportunities": commodities[:3],
            "currency_settlement": data["settlement_currency"],
            "key_insight": f"{data['corridor']} grew {data['growth_yoy_pct']}% YoY in Q1 2026. "
                           f"CNY settlement at {data['settlement_currency'].get('CNY', 0)}% - increasing de-dollarization.",
        }

    return {"error": "Specify a valid corridor",
            "available": list(TRADE_DATA.keys())}


def verify_supplier_background(company_name: str, jurisdiction: str = "") -> dict:
    """Background verification for trade suppliers."""
    # Check against known datasets
    known_companies = {
        "pt halal food jakarta": {
            "found": True, "country": "Indonesia", "cert": "MUI Halal, HACCP",
            "years_active": 8, "export_volume_annual_usd": "5-10M",
            "risk_level": "Low", "notes": "Verified halal exporter since 2018",
        },
        "huawei supply chain ltd": {
            "found": True, "country": "China", "cert": "ISO 9001, RoHS, CE",
            "years_active": 15, "export_volume_annual_usd": "100M+",
            "risk_level": "Low", "notes": "Major SEA electronics supplier",
        },
        "al ghurair food trading": {
            "found": True, "country": "UAE", "cert": "UAE.S GSO, HACCP",
            "years_active": 12, "export_volume_annual_usd": "20-50M",
            "risk_level": "Low", "notes": "Dubai-based halal food importer",
        },
    }

    result = known_companies.get(company_name.lower().strip())
    if result:
        return result
    return {
        "found": False,
        "company": company_name,
        "risk_level": "Unknown",
        "note": "Not in TALIMNA directory. Recommend independent verification.",
    }


def monitor_trade_flow(corridor: str = "", days: int = 7) -> dict:
    """Monitor trade corridor activity and generate alerts."""
    if not corridor or corridor not in TRADE_DATA:
        return {"error": "Specify valid corridor", "available": list(TRADE_DATA.keys())}

    data = TRADE_DATA[corridor]
    alerts = []

    # Generate intelligence alerts
    if data["growth_yoy_pct"] > 20:
        alerts.append(f"HIGH GROWTH: {data['corridor']} growing at {data['growth_yoy_pct']}% YoY")

    cny_share = data["settlement_currency"].get("CNY", 0)
    if cny_share > 30:
        alerts.append(f"CURRENCY SHIFT: CNY settlement at {cny_share}% - de-dollarization accelerating")

    top_commodity = data["top_commodities"][0]
    alerts.append(f"TOP COMMODITY: {top_commodity['name']} at ${top_commodity['value_b']}B ({top_commodity['share_pct']}% of corridor)")

    return {
        "corridor": data["corridor"],
        "volume_billion_usd": data["volume_billion_usd"],
        "period": data["period"],
        "alerts": alerts,
        "ndb_projects": data.get("ndb_projects_active", "N/A"),
    }


def list_datasets(industry: str = "", max_price: float = 0) -> dict:
    """List available trade intelligence datasets."""
    results = []
    for ds in DATASETS:
        if industry and industry.lower() not in ds["name"].lower() \
           and industry.lower() not in ds["description"].lower():
            continue
        if max_price and ds["price_usd"] > max_price:
            continue
        results.append(ds)
    return {"count": len(results), "datasets": results}


def purchase_dataset(dataset_id: str, buyer_email: str = "") -> dict:
    """Purchase a trade intelligence dataset."""
    ds = next((d for d in DATASETS if d["id"] == dataset_id), None)
    if not ds:
        return {"error": f"Dataset not found: {dataset_id}", "available": [d["id"] for d in DATASETS]}
    return {
        "dataset": ds["name"],
        "price_usd": ds["price_usd"],
        "format": ds["format"],
        "purchase_url": f"https://talimna.com/#intel?dataset={dataset_id}",
        "delivery_method": "Email link or API key",
        "payment": "Stripe (USD) / Crypto (USDT/BTC) / Bank transfer",
    }