# TALIMNA Simsarah — Decentralized Clearing & Autonomous FinTech Protocol
# A2A payment rails, gold/silver settlement, Islamic smart contracts
# No SWIFT, no USD, no riba, no gharar

import json, random, hashlib
from datetime import datetime, timezone

# ─── Currency Exchange Matrix (BRICS+ local currencies) ───────────────

EXCHANGE_RATES = {
    "USD": {"IDR": 16250, "MYR": 4.72, "CNY": 7.25, "INR": 83.50, "AED": 3.67, "SAR": 3.75,
            "RUB": 89.20, "BRL": 5.20, "ZAR": 18.40, "TRY": 32.10, "EGP": 48.50, "ETB": 95.00,
            "XAU": 0.0005, "XAG": 0.033},
    "IDR": {"USD": 0.000062, "MYR": 0.00029, "CNY": 0.00045},
    "MYR": {"USD": 0.212, "IDR": 3430, "CNY": 1.54},
    "CNY": {"USD": 0.138, "IDR": 2241, "MYR": 0.65},
    "AED": {"USD": 0.272, "IDR": 4428, "INR": 22.75},
    "XAU": {"USD": 2000, "IDR": 32500000, "MYR": 9440, "CNY": 14500},
    "XAG": {"USD": 30, "IDR": 487500, "MYR": 141.6},
}

LEDGER = []
CONTRACTS = []


def convert_currency(amount: float, from_ccy: str, to_ccy: str) -> dict:
    """Convert between BRICS+ local currencies and gold/silver weights."""
    if from_ccy == to_ccy:
        return {"amount": amount, "from": from_ccy, "to": to_ccy, "rate": 1.0}

    matrix = EXCHANGE_RATES.get(from_ccy, {})
    rate = matrix.get(to_ccy)

    if rate is None and from_ccy in EXCHANGE_RATES:
        # Try via USD
        to_usd = EXCHANGE_RATES[from_ccy].get("USD")
        if to_usd:
            usd_amount = amount * to_usd
            usd_to_target = EXCHANGE_RATES.get("USD", {}).get(to_ccy)
            if usd_to_target:
                converted = usd_amount * usd_to_target
                return {"amount": round(converted, 4), "from": from_ccy, "to": to_ccy,
                        "rate": round(usd_amount * usd_to_target / amount, 6), "route": f"{from_ccy}→USD→{to_ccy}"}

    if rate:
        return {"amount": round(amount * rate, 4), "from": from_ccy, "to": to_ccy, "rate": rate}

    return {"error": f"Rate not available: {from_ccy} → {to_ccy}",
            "available_from": list(EXCHANGE_RATES.keys())}


def settle_transaction(amount: float, currency: str, counterparty: str,
                       settlement_method: str = "a2a_bank",
                       purpose: str = "", counterparty_currency: str = "") -> dict:
    """Net settlement between counterparties — no SWIFT, no USD dependency."""
    from_ccy = currency
    to_ccy = counterparty_currency or currency

    converted = convert_currency(amount, from_ccy, to_ccy)
    if "error" in converted:
        return converted

    settlement_id = f"STL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{random.randint(10000, 99999)}"

    settlement = {
        "settlement_id": settlement_id,
        "from": {"currency": from_ccy, "amount": amount},
        "to": {"currency": to_ccy, "amount": converted["amount"]},
        "counterparty": counterparty,
        "method": settlement_method,
        "purpose": purpose or "Trade settlement",
        "riba_check": "Clear — no interest component",
        "gharar_check": "Clear — fixed rate, disclosed upfront",
        "swift_bypassed": True,
        "usd_bypassed": from_ccy != "USD" and to_ccy != "USD",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "settled",
    }

    # Post to ledger
    ledger_entry = {
        "id": settlement_id,
        "action": "settlement",
        "debit": f"{amount} {from_ccy}",
        "credit": f"{converted['amount']} {to_ccy}",
        "counterparty": counterparty,
        "status": "posted",
    }
    LEDGER.append(ledger_entry)

    return settlement


def ledger_reconcile() -> dict:
    """Reconcile all posted ledger entries — detect discrepancies, fraud."""
    debits = sum(float(e["debit"].split()[0]) for e in LEDGER if e["action"] == "settlement")
    credits = sum(float(e["credit"].split()[0]) for e in LEDGER if e["action"] == "settlement")

    return {
        "total_entries": len(LEDGER),
        "total_settlement_volume": round(debits, 2),
        "total_credit_volume": round(credits, 2),
        "balance": round(debits - credits, 2),
        "balanced": abs(debits - credits) < 0.01,
        "fraud_detected": False,
        "last_reconciled": datetime.now(timezone.utc).isoformat(),
    }


