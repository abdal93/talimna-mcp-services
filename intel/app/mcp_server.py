# TALIMNA Trade Intelligence MCP Server
# JSON-RPC 2.0 over HTTP
# Replaces: Data Intelligence Service
# Run: python3 -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8003

import json, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.intelligence import (
    query_trade_volume, get_market_intel, verify_supplier_background,
    monitor_trade_flow, list_datasets, purchase_dataset,
)

app = FastAPI(title="TALIMNA Trade Intelligence MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MCP_TOOLS = {
    "query_trade_volume": {"description": "Get trade volume data for BRICS+ corridors",
        "input_schema": {"type": "object", "properties": {
            "corridor_id": {"type": "string", "description": "Corridor ID (e.g. china_asean)"},
            "period": {"type": "string", "default": "latest"}}}},
    "get_market_intel": {"description": "AI-synthesized market intelligence for BRICS+ corridors",
        "input_schema": {"type": "object", "properties": {
            "corridor": {"type": "string"}, "industry": {"type": "string"}, "country": {"type": "string"}}}},
    "verify_supplier_background": {"description": "Background check on trade suppliers",
        "input_schema": {"type": "object", "properties": {
            "company_name": {"type": "string"}, "jurisdiction": {"type": "string"}},
            "required": ["company_name"]}},
    "monitor_trade_flow": {"description": "Monitor corridor activity with alerts",
        "input_schema": {"type": "object", "properties": {
            "corridor": {"type": "string"}, "days": {"type": "integer", "default": 7}}}},
    "list_datasets": {"description": "Available trade intelligence datasets for purchase",
        "input_schema": {"type": "object", "properties": {
            "industry": {"type": "string"}, "max_price": {"type": "number"}}}},
    "purchase_dataset": {"description": "Purchase a trade intelligence dataset",
        "input_schema": {"type": "object", "properties": {
            "dataset_id": {"type": "string"}, "buyer_email": {"type": "string"}},
            "required": ["dataset_id"]}},
}

HANDLERS = {
    "query_trade_volume": query_trade_volume,
    "get_market_intel": get_market_intel,
    "verify_supplier_background": verify_supplier_background,
    "monitor_trade_flow": monitor_trade_flow,
    "list_datasets": list_datasets,
    "purchase_dataset": purchase_dataset,
}


@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method", body.get("name", ""))
    params = body.get("params", body.get("arguments", body.get("input", {})))
    req_id = body.get("id", int(time.time() * 1000))
    if method in ("tools/list", "list_tools"):
        return {"jsonrpc": "2.0", "id": req_id, "result": {
            "tools": [{"name": name, **schema} for name, schema in MCP_TOOLS.items()]}}
    if method in HANDLERS:
        try:
            result = HANDLERS[method](**params) if isinstance(params, dict) else HANDLERS[method](params)
            return {"jsonrpc": "2.0", "id": req_id, "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


@app.get("/health")
async def health():
    return {"status": "operational", "service": "talimna-trade-intelligence", "version": "1.0.0",
            "mcp_endpoint": "/mcp", "tools": list(HANDLERS.keys()),
            "trade_corridors": len([k for k in ["china_asean_2026_q1","india_sea_2026_q1","uae_sea_2026_q1","china_russia_2026_q1","russia_india_2026_q1","china_brazil_2026_q1"]]),
            "datasets_available": 7}