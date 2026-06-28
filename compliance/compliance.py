# TALIMNA Sharia Compliance Engine
# Rule-based halal screening, zakat calculation, riba detection
# Based on: Quran, Authentic Hadith, Ahl al-Hadith, Athari tradition
# References: Al-Usul Ath-Thalatha, Kitab At-Tawhid, Hisn al-Muslim

import re
import json

# ─── Halal/Haram Sector Reference ─────────────────────────────────────

HALAL_SECTORS = {
    "agriculture": "Halal — food production, farming",
    "fishing": "Halal — seafood harvest",
    "livestock": "Halal — animal husbandry (halal slaughter required)",
    "manufacturing_food": "Halal — food processing (halal-certified)",
    "manufacturing_textile": "Halal — clothing, textiles",
    "manufacturing_electronics": "Halal — electronics production",
    "manufacturing_furniture": "Halal — furniture",
    "manufacturing_pharma": "Halal — halal pharmaceuticals",
    "construction": "Halal — building infrastructure",
    "logistics": "Halal — transport, shipping, warehousing",
    "retail_general": "Halal — general retail (halal products only)",
    "wholesale_trade": "Halal — wholesale",
    "real_estate": "Halal — property (no interest-based mortgages)",
    "software_dev": "Halal — software development",
    "it_services": "Halal — IT services",
    "data_analytics": "Halal — data services",
    "ai_services": "Halal — AI/ML services",
    "consulting": "Halal — business consulting (haram sectors excluded)",
    "education": "Halal — teaching, training",
    "healthcare": "Halal — medical services",
    "transportation": "Halal — passenger/goods transport",
    "renewable_energy": "Halal — solar, wind, hydro",
    "water_treatment": "Halal — water purification, sanitation",
    "telecom": "Halal — telecommunications",
    "halal_certification": "Halal — certification services",
    "islamic_finance": "Halal — sharia-compliant finance",
}

HARAM_SECTORS = {
    "alcohol": "Haram — production, distribution, sale of alcohol",
    "pork": "Haram — pork products, processing",
    "gambling": "Haram — casinos, betting, lottery, games of chance",
    "interest_finance": "Haram — conventional banking, riba-based lending",
    "insurance_conventional": "Haram — conventional insurance (gharar)",
    "derivatives": "Haram — options, futures, swaps (gharar)",
    "adult_entertainment": "Haram — pornography, adult content",
    "tobacco": "Haram — cigarette/tobacco production",
    "weapons_civilian": "Mashbuh (questionable) — civilian firearms",
    "music_instruments": "Mashbuh (questionable) — per difference of opinion",
    "entertainment_mixed": "Mashbuh — mixed-gender entertainment",
}


def check_sector(sector: str) -> dict:
    """Check if a business sector is halal."""
    sector = sector.lower().strip().replace(" ", "_")

    if sector in HALAL_SECTORS:
        return {"status": "halal", "detail": HALAL_SECTORS[sector]}
    if sector in HARAM_SECTORS:
        return {"status": "haram", "detail": HARAM_SECTORS[sector]}

    # Fuzzy match
    for key, val in {**HALAL_SECTORS, **HARAM_SECTORS}.items():
        if sector in key or key in sector:
            status = "halal" if key in HALAL_SECTORS else "haram"
            return {"status": status, "detail": val, "matched_on": key}

    return {"status": "unknown", "detail": "Sector not classified. Requires scholar review."}


# ─── Zakat Calculation ────────────────────────────────────────────────

ZAKAT_RATE = 0.025  # 2.5%
NISAB_GOLD_GRAMS = 85  # 85g gold
NISAB_SILVER_GRAMS = 595  # 595g silver
GOLD_PRICE_PER_GRAM_USD = 85  # Approximate 2026 market rate