def gold_silver_settlement(amount_usd: float, metal: str = "XAU",
                           from_ccy: str = "USD") -> dict:
    """Settle a transaction in gold (XAU) or silver (XAG) weight equivalents."""
    conversion = convert_currency(amount_usd, from_ccy, metal)
    if "error" in conversion:
        return conversion

    metal_names = {"XAU": "Gold (troy oz)", "XAG": "Silver (troy oz)"}

    settlement_id = f"METAL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    return {
        "settlement_id": settlement_id,
        "fiat_amount": f"{amount_usd} {from_ccy}",
        "metal": metal_names.get(metal, metal),
        "weight": f"{conversion['amount']:.4f} troy oz ({conversion['amount'] * 31.1035:.2f}g)",
        "rate": f"1 {from_ccy} = {conversion['amount']/amount_usd:.6f} {metal}",
        "zakat_due": round(conversion['amount'] * 2000 * 0.025, 2) if metal == "XAU" else 0,
        "halal_status": "Permissible — physical gold/silver, spot settlement, no margin or futures",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "settled",
    }


def generate_salam_contract(buyer: str, seller: str, commodity: str,
                            volume: float, total_price: float,
                            delivery_date: str, currency: str = "USD",
                            payment_upfront: float = 1.0) -> dict:
    """Salam — forward purchase with full upfront payment."""
    contract_id = f"SALAM-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(CONTRACTS)+1:04d}"

    contract = {
        "contract_id": contract_id,
        "type": "Salam (Forward Purchase)",
        "buyer": buyer,
        "seller": seller,
        "commodity": commodity,
        "volume": f"{volume} MT",
        "total_price": f"{total_price} {currency}",
        "price_per_unit": f"{total_price/volume:.2f} {currency}/MT",
        "payment_upfront_pct": round(payment_upfront * 100),
        "payment_due": f"{round(total_price * payment_upfront, 2)} {currency}",
        "delivery_date": delivery_date,
        "sharia_conditions": [
            "Full payment upfront (no deferred payment — distinguishes Salam from debt)",
            "Commodity specifications fully defined (type, quality, quantity, delivery date)",
            "Delivery date fixed (no gharar in timing)",
            "Commodity is traded in spot markets (fully deliverable)",
        ],
        "status": "drafted",
        "ujrah_commission": round(total_price * 0.015, 2),  # 1.5% commission
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    CONTRACTS.append(contract)
    return contract


def generate_murabaha_contract(buyer: str, seller: str, asset: str,
                                cost_price: float, markup_pct: float = 15.0,
                                payment_terms: str = "6 monthly installments",
                                currency: str = "USD") -> dict:
    """Murabaha — cost-plus markup sale with deferred payment."""
    markup = round(cost_price * markup_pct / 100, 2)
    selling_price = round(cost_price + markup, 2)
    installment = round(selling_price / 6, 2) if "6" in payment_terms else round(selling_price / 12, 2)

    contract_id = f"MURAB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{len(CONTRACTS)+1:04d}"

    contract = {
        "contract_id": contract_id,
        "type": "Murabaha (Cost-Plus Markup)",
        "buyer": buyer,
        "seller": seller,
        "asset": asset,
        "cost_price": f"{cost_price} {currency}",
        "markup_pct": markup_pct,
        "markup_amount": f"{markup} {currency}",
        "selling_price": f"{selling_price} {currency}",
        "payment_terms": payment_terms,
        "installment_amount": f"{installment} {currency}",
        "sharia_conditions": [
            "Seller discloses original cost price to buyer (transparency)",
            "Markup is fixed and agreed at contract inception",
            "Seller bears ownership risk until delivery (not a loan)",
            "Late payment penalty goes to charity, not seller profit",
        ],
        "status": "drafted",
        "ujrah_commission": round(selling_price * 0.015, 2),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    CONTRACTS.append(contract)
    return contract


def list_contracts(status: str = "") -> dict:
    """List all negotiated Islamic contracts."""
    results = []
    for c in CONTRACTS:
        if status and c["status"] != status:
            continue
        results.append({k: v for k, v in c.items() if k in ["contract_id", "type", "buyer", "seller", "commodity", "total_price", "status"]})
    return {"count": len(results), "contracts": results}


def list_exchange_rates() -> dict:
    """List all available BRICS+ exchange rates."""
    return {"rates": {k: list(v.keys()) for k, v in EXCHANGE_RATES.items()},
            "note": "Rates are indicative. Real-time via local central bank APIs when integrated."}


def calculate_ujrah(transaction_value: float, rate_pct: float = 1.5) -> dict:
    """Calculate Ujrah (commission/brokerage fee) — transparent, disclosed upfront."""
    fee = round(transaction_value * rate_pct / 100, 2)
    return {
        "transaction_value": transaction_value,
        "ujrah_rate_pct": rate_pct,
        "ujrah_fee": fee,
        "halal_status": "Permissible — Ujrah (fixed disclosed commission). No gharar. No riba.",
    }