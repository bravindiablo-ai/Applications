from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.auth.middleware import get_current_user

router = APIRouter(prefix="/shop", tags=["shop"])

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    original_price: Optional[float] = None
    discount: Optional[float] = None
    category: str
    subcategory: str
    brand: str
    images: List[str]
    sizes: List[str]
    colors: List[str]
    trending_score: float = 0.0
    in_stock: bool = True
    rating: float = 0.0
    review_count: int = 0

class CartItem(BaseModel):
    product_id: str
    quantity: int
    size: Optional[str] = None
    color: Optional[str] = None

class CheckoutRequest(BaseModel):
    items: List[CartItem]
    shipping_address: dict
    payment_method: str
    total_amount: float

class CategoryResponse(BaseModel):
    id: str
    name: str
    subcategories: List[str]
    image_url: str

# Mock data - replace with actual shopping API integration
MOCK_PRODUCTS = [
    ProductResponse(
        id="1",
        name="Vintage Denim Jacket",
        description="Classic vintage denim jacket with distressed details",
        price=89.99,
        original_price=120.00,
        discount=25.0,
        category="Clothing",
        subcategory="Jackets",
        brand="Urban Style",
        images=["https://example.com/product1_1.jpg", "https://example.com/product1_2.jpg"],
        sizes=["XS", "S", "M", "L", "XL"],
        colors=["Blue", "Black", "White"],
        trending_score=88.5,
        in_stock=True,
        rating=4.5,
        review_count=234
    ),
    ProductResponse(
        id="2",
        name="Wireless Headphones",
        description="Premium noise-cancelling wireless headphones",
        price=199.99,
        original_price=249.99,
        discount=20.0,
        category="Electronics",
        subcategory="Audio",
        brand="SoundMax",
        images=["https://example.com/product2_1.jpg", "https://example.com/product2_2.jpg"],
        sizes=["One Size"],
        colors=["Black", "Silver", "Rose Gold"],
        trending_score=92.3,
        in_stock=True,
        rating=4.7,
        review_count=567
    ),
    ProductResponse(
        id="3",
        name="Street Style Sneakers",
        description="Limited edition street style sneakers",
        price=129.99,
        original_price=159.99,
        discount=18.75,
        category="Footwear",
        subcategory="Sneakers",
        brand="Street Culture",
        images=["https://example.com/product3_1.jpg", "https://example.com/product3_2.jpg"],
        sizes=["7", "8", "9", "10", "11", "12"],
        colors=["White", "Black", "Red", "Blue"],
        trending_score=90.1,
        in_stock=True,
        rating=4.6,
        review_count=445
    ),
    ProductResponse(
        id="4",
        name="Minimalist Watch",
        description="Elegant minimalist watch with leather strap",
        price=149.99,
        original_price=199.99,
        discount=25.0,
        category="Accessories",
        subcategory="Watches",
        brand="Timeless",
        images=["https://example.com/product4_1.jpg", "https://example.com/product4_2.jpg"],
        sizes=["One Size"],
        colors=["Black", "Brown", "Navy"],
        trending_score=85.7,
        in_stock=True,
        rating=4.4,
        review_count=189
    ),
    ProductResponse(
        id="5",
        name="Graphic T-Shirt",
        description="Trendy graphic t-shirt with unique design",
        price=29.99,
        original_price=39.99,
        discount=25.0,
        category="Clothing",
        subcategory="T-Shirts",
        brand="Urban Graphics",
        images=["https://example.com/product5_1.jpg", "https://example.com/product5_2.jpg"],
        sizes=["XS", "S", "M", "L", "XL", "XXL"],
        colors=["White", "Black", "Gray", "Navy"],
        trending_score=87.2,
        in_stock=True,
        rating=4.3,
        review_count=312
    )
]

MOCK_CATEGORIES = [
    CategoryResponse(
        id="1",
        name="Clothing",
        subcategories=["T-Shirts", "Jackets", "Hoodies", "Jeans", "Dresses"],
        image_url="https://example.com/category_clothing.jpg"
    ),
    CategoryResponse(
        id="2",
        name="Footwear",
        subcategories=["Sneakers", "Boots", "Sandals", "Heels", "Flats"],
        image_url="https://example.com/category_footwear.jpg"
    ),
    CategoryResponse(
        id="3",
        name="Accessories",
        subcategories=["Watches", "Jewelry", "Bags", "Hats", "Sunglasses"],
        image_url="https://example.com/category_accessories.jpg"
    ),
    CategoryResponse(
        id="4",
        name="Electronics",
        subcategories=["Headphones", "Speakers", "Phone Cases", "Chargers"],
        image_url="https://example.com/category_electronics.jpg"
    )
]

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort_by: Optional[str] = Query("trending", description="Sort by: trending, price, rating"),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get shopping products with filtering and sorting"""
    products = MOCK_PRODUCTS
    
    if category:
        products = [p for p in products if category.lower() in p.category.lower()]
    
    if subcategory:
        products = [p for p in products if subcategory.lower() in p.subcategory.lower()]
    
    if brand:
        products = [p for p in products if brand.lower() in p.brand.lower()]
    
    if min_price:
        products = [p for p in products if p.price >= min_price]
    
    if max_price:
        products = [p for p in products if p.price <= max_price]
    
    if sort_by == "price":
        products = sorted(products, key=lambda x: x.price)
    elif sort_by == "rating":
        products = sorted(products, key=lambda x: x.rating, reverse=True)
    else:
        products = sorted(products, key=lambda x: x.trending_score, reverse=True)
    
    return products[:limit]

@router.get("/recommendations", response_model=List[ProductResponse])
async def get_product_recommendations(
    category: Optional[str] = Query(None, description="Preferred category"),
    style: Optional[str] = Query(None, description="Style preference"),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Get personalized product recommendations"""
    # TODO: Implement ML-based recommendations using user preferences
    products = MOCK_PRODUCTS
    
    if category:
        products = [p for p in products if category.lower() in p.category.lower()]
    
    return sorted(products, key=lambda x: x.trending_score, reverse=True)[:limit]

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(current_user: dict = Depends(get_current_user)):
    """Get available shopping categories"""
    return MOCK_CATEGORIES
