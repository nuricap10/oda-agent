import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Fake-Oda")

# Path to data/products.json relative to this file
DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"

def load_products() -> list[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

CART = []

@mcp.tool()
def search_products(query: str) -> list[dict]:
    """Search for groceries in the store based on a keyword (e.g., 'milk', 'eggs', 'butter')."""
    products = load_products()
    query = query.lower()
    return [p for p in products if query in p["name"].lower() or query in p["category"].lower()]

@mcp.tool()
def add_to_cart(product_id: str, quantity: int = 1) -> str:
    """Add a product to the shopping cart using its product_id."""
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return f"No product found with ID {product_id}. Search for the product first to find the correct ID."
    
    CART.append({
        "id": product["id"],
        "product": product["name"],
        "quantity": quantity,
        "subtotal": round(product["price"] * quantity, 2)
    })
    return f"Added {quantity}x {product['name']} to the cart."

@mcp.tool()
def get_cart() -> dict:
    """View all items currently in the shopping cart and the total price."""
    total = sum(item["subtotal"] for item in CART)
    return {"items": CART, "total_price": round(total, 2)}

if __name__ == "__main__":
    mcp.run()