import json
from pathlib import Path
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Fake-Oda")

# Path to data/products.json relative to this file
DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"

def load_products() -> list[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

CART = []

@mcp.tool()
def search_products(query: str) -> str:
    """Search for a single grocery item by keyword (e.g., 'milk', 'eggs', 'flour', 'butter'). Search one ingredient at a time."""
    products = load_products()
    query = query.lower()
    matches = [p for p in products if query in p["name"].lower() or query in p["category"].lower()]
    if not matches:
        return f"No products found for '{query}'. Try searching for a single basic ingredient like 'milk', 'eggs', 'flour', or 'butter'."
    return json.dumps(matches)
    
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