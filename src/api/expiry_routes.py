

from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.expiry.database import (
    add_product,
    get_products,
    delete_product
)


router = APIRouter(
    prefix="/api/expiry",
    tags=["Expiry Management"]
)


# Request format for adding a product
class ProductCreate(BaseModel):
    sku: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    category: str = Field(default="Other")
    batch_number: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    expiry_date: date
    store: str = Field(default="Downtown Flagship #01")


# Calculate expiry status
def get_expiry_status(expiry_date):
    today = date.today()
    days_remaining = (expiry_date - today).days

    if days_remaining < 0:
        status = "Expired"
    elif days_remaining <= 30:
        status = "Expiring Soon"
    else:
        status = "Safe"

    return status, days_remaining


# 1. Get all expiry products
@router.get("/")
def list_expiry_products():

    products = get_products()
    result = []

    for product in products:
        expiry_date = date.fromisoformat(product["expiry_date"])

        status, days_remaining = get_expiry_status(expiry_date)

        product["expiry_status"] = status
        product["days_remaining"] = days_remaining

        result.append(product)

    return {
        "total_products": len(result),
        "products": result
    }


# 2. Add a new expiry product
@router.post("/")
def create_expiry_product(product: ProductCreate):

    add_product(
        product_name=product.product_name.strip(),
        batch_number=product.batch_number.strip(),
        quantity=product.quantity,
        expiry_date=product.expiry_date.isoformat(),
        sku=product.sku.strip().upper(),
        category=product.category.strip(),
        store=product.store.strip()
    )

    return {
        "message": "Product added successfully",
        "product": product.model_dump(mode="json")
    }


# 3. Delete an expiry product
@router.delete("/{product_id}")
def remove_expiry_product(product_id: int):

    products = get_products()

    product_exists = any(
        product["id"] == product_id
        for product in products
    )

    if not product_exists:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    delete_product(product_id)

    return {
        "message": "Product deleted successfully",
        "product_id": product_id
    }
