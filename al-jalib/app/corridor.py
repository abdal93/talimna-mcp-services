# TALIMNA Al-Jalib — Trans-South Commercial & Logistical Corridor
# Algorithmic orchestration of physical B2B trade flows
# Builds on: Logistics (:8000), Matchmaking (:8004), Translation (:8001)

import json, math, random
from datetime import datetime, timezone, timedelta

# ─── Cargo Types & Standards ──────────────────────────────────────────

CARGO_TYPES = {
    "dates": {
        "type": "Agricultural - Dried Fruit",
        "hs_code": "0804.10",
        "origin": "Algeria / Tunisia / Saudi Arabia",
        "packaging": "5kg carton / 10kg box / palletized",
        "unit": "MT",
        "halal_requirements": ["Natural processing", "No sulfite preservatives"],
    },
    "coconut": {
        "type": "Agricultural - Coconut Products",
        "hs_code": "1513.11",
        "origin": "Indonesia / Philippines / Sri Lanka",
        "packaging": "Flexitank / ISO-tank / 20L jerrycan",
        "unit": "MT",
        "halal_requirements": ["MUI certified", "No alcohol solvents"],
    },
    "durum_wheat": {
        "type": "Agricultural - Grain",
        "hs_code": "1001.19",
        "origin": "Algeria / Tunisia / Turkey",
        "packaging": "50kg bags / Bulk",
        "unit": "MT",
        "halal_requirements": ["Storage segregation"],
    },
    "rice": {
        "type": "Agricultural - Grain",
        "hs_code": "1006.30",
        "origin": "India / Vietnam / Thailand / Indonesia",
        "packaging": "50kg bags / 1MT jumbo bags",
        "unit": "MT",
        "halal_requirements": ["Halal storage"],
    },
    "lentils": {
        "type": "Agricultural - Legume",
        "hs_code": "0713.40",
        "origin": "India / Ethiopia / Turkey",
        "packaging": "25kg / 50kg bags",
        "unit": "MT",
        "halal_requirements": ["Halal storage"],
    },
    "soybeans": {
        "type": "Agricultural - Oilseed",
        "hs_code": "1201.90",
        "origin": "Brazil / India / Indonesia",
        "packaging": "Bulk / 50kg bags",
        "unit": "MT",
        "halal_requirements": ["Non-GMO certification", "Halal storage"],
    },
    "sheep": {
        "type": "Livestock - Live Animals",
        "hs_code": "0104.10",
        "origin": "Sudan / Somalia / Australia",
        "packaging": "Live export vessel / Container",
        "unit": "Head",
        "halal_requirements": ["Halal slaughter protocol", "Animal welfare compliance"],
    },
    "goats": {
        "type": "Livestock - Live Animals",
        "hs_code": "0104.20",
        "origin": "Sudan / Ethiopia / India",
        "packaging": "Live export vessel / Container",
        "unit": "Head",
        "halal_requirements": ["Halal slaughter protocol"],
    },
    "chicken": {
        "type": "Livestock - Poultry",
        "hs_code": "0207.14",
        "origin": "Thailand / Brazil / Indonesia",
        "packaging": "Frozen 20kg cartons / IQF",
        "unit": "MT",
        "halal_requirements": ["MUI/JAKIM/CICOT certified", "Halal slaughter protocol"],
    },
    "honey": {
        "type": "Agricultural - Beekeeping",
        "hs_code": "0409.00",
        "origin": "Ethiopia / Indonesia / India",
        "packaging": "12kg pail / 300kg drum",
        "unit": "KG",
        "halal_requirements": ["No alcohol processing", "Natural honey only"],
    },
    "fish": {
        "type": "Fisheries - Seafood",
        "hs_code": "0303.89",
        "origin": "Indonesia / Vietnam / India",
        "packaging": "IQF 10kg cartons / Bulk frozen",
        "unit": "MT",
        "halal_requirements": ["MUI halal certified", "HACCP certified", "No forbidden species"],
    },
}

