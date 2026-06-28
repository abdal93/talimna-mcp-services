# TALIMNA Trade Matchmaking MCP Server
# JSON-RPC 2.0 over HTTP
# Replaces: Affiliate Engine + Drop Servicing Brokerage
#
# Run: python3 -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8004

import json
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.matchmaking import (
    find_buyers, find_suppliers, match_score, verify_trade_entity,
    initiate_negotiation, list_trade_corridors, get_trade_leads, list_hubs,
)

app = FastAPI(title="TALIMNA Trade Matchmaking MCP", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MCP_TOOLS = {
    "find_buyers": {
        "description": "Find active buyers in BRICS+ markets by product, country, industry, corridor",
        "input_schema": {
            "type": "object", "properties": {
                "product": {"type": "string"}, "country": {"type": "string"},
                "industry": {"type": "string"}, "corridor": {"type": "string"},
                "min_volume": {"type": "number"}, "limit": {"type": "integer", "default": 20},
            },
        },
    },
    "find_suppliers": {
        "description": "Find verified suppliers in BRICS+ markets with certification filters",
        "input_schema": {
            "type": "object", "properties": {
                "product": {"type": "string"}, "country": {"type": "string"},
                "industry": {"type": "string"}, "corridor": {"type": "string"},
                "cert_required": {"type": "string"}, "limit": {"type": "integer", "default": 20},
            },
        },
    },
    "match_score": {
        "description": "Score compatibility between a supplier and buyer (0-100)",
        "input_schema": {
            "type": "object", "properties": {
                "supplier_id": {"type": "string"}, "buyer_id": {"type": "string"},
            }, "required": ["supplier_id", "buyer_id"],
        },
    },
    "verify_trade_entity": {
        "description": "Verify a trade company's credentials in BRICS+ directory",
        "input_schema": {
            "type": "object", "properties": {
                "company_name": {"type": "string"}, "jurisdiction": {"type": "string"},
            }, "required": ["company_name"],
        },
    },
    "initiate_negotiation": {
        "description": "Create structured negotiation channel between matched buyer and supplier",
        "input_schema": {
            "type": "object", "properties": {
                "match_id": {"type": "string", "default": "auto"},
                "supplier_id": {"type": "string"}, "buyer_id": {"type": "string"},
                "terms_template": {"type": "string", "enum": ["standard"], "default": "standard"},
            }, "required": ["supplier_id", "buyer_id"],
        },
    },
    "list_trade_corridors": {
        "description": "List 8 BRICS+ trade corridors with volume, growth, industries",
        "input_schema": {"type": "object", "properties": {}},
    },
    "get_trade_leads": {
        "description": "Get trade leads filtered by industry, region, or type",
        "input_schema": {
            "type": "object", "properties": {
                "industry": {"type": "string"}, "region": {"type": "string"},
                "lead_type": {"type": "string", "enum": ["buyer", "supplier"]},
                "limit": {"type": "integer", "default": 10},
            },
        },
    },
    "list_hubs": {
        "description": "List major BRICS+ trade hubs with industries and location",
        "input_schema": {
            "type": "object", "properties": {
                "industry": {"type": "string"}, "country": {"type": "string"},
            },
        },
    },
}

HANDLERS = {
    "find_buyers": find_buyers, "find_suppliers": find_suppliers,
    "match_score": match_score, "verify_trade_entity": verify_trade_entity,
    "initiate_negotiation": initiate_negotiation,
    "list_trade_corridors": list_trade_corridors,
    "get_trade_leads": get_trade_leads, "list_hubs": list_hubs,
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
    return {
        "status": "operational", "service": "talimna-trade-matchmaking", "version": "1.0.0",
        "mcp_endpoint": "/mcp", "tools": list(HANDLERS.keys()),
        "trade_corridors": 8, "trade_hubs": 20, "trade_leads": 17,
        "corridors_volume_usd_b": 1715,  # sum of all 8 corridors
    }


@app.get("/mcp/tools")
async def list_tools():
    return {"tools": MCP_TOOLS}