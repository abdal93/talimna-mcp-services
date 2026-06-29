# TALIMNA Vetted Prospect List — OSINT Deep Research
# Generated: 2026-06-29 via OSINT tools (whatweb, holehe, subfinder, theHarvester)

PROSPECTS = [
    {
        "company": "Al Ghurair Group",
        "website": "alghurair.com",
        "email": "contact@alghurair.com",
        "country": "UAE",
        "city": "Dubai",
        "industry": "Food Import / Conglomerate",
        "subdomains": ["guest.alghurair.com", "npm.portal.alghurair.com", "relay.alghurair.com"],
        "tech_stack": "WordPress, PHP 8.3.12, Cloudflare",
        "other_emails": ["info@agis.ae", "sales@gulfex.com", "info@arabpack.com"],
        "relevance": "HIGH — Major UAE food importer. Needs halal cert verification + SEA supplier pipeline.",
        "pitch_template": "importer",
        "email_verified": True,
    },
    {
        "company": "Savola Group",
        "website": "savola.com",
        "email": "info@savola.com",
        "country": "Saudi Arabia",
        "city": "Jeddah",
        "industry": "Food Manufacturing / Edible Oils",
        "tech_stack": "whatweb confirmed",
        "relevance": "HIGH — $8B revenue food conglomerate. Imports palm oil from SEA. Al-Jalib corridor fit.",
        "pitch_template": "importer",
        "email_verified": True,
    },
    {
        "company": "Albwardy Investment",
        "website": "albwardy.com",
        "email": "info@albwardy.com",
        "country": "UAE",
        "city": "Dubai",
        "industry": "Food Import / Logistics",
        "relevance": "MEDIUM — UAE investment group with food import arm.",
        "pitch_template": "importer",
        "email_verified": True,
    },
    {
        "company": "CP Foods (Charoen Pokphand)",
        "website": "cpfworldwide.com",
        "email": "22mconsumercenter@cpf.co.th",
        "country": "Thailand",
        "city": "Bangkok",
        "industry": "Agri-Food / Halal Poultry",
        "relevance": "HIGH — World's largest halal chicken exporter. CICOT certified. Needs Gulf buyer matching.",
        "pitch_template": "exporter",
        "email_verified": True,
        "note": "Email is consumer center. Need to find B2B procurement contact."
    },
    {
        "company": "Indofood Sukses Makmur",
        "website": "indofood.com",
        "email": "export@indofood.co.id",
        "country": "Indonesia",
        "city": "Jakarta",
        "industry": "Food Processing / Instant Noodles",
        "relevance": "HIGH — $5B revenue, largest noodle producer globally. Exports across SEA/ME.",
        "pitch_template": "exporter",
        "email_verified": False,  # need to verify
    },
    {
        "company": "Gulf Trading & Services",
        "website": "gulftrading.ae",
        "email": "info@gulftrading.ae",
        "country": "UAE",
        "city": "Dubai",
        "industry": "General Trading / Import-Export",
        "relevance": "MEDIUM — Dubai-based trader. Small but approachable.",
        "pitch_template": "importer",
        "email_verified": True,
    },
]

# TARGET INDUSTRIES (additional prospects to research)
TARGET_INDUSTRIES = [
    "SEA halal food exporters (Indonesia, Malaysia, Thailand)",
    "Gulf food importers (UAE, Saudi Arabia, Qatar)",
    "BRICS+ commodity traders (agriculture, energy)",
    "Halal pharmaceutical exporters (India, Indonesia)",
    "Logistics intermediaries (Dubai re-export hub)",
]

# OUTREACH PRIORITY
# 1. Al Ghurair (contact@alghurair.com) — confirmed reachable 
# 2. Savola (info@savola.com) — confirmed reachable
# 3. Gulf Trading (info@gulftrading.ae) — confirmed reachable
# 4. Indofood (export@indofood.co.id) — unconfirmed, test send
# 5. CP Foods — need B2B contact (consumer center email not ideal)
