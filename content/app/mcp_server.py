# TALIMNA Industrial Content MCP — JSON-RPC 2.0
# Replaces: Content Agency Lite
# Run: python3 -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8005

import json, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.content import generate_technical_doc, generate_compliance_manual, list_content_catalog, purchase_content

app = FastAPI(title="TALIMNA Industrial Content MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MCP_TOOLS = {
    "generate_technical_doc": {"description": "Generate trade/compliance/NDB document templates",
        "input_schema": {"type": "object", "properties": {
            "doc_type": {"type": "string", "enum": ["trade_document", "compliance_manual", "project_documentation", "ndb_proposal"]},
            "industry": {"type": "string"}, "format": {"type": "string", "default": "pdf"}}}},
    "generate_compliance_manual": {"description": "Generate compliance manual for halal logistics or trade compliance",
        "input_schema": {"type": "object", "properties": {
            "industry": {"type": "string", "enum": ["halal_logistics", "trade_compliance"], "default": "halal_logistics"}}}},
    "list_content_catalog": {"description": "List available content products for purchase",
        "input_schema": {"type": "object", "properties": {"industry": {"type": "string"}}}},
    "purchase_content": {"description": "Purchase content from the catalog",
        "input_schema": {"type": "object", "properties": {"content_id": {"type": "string"}}, "required": ["content_id"]}},
}

HANDLERS = {"generate_technical_doc": generate_technical_doc,
    "generate_compliance_manual": generate_compliance_manual,
    "list_content_catalog": list_content_catalog, "purchase_content": purchase_content}

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
    return {"status": "operational", "service": "talimna-industrial-content", "version": "1.0.0",
            "mcp_endpoint": "/mcp", "tools": list(HANDLERS.keys()), "catalog_items": 6}