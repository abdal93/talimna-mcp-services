# TALIMNA Payment Engine — Stripe + USDC + Bank Transfer
# All prices from pricing.py. MCP server calls this for payment links.

import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Optional

# ─── Payment Methods ───────────────────────────────────────────────────

PAYMENT_METHODS = {
    "stripe": {
        "name": "Stripe (Cards, Apple Pay, Google Pay)",
        "currency": "USD",
        "fee_pct": 2.9 + 0.30,
        "halal_status": "halal — fixed processing fee, no riba",
        "setup_needed": "✅ Already configured on talimna.com",
    },
    "usdc": {
        "name": "USDC (Circle, Ethereum/Polygon/Solana)",
        "currency": "USDC",
        "fee_pct": 0.1,
        "halal_status": "halal — transparent, audited monthly",
        "setup_needed": "🔴 Need to generate wallet address",
        "recommended": True,
        "why": "Fully regulated, monthly Grant Thornton audits, best for BRICS+ cross-border",
    },
    "usdt": {
        "name": "USDT (Tether, Ethereum/Tron)",
        "currency": "USDT",
        "fee_pct": 0.1,
        "halal_status": "acceptable — widely used, but less transparent reserves",
        "setup_needed": "🔴 Need to generate wallet address",
        "note": "Available if buyer prefers. We recommend USDC for transparency.",
    },
    "bank_transfer": {
        "name": "Wire Transfer (International)",
        "currency": "USD / Local",
        "fee_pct": "Varies ($10-50)",
        "halal_status": "halal — bank fees are service charges, not riba",
        "setup_needed": "🟡 Via Mercury bank (already configured)",
        "best_for": "B2B invoices over $1,000",
    },
}


# ─── Service Pricing (sourced from pricing.py) ─────────────────────────

SERVICES = {
    "trade_translation": {
        "name": "Trade Translation MCP",
        "port": 8001,
        "plans": {
            "pay_per_word": {"price": 0.10, "unit": "word", "min": 10},
            "per_document": {"price": 15, "unit": "document", "details": "avg $5-25"},
            "volume_monthly": {"price": 200, "unit": "month", "words": 5000},
            "enterprise": {"price": 500, "unit": "month", "words": 20000},
        },
    },
    "sharia_compliance": {
        "name": "Sharia Compliance MCP",
        "port": 8002,
        "plans": {
            "pay_per_screen": {"price": 0.50, "unit": "screen", "min": 10},
            "starter_monthly": {"price": 99, "unit": "month", "screens": 500},
            "business_monthly": {"price": 299, "unit": "month", "screens": 2500},
            "enterprise": {"price": 999, "unit": "month", "screens": 10000},
        },
    },
    "trade_matchmaking": {
        "name": "Trade Matchmaking MCP",
        "port": 8004,
        "plans": {
            "per_match": {"price": 50, "unit": "match"},
            "starter_monthly": {"price": 99, "unit": "month", "matches": 10},
            "business_monthly": {"price": 299, "unit": "month", "matches": 50},
            "enterprise": {"price": 999, "unit": "month", "matches": -1},
        },
    },
    "trade_intelligence": {
        "name": "Trade Intelligence MCP",
        "port": 8003,
        "plans": {
            "data_monthly": {"price": 199, "unit": "month"},
            "api_access": {"price": 499, "unit": "month"},
        },
    },
    "industrial_content": {
        "name": "Industrial Content MCP",
        "port": 8005,
        "plans": {
            "content_monthly": {"price": 199, "unit": "month", "docs": 5},
        },
    },
    "logistics_dispatch": {
        "name": "Logistics Dispatch MCP",
        "port": 8000,
        "plans": {
            "per_dispatch": {"price": 2, "unit": "dispatch", "min": 50},
            "starter_monthly": {"price": 99, "unit": "month", "dispatches": 100},
            "business_monthly": {"price": 299, "unit": "month", "dispatches": 500},
            "enterprise": {"price": 999, "unit": "month", "dispatches": -1},
        },
    },
}

# ─── Payment Record Store ─────────────────────────────────────────────

PAYMENTS = {}  # In-memory. In production, use PostgreSQL.
INVOICES = {}


def _generate_id(prefix: str = "pay") -> str:
    ts = int(time.time() * 1000)
    h = hashlib.md5(str(ts).encode()).hexdigest()[:8]
    return f"{prefix}_{ts}_{h}"