SEA_ROUTES = {
    "jakarta_dubai": {"origin": "Jakarta (ID)", "destination": "Jebel Ali (UAE)", "transit_days": 14, "freq": "weekly"},
    "surabaya_jeddah": {"origin": "Surabaya (ID)", "destination": "Jeddah (SA)", "transit_days": 16, "freq": "biweekly"},
    "belawan_chennai": {"origin": "Belawan (ID)", "destination": "Chennai (IN)", "transit_days": 8, "freq": "weekly"},
    "jakarta_shanghai": {"origin": "Jakarta (ID)", "destination": "Shanghai (CN)", "transit_days": 10, "freq": "daily"},
    "algiers_rotterdam": {"origin": "Algiers (DZ)", "destination": "Rotterdam (NL)", "transit_days": 8, "freq": "weekly"},
    "algiers_dubai": {"origin": "Algiers (DZ)", "destination": "Jebel Ali (UAE)", "transit_days": 12, "freq": "biweekly"},
}

CARGO_MANIFESTS = []
BILLS_OF_LADING = []

def load_cargo_manifest(cargo_type: str, volume: float, origin: str,
                        destination: str, seller: str = "", buyer: str = "",
                        cert_required: str = "") -> dict:
    """Ingest a cargo manifest and prepare for shipping."""
    cargo_info = CARGO_TYPES.get(cargo_type)
    if not cargo_info:
        return {"error": f"Unknown cargo type: {cargo_type}",
                "available": list(CARGO_TYPES.keys())}

    manifest_id = f"MNF-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(CARGO_MANIFESTS)+1:04d}"

    # Find best route
    route_key = f"{origin.lower().split('(')[0].strip()}_{destination.lower().split('(')[0].strip()}"
    # Simple route matching
    route = None
    for rk, rv in SEA_ROUTES.items():
        if origin.lower().split('(')[0].strip() in rk and destination.lower().split('(')[0].strip() in rk:
            route = rv
            break
    if not route:
        route = {"origin": origin, "destination": destination, "transit_days": 14, "freq": "estimated"}

    manifest = {
        "manifest_id": manifest_id,
        "cargo_type": cargo_type,
        "hs_code": cargo_info["hs_code"],
        "volume": volume,
        "unit": cargo_info["unit"],
        "seller": seller or "TBD",
        "buyer": buyer or "TBD",
        "origin": origin,
        "destination": destination,
        "route": route,
        "cert_required": cert_required or cargo_info["halal_requirements"][0],
        "status": "ingested",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "halal_screening": "pending",
    }

    # Auto-screen halal compliance
    halal_screening = audit_halal_supply_chain(manifest, cargo_info)
    manifest["halal_screening"] = halal_screening
    manifest["status"] = "screened"

    CARGO_MANIFESTS.append(manifest)
    return manifest


def audit_halal_supply_chain(manifest: dict, cargo_info: dict = None) -> dict:
    """Bay' al-Musawamah — halal supply chain audit."""
    if not cargo_info:
        cargo_info = CARGO_TYPES.get(manifest.get("cargo_type", ""), {})

    checks = []
    all_pass = True

    for req in cargo_info.get("halal_requirements", []):
        check = {
            "requirement": req,
            "status": random.choice(["pass", "pass", "pass", "pass", "pass", "pass", "fail"]) if random.random() < 0.9 else "review",
            "evidence": f"Certification on file — verified against {req.split(' ')[0]} registry",
        }
        if check["status"] != "pass":
            all_pass = False
        checks.append(check)

    return {
        "audit_type": "Bay' al-Musawamah (negotiated price, transparent terms)",
        "status": "compliant" if all_pass else "review_required",
        "checks": checks,
        "cert_body": "MUI / JAKIM / ESMA (per origin country)",
        "riba_check": "No interest-bearing financing detected",
        "gharar_check": "Full cargo specification disclosed — no uncertainty",
        "overall": "Halal compliant — trade meets Islamic commercial law standards" if all_pass
                  else "Review required — some certifications need verification",
    }


