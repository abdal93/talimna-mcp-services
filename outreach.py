#!/usr/bin/env python3
"""TALIMNA Client Acquisition — OSINT Vetted Prospects"""
import sys, json, ssl, smtplib
from email.message import EmailMessage

SMTP_HOST = "mail.infomaniak.com"
SMTP_PORT = 587
ADDR = "arya.wang@talimna.com"
PASS = os.environ.get("TALIMNA_SMTP_PASS", "")

TARGETS = [
    {"to": "contact@alghurair.com", "company": "Al Ghurair Group", "country": "UAE", "tmpl": "importer"},
    {"to": "info@savola.com", "company": "Savola Group", "country": "Saudi Arabia", "tmpl": "importer"},
    {"to": "info@albwardy.com", "company": "Albwardy Investment", "country": "UAE", "tmpl": "importer"},
    {"to": "info@gulftrading.ae", "company": "Gulf Trading & Services", "country": "UAE", "tmpl": "importer"},
    {"to": "export@indofood.co.id", "company": "Indofood Sukses Makmur", "country": "Indonesia", "tmpl": "exporter"},
]

SUBJECTS = {
    "importer": "SEA Halal Supplier Pipeline — Al-Jalib Corridor Access",
    "exporter": "Gulf Buyer Matching — TALIMNA Export Pipeline",
    "bulk": "BRICS+ Commodity Corridor — Automated Trade Infrastructure",
}

BODIES = {
    "importer": """Dear {company} Team,

TALIMNA operates the Al-Jalib Trans-South Commercial Corridor — an algorithmic logistics network connecting Southeast Asian commodity suppliers directly to Gulf importers.

We are currently onboarding halal food suppliers from Indonesia, Malaysia, and Thailand who are actively seeking Gulf buyers. Our system handles:
- Cargo manifest ingestion and Bill of Lading generation
- Halal certification verification (MUI, JAKIM, ESMA, SFDA)
- Route optimization and carrier dispatch
- Multi-currency settlement (A2A rails, no SWIFT dependency)

I can share a list of pre-vetted suppliers matched to your import profile. No obligation.

Best regards,
Arya Wang
CEO, TALIMNA
arya.wang@talimna.com
mcp.talimna.com""",

    "exporter": """Dear {company} Team,

TALIMNA's Al-Jalib Corridor provides an end-to-end algorithmic export pipeline for Southeast Asian halal commodity producers targeting Gulf and BRICS markets.

Our system automates:
- Route optimization across Jakarta, Surabaya, Bangkok to Dubai, Jeddah, Chennai
- Halal certification compliance (MUI, JAKIM, CICOT verification)
- Automated Bill of Lading and customs clearance
- No-USD settlement via A2A rails or gold/silver equivalents

We are actively matching SEA exporters with verified buyers in UAE, Saudi Arabia, and India.

Would you be open to an introduction?

Best regards,
Arya Wang
CEO, TALIMNA
arya.wang@talimna.com
mcp.talimna.com""",
}

def send(to, subject, body):
    msg = EmailMessage()
    msg["From"] = f"Arya Wang CEO <{ADDR}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls(context=ctx)
        s.login(ADDR, PASS)
        s.send_message(msg)
    return True

if len(sys.argv) < 2:
    print("Usage: python3 outreach.py preview|send <name>|send all")
    sys.exit(1)

if sys.argv[1] == "preview":
    for t in TARGETS:
        body = BODIES[t["tmpl"]].format(company=t["company"])
        print(f"\n{'='*50}")
        print(f"TO: {t['company']} <{t['to']}>")
        print(f"SUBJECT: {SUBJECTS[t['tmpl']]}")
        print(body[:200] + "...")

elif sys.argv[1] == "send":
    if len(sys.argv) > 2 and sys.argv[2] == "all":
        sent = 0
        for t in TARGETS:
            body = BODIES[t["tmpl"]].format(company=t["company"])
            send(t["to"], SUBJECTS[t["tmpl"]], body)
            print(f"✅ {t['company']:30} → {t['to']}")
            sent += 1
        print(f"\nSent {sent}/{len(TARGETS)}")
    elif len(sys.argv) > 2:
        name = sys.argv[2].lower()
        for t in TARGETS:
            if name in t["company"].lower():
                body = BODIES[t["tmpl"]].format(company=t["company"])
                send(t["to"], SUBJECTS[t["tmpl"]], body)
                print(f"✅ Sent to {t['company']} <{t['to']}>")
                break
        else:
            print(f"Target not found: {name}")
            print(f"Available: {[t['company'] for t in TARGETS]}")
