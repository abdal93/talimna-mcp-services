# TALIMNA Payment API MCP Server — JSON-RPC 2.0
# Run: python3 -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8007

import json, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.payments import (
    get_payment_link, process_payment, check_payment_status,
    generate_invoice, list_payment_methods, list_services_available,
)

app = FastAPI(title="TALIMNA Payment API MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MCP_TOOLS = {
    "get_payment_link": {
        "description": "Generate a payment link for a service tier",
        "input_schema": {"type": "object", "properties": {
            "service": {"type": "string", "description": "Service name e.g. trade_translation"},
            "tier": {"type": "string", "description": "Pricing tier e.g. volume_monthly"},
            "method": {"type": "string", "enum": ["stripe", "usdc", "usdt", "bank_transfer"], "default": "stripe"},
            "amount": {"type": "number"}, "buyer_email": {"type": "string"},
            "description": {"type": "string"},
        }, "required": ["service", "tier"]},
    },
    "process_payment": {
        "description": "Mark a payment as completed (webhook or manual confirmation)",
        "input_schema": {"type": "object", "properties": {
            "payment_id": {"type": "string"}, "tx_hash": {"type": "string"}, "method": {"type": "string"},
        }, "required": ["payment_id"]},
    },
    "check_payment_status": {
        "description": "Check if a payment has been completed",
        "input_schema": {"type": "object", "properties": {
            "payment_id": {"type": "string"},
        }, "required": ["payment_id"]},
    },
    "generate_invoice": {
        "description": "Generate a halal-compliant invoice for a payment",
        "input_schema": {"type": "object", "properties": {
            "payment_id": {"type": "string"},
        }, "required": ["payment_id"]},
    },
    "list_payment_methods": {
        "description": "List supported payment methods with halal status",
        "input_schema": {"type": "object", "properties": {}},
    },
    "list_services_available": {
        "description": "List all services with pricing tiers",
        "input_schema": {"type": "object", "properties": {}},
    },
}

HANDLERS = {
    "get_payment_link": get_payment_link,
    "process_payment": process_payment,
    "check_payment_status": check_payment_status,
    "generate_invoice": generate_invoice,
    "list_payment_methods": list_payment_methods,
    "list_services_available": list_services_available,
}


@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method", body.get("name", ""))
    params = body.get("params", body.get("arguments", body.get("input", {})))
    req_id = body.get("id", int(time.time() * 1000))

    if method in ("tools/list", "list_tools"):
        return {"jsonrpc": "2.0", "id": req_id, "result": {
            "tools": [{"name": n, **s} for n, s in MCP_TOOLS.items()]}}

    if method in HANDLERS:
        try:
            r = HANDLERS[method](**params) if isinstance(params, dict) else HANDLERS[method](params)
            return {"jsonrpc": "2.0", "id": req_id, "result": {
                "content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


@app.get("/health")
async def health():
    return {"status": "operational", "service": "talimna-payment-api", "version": "1.0.0",
            "mcp_endpoint": "/mcp", "tools": list(HANDLERS.keys()),
            "payment_methods": 4, "services_available": 6}


@app.get("/pay/{service}/{tier}")
async def payment_page(service: str, tier: str, method: str = "stripe"):
    """Simple payment landing page (HTML)."""
    result = get_payment_link(service, tier, method)
    html = f"""<!DOCTYPE html>
<html><head><title>Pay - TALIMNA MCP</title>
<meta name="viewport" content="width=device-width">
<style>body{{font-family:sans-serif;max-width:600px;margin:auto;padding:20px}}
.price{{font-size:2em;color:#2d7d2d}} .btn{{display:block;padding:15px;background:#2d7d2d;
color:white;text-decoration:none;text-align:center;border-radius:8px;margin:20px 0}}
.detail{{color:#666;font-size:0.9em}} .halal{{color:#2d7d2d;font-weight:bold}}</style>
</head><body>
<h2>{result.get('service','Service')}</h2>
<p class="price">${result.get('amount_usd',0):.2f}</p>
<p class="detail">{result.get('tier','')} plan</p>
<p class="halal">✓ Halal — {result.get('halal_gate','')}</p>
<a class="btn" href="{result.get('payment_url','#')}">Pay Now</a>
<p class="detail">{result.get('instructions','')}</p>
<p class="detail">Powered by TALIMNA — BRICS+ Commerce Infrastructure</p>
</body></html>"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)