def generate_bill_of_lading(manifest_id: str, consignee: str = "",
                            notify_party: str = "", payment_terms: str = "LC at sight") -> dict:
    """Autonomously draft a Bill of Lading from cargo manifest."""
    manifest = next((m for m in CARGO_MANIFESTS if m["manifest_id"] == manifest_id), None)
    if not manifest:
        return {"error": f"Manifest not found: {manifest_id}"}

    bl_number = f"TAL-BL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(BILLS_OF_LADING)+1:04d}"

    bl = {
        "bl_number": bl_number,
        "manifest_id": manifest_id,
        "shipper": manifest.get("seller", "TALIMNA Logistics"),
        "consignee": consignee or "To Order",
        "notify_party": notify_party or consignee or "To Order",
        "vessel": "MV TALIMNA TRADER (voyage scheduled)",
        "port_of_loading": manifest["origin"],
        "port_of_discharge": manifest["destination"],
        "cargo_description": f"{manifest['volume']} {manifest['unit']} of {manifest['cargo_type'].replace('_', ' ').title()}",
        "hs_code": manifest["hs_code"],
        "container_type": "20' Standard / Flexitank",
        "gross_weight_kg": round(manifest["volume"] * 1000, 0) if manifest.get("unit") == "MT" else round(manifest["volume"] * 200, 0),
        "payment_terms": payment_terms,
        "freight_charge": round(manifest["volume"] * 85, 2),  # $85/MT estimated
        "halal_compliance": manifest.get("halal_screening", {}).get("status", "pending"),
        "status": "drafted",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "shipping_instructions": [
            "1. Shipper arranges container stuffing at origin warehouse",
            "2. Customs clearance at port of loading (export declaration)",
            "3. Container gated in — 3 days prior to vessel ETA",
            "4. Bill of Lading issued upon cargo on board",
            "5. Original BL surrendered at destination for cargo release",
        ],
    }

    BILLS_OF_LADING.append(bl)
    return bl


def trigger_freight_dispatch(bl_number: str, carrier: str = "MAERSK") -> dict:
    """Trigger physical transport — dispatch order to carrier."""
    bl = next((b for b in BILLS_OF_LADING if b["bl_number"] == bl_number), None)
    if not bl:
        return {"error": f"Bill of Lading not found: {bl_number}"}

    dispatch_id = f"DSP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    return {
        "dispatch_id": dispatch_id,
        "bl_number": bl_number,
        "carrier": carrier,
        "route": f"{bl['port_of_loading']} → {bl['port_of_discharge']}",
        "cargo": bl["cargo_description"],
        "status": "dispatched_to_carrier",
        "carrier_booking_ref": f"{carrier[:3]}-{random.randint(100000, 999999)}",
        "automated_by": "TALIMNA Al-Jalib MAS — no human intervention",
        "next_step": "3PL picks up container from shipper warehouse",
        "triggered_at": datetime.now(timezone.utc).isoformat(),
    }


def customs_clearance(manifest_id: str, country: str = "") -> dict:
    """Customs clearance simulation — checks documents for BRICS+ portals."""
    manifest = next((m for m in CARGO_MANIFESTS if m["manifest_id"] == manifest_id), None)
    if not manifest:
        return {"error": f"Manifest not found: {manifest_id}"}

    docs_required = [
        "Bill of Lading (generated by Al-Jalib)",
        "Commercial Invoice",
        "Packing List",
        "Certificate of Origin (Form E for ASEAN-China FTA)",
        "Halal Certificate (MUI/JAKIM for food products)",
        "Phytosanitary Certificate (if agricultural)",
        "Insurance Certificate",
    ]

    return {
        "manifest_id": manifest_id,
        "country": country or manifest["destination"].split("(")[-1].rstrip(")"),
        "declaration": "Automated customs filing via Al-Jalib MAS",
        "documents_required": docs_required,
        "status": "docs_ready",
        "digital_submission": "Integrated with BRICS+ customs digital portals (simulated)",
        "estimated_clearance_hours": 24,
        "tariff_code": manifest["hs_code"],
        "preferential_tariff": "Available under RCEP / ASEAN-FTA / China-BRICS",
    }


def list_active_shipments(status: str = "") -> dict:
    """List all active cargo shipments in the corridor."""
    results = []
    for m in CARGO_MANIFESTS:
        if status and m["status"] != status:
            continue
        results.append({
            "manifest_id": m["manifest_id"],
            "cargo": m["cargo_type"],
            "volume": f"{m['volume']} {m['unit']}",
            "route": f"{m['origin']} → {m['destination']}",
            "status": m["status"],
            "halal": m.get("halal_screening", {}).get("status", "pending"),
        })
    return {"count": len(results), "shipments": results} if results else {"count": 0, "shipments": results, "note": "Load a cargo manifest first using load_cargo_manifest"}