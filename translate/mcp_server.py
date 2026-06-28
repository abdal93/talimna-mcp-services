# TALIMNA Trade Translation MCP Server
# JSON-RPC 2.0 over HTTP
#
# Exposes translation tools via MCP protocol for any MCP client (Hermes, Claude, Cursor)
#
# MCP endpoints:
#   translate_doc       — Translate trade document text
#   batch_translate     — Multi-entry translation
#   detect_language     — Language detection
#   list_languages      — All 33 BRICS+ supported languages
#   translate_trade_doc — Full pipeline: translate + extract fields
#   list_doc_types      — Trade doc types with extractable fields
#
# Run: uvicorn app.mcp_server:app --host 0.0.0.0 --port 8001

import json
import time
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.translator import (
    translate, batch_translate, detect_language, list_languages,
    translate_trade_doc, list_doc_types, LANGUAGES
)

app = FastAPI(title="TALIMNA Trade Translation MCP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── MCP Tool Registry ────────────────────────────────────────────────

MCP_TOOLS = {
    "translate_doc": {
        "description": "Translate text between BRICS+ languages",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to translate"},
                "source": {"type": "string", "description": "Source language code (e.g. 'en', 'zh-cn')", "default": "auto"},
                "target": {"type": "string", "description": "Target language code (e.g. 'ms', 'ar')"},
            },
            "required": ["text", "target"],
        },
    },
    "batch_translate": {
        "description": "Translate multiple texts in one call",
        "input_schema": {
            "type": "object",
            "properties": {
                "entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "source": {"type": "string", "default": "auto"},
                            "target": {"type": "string"},
                        },
                        "required": ["text", "target"],
                    },
                },
            },
            "required": ["entries"],
        },
    },
    "detect_language": {
        "description": "Detect language of input text",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to detect language of"},
            },
            "required": ["text"],
        },
    },
    "list_languages": {
        "description": "List all 33 supported BRICS+ languages",
        "input_schema": {"type": "object", "properties": {}},
    },
    "translate_trade_doc": {
        "description": "Full pipeline: translate + extract trade document fields",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "source": {"type": "string", "default": "auto"},
                "target": {"type": "string"},
                "doc_type": {
                    "type": "string",
                    "enum": ["bill_of_lading", "invoice", "customs_declaration",
                             "cert_of_origin", "contract"],
                    "description": "Type of trade document for field extraction",
                },
            },
            "required": ["text", "target"],
        },
    },
    "list_doc_types": {
        "description": "List supported trade document types with extractable fields",
        "input_schema": {"type": "object", "properties": {}},
    },
}

# ─── MCP JSON-RPC Handler ─────────────────────────────────────────────

TOOL_HANDLERS = {
    "translate_doc": lambda args: translate(
        args.get("text", ""),
        args.get("source", "auto"),
        args["target"],
    ),
    "batch_translate": lambda args: batch_translate(args.get("entries", [])),
    "detect_language": lambda args: detect_language(args.get("text", "")),
    "list_languages": lambda args: list_languages(),
    "translate_trade_doc": lambda args: translate_trade_doc(
        args.get("text", ""),
        args.get("source", "auto"),
        args["target"],
        args.get("doc_type"),
    ),
    "list_doc_types": lambda args: list_doc_types(),
}


@app.post("/mcp")
async def mcp_handler(request: Request):
    """MCP JSON-RPC 2.0 endpoint."""
    body = await request.json()

    method = body.get("method", body.get("name", ""))
    params = body.get("params", body.get("arguments", body.get("input", {})))
    req_id = body.get("id", int(time.time() * 1000))

    # MCP tool list request
    if method in ("tools/list", "list_tools"):
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {"name": name, **schema}
                    for name, schema in MCP_TOOLS.items()
                ],
            },
        }

    # MCP tool call
    if method in TOOL_HANDLERS:
        try:
            result = TOOL_HANDLERS[method](params)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)},
            }

    # MCP resources/list
    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": [
                    {"uri": "mcp://talimna-translate/languages",
                     "name": "Supported Languages",
                     "description": f"{len(LANGUAGES)} BRICS+ languages"},
                    {"uri": "mcp://talimna-translate/doc-types",
                     "name": "Trade Document Types",
                     "description": "5 trade doc types with field extraction"},
                ],
            },
        }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


# ─── REST Health / Info ──────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "operational",
        "service": "talimna-trade-translation",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "languages": len(LANGUAGES),
        "doc_types": list(list_doc_types()["doc_types"].keys()),
        "backend": "google_translate (swap path: NLLB-200)",
    }


@app.get("/mcp/tools")
async def list_tools():
    """Human-readable tool listing."""
    return {"tools": MCP_TOOLS}
