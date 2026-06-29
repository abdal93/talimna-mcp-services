# TALIMNA Al-Jalib MCP Server — JSON-RPC 2.0
# Trans-South Commercial & Logistical Corridor
# Run: python3 -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8008

import json, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.corridor import (
    load_cargo_manifest, audit_halal_supply_chain, generate_bill_of_lading,
    trigger_freight_dispatch, customs_clearance, list_active_shipments,
    CARGO_MANIFESTS, BILLS_OF_LADING,
)

app = FastAPI(title="Al-Jalib Trans-South Corridor MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MCP_TOOLS = {
    "load_cargo_manifest": {"description": "Ingest cargo manifest — auto-screens halal, matches routes",
        "input_schema": {"type": "object", "properties": {
            "cargo_type": {"type": "string", "enum": ["dates", "coconut", "durum_wheat", "rice", "lentils", "soybeans", "sheep", "goats", "chicken", "honey", "fish"]},
            "volume": {"type": "number"}, "origin": {"type": "string"},
            "destination": {"type": "string"}, "seller": {"type": "string"},
            "buyer": {"type": "string"}, "cert_required": {"type": "string"},
        }, "required": ["cargo_type", "volume", "origin", "destination"]}},
    "audit_halal_supply_chain": {"description": "Bay' al-Musawamah — audit halal compliance of supply chain",
        "input_schema": {"type": "object", "properties": {
            "manifest_id": {"type": "string"}, "cargo_type": {"type": "string"},
        }}},
    "generate_bill_of_lading": {"description": "Autonomously draft Bill of Lading from manifest",
        "input_schema": {"type": "object", "properties": {
            "manifest_id": {"type": "string"}, "consignee": {"type": "string"},
            "notify_party": {"type": "string"}, "payment_terms": {"type": "string", "default": "LC at sight"},
        }, "required": ["manifest_id"]}},
    "trigger_freight_dispatch": {"description": "Trigger physical transport — dispatch to carrier",
        "input_schema": {"type": "object", "properties": {
            "bl_number": {"type": "string"}, "carrier": {"type": "string", "default": "MAERSK"},
        }, "required": ["bl_number"]}},
    "customs_clearance": {"description": "Simulate customs clearance filing for BRICS+ portals",
        "input_schema": {"type": "object", "properties": {
            "manifest_id": {"type": "string"}, "country": {"type": "string"},
        }, "required": ["manifest_id"]}},
    "list_active_shipments": {"description": "List all cargo shipments in corridor pipeline",
        "input_schema": {"type": "object", "properties": {
            "status": {"type": "string"},
        }}},
}

HANDLERS = {
    "load_cargo_manifest": lambda p: load_cargo_manifest(**{k: p.get(k) for k in ["cargo_type", "volume", "origin", "destination", "seller", "buyer", "cert_required"] if p.get(k)}),
    "audit_halal_supply_chain": lambda p: audit_halal_supply_chain(p.get("manifest_id", ""), p.get("cargo_type", "")),
    "generate_bill_of_lading": lambda p: generate_bill_of_lading(p["manifest_id"], p.get("consignee", ""), p.get("notify_party", ""), p.get("payment_terms", "LC at sight")),
    "trigger_freight_dispatch": lambda p: trigger_freight_dispatch(p["bl_number"], p.get("carrier", "MAERSK")),
    "customs_clearance": lambda p: customs_clearance(p["manifest_id"], p.get("country", "")),
    "list_active_shipments": lambda p: list_active_shipments(p.get("status", "")),
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
    return {"status": "operational", "service": "al-jalib-corridor", "version": "1.0.0",
            "tools": list(MCP_TOOLS.keys()), "cargo_types": 5, "sea_routes": 6,
            "pipeline": f"{len(CARGO_MANIFESTS)} manifests, {len(BILLS_OF_LADING)} BLs",
            "integrates": ["Logistics :8000", "Matchmaking :8004", "Translation :8001"]}