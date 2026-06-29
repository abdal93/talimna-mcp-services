# TALIMNA Simsarah MCP Server — JSON-RPC 2.0
# Decentralized Clearing & Autonomous FinTech Protocol
# Run: python3 -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8009

import json, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.clearing import (
    convert_currency, settle_transaction, ledger_reconcile,
    gold_silver_settlement, generate_salam_contract, generate_murabaha_contract,
    list_contracts, list_exchange_rates, calculate_ujrah,
)

app = FastAPI(title="Simsarah Clearing Protocol MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MCP_TOOLS = {
    "convert_currency": {"description": "Convert between BRICS+ local currencies and gold/silver",
        "input_schema": {"type": "object", "properties": {
            "amount": {"type": "number"}, "from_ccy": {"type": "string"},
            "to_ccy": {"type": "string"}}, "required": ["amount", "from_ccy", "to_ccy"]}},
    "settle_transaction": {"description": "Net settlement between counterparties — no SWIFT, no USD",
        "input_schema": {"type": "object", "properties": {
            "amount": {"type": "number"}, "currency": {"type": "string"},
            "counterparty": {"type": "string"},
            "settlement_method": {"type": "string", "enum": ["a2a_bank", "crypto_usdc", "gold_silver"]},
            "purpose": {"type": "string"}, "counterparty_currency": {"type": "string"}},
            "required": ["amount", "currency", "counterparty"]}},
    "gold_silver_settlement": {"description": "Settle in gold (XAU) or silver (XAG) weight equivalents",
        "input_schema": {"type": "object", "properties": {
            "amount_usd": {"type": "number"}, "metal": {"type": "string", "enum": ["XAU", "XAG"]},
            "from_ccy": {"type": "string", "default": "USD"}},
            "required": ["amount_usd"]}},
    "ledger_reconcile": {"description": "Reconcile ledger — detect discrepancies and fraud",
        "input_schema": {"type": "object", "properties": {}}},
    "generate_salam_contract": {"description": "Salam — forward purchase with full upfront payment",
        "input_schema": {"type": "object", "properties": {
            "buyer": {"type": "string"}, "seller": {"type": "string"},
            "commodity": {"type": "string"}, "volume": {"type": "number"},
            "total_price": {"type": "number"}, "delivery_date": {"type": "string"},
            "currency": {"type": "string", "default": "USD"}},
            "required": ["buyer", "seller", "commodity", "volume", "total_price", "delivery_date"]}},
    "generate_murabaha_contract": {"description": "Murabaha — cost-plus markup sale with deferred payment",
        "input_schema": {"type": "object", "properties": {
            "buyer": {"type": "string"}, "seller": {"type": "string"},
            "asset": {"type": "string"}, "cost_price": {"type": "number"},
            "markup_pct": {"type": "number", "default": 15},
            "payment_terms": {"type": "string", "default": "6 monthly installments"},
            "currency": {"type": "string", "default": "USD"}},
            "required": ["buyer", "seller", "asset", "cost_price"]}},
    "list_contracts": {"description": "List all negotiated Islamic contracts",
        "input_schema": {"type": "object", "properties": {"status": {"type": "string"}}}},
    "calc_ujrah": {"description": "Calculate Ujrah commission — transparent, disclosed upfront",
        "input_schema": {"type": "object", "properties": {
            "transaction_value": {"type": "number"}, "rate_pct": {"type": "number", "default": 1.5}},
            "required": ["transaction_value"]}},
}

HANDLERS = {"convert_currency": lambda p: convert_currency(**p),
    "settle_transaction": lambda p: settle_transaction(**p),
    "gold_silver_settlement": lambda p: gold_silver_settlement(**p),
    "ledger_reconcile": lambda p: ledger_reconcile(),
    "generate_salam_contract": lambda p: generate_salam_contract(**p),
    "generate_murabaha_contract": lambda p: generate_murabaha_contract(**p),
    "list_contracts": lambda p: list_contracts(p.get("status", "")),
    "calc_ujrah": lambda p: calculate_ujrah(**p),
}

@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method", body.get("name", ""))
    params = body.get("params", body.get("arguments", body.get("input", {})))
    req_id = body.get("id", int(time.time() * 1000))
    if method in ("tools/list", "list_tools"):
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": [{"name": n, **s} for n,s in MCP_TOOLS.items()]}}
    if method in HANDLERS:
        try:
            r = HANDLERS[method](params)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

@app.get("/health")
async def health():
    return {"status": "operational", "service": "simsarah-clearing", "version": "1.0.0",
            "tools": list(MCP_TOOLS.keys()), "contract_count": 0,
            "currencies": list(EXCHANGE_RATES.keys()) if 'EXCHANGE_RATES' in dir() else 13,
            "integrates": ["Compliance :8002", "Payment :8007"]}