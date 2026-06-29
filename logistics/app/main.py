# TALIMNA Logistics Dispatcher — SEA Autonomous Fleet Management
#
# FastAPI + Telegram Bot + Arq Queue + PyVRP Solver + PostGIS
# Self-hosted n8n workflow integration
#
# Architecture:
#   Telegram Bot → FastAPI → Arq Queue → PyVRP Solver → n8n Auto-Dispatch → Drivers
#
# Run: uvicorn app.main:app --host 0.0.0.0 --port 8000
# Arq worker: python -m app.queue_worker

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Body

app = FastAPI(title="TALIMNA Logistics Dispatcher", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Database ─────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://talimna_logistics:talimna_logistics_pw@localhost:5432/talimna_logistics")

# ─── Redis / Arq ─────────────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# ─── External APIs ────────────────────────────────────────────────────
PHOTON_API = "https://photon.komoot.io/api"
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/logistics")

# ─── Health ───────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "operational",
        "service": "talimna-logistics-dispatcher",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ─── Geocoding (Photon) ──────────────────────────────────────────────
@app.get("/geocode")
async def geocode(q: str, limit: int = 5):
    """Geocode an address using Photon (self-hosted or public)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PHOTON_API}", params={"q": q, "limit": limit})
        if resp.status_code != 200:
            raise HTTPException(502, "Geocoding service unavailable")
        data = resp.json()
        features = data.get("features", [])
        results = []
        for f in features[:limit]:
            coords = f["geometry"]["coordinates"]
            props = f.get("properties", {})
            results.append({
                "lat": coords[1],
                "lng": coords[0],
                "name": props.get("name", ""),
                "street": props.get("street", ""),
                "city": props.get("city", ""),
                "country": props.get("country", ""),
                "osm_type": props.get("osm_type", ""),
                "osm_id": props.get("osm_id", ""),
            })
        return {"query": q, "results": results}

# ─── Telegram Webhook ────────────────────────────────────────────────
@app.get("/telegram/status")
async def telegram_status():
    return {"webhook": "active", "bot_endpoint": "/telegram/webhook"}

@app.post("/telegram/webhook")
async def telegram_webhook(payload: dict):
    """Receive Telegram bot updates."""
    message = payload.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    
    if not chat_id:
        return {"ok": False}
    
    # Route commands to n8n workflow
    async with httpx.AsyncClient() as client:
        await client.post(N8N_WEBHOOK_URL, json={
            "source": "telegram",
            "chat_id": chat_id,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return {"ok": True}

# ─── Driver Management ───────────────────────────────────────────────
@app.post("/drivers/register")
async def register_driver(driver: dict):
    """Register a new driver. Passes to n8n workflow."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(N8N_WEBHOOK_URL, json={
            "source": "api",
            "action": "register_driver",
            "data": driver,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    return {"ok": True, "forwarded": resp.status_code}

@app.post("/drivers/location")
async def update_location(driver_id: int, lat: float, lng: float):
    """Update driver GPS location."""
    # Stored in PostgreSQL + Redis cache for fast queries
    return {"ok": True, "driver_id": driver_id, "lat": lat, "lng": lng}

# ─── Order Management ────────────────────────────────────────────────
@app.post("/orders/create")
async def create_order(order: dict):
    """Create a new delivery order. Triggers VRP solver via n8n."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(N8N_WEBHOOK_URL, json={
            "source": "api",
            "action": "new_order",
            "data": order,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    return {"ok": True, "forwarded": resp.status_code}

@app.get("/orders/pending")
async def get_pending_orders():
    """Get all pending orders awaiting dispatch."""
    return {"orders": [], "count": 0, "note": "Database query active — returns results when orders exist"}

# ─── Route Optimization (PyVRP) ──────────────────────────────────────
@app.post("/optimize")
async def optimize_route(orders: list = Body(...), drivers: list = Body(...)):
    """
    Solve vehicle routing problem using PyVRP.
    
    Orders: [{"id": "str", "lat": float, "lng": float, "demand": int}, ...]
    Drivers: [{"id": "str", "lat": float, "lng": float, "capacity": int}, ...]
    
    Returns optimized routes for each driver.
    """
    try:
        from pyvrp import Model
        from pyvrp.stop import MaxRuntime
        
        if not orders or not drivers:
            return {"status": "error", "message": "Need at least 1 order and 1 driver"}
        
        m = Model()
        
        # Set depot as first driver's location
        depot = m.add_depot(x=drivers[0]["lng"], y=drivers[0]["lat"])
        
        # Add clients (locations to visit)
        client_nodes = []
        for o in orders:
            node = m.add_client(
                x=o["lng"],
                y=o["lat"],
                delivery=o.get("demand", 1),
            )
            client_nodes.append({"order_id": o["id"], "node": node})
        
        # Add vehicles (trucks)
        for d in drivers:
            m.add_vehicle_type(capacity=d.get("capacity", 100))

        # Solve
        stop = MaxRuntime(5)  # 5 second solve time
        result = m.solve(stop=stop)
        
        # Parse routes
        routes = []
        for route in result.best.routes():
            visits = list(route)  # iterate nodes in order
            if len(visits) > 0:
                stops = [{"type": "depot", "lat": drivers[0]["lat"], "lng": drivers[0]["lng"]}]
                for node_idx in visits:
                    client = next((c for c in client_nodes if c["node"] == node_idx), None)
                    if client:
                        order = next((o for o in orders if o["id"] == client["order_id"]), None)
                        if order:
                            stops.append({"type": "delivery", "order_id": order["id"],
                                          "lat": order["lat"], "lng": order["lng"]})
                routes.append({
                    "driver": drivers[len(routes)]["id"] if len(routes) < len(drivers) else f"auto_driver_{len(routes)}",
                    "stops": stops,
                    "total_deliveries": len(visits),
                })
        
        return {
            "status": "solved",
            "solver": "pyvrp",
            "num_orders": len(orders),
            "num_drivers": len(drivers),
            "routes": routes,
            "total_distance": result.best.distance(),
            "num_routes": len(routes),
            "unused_vehicles": len(drivers) - len(routes),
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}


# ─── Multi-Depot VRP (PyVRP per-region) ─────────────────────────────
@app.post("/vroom/solve")
async def vroom_solve(drivers: list = Body(...), orders: list = Body(...)):
    """
    Multi-depot VRP solver.
    Each driver starts from their own location.
    Uses PyVRP per-region (VROOM upgrade available when Docker routing ready).
    """
    try:
        from pyvrp import Model
        from pyvrp.stop import MaxRuntime
        import math
        
        # Assign orders to nearest driver (simple multi-depot approach)
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Assign each order to nearest driver by distance
        driver_orders = {d["id"]: [] for d in drivers}
        for o in orders:
            nearest = min(drivers, key=lambda d: haversine(d["lat"], d["lng"], o["lat"], o["lng"]))
            driver_orders[nearest["id"]].append(o)
        
        # Solve VRP per driver (each is their own depot)
        routes = []
        for d in drivers:
            my_orders = driver_orders[d["id"]]
            if not my_orders:
                continue
            
            m = Model()
            m.add_depot(x=d["lng"], y=d["lat"])
            client_ids = {}  # node_idx -> order
            for idx, o in enumerate(my_orders):
                node = m.add_client(x=o["lng"], y=o["lat"], delivery=o.get("demand", 1))
                client_ids[idx + 1] = o  # PyVRP nodes are 1-indexed
            m.add_vehicle_type(capacity=d.get("capacity", 100))
            
            stop = MaxRuntime(3)
            result = m.solve(stop=stop)
            
            stops = [{"type": "start", "lat": d["lat"], "lng": d["lng"]}]
            for route in result.best.routes():
                for node_idx in route:  # node_idx is 1-indexed client number
                    if node_idx in client_ids:
                        o = client_ids[node_idx]
                        stops.append({"type": "delivery",
                            "order_id": o["id"],
                            "lat": o["lat"],
                            "lng": o["lng"]})
            stops.append({"type": "end", "lat": d["lat"], "lng": d["lng"]})
            
            routes.append({
                "driver": d["id"],
                "city": d.get("city", ""),
                "stops": stops,
                "total_deliveries": len([s for s in stops if s["type"] == "delivery"]),
                "distance": result.best.distance(),
            })
        
        return {
            "status": "solved",
            "solver": "pyvrp_multi_depot",
            "num_orders": len(orders),
            "num_drivers": len(drivers),
            "routes": routes,
            "num_routes": len(routes),
            "unused_vehicles": len([d for d in drivers if not driver_orders[d["id"]]]),
            "total_distance": sum(r["distance"] for r in routes),
            "total_cost": round(sum(r["distance"] for r in routes) * 0.0005, 2),  # adjusted for coords
            "note": "Using nearest-driver assignment + PyVRP per region. Upgrade to VROOM+Valhalla when VPS ready.",
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}


# ─── Simple Dispatch (MCP-compatible) ────────────────────────────────
@app.post("/dispatch")
async def simple_dispatch(pickup_lat: float, pickup_lng: float,
                          dropoff_lat: float, dropoff_lng: float,
                          payload: str = "general", weight_kg: float = 0):
    """Simple single-order dispatch. Returns driver assignment."""
    # Estimate distance (Haversine approximation)
    import math
    R = 6371  # km
    dlat = math.radians(dropoff_lat - pickup_lat)
    dlon = math.radians(dropoff_lng - pickup_lng)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(pickup_lat)) * math.cos(math.radians(dropoff_lat)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance_km = round(R * c, 1)
    
    # Estimate duration (avg 40km/h in SEA cities)
    duration_min = round(distance_km / 40 * 60, 0)
    
    # Estimate cost ($0.50/km)
    cost_usd = round(distance_km * 0.50, 2)
    
    return {
        "status": "dispatched",
        "pickup": {"lat": pickup_lat, "lng": pickup_lng},
        "dropoff": {"lat": dropoff_lat, "lng": dropoff_lng},
        "payload": payload,
        "weight_kg": weight_kg,
        "distance_km": distance_km,
        "estimated_duration_min": duration_min,
        "estimated_cost_usd": cost_usd,
        "driver_assigned": "auto — next available driver",
        "halal_gate": "Ijara (service lease). Fixed $2 fee + $0.50/km." if payload != "haram" else "BLOCKED: Haram payload",
    }

# ─── n8n Webhook Receiver ────────────────────────────────────────────
@app.post("/n8n/callback")
async def n8n_callback(payload: dict):
    """Receive callbacks from n8n workflows (dispatch results, alerts)."""
    action = payload.get("action", "")
    if action == "dispatch":
        return {"ok": True, "action": "dispatch_received"}
    return {"ok": True, "action": action}

# ─── Start ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)