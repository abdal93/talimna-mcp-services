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

app = FastAPI(title="TALIMNA Sharia Compliance MCP", version="1.0.0")

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
                "sector": {"type": "string", "description": "Business sector (e.g. 'agriculture', 'logistics', 'finance')"},
                "purpose": {"type": "string", "description": "Transaction purpose description"},
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
                "assets": {
                    "type": "object",
                    "description": "Asset breakdown",
                    "properties": {
                        "cash": {"type": "number", "description": "Cash in bank/on hand (USD)"},
                        "gold_grams": {"type": "number", "description": "Gold held in grams"},
                        "silver_grams": {"type": "number", "description": "Silver held in grams"},
                        "business_inventory": {"type": "number", "description": "Trade goods value (USD)"},
                        "accounts_receivable": {"type": "number", "description": "Money owed to you (USD)"},
                        "investment_value": {"type": "number", "description": "Halal investments (USD)"},
                        "accounts_payable": {"type": "number", "description": "Debts you owe (USD)"},
                    },
                },
                "hawl_complete": {"type": "boolean", "description": "Has one lunar year passed?", "default": True},
            },
            "required": ["assets"],
        },
    },
    "detect_riba": {
        "description": "Scan contract/document text for riba (interest) and gharar (uncertainty) clauses",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Contract or document text to scan"},
            },
            "required": ["text"],
        },
    },
    "check_sector": {
        "description": "Check if a business sector is halal, haram, or mashbuh",
        "input_schema": {
            "type": "object",
            "properties": {
                "sector": {"type": "string", "description": "Sector name (e.g. 'logistics', 'alcohol', 'gambling')"},
            },
            "required": ["sector"],
        },
    },
    "generate_sharia_report": {
        "description": "Generate comprehensive Sharia compliance report with transactions, contract review, and zakat",
        "input_schema": {
            "type": "object",
            "properties": {
                "transactions": {
                    "type": "array",
                    "description": "List of transactions to screen",
                    "items": {"type": "object"},
                },
                "contract_text": {"type": "string", "description": "Contract text to review"},
                "portfolio_value": {"type": "number", "description": "Total portfolio value for zakat calculation"},
                "include_zakat": {"type": "boolean", "description": "Include zakat calculation", "default": True},
            },
        },
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
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "tools": list(MCP_TOOLS.keys()),
        "references": ["Al-Usul Ath-Thalatha", "Kitab At-Tawhid", "Quran 2:275-279"],
    }


@app.get("/mcp/tools")
async def list_tools():
    return {"tools": MCP_TOOLS}
