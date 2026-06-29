# TALIMNA Client Acquisition System
# OSINT research → personalized pitch → email outreach

CLIENTS = {
    "al_ghurair": {
        "company": "Al Ghurair Food Trading LLC",
        "country": "UAE",
        "city": "Dubai",
        "industry": "halal_food",
        "interest": "Processed halal food imports from SEA",
        "match_svc": "Al-Jalib (cargo: coconut_oil, dates), Compliance (cert verification)",
        "pitch_template": "trade_importer",
        "email_guess": "info@alghurair.com",
        "notes": "Major UAE food importer. Needs MUI/JAKIM certified suppliers from Indonesia."
    },
    "cofco": {
        "company": "COFCO International",
        "country": "China",
        "city": "Shanghai",
        "industry": "agriculture",
        "interest": "Bulk soybean imports from Brazil",
        "match_svc": "Al-Jalib (cargo: palm_oil, soy), Intel (market data), Translation",
        "pitch_template": "bulk_trader",
        "email_guess": "trade@cofco.com",
        "notes": "State-owned grain trader. $50B+ annual trade volume."
    },
    "pt_halal_food": {
        "company": "PT Halal Food Jakarta",
        "country": "Indonesia",
        "city": "Jakarta",
        "industry": "halal_food",
        "interest": "Export frozen halal chicken to UAE/ME",
        "match_svc": "Al-Jalib (logistics), Compliance (MUI cert verification), Matchmaking (buyer matching)",
        "pitch_template": "sea_exporter",
        "email_guess": "export@pt-halalfood.com",
        "notes": "MUI-certified halal meat exporter. Looking for Gulf buyers."
    },
    "sun_pharma": {
        "company": "Sun Pharma Exports",
        "country": "India",
        "city": "Mumbai",
        "industry": "pharmaceuticals",
        "interest": "Generic pharma exports to SEA and Africa",
        "match_svc": "Compliance (halal pharma cert), Translation, Logistics",
        "pitch_template": "pharma_exporter",
        "email_guess": "exports@sunpharma.com",
        "notes": "Major Indian generic pharma exporter. Needs halal pharma certification for SEA."
    },
    "cp_foods": {
        "company": "CP Foods Public Company Ltd",
        "country": "Thailand",
        "city": "Bangkok",
        "industry": "halal_food",
        "interest": "Export halal frozen chicken to Middle East",
        "match_svc": "Al-Jalib (logistics), Compliance (CICOT cert), Matchmaking",
        "pitch_template": "sea_exporter",
        "email_guess": "export@cpf.co.th",
        "notes": "Thailand's largest agri-industrial group. CICOT certified."
    },
    "indofood": {
        "company": "PT Indofood Sukses Makmur Tbk",
        "country": "Indonesia",
        "city": "Jakarta",
        "industry": "food_processing",
        "interest": "Instant noodle exports across SEA/ME",
        "match_svc": "Logistics (route optimization), Translation, Compliance",
        "pitch_template": "sea_exporter",
        "email_guess": "export@indofood.co.id",
        "notes": "Largest instant noodle producer globally. $5B revenue."
    },
    "almarai": {
        "company": "Almarai Company",
        "country": "Saudi Arabia",
        "city": "Riyadh",
        "industry": "dairy_food",
        "interest": "Dairy imports and distribution",
        "match_svc": "Compliance (SFDA cert), Logistics, Matchmaking",
        "pitch_template": "trade_importer",
        "email_guess": "supplychain@almarai.com",
        "notes": "Largest integrated dairy company in the Middle East."
    },
}


