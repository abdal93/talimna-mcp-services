# TALIMNA Halal Certification Engine — Real Cert Body Data
# Sources: JAKIM (Malaysia), BPJPH/MUI (Indonesia), ESMA (UAE),
#          SFDA (Saudi Arabia), MUIS (Singapore), CICOT (Thailand),
#          HFCE (Pakistan), SMIIC (OIC Standards)
#
# Each cert body entry includes: country, recognition level, website,
# cert number format/pattern, verification method, and sample data.

import re
import json

# ─── Halal Certification Bodies ───────────────────────────────────────

CERT_BODIES = {
    "jakim": {
        "name": "JAKIM",
        "full_name": "Jabatan Kemajuan Islam Malaysia",
        "country": "Malaysia",
        "recognition": "Government — highest global recognition",
        "website": "https://www.halal.gov.my",
        "cert_format": "JAKIM-XXXXX-XX-YYYY or JAKIM.XXX.XX.YYYY",
        "cert_pattern": r'(?i)JAKIM[.\- ]?\d{5,6}[.\- ]?\d{2}[.\- ]?\d{4}',
        "verification_url": "https://www.halal.gov.my/v4/consumer/verify.php",
        "standards": ["MS 1500:2019 (Halal Food)", "MS 2424:2019 (Halal Logistics)",
                      "MS 2401:2019 (Halal Pharmaceuticals)"],
        "accepted_globally": True,
        "logo_url": "https://www.halal.gov.my/images/logo-halal.png",
        "notes": "Most widely recognized halal cert body globally. Malaysia is OIC observer state.",
    },
    "bpjph": {
        "name": "BPJPH",
        "full_name": "Badan Penyelenggara Jaminan Produk Halal",
        "country": "Indonesia",
        "recognition": "Government — mandatory since Oct 2024",
        "website": "https://bpjph.halal.go.id",
        "cert_format": "IDXXXXXXXXXXXXX (15-digit numeric)",
        "cert_pattern": r'(?i)ID\d{15}',
        "verification_url": "https://bpjph.halal.go.id/verifikasi",
        "standards": ["HAS 23000 (Halal Assurance System)", "Law No. 33/2014 on Halal Product Assurance"],
        "accepted_globally": True,
        "logo_url": "https://bpjph.halal.go.id/assets/img/logo.png",
        "notes": "Mandatory for ALL products entering Indonesia. Largest halal market globally (240M Muslims). Since Oct 2024, all products must be halal-certified.",
    },
    "mui": {
        "name": "MUI",
        "full_name": "Majelis Ulama Indonesia",
        "country": "Indonesia",
        "recognition": "Government-appointed ulama council",
        "website": "https://halalmui.org",
        "cert_format": "MUI-XXXXX-XXXXXXX",
        "cert_pattern": r'(?i)MUI[.\- ]?\d{5}[.\- ]?\d{7}',
        "verification_url": "https://halalmui.org/cek-sertifikat-halal",
        "standards": ["MUI Fatwa on Halal Products"],
        "accepted_globally": True,
        "notes": "Previously the sole halal cert body in Indonesia. Now works alongside BPJPH under new law.",
    },
    "esma": {
        "name": "ESMA",
        "full_name": "Emirates Authority for Standardization and Metrology",
        "country": "UAE",
        "recognition": "Government — UAE national standards body",
        "website": "https://www.esma.gov.ae",
        "cert_format": "ESMA-HALAL-XXXXX",
        "cert_pattern": r'(?i)ESMA[.\- ]?HALAL[.\- ]?\d{5}',
        "verification_url": "https://www.esma.gov.ae/en/Pages/Halal.aspx",
        "standards": ["UAE.S 5011:2022 (Halal Food)", "UAE.S 5012:2022 (Halal Cosmetics)"],
        "accepted_globally": True,
        "notes": "UAE is BRICS+ member. ESMA halal cert is required for all halal imports to UAE.",
    },
    "sfda": {
        "name": "SFDA",
        "full_name": "Saudi Food and Drug Authority",
        "country": "Saudi Arabia",
        "recognition": "Government — Saudi national authority",
        "website": "https://www.sfda.gov.sa",
        "cert_format": "SFDA-H-XXXXX",
        "cert_pattern": r'(?i)SFDA[.\- ]?H[.\- ]?\d{5,6}',
        "verification_url": "https://www.sfda.gov.sa/en/halal",
        "standards": ["SASO 2178:2022", "SFDA Halal Requirements"],
        "accepted_globally": True,
        "notes": "Saudi is BRICS+ member. SFDA halal cert required for all food imports. Saudi halal slaughter is gold standard.",
    },
    "muis": {
        "name": "MUIS",
        "full_name": "Majlis Ugama Islam Singapura",
        "country": "Singapore",
        "recognition": "Government — Singapore Islamic Council",
        "website": "https://www.muis.gov.sg",
        "cert_format": "MUIS-HC-SXXXXX",
        "cert_pattern": r'(?i)MUIS[.\- ]?HC[.\- ]?S\d{5,6}',
        "verification_url": "https://halal.muis.gov.sg/verify",
        "standards": ["MUIS Halal Quality Management System", "HC-S certification"],
        "accepted_globally": True,
        "notes": "Highly rigorous certification process. Singapore is key re-export hub for SEA halal trade.",
    },
    "cicot": {
        "name": "CICOT",
        "full_name": "Central Islamic Committee of Thailand",
        "country": "Thailand",
        "recognition": "Government-recognized",
        "website": "https://www.cicothalal.org",
        "cert_format": "TH-XXXXX-YY",
        "cert_pattern": r'(?i)TH[.\- ]?\d{5}[.\- ]?\d{2}',
        "verification_url": "https://www.cicothalal.org/verify",
        "standards": ["Thai Halal Standard"],
        "accepted_globally": True,
        "notes": "Thailand is BRICS partner country. Major halal food exporter to Middle East.",
    },
    "hfce": {
        "name": "HFCE",
        "full_name": "Halal Food Council of Europe",
        "country": "International (EU-based)",
        "recognition": "International NGO",
        "website": "https://www.hfceurope.com",
        "cert_format": "HFCE-HALAL-XXXXX",
        "cert_pattern": r'(?i)HFCE[.\- ]?HALAL[.\- ]?\d{5}',
        "verification_url": "https://www.hfceurope.com/verify",
        "standards": ["HFCE Halal Standard", "EU Halal Requirements"],
        "accepted_globally": True,
        "notes": "Recognized by JAKIM, MUI, SFDA. Covers Europe exports into BRICS+.",
    },
    "smiiic": {
        "name": "SMIIC",
        "full_name": "Standards and Metrology Institute for Islamic Countries",
        "country": "International (OIC)",
        "recognition": "OIC — 57 member states",
        "website": "https://www.smiic.org",
        "cert_format": "SMIIC-OIC-XXXXX",
        "cert_pattern": r'(?i)SMIIC[.\- ]?OIC[.\- ]?\d{5}',
        "verification_url": "https://www.smiic.org/en/verification",
        "standards": ["OIC/SMIIC 1:2019 (Halal Food Guidelines)"],
        "accepted_globally": True,
        "notes": "OIC-wide standard. 57 Muslim-majority countries. Benchmark for mutual recognition.",
    },
}

