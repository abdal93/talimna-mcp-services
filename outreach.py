#!/usr/bin/env python3
import sys, json, ssl, smtplib
from email.message import EmailMessage

SMTP_HOST = "mail.infomaniak.com"
SMTP_PORT = 587
ADDR = "arya.wang@talimna.com"
PASS = os.environ.get("TALIMNA_SMTP_PASS", "")

TARGETS = [
    {"to": "info@alghurair.com", "company": "Al Ghurair Food Trading", "tmpl": "importer"},
    {"to": "export@pt-halalfood.com", "company": "PT Halal Food Jakarta", "tmpl": "exporter"},
    {"to": "export@cpf.co.th", "company": "CP Foods Thailand", "tmpl": "exporter"},
    {"to": "trade@cofco.com", "company": "COFCO International", "tmpl": "bulk"},
    {"to": "supplychain@almarai.com", "company": "Almarai Company", "tmpl": "importer"},
]

PITCHES = {
    "importer": lambda c: f"Al-Jalib Corridor access — SEA halal supplier pipeline for {c}. Our system automates cargo, customs, cert verification, and settlement.",
    "exporter": lambda c: f"Gulf buyer matching for {c} via TALIMNA's export pipeline. Automated logistics, halal compliance, and documentation.",
    "bulk": lambda c: f"BRICS+ commodity corridor infrastructure for {c} — route optimization, automated docs, no-SWIFT settlement.",
}

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

    "bulk": """Dear {company} Team,

TALIMNA provides algorithmic trade infrastructure for BRICS+ commodity corridors. Our Al-Jalib system handles:

- Real-time route optimization and freight dispatch
- Automated documentation (manifests, BL, customs)
- Multi-currency settlement bypassing USD/SWIFT
- Trade intelligence for BRICS+ corridors

We are operational on 10 corridors with live API services.

Happy to schedule a brief demonstration.

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

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        sent = 0
        for t in TARGETS:
            body = BODIES[t["tmpl"]].format(company=t["company"])
            subj = SUBJECTS[t["tmpl"]]
            try:
                send(t["to"], subj, body)
                print(f"✅ {t['company']:30} → {t['to']}")
                sent += 1
            except Exception as e:
                print(f"❌ {t['company']:30} → {e}")
        print(f"\nSent {sent}/{len(TARGETS)} emails")
    elif len(sys.argv) > 1 and sys.argv[1] == "preview":
        for t in TARGETS:
            body = BODIES[t["tmpl"]].format(company=t["company"])
            print(f"\n{'='*50}")
            print(f"TO: {t['company']} <{t['to']}>")
            print(f"SUBJECT: {SUBJECTS[t['tmpl']]}")
            print(body[:150] + "...")
    else:
        print("Usage: outreach.py preview|all")
        print("  preview  — show all emails without sending")
        print("  all      — send to all prospects")
