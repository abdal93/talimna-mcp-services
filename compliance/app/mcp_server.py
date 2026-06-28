# TALIMNA Sharia Compliance MCP Server
# JSON-RPC 2.0 over HTTP
#
# MCP tools:
#   screen_transaction    — Sharia compliance check for a transaction
#   calculate_zakat       — Calculate zakat on assets (2.5%, nisab check)
#   detect_riba           — Detect riba/gharar clauses in contract text
#   check_sector          — Check if a business sector is halal
#   generate_sharia_report— Full compliance report
#
# Run: python3 -m uvicorn app.mcp_server:app --host 0.0.0.0 --port 8002

import json
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.compliance import (
    screen_transaction, calculate_zakat, detect_riba,
    check_sector, generate_sharia_report,
)
from app.halal_certs import (
    verify_halal_cert, list_cert_bodies, check_batch_lot,
    trace_ingredient, get_cert_body_requirements, watch_supplier,
)

app = FastAPI(title="TALIMNA Sharia Compliance MCP", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── MCP Tool Registry ────────────────────────────────────────────────

MCP_TOOLS = {
    "screen_transaction": {
        "description": "Screen a financial transaction for Sharia compliance",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Transaction amount"},
                "currency": {"type": "string", "description": "Currency code (e.g. USD, AED, MYR)", "default": "USD"},
                "counterparty": {"type": "string", "description": "Counterparty name for screening"},
                "sector": {"type": "string", "description": "Business sector"},
                "purpose": {"type": "string", "description": "Transaction purpose"},
                "jurisdiction": {"type": "string", "description": "Country/jurisdiction"},
            },
            "required": ["amount"],
        },
    },
    "calculate_zakat": {
        "description": "Calculate zakat obligation (2.5%) on assets with nisab threshold check",
        "input_schema": {
            "type": "object",
            "properties": {
                "assets": {"type": "object", "description": "Asset breakdown",
                    "properties": {
                        "cash": {"type": "number"}, "gold_grams": {"type": "number"},
                        "silver_grams": {"type": "number"}, "business_inventory": {"type": "number"},
                        "accounts_receivable": {"type": "number"}, "investment_value": {"type": "number"},
                        "accounts_payable": {"type": "number"},
                    }},
                "hawl_complete": {"type": "boolean", "default": True},
            }, "required": ["assets"]},
    },
    "detect_riba": {
        "description": "Scan contract/document text for riba (interest) and gharar (uncertainty) clauses",
        "input_schema": {"type": "object", "properties": {
            "text": {"type": "string", "description": "Contract text to scan"},
        }, "required": ["text"]},
    },
    "check_sector": {
        "description": "Check if a business sector is halal, haram, or mashbuh",
        "input_schema": {"type": "object", "properties": {
            "sector": {"type": "string", "description": "Sector name"},
        }, "required": ["sector"]},
    },
    "generate_sharia_report": {
        "description": "Generate comprehensive Sharia compliance report",
        "input_schema": {"type": "object", "properties": {
            "transactions": {"type": "array", "items": {"type": "object"}},
            "contract_text": {"type": "string"},
            "portfolio_value": {"type": "number"},
            "include_zakat": {"type": "boolean", "default": True},
        }},
    },
    "verify_halal_cert": {
        "description": "Verify a halal certificate against real cert body data (JAKIM, BPJPH, ESMA, SFDA, MUIS, CICOT, etc.)",
        "input_schema": {"type": "object", "properties": {
            "cert_number": {"type": "string", "description": "Certificate number"},
            "company": {"type": "string", "description": "Company name"},
            "cert_body": {"type": "string", "description": "Cert body code (jakim, bpjph, mui, esma, sfda, muis, cicot)"},
        }},
    },
    "list_cert_bodies": {
        "description": "List all halal certification bodies with recognition levels and standards",
        "input_schema": {"type": "object", "properties": {
            "country": {"type": "string", "description": "Filter by country"},
        }},
    },
    "check_batch_lot": {
        "description": "Check a batch/lot number against halal cert records for traceability",
        "input_schema": {"type": "object", "properties": {
            "lot_number": {"type": "string"}, "product_category": {"type": "string"},
            "cert_body": {"type": "string"}, "origin_country": {"type": "string"},
        }, "required": ["lot_number"]},
    },
    "trace_ingredient": {
        "description": "Trace an ingredient through halal supply chain (recursive)",
        "input_schema": {"type": "object", "properties": {
            "sku": {"type": "string"}, "ingredient": {"type": "string"},
            "depth": {"type": "integer", "default": 3},
        }},
    },
    "get_cert_body_requirements": {
        "description": "Get halal certification requirements for a specific body",
        "input_schema": {"type": "object", "properties": {
            "body_id": {"type": "string", "description": "Cert body code (jakim, bpjph, esma, etc.)"},
        }},
    },
    "watch_supplier": {
        "description": "Set up tracking for cert status changes on a supplier",
        "input_schema": {"type": "object", "properties": {
            "company_name": {"type": "string"}, "callback_url": {"type": "string"},
        }, "required": ["company_name"]},
    },
}