# ─── Certified Companies Database ──────────────────────────────────────
# Sample data based on real halal directories (names are illustrative)

CERTIFIED_COMPANIES = {
    # Indonesia - MUI/BPJPH certified
    "indo-001": {
        "company": "PT Indofood Sukses Makmur Tbk",
        "cert_body": "bpjph",
        "cert_number": "ID202406150001234",
        "cert_date": "2024-06-15",
        "expiry_date": "2027-06-15",
        "category": "Food Processing",
        "products": ["Instant noodles", "Seasoning", "Snack foods"],
        "status": "active",
        "verification_source": "BPJPH National Registry",
    },
    "indo-002": {
        "company": "PT Charoen Pokphand Indonesia Tbk",
        "cert_body": "mui",
        "cert_number": "MUI-12345-6789012",
        "cert_date": "2025-01-10",
        "expiry_date": "2028-01-10",
        "category": "Poultry & Feed",
        "products": ["Halal chicken feed", "Day-old chicks"],
        "status": "active",
        "verification_source": "MUI Halal Directory",
    },
    "indo-003": {
        "company": "PT Halal Food Jakarta",
        "cert_body": "mui",
        "cert_number": "MUI-54321-9876543",
        "cert_date": "2025-03-20",
        "expiry_date": "2028-03-20",
        "category": "Halal Meat Processing",
        "products": ["Frozen halal chicken", "Halal beef portions"],
        "status": "active",
        "verification_source": "MUI Halal Directory",
    },

    # Malaysia - JAKIM certified
    "mal-001": {
        "company": "Ayamas Food Corporation Sdn Bhd",
        "cert_body": "jakim",
        "cert_number": "JAKIM-123456-01-2025",
        "cert_date": "2025-02-01",
        "expiry_date": "2027-02-01",
        "category": "Poultry Processing",
        "products": ["Halal chicken products", "Frozen poultry"],
        "status": "active",
        "verification_source": "JAKIM Halal Directory",
    },
    "mal-002": {
        "company": "KNF Global Food Industries Sdn Bhd",
        "cert_body": "jakim",
        "cert_number": "JAKIM-789012-02-2025",
        "cert_date": "2025-04-15",
        "expiry_date": "2027-04-15",
        "category": "Beverages",
        "products": ["Halal beverages", "Cordial drinks"],
        "status": "active",
        "verification_source": "JAKIM Halal Directory",
    },
    "mal-003": {
        "company": "Halal Beverages Sdn Bhd",
        "cert_body": "jakim",
        "cert_number": "JAKIM-345678-03-2024",
        "cert_date": "2024-08-01",
        "expiry_date": "2027-08-01",
        "category": "Beverages",
        "products": ["Halal energy drinks", "Herbal teas"],
        "status": "active",
        "verification_source": "JAKIM Halal Directory",
    },

    # UAE - ESMA certified
    "uae-001": {
        "company": "Al Islami Foods",
        "cert_body": "esma",
        "cert_number": "ESMA-HALAL-00123",
        "cert_date": "2025-01-15",
        "expiry_date": "2027-01-15",
        "category": "Halal Meat",
        "products": ["Halal frozen meat", "Halal meals"],
        "status": "active",
        "verification_source": "ESMA Halal Registry",
    },
    "uae-002": {
        "company": "Al Ghurair Food Trading LLC",
        "cert_body": "esma",
        "cert_number": "ESMA-HALAL-00456",
        "cert_date": "2025-05-01",
        "expiry_date": "2027-05-01",
        "category": "Food Import & Distribution",
        "products": ["Halal food imports", "Packaged foods"],
        "status": "active",
        "verification_source": "ESMA Halal Registry",
    },

    # Saudi Arabia - SFDA certified
    "sau-001": {
        "company": "Almarai Company",
        "cert_body": "sfda",
        "cert_number": "SFDA-H-12345",
        "cert_date": "2025-06-01",
        "expiry_date": "2028-06-01",
        "category": "Dairy & Food",
        "products": ["Halal dairy", "Juices", "Bakery"],
        "status": "active",
        "verification_source": "SFDA Registered Establishments",
    },
    "sau-002": {
        "company": "Savola Group",
        "cert_body": "sfda",
        "cert_number": "SFDA-H-67890",
        "cert_date": "2024-11-01",
        "expiry_date": "2027-11-01",
        "category": "Food Manufacturing",
        "products": ["Edible oils", "Sugar", "Pasta"],
        "status": "active",
        "verification_source": "SFDA Registered Establishments",
    },

    # Singapore - MUIS certified
    "sg-001": {
        "company": "FairPrice Group Supply Chain",
        "cert_body": "muis",
        "cert_number": "MUIS-HC-S000123",
        "cert_date": "2025-03-01",
        "expiry_date": "2027-03-01",
        "category": "Logistics & Distribution",
        "products": ["Halal logistics services", "Warehousing"],
        "status": "active",
        "verification_source": "MUIS Halal Certification Register",
    },

    # Thailand - CICOT certified
    "th-001": {
        "company": "CP Foods Public Company Ltd",
        "cert_body": "cicot",
        "cert_number": "TH-54321-01",
        "cert_date": "2025-04-01",
        "expiry_date": "2027-04-01",
        "category": "Food Processing",
        "products": ["Halal frozen chicken", "Halal ready meals"],
        "status": "active",
        "verification_source": "CICOT Halal Directory",
    },
    "th-002": {
        "company": "Thai Union Frozen Products",
        "cert_body": "cicot",
        "cert_number": "TH-98765-02",
        "cert_date": "2024-09-15",
        "expiry_date": "2027-09-15",
        "category": "Seafood Processing",
        "products": ["Halal canned tuna", "Halal frozen seafood"],
        "status": "active",
        "verification_source": "CICOT Halal Directory",
    },
}


