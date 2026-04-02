from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

# Products list (temporary database)
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []
order_counter = 1


# Helper function

def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


# Pydantic model
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)


@app.get("/")
def home():
    return {"message": "FastAPI is working"}


# Q1 - Search products
@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [product for product in products if keyword.lower() in product["name"].lower()]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results,
    }


# Q2 - Sort products
@app.get("/products/sort")
def sort_products(sort_by: str = Query("price"), order: str = Query("asc")):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    reverse = order == "desc"
    results = sorted(products, key=lambda product: product[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": results,
    }


# Q3 - Pagination
@app.get("/products/page")
def paginate_products(page: int = Query(1, ge=1), limit: int = Query(2, ge=1, le=20)):
    start = (page - 1) * limit
    paged_products = products[start:start + limit]
    total_pages = -(-len(products) // limit)

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": total_pages,
        "products": paged_products,
    }


# Q5 - Sort by category, then price
@app.get("/products/sort-by-category")
def sort_by_category():
    results = sorted(products, key=lambda product: (product["category"], product["price"]))

    return {
        "message": "Products sorted by category and then price",
        "total_found": len(results),
        "products": results,
    }


# Q6 - Browse products (search + sort + pagination)
@app.get("/products/browse")
def browse_products(
    keyword: str = Query(""),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=20),
):
    results = products

    # Step 1: Search
    if keyword:
        results = [product for product in results if keyword.lower() in product["name"].lower()]

    # Step 2: Sort
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    results = sorted(results, key=lambda product: product[sort_by], reverse=(order == "desc"))

    # Step 3: Pagination
    total_found = len(results)
    start = (page - 1) * limit
    paged_products = results[start:start + limit]
    total_pages = -(-total_found // limit) if total_found > 0 else 0

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total_found,
        "total_pages": total_pages,
        "products": paged_products,
    }


# Orders endpoint
@app.post("/orders")
def place_order(order_data: OrderRequest):
    global order_counter

    product = find_product(order_data.product_id)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}

    total_price = product["price"] * order_data.quantity

    order = {
        "order_id": order_counter,
        "customer_name": order_data.customer_name,
        "product": product["name"],
        "quantity": order_data.quantity,
        "delivery_address": order_data.delivery_address,
        "total_price": total_price,
    }

    orders.append(order)
    order_counter += 1

    return {"message": "Order placed successfully", "order": order}


@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders),
    }


# Q4 - Search orders
@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    results = [
        order for order in orders
        if customer_name.lower() in order["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results,
    }


# Extra endpoint - Orders pagination
@app.get("/orders/page")
def get_orders_paged(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=20)):
    start = (page - 1) * limit
    paged_orders = orders[start:start + limit]
    total_pages = -(-len(orders) // limit) if len(orders) > 0 else 0

    return {
        "page": page,
        "limit": limit,
        "total_orders": len(orders),
        "total_pages": total_pages,
        "orders": paged_orders,
    }