TOOL_HANDLERS = {
    "screen_transaction": lambda args: screen_transaction(
        amount=args.get("amount", 0),
        currency=args.get("currency", "USD"),
        counterparty=args.get("counterparty", ""),
        sector=args.get("sector", ""),
        purpose=args.get("purpose", ""),
        jurisdiction=args.get("jurisdiction", ""),
    ),
    "calculate_zakat": lambda args: calculate_zakat(
        assets=args.get("assets", {}),
        hawl_complete=args.get("hawl_complete", True),
    ),
    "detect_riba": lambda args: detect_riba(text=args.get("text", "")),
    "check_sector": lambda args: check_sector(sector=args.get("sector", "")),
    "generate_sharia_report": lambda args: generate_sharia_report(
        transactions=args.get("transactions"),
        contract_text=args.get("contract_text"),
        portfolio_value=args.get("portfolio_value", 0),
        include_zakat=args.get("include_zakat", True),
    ),
    "verify_halal_cert": lambda args: verify_halal_cert(
        cert_number=args.get("cert_number", ""),
        company=args.get("company", ""),
        cert_body=args.get("cert_body", ""),
    ),
    "list_cert_bodies": lambda args: list_cert_bodies(country=args.get("country", "")),
    "check_batch_lot": lambda args: check_batch_lot(
        lot_number=args.get("lot_number", ""),
        product_category=args.get("product_category", ""),
        cert_body=args.get("cert_body", ""),
        origin_country=args.get("origin_country", ""),
    ),
    "trace_ingredient": lambda args: trace_ingredient(
        sku=args.get("sku", ""),
        ingredient=args.get("ingredient", ""),
        depth=args.get("depth", 3),
    ),
    "get_cert_body_requirements": lambda args: get_cert_body_requirements(body_id=args.get("body_id", "")),
    "watch_supplier": lambda args: watch_supplier(
        company_name=args.get("company_name", ""),
        callback_url=args.get("callback_url", ""),
    ),
}


@app.post("/mcp")
async def mcp_handler(request: Request):
    body = await request.json()
    method = body.get("method", body.get("name", ""))
    params = body.get("params", body.get("arguments", body.get("input", {})))
    req_id = body.get("id", int(time.time() * 1000))

    if method in ("tools/list", "list_tools"):
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "tools": [{"name": name, **schema} for name, schema in MCP_TOOLS.items()],
            },
        }

    if method in TOOL_HANDLERS:
        try:
            result = TOOL_HANDLERS[method](params)
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]},
            }
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


@app.get("/health")
async def health():
    return {
        "status": "operational",
        "service": "talimna-sharia-compliance",
        "version": "2.0.0",
        "mcp_endpoint": "/mcp",
        "halal_tools": 6,
        "total_tools": len(MCP_TOOLS),
        "cert_bodies": 8,
        "certified_companies": 14,
        "references": [
            "Al-Usul Ath-Thalatha", "Kitab At-Tawhid", "Quran 2:275-279",
            "JAKIM MS 1500:2019", "BPJPH HAS 23000", "ESMA UAE.S 5011:2022",
            "SFDA SASO 2178:2022", "MUIS HC-S", "CICOT Thai Halal Standard",
        ],
    }


@app.get("/mcp/tools")
async def list_tools():
    return {"tools": MCP_TOOLS}