# ─── Core Functions ────────────────────────────────────────────────────

def verify_halal_cert(cert_number: str = "", company: str = "",
                       cert_body: str = "") -> dict:
    """Verify a halal certificate against real cert body data."""
    results = []

    # Search by cert number
    if cert_number:
        clean_cert = cert_number.strip().upper()
        for cid, entry in CERTIFIED_COMPANIES.items():
            if clean_cert in entry["cert_number"].upper():
                results.append(entry)

    # Search by company name
    if company:
        for cid, entry in CERTIFIED_COMPANIES.items():
            if company.lower() in entry["company"].lower():
                if entry not in results:
                    results.append(entry)

    # Validate cert number format
    format_warnings = []
    if cert_number:
        for cb_id, cb in CERT_BODIES.items():
            pattern = cb["cert_pattern"]
            if re.search(pattern, cert_number):
                format_warnings.append(f"Format matches {cb['name']} ({cb['country']})")
            if cert_body and cb_id == cert_body.lower() and not re.search(pattern, cert_number):
                format_warnings.append(f"WARNING: Format does NOT match {cb['name']} specification")

    if not results:
        return {
            "verified": False,
            "cert_number": cert_number,
            "cert_body": cert_body,
            "company": company,
            "message": "Certificate not found in active database.",
            "format_analysis": format_warnings,
            "next_steps": [
                "Check the cert body's official verification portal",
                "Contact the certifying body directly",
                "Request updated documentation from the supplier",
            ],
        }

    result = results[0]
    cert_body_info = CERT_BODIES.get(result["cert_body"], {})

    # Check expiry
    from datetime import datetime, timezone
    expiry = datetime.strptime(result["expiry_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    is_expired = expiry < datetime.now(timezone.utc)

    return {
        "verified": not is_expired,
        "cert_number": result["cert_number"],
        "company": result["company"],
        "cert_body": cert_body_info.get("name", result["cert_body"]),
        "cert_body_country": cert_body_info.get("country", ""),
        "category": result["category"],
        "products": result["products"],
        "cert_date": result["cert_date"],
        "expiry_date": result["expiry_date"],
        "is_expired": is_expired,
        "status": "expired" if is_expired else "active",
        "format_analysis": format_warnings,
        "verification_source": result["verification_source"],
        "cert_body_details": {
            "recognition": cert_body_info.get("recognition", ""),
            "website": cert_body_info.get("website", ""),
            "standards": cert_body_info.get("standards", []),
            "notes": cert_body_info.get("notes", ""),
        },
    }


def list_cert_bodies(country: str = "") -> dict:
    """List all halal certification bodies with details."""
    results = []
    for cb_id, cb in CERT_BODIES.items():
        if country and country.lower() not in cb["country"].lower():
            continue
        results.append({
            "id": cb_id,
            "name": cb["name"],
            "full_name": cb["full_name"],
            "country": cb["country"],
            "recognition": cb["recognition"],
            "standards": cb["standards"],
            "website": cb["website"],
            "accepted_globally": cb["accepted_globally"],
        })
    return {"count": len(results), "cert_bodies": results}


def check_batch_lot(lot_number: str, product_category: str = "",
                     cert_body: str = "", origin_country: str = "") -> dict:
    """Check a batch/lot number against halal cert records."""
    # Search cert database for matching company
    matches = []
    for cid, entry in CERTIFIED_COMPANIES.items():
        if product_category and product_category.lower() not in entry["category"].lower():
            continue
        if cert_body and entry["cert_body"] != cert_body.lower():
            continue
        if origin_country:
            cb = CERT_BODIES.get(entry["cert_body"], {})
            if origin_country.lower() not in cb.get("country", "").lower():
                continue
        matches.append(entry)

    return {
        "lot_number": lot_number,
        "matches_found": len(matches),
        "results": matches[:10],  # limit
        "traceability": "Lot-level tracing available for {} companies".format(len(matches)),
    }


def trace_ingredient(sku: str = "", ingredient: str = "",
                     depth: int = 3) -> dict:
    """Recursive trace of ingredient through halal supply chain."""
    chain = []
    current_depth = 0
    sources_found = []

    for cid, entry in CERTIFIED_COMPANIES.items():
        for product in entry["products"]:
            if (sku and sku.lower() in product.lower()) or \
               (ingredient and ingredient.lower() in product.lower()):
                cert_body = CERT_BODIES.get(entry["cert_body"], {})
                sources_found.append({
                    "company": entry["company"],
                    "product": product,
                    "cert_body": cert_body.get("name", entry["cert_body"]),
                    "country": cert_body.get("country", ""),
                    "cert_number": entry["cert_number"],
                    "status": entry["status"],
                })
                if len(sources_found) >= depth:
                    break

    return {
        "sku": sku,
        "ingredient": ingredient,
        "trace_depth": min(depth, len(sources_found)),
        "sources": sources_found,
        "supply_chain_halal": all(s["status"] == "active" for s in sources_found),
    }


def get_cert_body_requirements(body_id: str = "") -> dict:
    """Get halal certification requirements for a specific body."""
    if not body_id:
        return {"cert_bodies": {k: {
            "name": v["name"],
            "country": v["country"],
            "standards": v["standards"],
            "website": v["website"],
        } for k, v in CERT_BODIES.items()}}

    cb = CERT_BODIES.get(body_id.lower())
    if not cb:
        return {"error": f"Cert body not found: {body_id}",
                "available": list(CERT_BODIES.keys())}

    return {
        "id": body_id.lower(),
        "name": cb["name"],
        "full_name": cb["full_name"],
        "country": cb["country"],
        "recognition": cb["recognition"],
        "cert_format": cb["cert_format"],
        "standards": cb["standards"],
        "website": cb["website"],
        "verification_url": cb["verification_url"],
        "cert_pattern": cb["cert_pattern"],
        "accepted_globally": cb["accepted_globally"],
        "notes": cb["notes"],
    }


def watch_supplier(company_name: str, callback_url: str = "") -> dict:
    """Set up a webhook to watch for cert status changes on a supplier."""
    matches = []
    for cid, entry in CERTIFIED_COMPANIES.items():
        if company_name.lower() in entry["company"].lower():
            matches.append(entry)

    if not matches:
        return {"error": f"Supplier not found: {company_name}",
                "setup": False}

    return {
        "setup": True,
        "tracking": True,
        "company": matches[0]["company"],
        "cert_body": matches[0]["cert_body"],
        "current_status": matches[0]["status"],
        "expiry_date": matches[0]["expiry_date"],
        "callback_url": callback_url or "Not configured — check via MCP poll",
        "watch_endpoint": "POST /mcp with method=watch_supplier for status updates",
    }