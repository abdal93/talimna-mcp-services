# TALIMNA Trade Matchmaking Engine
# B2B buyer-supplier matching for BRICS+ trade corridors
# Replaces: Affiliate Engine + Drop Servicing Brokerage
#
# BRICS+ Trade Corridors:
#   China↔ASEAN ($1T), India↔SEA ($120B), UAE↔SEA ($80B)
#   China↔Russia ($240B), China↔Brazil ($150B), India↔UAE ($60B)

import json
import random
import re
from datetime import datetime, timezone
from typing import Optional

# ─── BRICS+ Trade Corridors ───────────────────────────────────────────

TRADE_CORRIDORS = {
    "china_asean": {
        "name": "China ↔ ASEAN",
        "volume_usd_b": 1000,
        "growth_pct": 12.5,
        "key_industries": ["electronics", "machinery", "textiles", "chemicals",
                           "agriculture", "automotive", "consumer_goods"],
        "top_routes": ["Shanghai → Singapore", "Shenzhen → Jakarta",
                       "Guangzhou → Bangkok", "Ningbo → Ho Chi Minh City",
                       "Qingdao → Manila"],
        "ndb_alignment": "Transport Infrastructure priority",
    },
    "india_sea": {
        "name": "India ↔ Southeast Asia",
        "volume_usd_b": 120,
        "growth_pct": 15.3,
        "key_industries": ["pharmaceuticals", "textiles", "software",
                           "agriculture", "automotive_parts", "gems_jewelry"],
        "top_routes": ["Mumbai → Singapore", "Chennai → Kuala Lumpur",
                       "Delhi → Bangkok", "Kolkata → Jakarta"],
        "ndb_alignment": "Digital Infrastructure + Social Infrastructure",
    },
    "uae_sea": {
        "name": "UAE ↔ Southeast Asia",
        "volume_usd_b": 80,
        "growth_pct": 18.2,
        "key_industries": ["logistics", "re_exports", "halal_food",
                           "petrochemicals", "gold_jewelry", "tech_hardware"],
        "top_routes": ["Dubai → Singapore", "Abu Dhabi → Kuala Lumpur",
                       "Dubai → Jakarta", "Sharjah → Bangkok"],
        "ndb_alignment": "Ports + Logistics infrastructure",
    },
    "china_russia": {
        "name": "China ↔ Russia",
        "volume_usd_b": 240,
        "growth_pct": 34.0,
        "key_industries": ["energy", "agriculture", "machinery",
                           "electronics", "timber", "chemicals"],
        "top_routes": ["Manzhouli → Chita", "Suzhou → Moscow",
                       "Harbin → Vladivostok", "Chengdu → Novosibirsk"],
        "ndb_alignment": "Energy + Transport Infrastructure",
    },
    "china_brazil": {
        "name": "China ↔ Brazil",
        "volume_usd_b": 150,
        "growth_pct": 8.1,
        "key_industries": ["agriculture", "iron_ore", "oil", "soybeans",
                           "beef", "machinery", "chemicals"],
        "top_routes": ["Shanghai → Santos", "Tianjin → Rio de Janeiro",
                       "Shenzhen → Sao Paulo", "Ningbo → Paranagua"],
        "ndb_alignment": "Agriculture + Clean Energy",
    },
    "india_uae": {
        "name": "India ↔ UAE",
        "volume_usd_b": 60,
        "growth_pct": 22.0,
        "key_industries": ["petroleum", "gems_jewelry", "pharmaceuticals",
                           "textiles", "food_grain", "engineering_goods"],
        "top_routes": ["Mumbai → Dubai", "Delhi → Abu Dhabi",
                       "Chennai → Sharjah", "Kochi → Dubai"],
        "ndb_alignment": "Infrastructure + Trade Finance",
    },
    "russia_india": {
        "name": "Russia ↔ India",
        "volume_usd_b": 50,
        "growth_pct": 45.0,
        "key_industries": ["energy", "defense", "diamonds", "fertilizers",
                           "pharmaceuticals", "tea", "electronics"],
        "top_routes": ["Moscow → Mumbai", "Novorossiysk → Chennai",
                       "Vladivostok → Kolkata"],
        "ndb_alignment": "Energy Security + Strategic Partnership",
    },
    "brazil_indonesia": {
        "name": "Brazil ↔ Indonesia",
        "volume_usd_b": 15,
        "growth_pct": 25.0,
        "key_industries": ["agriculture", "beef", "sugar", "coffee",
                           "palm_oil", "coal", "pulp_paper"],
        "top_routes": ["Santos → Jakarta", "Rio de Janeiro → Surabaya",
                       "Paranagua → Medan"],
        "ndb_alignment": "South-South cooperation, Agriculture",
    },
}