def get_pitch(template: str, client: dict) -> str:
    """Generate personalized pitch based on client profile."""
    pitches = {
        "trade_importer": f"""Dear {client['company']} Team,

I am reaching out because TALIMNA operates the Al-Jalib Trans-South Commercial Corridor — an algorithmic logistics network connecting Southeast Asian commodity suppliers directly to Gulf importers.

We are currently onboarding {client['industry'].replace('_',' ').title()} suppliers from Indonesia, Malaysia, and Thailand who are actively seeking Gulf buyers. Our system handles:
- Cargo manifest ingestion and Bill of Lading generation
- Halal certification verification (MUI, JAKIM, ESMA, SFDA)
- Route optimization and carrier dispatch
- Multi-currency settlement (A2A rails, no SWIFT dependency)

I would be happy to share a list of pre-vetted suppliers matched to your import profile. No obligation.

Best regards,
Arya Wang
CEO, TALIMNA
arya.wang@talimna.com
mcp.talimna.com""",

        "sea_exporter": f"""Dear {client['company']} Team,

I am contacting you regarding TALIMNA's Al-Jalib Corridor — an end-to-end algorithmic export pipeline for Southeast Asian halal commodity producers targeting Gulf and BRICS markets.

Our system automates everything from cargo manifest to customs clearance:
- Route optimization across Jakarta, Surabaya, Bangkok to Dubai, Jeddah, Chennai
- Halal certification compliance (MUI, JAKIM, CICOT certification verification)
- Automated Bill of Lading generation and carrier dispatch
- No-USD settlement via A2A rails or gold/silver equivalents

We are actively matching SEA exporters with verified buyers in the UAE, Saudi Arabia, and India markets.

Would you be open to a brief introduction to our system?

Best regards,
Arya Wang
CEO, TALIMNA
arya.wang@talimna.com
mcp.talimna.com""",

        "bulk_trader": f"""Dear {client['company']} Team,

I am writing to introduce TALIMNA's trade infrastructure for BRICS+ commodity corridors. Our Al-Jalib system provides algorithmic orchestration of physical trade flows across Global South nodes.

Given your expertise in bulk agricultural trading, our platform may be relevant for:
- Real-time route optimization and freight dispatch
- Automated documentation (cargo manifests, bills of lading, customs)
- Multi-currency settlement bypassing USD/SWIFT
- Trade intelligence and market data for BRICS+ corridors

We are currently operational on 10 corridors with live API services.

Happy to schedule a brief demonstration.

Best regards,
Arya Wang
CEO, TALIMNA
arya.wang@talimna.com
mcp.talimna.com""",

        "pharma_exporter": f"""Dear {client['company']} Team,

I am reaching out because TALIMNA provides automated halal compliance verification and trade logistics for pharmaceutical exports to Southeast Asian and Middle Eastern markets.

Our system verifies pharmaceutical halal certification against WHO GMP and relevant national standards (BPJPH, SFDA, JAKIM), alongside automated logistics dispatch and document generation.

We can help streamline your halal pharma certification process for SEA and Gulf market entry.

Would you be interested in a brief demo of our compliance verification system?

Best regards,
Arya Wang
CEO, TALIMNA
arya.wang@talimna.com
mcp.talimna.com""",
    }

    body = pitches.get(template, pitches["trade_importer"])
    return body


def get_subject(client: dict) -> str:
    """Generate relevant subject line."""
    subjects = {
        "trade_importer": f"SEA Halal Supplier Pipeline — Al-Jalib Corridor Access",
        "sea_exporter": f"Gulf Buyer Matching — TALIMNA Export Pipeline",
        "bulk_trader": f"BRICS+ Commodity Corridor — Automated Trade Infrastructure",
        "pharma_exporter": f"Halal Pharma Certification + SEA Trade Logistics",
    }
    return subjects.get(client.get("pitch_template", "trade_importer"))


if __name__ == "__main__":
    for cid, client in sorted(CLIENTS.items()):
        print(f"\n{'='*60}")
        print(f"TO: {client['company']} ({client['country']})")
        print(f"SUBJECT: {get_subject(client)}")
        print(f"{'='*60}")
        body = get_pitch(client["pitch_template"], client)
        print(body[:200] + "...")
        print()