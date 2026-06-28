# TALIMNA Digital Commerce MCP — JSON-RPC 2.0
# Replaces: Digital Products & POD
# Run: python3 -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8006

import json, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.commerce import list_products, process_order, manage_license

app = FastAPI(title="TALIMNA Digital Commerce MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MCP_TOOLS = {
    "list_products": {"description": "List digital products by category",
        "input_schema": {"type": "object", "properties": {
            "category": {"type": "string", "enum": ["trade_tools", "trade_compliance", "ai_tools", "islamic_content", "islamic_finance", "project_finance"]}}}},
    "process_order": {"description": "Purchase a digital product",
        "input_schema": {"type": "object", "properties": {
            "product_id": {"type": "string"}, "buyer_email": {"type": "string"},
            "payment_method": {"type": "string", "default": "stripe"}},
            "required": ["product_id"]}},
    "manage_license": {"description": "Manage product license for commercial use",
        "input_schema": {"type": "object", "properties": {
            "product_id": {"type": "string"}, "action": {"type": "string", "default": "info"},
            "licensee": {"type": "string"}}, "required": ["product_id"]}},
}

HANDLERS = {"list_products": list_products, "process_order": process_order, "manage_license": manage_license}

@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json(); method = body.get("method", body.get("name", ""))
    params = body.get("params", body.get("arguments", body.get("input", {})))
    req_id = body.get("id", int(time.time() * 1000))
    if method in ("tools/list", "list_tools"):
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": [{"name": n, **s} for n, s in MCP_TOOLS.items()]}}
    if method in HANDLERS:
        try:
            r = HANDLERS[method](**params) if isinstance(params, dict) else HANDLERS[method](params)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(r, ensure_ascii=False)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

@app.get("/health")
async def health():
    return {"status": "operational", "service": "talimna-digital-commerce", "version": "1.0.0",
            "mcp_endpoint": "/mcp", "tools": list(HANDLERS.keys()), "products_count": 8}