# ─── BRICS+ Major Trade Hubs ──────────────────────────────────────────

TRADE_HUBS = {
    "singapore": {"country": "Singapore", "type": "hub_port", "lat": 1.3521, "lng": 103.8198,
                  "industries": ["electronics", "chemicals", "pharma", "logistics", "finance"]},
    "dubai": {"country": "UAE", "type": "re_export_hub", "lat": 25.2048, "lng": 55.2708,
              "industries": ["re_exports", "gold", "logistics", "halal_food", "electronics"]},
    "shanghai": {"country": "China", "type": "mega_port", "lat": 31.2304, "lng": 121.4737,
                 "industries": ["electronics", "machinery", "automotive", "steel", "chemicals"]},
    "shenzhen": {"country": "China", "type": "manufacturing_hub", "lat": 22.5431, "lng": 114.0579,
                 "industries": ["electronics", "telecom", "ai_hardware", "consumer_goods"]},
    "mumbai": {"country": "India", "type": "mega_port", "lat": 19.0760, "lng": 72.8777,
               "industries": ["textiles", "pharma", "gems_jewelry", "petrochemicals"]},
    "jakarta": {"country": "Indonesia", "type": "mega_port", "lat": -6.2088, "lng": 106.8456,
                "industries": ["palm_oil", "textiles", "food_processing", "electronics"]},
    "kuala_lumpur": {"country": "Malaysia", "type": "hub_port", "lat": 3.1390, "lng": 101.6869,
                     "industries": ["electronics", "palm_oil", "halal_food", "petrochemicals"]},
    "bangkok": {"country": "Thailand", "type": "hub_port", "lat": 13.7563, "lng": 100.5018,
                "industries": ["automotive", "electronics", "food_processing", "tourism_goods"]},
    "ho_chi_minh": {"country": "Vietnam", "type": "manufacturing_hub", "lat": 10.8231, "lng": 106.6297,
                    "industries": ["textiles", "electronics", "footwear", "agriculture"]},
    "manila": {"country": "Philippines", "type": "hub_port", "lat": 14.5995, "lng": 120.9842,
               "industries": ["electronics", "bpo", "agriculture", "food_processing"]},
    "moscow": {"country": "Russia", "type": "inland_hub", "lat": 55.7558, "lng": 37.6173,
               "industries": ["energy", "machinery", "chemicals", "it_services"]},
    "sao_paulo": {"country": "Brazil", "type": "inland_hub", "lat": -23.5505, "lng": -46.6333,
                  "industries": ["agriculture", "automotive", "chemicals", "food_processing"]},
    "rio_de_janeiro": {"country": "Brazil", "type": "mega_port", "lat": -22.9068, "lng": -43.1729,
                       "industries": ["oil_gas", "mining", "steel", "shipping"]},
    "cape_town": {"country": "South Africa", "type": "hub_port", "lat": -33.9249, "lng": 18.4241,
                  "industries": ["mining", "agriculture", "wine", "chemicals"]},
    "riyadh": {"country": "Saudi Arabia", "type": "inland_hub", "lat": 24.7136, "lng": 46.6753,
               "industries": ["energy", "petrochemicals", "construction", "logistics"]},
    "doha": {"country": "Qatar", "type": "hub_port", "lat": 25.2854, "lng": 51.5310,
             "industries": ["energy", "petrochemicals", "finance", "logistics"]},
    "istanbul": {"country": "Turkey", "type": "hub_port", "lat": 41.0082, "lng": 28.9784,
                 "industries": ["textiles", "automotive", "electronics", "logistics"]},
    "cairo": {"country": "Egypt", "type": "hub_port", "lat": 30.0444, "lng": 31.2357,
              "industries": ["textiles", "agriculture", "chemicals", "logistics"]},
    "addis_ababa": {"country": "Ethiopia", "type": "inland_hub", "lat": 9.0320, "lng": 38.7469,
                    "industries": ["agriculture", "textiles", "leather", "coffee"]},
    "tehran": {"country": "Iran", "type": "inland_hub", "lat": 35.6892, "lng": 51.3890,
               "industries": ["energy", "petrochemicals", "carpets", "agriculture"]},
}