def get_payment_link(service: str, tier: str,
                     method: str = "stripe",
                     amount: float = None,
                     buyer_email: str = "",
                     description: str = "") -> dict:
    """Generate a payment link for a service tier."""
    # Find the service
    svc = SERVICES.get(service)
    if not svc:
        return {"error": f"Service not found: {service}",
                "available": list(SERVICES.keys())}

    # Find the plan
    plan = svc["plans"].get(tier)
    if not plan:
        return {"error": f"Tier not found: {tier} for {service}",
                "available_tiers": list(svc["plans"].keys())}

    # Check payment method
    pm = PAYMENT_METHODS.get(method)
    if not pm:
        return {"error": f"Payment method not supported: {method}",
                "available": list(PAYMENT_METHODS.keys())}

    price = amount if amount else plan["price"]
    unit = plan.get("unit", "unit")

    pay_id = _generate_id()
    payment = {
        "id": pay_id,
        "service": svc["name"],
        "tier": tier,
        "amount_usd": price,
        "payment_method": pm["name"],
        "unit": unit,
        "description": description or f"{svc['name']} - {tier}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "buyer_email": buyer_email,
    }

    # Generate payment URLs based on method
    if method == "stripe":
        payment["payment_url"] = f"https://buy.stripe.com/test_{pay_id}"
        payment["instructions"] = "Pay via card, Apple Pay, or Google Pay"
    elif method in ("usdc", "usdt"):
        payment["payment_url"] = f"https://talimna.com/pay/{pay_id}"
        wallet = "CESJmirHhG9Vh2Wd7BXzQTiFcP86YyQvTJdawW4WUDxW"
        payment["wallet_address"] = wallet
        payment["instructions"] = f"Send {price} USDC (Solana) to: {wallet}"
    elif method == "bank_transfer":
        payment["payment_url"] = f"https://talimna.com/invoice/{pay_id}"
        payment["instructions"] = "Wire to Mercury bank account. Details on invoice."

    payment["halal_gate"] = pm["halal_status"]

    PAYMENTS[pay_id] = payment
    return payment


def process_payment(payment_id: str, tx_hash: str = "",
                    method: str = "") -> dict:
    """Mark a payment as completed (called by webhook or manually)."""
    payment = PAYMENTS.get(payment_id)
    if not payment:
        return {"error": f"Payment not found: {payment_id}"}

    payment["status"] = "completed"
    payment["completed_at"] = datetime.now(timezone.utc).isoformat()
    payment["tx_hash"] = tx_hash or f"manual_{_generate_id()}"

    # Generate invoice
    inv_id = _generate_id("inv")
    invoice = generate_invoice(payment_id)
    INVOICES[inv_id] = invoice

    return {
        "status": "completed",
        "payment": payment,
        "invoice": invoice,
        "access": f"API key for {payment['service']} sent to {payment['buyer_email'] or 'pending'}"
    }


def check_payment_status(payment_id: str) -> dict:
    """Check if a payment has been completed."""
    payment = PAYMENTS.get(payment_id)
    if not payment:
        return {"error": f"Payment not found: {payment_id}"}
    return {
        "id": payment["id"],
        "service": payment["service"],
        "tier": payment["tier"],
        "amount_usd": payment["amount_usd"],
        "status": payment["status"],
        "created_at": payment["created_at"],
    }


def generate_invoice(payment_id: str) -> dict:
    """Generate a halal-compliant invoice for a payment."""
    payment = PAYMENTS.get(payment_id)
    if not payment:
        return {"error": f"Payment not found: {payment_id}"}

    inv_id = _generate_id("inv")
    invoice = {
        "invoice_id": inv_id,
        "payment_id": payment_id,
        "date": datetime.now(timezone.utc).isoformat(),
        "seller": {
            "name": "TALIMNA",
            "ceo": "Arya Wang",
            "contact": "arya.wang@talimna.com",
        },
        "buyer": {
            "email": payment.get("buyer_email", "TBD"),
        },
        "service": payment["service"],
        "tier": payment["tier"],
        "amount_usd": payment["amount_usd"],
        "payment_method": payment["payment_method"],
        "status": payment["status"],
        "halal_compliance": {
            "contract_type": "Ijara (service lease) / Bai' (sale) / Ju'ala (commission)",
            "riba": "None — fixed price, no interest",
            "gharar": "None — transparent scope and deliverables",
            "maysir": "None — no speculation",
            "zakat": "2.5% auto-calculated on profit",
        },
        "notes": "This invoice is Sharia-compliant. Payment is for services rendered at fixed agreed price.",
    }
    return invoice


def list_payment_methods() -> dict:
    """List all payment methods with details."""
    return {"methods": PAYMENT_METHODS,
            "recommended": "usdc",
            "why_usdc": "Fully regulated, monthly audits, transparent. Best for BRICS+ cross-border trade."}


def list_services_available() -> dict:
    """List all services and their pricing tiers."""
    result = {}
    for sid, svc in SERVICES.items():
        result[sid] = {
            "name": svc["name"],
            "port": svc["port"],
            "plans": {tier: info for tier, info in svc["plans"].items()},
        }
    return {"services": result}