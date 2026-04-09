"""
CloudMart - Seed Data Script
Populates the products container with sample e-commerce products.
Run once: python -m app.seed_data
"""
import os
import sys
from azure.cosmos import CosmosClient

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "")
COSMOS_KEY = os.getenv("COSMOS_KEY", "")
DATABASE_NAME = "cloudmart"

PRODUCTS = [
    {
        "id": "1",
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "price": 79.99,
        "description": "Premium noise-cancelling wireless headphones with 30-hour battery life. Features Bluetooth 5.0, deep bass, and a comfortable over-ear design.",
        "image_url": "https://img.icons8.com/3d-fluency/94/headphones.png",
        "in_stock": True
    },
    {
        "id": "2",
        "name": "USB-C Fast Charging Cable (3-Pack)",
        "category": "Electronics",
        "price": 19.99,
        "description": "Durable braided USB-C cables (1m, 1.5m, 2m) supporting 100W PD fast charging. Compatible with all USB-C devices.",
        "image_url": "https://img.icons8.com/3d-fluency/94/usb-c.png",
        "in_stock": True
    },
    {
        "id": "3",
        "name": "Mechanical Keyboard (RGB)",
        "category": "Electronics",
        "price": 129.99,
        "description": "Full-size mechanical keyboard with Cherry MX Blue switches, per-key RGB lighting, and aircraft-grade aluminum frame.",
        "image_url": "https://img.icons8.com/3d-fluency/94/keyboard.png",
        "in_stock": True
    },
    {
        "id": "4",
        "name": "Classic Denim Jacket",
        "category": "Clothing",
        "price": 89.99,
        "description": "Timeless medium-wash denim jacket with button closure. Made from 100% premium cotton with a comfortable regular fit.",
        "image_url": "https://img.icons8.com/3d-fluency/94/jacket.png",
        "in_stock": True
    },
    {
        "id": "5",
        "name": "Performance Running Shoes",
        "category": "Clothing",
        "price": 149.99,
        "description": "Lightweight running shoes with responsive foam cushioning and breathable mesh upper. Perfect for road and light trail running.",
        "image_url": "https://img.icons8.com/3d-fluency/94/running-shoe.png",
        "in_stock": True
    },
    {
        "id": "6",
        "name": "Organic Cotton T-Shirt",
        "category": "Clothing",
        "price": 34.99,
        "description": "Soft, sustainably sourced organic cotton crew-neck t-shirt. Available in multiple colors. Machine washable.",
        "image_url": "https://img.icons8.com/3d-fluency/94/t-shirt.png",
        "in_stock": True
    },
    {
        "id": "7",
        "name": "Cloud Computing Fundamentals",
        "category": "Books",
        "price": 49.99,
        "description": "Comprehensive guide covering AWS, Azure, and GCP. Includes hands-on labs, architecture patterns, and certification prep material.",
        "image_url": "https://img.icons8.com/3d-fluency/94/book.png",
        "in_stock": True
    },
    {
        "id": "8",
        "name": "Python for DevOps",
        "category": "Books",
        "price": 44.99,
        "description": "Learn automation, CI/CD, monitoring, and infrastructure-as-code with Python. Covers Docker, Kubernetes, and Terraform integration.",
        "image_url": "https://img.icons8.com/3d-fluency/94/literature.png",
        "in_stock": True
    },
    {
        "id": "9",
        "name": "Portable SSD 1TB",
        "category": "Electronics",
        "price": 109.99,
        "description": "Ultra-fast portable solid-state drive with USB 3.2 Gen 2. Read speeds up to 1050 MB/s. Shock-resistant and pocket-sized.",
        "image_url": "https://img.icons8.com/3d-fluency/94/ssd.png",
        "in_stock": True
    },
    {
        "id": "10",
        "name": "Networking & Security Handbook",
        "category": "Books",
        "price": 59.99,
        "description": "Essential reference for firewalls, IDS/IPS, VPNs, and cloud security. Covers real-world scenarios and compliance frameworks.",
        "image_url": "https://img.icons8.com/3d-fluency/94/security-checked.png",
        "in_stock": True
    }
]


def seed_products():
    """Insert sample products into Cosmos DB."""
    if not COSMOS_ENDPOINT or not COSMOS_KEY:
        print("ERROR: Set COSMOS_ENDPOINT and COSMOS_KEY environment variables first.")
        sys.exit(1)
    
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client("products")
    
    print(f"Seeding products into Cosmos DB ({COSMOS_ENDPOINT})...")
    for product in PRODUCTS:
        try:
            container.upsert_item(body=product)
            print(f"  ✓ {product['name']} (${product['price']})")
        except Exception as e:
            print(f"  ✗ {product['name']}: {e}")
    
    print(f"\nDone! Seeded {len(PRODUCTS)} products across {len(set(p['category'] for p in PRODUCTS))} categories.")


if __name__ == "__main__":
    seed_products()