# ─── Trade Leads Database ─────────────────────────────────────────────

# Pre-populated with realistic BRICS+ trade leads
# In production, these would be scraped from trade directories
TRADE_LEADS = [
    # Electronics - China selling to ASEAN
    {"id": "lead-001", "type": "buyer", "industry": "electronics",
     "product": "Smartphone components", "country": "Thailand",
     "city": "Bangkok", "company": "Siam Electronics Assembly",
     "volume_min_usd": 50000, "volume_max_usd": 500000,
     "cert_required": "ISO 9001", "payment_terms": "LC at sight",
     "posted": "2026-06-25", "status": "active",
     "corridor": "china_asean", "description": "Need PCB boards and display modules for smartphone assembly"},
    {"id": "lead-002", "type": "buyer", "industry": "electronics",
     "product": "Consumer electronics", "country": "Indonesia",
     "city": "Jakarta", "company": "PT Tech Nusantara",
     "volume_min_usd": 100000, "volume_max_usd": 2000000,
     "cert_required": "SNI", "payment_terms": "TT 30 days",
     "posted": "2026-06-24", "status": "active",
     "corridor": "china_asean", "description": "Distributor seeking smartphones, tablets, wearables"},
    {"id": "lead-003", "type": "supplier", "industry": "electronics",
     "product": "Semiconductors", "country": "China",
     "city": "Shenzhen", "company": "Huawei Supply Chain Ltd",
     "volume_min_usd": 20000, "volume_max_usd": 1000000,
     "cert_required": "ISO 9001, RoHS", "payment_terms": "LC or TT",
     "posted": "2026-06-23", "status": "active",
     "corridor": "china_asean", "description": "RFID chips, IoT modules, display drivers for SEA market"},
    {"id": "lead-004", "type": "supplier", "industry": "electronics",
     "product": "Telecom equipment", "country": "China",
     "city": "Shenzhen", "company": "ZTE International Trading",
     "volume_min_usd": 100000, "volume_max_usd": 5000000,
     "cert_required": "ISO, CE, FCC", "payment_terms": "LC",
     "posted": "2026-06-22", "status": "active",
     "corridor": "china_asean", "description": "5G equipment, fiber optic cable, routers for SEA deployment"},

    # Halal Food - Indonesia/Malaysia selling to UAE
    {"id": "lead-005", "type": "buyer", "industry": "halal_food",
     "product": "Processed halal food", "country": "UAE",
     "city": "Dubai", "company": "Al Ghurair Food Trading",
     "volume_min_usd": 100000, "volume_max_usd": 1000000,
     "cert_required": "MUI/JAKIM halal cert", "payment_terms": "LC 60 days",
     "posted": "2026-06-26", "status": "active",
     "corridor": "uae_sea", "description": "Seeking halal-certified packaged foods for Dubai supermarts"},
    {"id": "lead-006", "type": "supplier", "industry": "halal_food",
     "product": "Frozen halal chicken", "country": "Indonesia",
     "city": "Jakarta", "company": "PT Halal Food Jakarta",
     "volume_min_usd": 50000, "volume_max_usd": 500000,
     "cert_required": "MUI halal, HACCP", "payment_terms": "LC at sight",
     "posted": "2026-06-25", "status": "active",
     "corridor": "uae_sea", "description": "20MT container loads of frozen halal chicken - MUI certified"},
    {"id": "lead-007", "type": "supplier", "industry": "halal_food",
     "product": "Halal beverages", "country": "Malaysia",
     "city": "Kuala Lumpur", "company": "Halal Beverages Sdn Bhd",
     "volume_min_usd": 30000, "volume_max_usd": 300000,
     "cert_required": "JAKIM halal", "payment_terms": "TT 30 days",
     "posted": "2026-06-24", "status": "active",
     "corridor": "uae_sea", "description": "Halal energy drinks and herbal teas - JAKIM certified since 2021"},

    # Pharmaceuticals - India selling to SEA and Africa
    {"id": "lead-008", "type": "buyer", "industry": "pharmaceuticals",
     "product": "Generic medicines", "country": "South Africa",
     "city": "Cape Town", "company": "MediSupply Africa",
     "volume_min_usd": 200000, "volume_max_usd": 2000000,
     "cert_required": "WHO GMP, SAHPRA", "payment_terms": "LC 90 days",
     "posted": "2026-06-24", "status": "active",
     "corridor": "russia_india",
     "description": "Government tender for generic antibiotics and antivirals"},
    {"id": "lead-009", "type": "supplier", "industry": "pharmaceuticals",
     "product": "Generic pharma", "country": "India",
     "city": "Mumbai", "company": "Sun Pharma Exports",
     "volume_min_usd": 50000, "volume_max_usd": 5000000,
     "cert_required": "WHO GMP, USFDA", "payment_terms": "LC or TT",
     "posted": "2026-06-23", "status": "active",
     "corridor": "india_sea", "description": "Antibiotics, antivirals, cardiovascular drugs for SEA and Africa"},

    # Agriculture - Brazil to China
    {"id": "lead-010", "type": "buyer", "industry": "agriculture",
     "product": "Soybeans", "country": "China",
     "city": "Shanghai", "company": "COFCO International",
     "volume_min_usd": 1000000, "volume_max_usd": 50000000,
     "cert_required": "Non-GMO cert", "payment_terms": "LC at sight",
     "posted": "2026-06-22", "status": "active",
     "corridor": "china_brazil", "description": "Bulk soybean imports for crushing and feed production"},
    {"id": "lead-011", "type": "supplier", "industry": "agriculture",
     "product": "Beef", "country": "Brazil",
     "city": "Sao Paulo", "company": "JBS Trading SA",
     "volume_min_usd": 500000, "volume_max_usd": 10000000,
     "cert_required": "Halal, SIF, Chinese import license",
     "payment_terms": "LC 30 days", "posted": "2026-06-21", "status": "active",
     "corridor": "china_brazil",
     "description": "Frozen beef for China market - 30+ containers available monthly"},

    # Textiles - Vietnam to India
    {"id": "lead-012", "type": "buyer", "industry": "textiles",
     "product": "Cotton yarn", "country": "India",
     "city": "Mumbai", "company": "Reliance Textiles Ltd",
     "volume_min_usd": 100000, "volume_max_usd": 1000000,
     "cert_required": "OEKO-TEX, BCI", "payment_terms": "LC 60 days",
     "posted": "2026-06-26", "status": "active",
     "corridor": "india_sea", "description": "Need premium cotton yarn for textile manufacturing"},
    {"id": "lead-013", "type": "supplier", "industry": "textiles",
     "product": "Cotton fabrics", "country": "Vietnam",
     "city": "Ho Chi Minh City", "company": "Vinatex Export",
     "volume_min_usd": 50000, "volume_max_usd": 500000,
     "cert_required": "OEKO-TEX, GOTS", "payment_terms": "TT 30 days",
     "posted": "2026-06-25", "status": "active",
     "corridor": "india_sea", "description": "Organic cotton fabrics for Indian garment exporters"},

    # Energy - Russia to India
    {"id": "lead-014", "type": "buyer", "industry": "energy",
     "product": "Crude oil", "country": "India",
     "city": "Mumbai", "company": "Indian Oil Corporation",
     "volume_min_usd": 10000000, "volume_max_usd": 100000000,
     "cert_required": "API gravity specs, sulfur content", "payment_terms": "LC",
     "posted": "2026-06-20", "status": "active",
     "corridor": "russia_india", "description": "Monthly crude oil offtake agreement - Urals grade"},
    {"id": "lead-015", "type": "supplier", "industry": "energy",
     "product": "Crude oil", "country": "Russia",
     "city": "Moscow", "company": "Rosneft Trading",
     "volume_min_usd": 5000000, "volume_max_usd": 200000000,
     "cert_required": "Quality specs per contract", "payment_terms": "LC, yuan/ruble",
     "posted": "2026-06-19", "status": "active",
     "corridor": "russia_india", "description": "Urals crude for Indian refineries - yuan settlement available"},

    # Logistics services
    {"id": "lead-016", "type": "buyer", "industry": "logistics",
     "product": "Container shipping", "country": "Indonesia",
     "city": "Surabaya", "company": "PT Indo Logistics Solutions",
     "volume_min_usd": 20000, "volume_max_usd": 200000,
     "cert_required": "N/A", "payment_terms": "TT 14 days",
     "posted": "2026-06-26", "status": "active",
     "corridor": "china_asean",
     "description": "Need 20ft reefer containers Jakarta→Dubai route, weekly"},
    {"id": "lead-017", "type": "supplier", "industry": "logistics",
     "product": "Warehousing + distribution", "country": "UAE",
     "city": "Dubai", "company": "DP World Logistics",
     "volume_min_usd": 50000, "volume_max_usd": 500000,
     "cert_required": "ISO 28000 supply chain security", "payment_terms": "Monthly",
     "posted": "2026-06-25", "status": "active",
     "corridor": "uae_sea", "description": "Jebel Ali warehousing + last-mile across UAE for SEA exporters"},
]


