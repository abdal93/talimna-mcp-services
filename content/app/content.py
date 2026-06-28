# TALIMNA Industrial Content MCP — replaces Content Agency Lite
# Generates trade docs, compliance manuals, technical content for NDB projects

INDUSTRY_TEMPLATES = {
    "trade_document": [
        "Bill of Lading template (FOB/CIF terms)",
        "Commercial Invoice proforma",
        "Packing List with HS code classification",
        "Certificate of Origin template",
        "Shipper's Letter of Instruction",
        "Customs Declaration form guidance",
    ],
    "compliance_manual": {
        "halal_logistics": [
            "Halal Supply Chain Standard Operating Procedure",
            "Segregation Protocol for Halal/Non-Halal goods in transit",
            "Temperature Control Log for refrigerated halal shipments",
            "Cleaning & Sanitization Schedule (cross-contamination prevention)",
        ],
        "trade_compliance": [
            "RCEP Rules of Origin Documentation Guide",
            "BRICS+ Customs Clearance Checklist",
            "Import/Export License Requirements by Country",
            "Anti-Bribery & Transparency Declaration",
        ],
    },
    "project_documentation": [
        "Infrastructure Project Feasibility Report template",
        "Environmental Impact Assessment outline",
        "Stakeholder Communication Plan",
        "Project Milestone & Deliverables Tracker",
    ],
    "ndb_proposal": [
        "NDB Project Concept Note template",
        "Project Preparation Facility request",
        "Safeguard Policy Compliance Statement",
        "Country Systems Assessment framework",
    ],
}

CONTENT_CATALOG = [
    {"id": "ct-001", "title": "Halal Logistics SOP for SEA Trade Routes",
     "type": "Compliance Manual", "price_usd": 299,
     "industries": ["halal_logistics", "logistics", "food_trade"]},
    {"id": "ct-002", "title": "RCEP Tariff Classification Guide",
     "type": "Reference Document", "price_usd": 199,
     "industries": ["trade", "customs", "import_export"]},
    {"id": "ct-003", "title": "NDB Project Concept Note Template Set",
     "type": "Template Bundle", "price_usd": 399,
     "industries": ["infrastructure", "development_finance"]},
    {"id": "ct-004", "title": "BRICS+ Customs Clearance Handbook",
     "type": "Handbook", "price_usd": 149,
     "industries": ["logistics", "customs_brokerage"]},
    {"id": "ct-005", "title": "Halal Supply Chain Audit Checklist",
     "type": "Audit Template", "price_usd": 249,
     "industries": ["halal", "food", "pharma"]},
    {"id": "ct-006", "title": "Cross-Border E-Commerce Compliance Toolkit",
     "type": "Toolkit", "price_usd": 179,
     "industries": ["ecommerce", "trade"]},
]


def generate_technical_doc(doc_type: str = "trade_document",
                           industry: str = "",
                           format: str = "pdf") -> dict:
    """Generate a technical or trade document template."""
    if doc_type in INDUSTRY_TEMPLATES:
        content = INDUSTRY_TEMPLATES[doc_type]
        return {
            "doc_type": doc_type,
            "description": f"{doc_type.replace('_', ' ').title()} template",
            "available_documents": content if isinstance(content, list) else list(content.keys()),
            "format": format,
            "estimated_pages": 5 if isinstance(content, list) else 12,
            "language": "English (multi-language available)",
        }

    if doc_type == "compliance_manual" and industry:
        content = INDUSTRY_TEMPLATES.get("compliance_manual", {}).get(industry)
        if content:
            return {"doc_type": f"compliance_manual/{industry}", "sections": content, "format": format}

    return {"error": f"Unknown doc type: {doc_type}",
            "available": list(INDUSTRY_TEMPLATES.keys())}


def generate_compliance_manual(industry: str = "halal_logistics") -> dict:
    """Generate a compliance manual for a specific industry."""
    return generate_technical_doc(doc_type="compliance_manual", industry=industry)


def list_content_catalog(industry: str = "") -> dict:
    """List available content products for purchase."""
    results = []
    for item in CONTENT_CATALOG:
        if industry and industry not in item["industries"]:
            continue
        results.append(item)
    return {"count": len(results), "catalog": results}


def purchase_content(content_id: str) -> dict:
    """Purchase content from the catalog."""
    item = next((c for c in CONTENT_CATALOG if c["id"] == content_id), None)
    if not item:
        return {"error": f"Content not found: {content_id}"}
    return {
        "title": item["title"],
        "price_usd": item["price_usd"],
        "delivery": "PDF via email / API download",
        "purchase_url": "https://talimna.com/#content",
    }
