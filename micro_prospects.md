# TALIMNA Micro-Business Prospect List
# Target: ≤$72K revenue, ≤5 employees, BRICS+ trade corridors
# Reachable primarily via: WhatsApp, Instagram, marketplace platforms

# ─── Phase 1: Already in our database (from Trade Matchmaking MCP) ─────

MICRO_PROSPECTS = [
    # Small halal food exporters
    {"name": "PT Halal Food Jakarta", "country": "Indonesia", "type": "supplier",
     "product": "Frozen halal chicken", "volume": "$50K-500K",
     "platforms": ["Instagram", "WhatsApp", "Shopee"],
     "notes": "MUI certified. Looking for Gulf buyers. Our corrider JKT→DXB perfect."},
    
    {"name": "Halal Beverages Sdn Bhd", "country": "Malaysia", "type": "supplier",
     "product": "Halal energy drinks", "volume": "$30K-300K",
     "platforms": ["Facebook", "WhatsApp"],
     "notes": "JAKIM certified since 2021. Small team. Needs UAE distributor."},
    
    {"name": "MediSupply Africa", "country": "South Africa", "type": "buyer",
     "product": "Generic medicines", "volume": "$200K-2M",
     "platforms": ["LinkedIn", "TradeIndia"],
     "notes": "Small pharma distributor. Needs Indian generic suppliers."},
    
    {"name": "Siam Electronics Assembly", "country": "Thailand", "type": "buyer",
     "product": "Smartphone components", "volume": "$50K-500K",
     "platforms": ["Alibaba", "LinkedIn"],
     "notes": "Thai electronics assembler. Needs Chinese component suppliers."},
    
    {"name": "PT Tech Nusantara", "country": "Indonesia", "type": "buyer",
     "product": "Consumer electronics", "volume": "$100K-2M",
     "platforms": ["Tokopedia", "Alibaba"],
     "notes": "Jakarta-based electronics distributor."},
]

# ─── Phase 2: Trade corridor micro-business profiles ────────────────────

CORRIDOR_PROFILES = {
    "jakarta_dubai": {
        "corridor": "Jakarta → Dubai",
        "commodity": "Coconut oil, spices, coffee",
        "micro_exporters": "50+ home-based coconut oil producers in Sulawesi",
        "volume_per_exporter": "$5K-50K/year",
        "platforms": ["Tokopedia", "Shopee", "WhatsApp Groups"],
        "approach": "They sell via marketplace. Need help exporting internationally.",
    },
    "bandung_jeddah": {
        "corridor": "Bandung → Jeddah",
        "commodity": "Textiles, modest fashion",
        "micro_exporters": "200+ small textile workshops in Bandung",
        "volume_per_exporter": "$10K-100K/year",
        "platforms": ["Instagram", "Shopee", "WhatsApp"],
        "approach": "Instagram-heavy. Visual products. No logistics setup for ME market.",
    },
    "surabaya_chennai": {
        "corridor": "Surabaya → Chennai",
        "commodity": "Spices, agricultural products",
        "micro_exporters": "30+ spice processors in East Java",
        "volume_per_exporter": "$5K-30K/year",
        "platforms": ["TradeIndia", "WhatsApp"],
        "approach": "Traditional exporters. Need documentation and logistics help.",
    },
}

# ─── Contact discovery strategy ───────────────────────────────────────
# Micro-businesses in SEA are NOT findable via website scraping.
# They operate on:
#   WhatsApp Business — primary B2B communication tool in SEA
#   Instagram — visual product showcase
#   Shopee/Tokopedia — marketplace sales
#   Facebook Page — basic web presence
#
# Best way to reach them:
# 1. Search Instagram for trade hashtags (#jualminyakkelapa #exportirhalal)
# 2. Find their WhatsApp Business number
# 3. Or send via Instagram DM → they share WhatsApp
#
# Alternative: Trade platforms
#   Alibaba.com — search "Indonesia halal food supplier" → contact supplier
#   TradeIndia.com — Indian exporters with email
#   EC21.com — Korean B2B platform with contact info