# ─── Core Functions ────────────────────────────────────────────────────

def find_buyers(
    product: str = "",
    country: str = "",
    industry: str = "",
    corridor: str = "",
    min_volume: float = 0,
    limit: int = 20,
) -> dict:
    """Find active buyers in BRICS+ markets."""
    results = []
    for lead in TRADE_LEADS:
        if lead["type"] != "buyer":
            continue
        if product and product.lower() not in lead["product"].lower():
            continue
        if country and country.lower() not in lead["country"].lower():
            continue
        if industry and industry.lower() not in lead["industry"].lower():
            continue
        if corridor and corridor != lead.get("corridor", ""):
            continue
        if min_volume and lead["volume_max_usd"] < min_volume:
            continue
        results.append(lead)
        if len(results) >= limit:
            break
    return {"type": "buyers", "count": len(results), "results": results}


def find_suppliers(
    product: str = "",
    country: str = "",
    industry: str = "",
    corridor: str = "",
    cert_required: str = "",
    limit: int = 20,
) -> dict:
    """Find verified suppliers in BRICS+ markets."""
    results = []
    for lead in TRADE_LEADS:
        if lead["type"] != "supplier":
            continue
        if product and product.lower() not in lead["product"].lower():
            continue
        if country and country.lower() not in lead["country"].lower():
            continue
        if industry and industry.lower() not in lead["industry"].lower():
            continue
        if corridor and corridor != lead.get("corridor", ""):
            continue
        if cert_required and cert_required.lower() not in lead.get("cert_required", "").lower():
            continue
        results.append(lead)
        if len(results) >= limit:
            break
    return {"type": "suppliers", "count": len(results), "results": results}


