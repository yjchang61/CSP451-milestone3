"""
CloudMart - FastAPI Application
E-commerce API with Cosmos DB backend and static frontend.
"""
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

import app.database as db
from app.models import CartItemRequest, HealthResponse

# ─── Create FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title="CloudMart API",
    description="CSP451 Milestone 3 — E-Commerce API on Azure",
    version="1.0.0"
)

# ─── Startup Event ────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    """Initialize database connection on app startup."""
    db.init_db()

# ─── Health Check ─────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint — verifies app is running and DB is connected.
    Used by Azure Monitor, load balancers, and CI/CD pipelines.
    """
    db_status = "connected" if db.is_connected() else "disconnected"
    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        cosmos_endpoint=db.COSMOS_ENDPOINT or "not configured",
        timestamp=datetime.now(timezone.utc).isoformat()
    )

# ─── Product Endpoints ───────────────────────────────────────────────
@app.get("/api/v1/products", tags=["Products"])
async def list_products(category: Optional[str] = Query(None, description="Filter by category")):
    """
    List all products, optionally filtered by category.
    GET /api/v1/products
    GET /api/v1/products?category=Electronics
    """
    try:
        if category:
            query = "SELECT * FROM c WHERE c.category = @category"
            params = [{"name": "@category", "value": category}]
            items = list(db.products_container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True
            ))
        else:
            items = list(db.products_container.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            ))
        # Clean Cosmos metadata from response
        cleaned = [{k: v for k, v in item.items() if not k.startswith('_')} for item in items]
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


@app.get("/api/v1/products/{product_id}", tags=["Products"])
async def get_product(product_id: str):
    """Get a single product by its ID."""
    try:
        query = "SELECT * FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": product_id}]
        items = list(db.products_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if not items:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        item = items[0]
        cleaned = {k: v for k, v in item.items() if not k.startswith('_')}
        return cleaned
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")


@app.get("/api/v1/categories", tags=["Products"])
async def list_categories():
    """List all unique product categories."""
    try:
        items = list(db.products_container.query_items(
            query="SELECT DISTINCT c.category FROM c",
            enable_cross_partition_query=True
        ))
        categories = [item["category"] for item in items]
        return sorted(categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

# ─── Cart Endpoints ──────────────────────────────────────────────────
DEMO_USER = "demo-user"

@app.get("/api/v1/cart", tags=["Cart"])
async def get_cart():
    """Get all items in the current cart."""
    try:
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        params = [{"name": "@user_id", "value": DEMO_USER}]
        items = list(db.cart_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        cleaned = [{k: v for k, v in item.items() if not k.startswith('_')} for item in items]
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cart: {str(e)}")


@app.post("/api/v1/cart/items", tags=["Cart"])
async def add_to_cart(item: CartItemRequest):
    """Add a product to the shopping cart."""
    try:
        # Look up the product
        query = "SELECT * FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": item.product_id}]
        products = list(db.products_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if not products:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        product = products[0]
        cart_item = {
            "id": str(uuid.uuid4()),
            "user_id": DEMO_USER,
            "product_id": item.product_id,
            "product_name": product["name"],
            "price": product["price"],
            "quantity": item.quantity,
            "subtotal": round(product["price"] * item.quantity, 2)
        }
        db.cart_container.create_item(body=cart_item)
        return {"message": "Item added to cart", "item": cart_item}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to cart: {str(e)}")


@app.delete("/api/v1/cart/items/{item_id}", tags=["Cart"])
async def remove_from_cart(item_id: str):
    """Remove an item from the cart by its cart-item ID."""
    try:
        db.cart_container.delete_item(item=item_id, partition_key=DEMO_USER)
        return {"message": f"Item {item_id} removed from cart"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing item: {str(e)}")

# ─── Order Endpoints ─────────────────────────────────────────────────
@app.post("/api/v1/orders", tags=["Orders"])
async def create_order():
    """Create an order from all items currently in the cart."""
    try:
        # Get cart items
        query = "SELECT * FROM c WHERE c.user_id = @user_id"
        params = [{"name": "@user_id", "value": DEMO_USER}]
        cart_items = list(db.cart_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty. Add items before placing an order.")
        
        # Build order
        order_items = []
        total = 0.0
        for ci in cart_items:
            order_item = {
                "product_id": ci["product_id"],
                "product_name": ci["product_name"],
                "price": ci["price"],
                "quantity": ci["quantity"],
                "subtotal": ci["subtotal"]
            }
            order_items.append(order_item)
            total += ci["subtotal"]
        
        order = {
            "id": str(uuid.uuid4()),
            "user_id": DEMO_USER,
            "items": order_items,
            "total": round(total, 2),
            "status": "confirmed",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        db.orders_container.create_item(body=order)
        
        # Clear the cart
        for ci in cart_items:
            db.cart_container.delete_item(item=ci["id"], partition_key=DEMO_USER)
        
        return {"message": "Order placed successfully", "order": order}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")


@app.get("/api/v1/orders", tags=["Orders"])
async def list_orders():
    """List all orders for the demo user."""
    try:
        query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.created_at DESC"
        params = [{"name": "@user_id", "value": DEMO_USER}]
        items = list(db.orders_container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        cleaned = [{k: v for k, v in item.items() if not k.startswith('_')} for item in items]
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")

# ─── Static Files & Homepage ─────────────────────────────────────────
# Mount static files directory
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", tags=["Frontend"])
async def homepage():
    """Serve the CloudMart storefront homepage."""
    index_path = os.path.join(static_dir, "index.html")
    return FileResponse(index_path)