def calculate_zakat(assets: dict, hawl_complete: bool = True) -> dict:
    """Calculate zakat on assets.
    
    assets: {
        "cash": float,           # Cash on hand and in bank
        "gold_grams": float,     # Gold held (jewelry subject to differences)
        "silver_grams": float,   # Silver held
        "business_inventory": float,  # Trade goods value
        "accounts_receivable": float,  # Money owed to you
        "investment_value": float,     # Halal investments
        "accounts_payable": float,     # Debts you owe (deductible)
        "personal_use_items": float,   # Exempt (car, home, clothing)
    }
    """
    # Calculate zakatable assets
    cash = assets.get("cash", 0)
    gold_value = assets.get("gold_grams", 0) * GOLD_PRICE_PER_GRAM_USD
    silver_value = assets.get("silver_grams", 0) * (GOLD_PRICE_PER_GRAM_USD / 85)  # approximate
    business_inventory = assets.get("business_inventory", 0)
    accounts_receivable = assets.get("accounts_receivable", 0)
    investment_value = assets.get("investment_value", 0)

    # Deductible
    accounts_payable = assets.get("accounts_payable", 0)

    # Calculate
    total_zakatable = cash + gold_value + silver_value + business_inventory + accounts_receivable + investment_value
    net_zakatable = max(0, total_zakatable - accounts_payable)

    # Nisab check (gold standard)
    nisab_value = NISAB_GOLD_GRAMS * GOLD_PRICE_PER_GRAM_USD
    nisab_met = net_zakatable >= nisab_value

    # Zakat due
    zakat_due = round(net_zakatable * ZAKAT_RATE, 2) if nisab_met and hawl_complete else 0

    return {
        "zakat_due_usd": zakat_due,
        "nisab_met": nisab_met,
        "nisab_threshold_usd": nisab_value,
        "hawl_complete": hawl_complete,
        "total_zakatable_assets_usd": round(total_zakatable, 2),
        "net_zakatable_after_debts_usd": round(net_zakatable, 2),
        "breakdown": {
            "cash": cash,
            "gold_value_usd": round(gold_value, 2),
            "silver_value_usd": round(silver_value, 2),
            "business_inventory": business_inventory,
            "accounts_receivable": accounts_receivable,
            "investment_value": investment_value,
            "accounts_payable": accounts_payable,
        },
        "eligible_recipients": [
            "Fakir (extreme poverty)",
            "Miskin (moderate poverty)",
            "Amil (zakat collectors)",
            "Muallaf (new Muslims)",
            "Riqab (freeing slaves)",
            "Gharimin (debtors)",
            "Fisabilillah (in Allah's path)",
            "Ibn Sabil (travelers in need)",
        ],
    }


# ─── Riba Detection ───────────────────────────────────────────────────

RIBA_KEYWORDS = {
    "interest": "Interest (riba) — explicitly prohibited in Quran 2:275-279",
    "interest rate": "Interest rate — riba al-fadl",
    "apr": "Annual Percentage Rate — form of riba",
    "apy": "Annual Percentage Yield — form of riba",
    "compound interest": "Compound interest — severe riba",
    "usury": "Usury — riba, prohibited",
    "late fee interest": "Late payment interest — riba al-jahiliyyah",
    "overdue interest": "Overdue interest — riba",
    "penalty interest": "Penalty interest — riba",
    "loan shark": "Loan shark — riba, haram",
    "fixed interest": "Fixed interest — riba al-fadl",
    "variable interest": "Variable interest — riba",
    "prime rate": "Prime rate — riba benchmark",
    "libor": "LIBOR — riba benchmark",
    "benchmark rate": "Benchmark rate — potential riba reference",
}

GHARAR_KEYWORDS = {
    "speculation": "Speculation (gharar/maysir) — excessive uncertainty",
    "gambling": "Gambling (maysir) — explicitly prohibited",
    "bet": "Betting — maysir",
    "lottery": "Lottery — maysir",
    "derivative": "Derivative contract — gharar",
    "futures contract": "Futures — gharar (uncertain delivery)",
    "option contract": "Options — gharar",
    "swap agreement": "Swap — gharar",
    "forward contract": "Forward — gharar",
    "insurance premium": "Conventional insurance — gharar",
}


def detect_riba(text: str) -> dict:
    """Detect riba/gharar clauses in contract or document text."""
    text_lower = text.lower()
    findings = []

    for keyword, explanation in RIBA_KEYWORDS.items():
        if keyword in text_lower:
            # Find context
            for line in text.split("\n"):
                if keyword in line.lower():
                    findings.append({
                        "type": "riba",
                        "keyword": keyword,
                        "explanation": explanation,
                        "context": line.strip()[:150],
                    })
                    break

    for keyword, explanation in GHARAR_KEYWORDS.items():
        if keyword in text_lower:
            for line in text.split("\n"):
                if keyword in line.lower():
                    findings.append({
                        "type": "gharar",
                        "keyword": keyword,
                        "explanation": explanation,
                        "context": line.strip()[:150],
                    })
                    break

    severity = "clean" if not findings else (
        "high" if any(f["type"] == "riba" for f in findings) else "medium"
    )

    return {
        "status": "non_compliant" if findings else "compliant",
        "severity": severity,
        "findings_count": len(findings),
        "findings": findings,
        "summary": f"Found {len(findings)} potential Sharia violations: {sum(1 for f in findings if f['type']=='riba')} riba, {sum(1 for f in findings if f['type']=='gharar')} gharar",
    }


# ─── Transaction Screening ────────────────────────────────────────────