def match_score(supplier_id: str, buyer_id: str) -> dict:
    """Score compatibility between a supplier and buyer."""
    supplier = next((l for l in TRADE_LEADS if l["id"] == supplier_id), None)
    buyer = next((l for l in TRADE_LEADS if l["id"] == buyer_id), None)

    if not supplier or not buyer:
        return {"error": "Supplier or buyer not found", "score": 0}

    score = 0
    factors = []

    # Industry match
    if supplier["industry"] == buyer["industry"]:
        score += 30
        factors.append({"factor": "industry_match", "weight": 30, "matched": supplier["industry"]})
    else:
        factors.append({"factor": "industry_match", "weight": 0, "note": "Different industries"})

    # Product overlap
    s_words = set(supplier["product"].lower().split())
    b_words = set(buyer["product"].lower().split())
    overlap = s_words & b_words
    if overlap:
        overlap_score = min(len(overlap) * 10, 25)
        score += overlap_score
        factors.append({"factor": "product_overlap", "weight": overlap_score,
                        "matched_terms": list(overlap)})

    # Volume compatibility
    if buyer["volume_min_usd"] <= supplier["volume_max_usd"]:
        score += 20
        factors.append({"factor": "volume_compatible", "weight": 20})
    elif buyer["volume_min_usd"] <= supplier["volume_max_usd"] * 1.5:
        score += 10
        factors.append({"factor": "volume_partial", "weight": 10})

    # Corridor match
    if supplier.get("corridor") == buyer.get("corridor"):
        score += 15
        factors.append({"factor": "corridor_match", "weight": 15,
                        "corridor": TRADE_CORRIDORS.get(supplier["corridor"], {}).get("name", supplier["corridor"])})

    # Certification overlap
    s_certs = set(re.findall(r'\w+', supplier.get("cert_required", "").lower()))
    b_certs = set(re.findall(r'\w+', buyer.get("cert_required", "").lower()))
    cert_overlap = s_certs & b_certs
    if cert_overlap:
        cert_score = min(len(cert_overlap) * 5, 10)
        score += cert_score
        factors.append({"factor": "certification_overlap", "weight": cert_score,
                        "shared_certs": list(cert_overlap)})

    grade = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"

    return {
        "supplier_id": supplier_id,
        "buyer_id": buyer_id,
        "score": score,
        "grade": grade,
        "recommendation": "Highly recommended" if score >= 70 else (
            "Recommended" if score >= 50 else "Possible match" if score >= 30 else "Weak match"),
        "factors": factors,
        "supplier": supplier["company"],
        "buyer": buyer["company"],
        "supplier_product": supplier["product"],
        "buyer_product": buyer["product"],
    }


