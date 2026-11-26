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

@mcp.tool()
def checkout() -> str:
    """ONLY call this tool when the user explicitly says 'checkout', 'pay', or 'complete order'. Never call this automatically after adding items."""
    if not CART:
        return "The shopping cart is empty. Add items before checking out."
    
    total = round(sum(item["subtotal"] for item in CART), 2)
    item_count = sum(item["quantity"] for item in CART)
    CART.clear()
    return f"Order confirmed! Paid {total} NOK for {item_count} item(s). Your cart is now empty."

if __name__ == "__main__":
    mcp.run()