HARAM_COUNTERPARTIES_KEYWORDS = [
    "alcohol", "wine", "beer", "liquor", "spirits",
    "pork", "bacon", "ham", "lard",
    "casino", "gambling", "betting", "poker",
    "adult", "porn", "escort", "massage parlor",
    "tobacco", "cigarette", "cigar",
    "weapons manufacturer", "arms dealer",
    "conventional bank", "interest", "lending",
]


def screen_transaction(
    amount: float,
    currency: str = "USD",
    counterparty: str = "",
    sector: str = "",
    purpose: str = "",
    jurisdiction: str = "",
) -> dict:
    """Screen a transaction for Sharia compliance."""
    flags = []

    # Check amount
    if amount <= 0:
        flags.append({"field": "amount", "issue": "Amount must be positive"})

    # Check sector
    if sector:
        sector_check = check_sector(sector)
        if sector_check["status"] != "halal":
            flags.append({
                "field": "sector",
                "issue": f"Sector is {sector_check['status']}: {sector_check['detail']}",
            })

    # Check counterparty
    if counterparty:
        cp_lower = counterparty.lower()
        for keyword in HARAM_COUNTERPARTIES_KEYWORDS:
            if keyword in cp_lower:
                flags.append({
                    "field": "counterparty",
                    "issue": f"Counterparty appears to deal in: {keyword}",
                })
                break

    # Check purpose
    if purpose:
        purpose_lower = purpose.lower()
        for keyword in HARAM_COUNTERPARTIES_KEYWORDS:
            if keyword in purpose_lower:
                flags.append({
                    "field": "purpose",
                    "issue": f"Purpose relates to: {keyword}",
                })
                break

    # Check currency (riba al-fadl)
    if currency.upper() in ("USD", "EUR", "GBP", "CNY", "INR", "RUB", "BRL"):
        # Fiat currencies are acceptable for trade, but riba applies to loans
        pass  # No flag for normal trade

    verdict = "non_compliant" if flags else "compliant"

    return {
        "transaction": {
            "amount": amount,
            "currency": currency,
            "counterparty": counterparty or "N/A",
            "sector": sector or "N/A",
            "purpose": purpose or "N/A",
            "jurisdiction": jurisdiction or "N/A",
        },
        "verdict": verdict,
        "flags_count": len(flags),
        "flags": flags,
        "recommendation": "Transaction may proceed - no concerns" if not flags else (
            "Requires Sharia scholar review" if any(f.get("issue", "").startswith("Mashbuh") or f.get("issue", "").startswith("Sector is unknown") for f in flags)
            else "Transaction NOT permitted in current form"
        ),
    }


# ─── Sharia Report ────────────────────────────────────────────────────

def generate_sharia_report(
    transactions: list = None,
    contract_text: str = None,
    portfolio_value: float = 0,
    include_zakat: bool = True,
) -> dict:
    """Generate comprehensive Sharia compliance report."""
    report = {
        "summary": {},
        "transaction_review": [],
        "contract_review": None,
        "zakat_obligation": None,
        "recommendations": [],
    }

    # Review transactions
    if transactions:
        for tx in transactions:
            result = screen_transaction(**tx)
            report["transaction_review"].append(result)
            if result["verdict"] == "non_compliant":
                report["recommendations"].append(
                    f"Review transaction {len(report['transaction_review'])}: {result['flags'][0]['issue'] if result['flags'] else 'Unknown issue'}"
                )

    # Review contract
    if contract_text:
        riba_result = detect_riba(contract_text)
        report["contract_review"] = riba_result
        if riba_result["status"] == "non_compliant":
            report["recommendations"].append(
                f"Contract contains {riba_result['findings_count']} Sharia violations"
            )

    # Zakat
    if include_zakat and portfolio_value > 0:
        zakat = calculate_zakat({"cash": portfolio_value})
        report["zakat_obligation"] = zakat
        if zakat["zakat_due_usd"] > 0:
            report["recommendations"].append(
                f"Zakat due: ${zakat['zakat_due_usd']:,.2f}"
            )

    tx_count = len(report["transaction_review"])
    tx_non_compliant = sum(1 for t in report["transaction_review"] if t["verdict"] == "non_compliant")
    contract_issues = report["contract_review"]["findings_count"] if report["contract_review"] else 0

    report["summary"] = {
        "overall_status": "needs_review" if (tx_non_compliant > 0 or contract_issues > 0) else "compliant",
        "transactions_screened": tx_count,
        "transactions_non_compliant": tx_non_compliant,
        "contract_issues_found": contract_issues,
        "recommendations_count": len(report["recommendations"]),
    }

    return report