def verify_trade_entity(company_name: str, jurisdiction: str = "") -> dict:
    """Verify a trade entity's basic credentials."""
    # In production, this would check against trade registries
    # For MVP, return structured info based on our database
    for lead in TRADE_LEADS:
        if company_name.lower() in lead["company"].lower():
            return {
                "found": True,
                "company": lead["company"],
                "country": lead["country"],
                "city": lead["city"],
                "industry": lead["industry"],
                "product": lead["product"],
                "certifications": lead.get("cert_required", "N/A"),
                "verification_status": "verified_in_directory",
                "note": "Found in BRICS+ trade directory",
            }

    return {
        "found": False,
        "company": company_name,
        "jurisdiction": jurisdiction,
        "verification_status": "not_found",
        "note": "Not found in our directory. Recommend independent verification via local chamber of commerce.",
    }


def initiate_negotiation(match_id: str = "auto", supplier_id: str = "", buyer_id: str = "",
                         terms_template: str = "standard") -> dict:
    """Create a structured negotiation channel between matched parties."""
    if match_id == "auto":
        match_id = f"neg-{random.randint(10000, 99999)}"

    supplier = next((l for l in TRADE_LEADS if l["id"] == supplier_id), None)
    buyer = next((l for l in TRADE_LEADS if l["id"] == buyer_id), None)

    if not supplier or not buyer:
        return {"error": "Supplier or buyer not found"}

    terms = {
        "standard": {
            "payment": ["LC at sight", "LC 30 days", "TT 50% upfront"],
            "delivery": ["FOB", "CIF", "DDP"],
            "inspection": ["SGS", "Bureau Veritas", "Buyer's representative"],
            "arbitration": ["Singapore International Arbitration Centre",
                           "Dubai International Arbitration Centre",
                           "ICC Paris"],
        }
    }.get(terms_template, {"payment": ["LC"], "delivery": ["FOB"], "arbitration": ["SIAC"]})

    created_at = datetime.now(timezone.utc).isoformat()

    return {
        "match_id": match_id,
        "status": "initiated",
        "supplier": supplier["company"],
        "buyer": buyer["company"],
        "product": supplier["product"],
        "estimated_volume": f"${buyer['volume_min_usd']:,} - ${min(buyer['volume_max_usd'], supplier['volume_max_usd']):,}",
        "proposed_terms": terms,
        "corridor": TRADE_CORRIDORS.get(supplier.get("corridor", ""), {}).get("name", "Unknown"),
        "halal_screening": "Required" if supplier["industry"] in ("halal_food", "pharmaceuticals") else "Standard",
        "created_at": created_at,
        "next_steps": [
            "1. Supplier sends product specification sheet + certification",
            "2. Buyer reviews samples (third-party lab if needed)",
            "3. Agree on price, payment terms, delivery schedule",
            "4. Draft and sign sales contract",
            "5. Open LC or arrange payment",
            "6. Schedule inspection + shipping",
        ],
    }


def list_trade_corridors() -> dict:
    """List all BRICS+ trade corridors with data."""
    corridors = []
    for c_id, data in TRADE_CORRIDORS.items():
        corridors.append({
            "id": c_id,
            **data,
            "top_industries": data["key_industries"][:5],
        })
    return {"count": len(corridors), "corridors": corridors}


def get_trade_leads(industry: str = "", region: str = "",
                    lead_type: str = "", limit: int = 10) -> dict:
    """Get trade leads filtered by industry, region, or type."""
    results = []
    for lead in TRADE_LEADS:
        if lead_type and lead["type"] != lead_type:
            continue
        if industry and industry.lower() not in lead["industry"].lower():
            continue
        if region and region.lower() not in lead["country"].lower():
            continue
        results.append(lead)
        if len(results) >= limit:
            break
    return {"count": len(results), "type": lead_type or "all", "results": results}


def list_hubs(industry: str = "", country: str = "") -> dict:
    """List BRICS+ trade hubs."""
    results = []
    for h_id, hub in TRADE_HUBS.items():
        if industry and industry.lower() not in " ".join(hub["industries"]).lower():
            continue
        if country and country.lower() not in hub["country"].lower():
            continue
        results.append({"id": h_id, **hub})
    return {"count": len(results), "hubs": results}
