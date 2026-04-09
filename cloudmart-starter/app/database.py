"""
CloudMart - Cosmos DB Client Initialization
Connects to Azure Cosmos DB using environment variables.
"""
import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Read credentials from environment variables
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "")
COSMOS_KEY = os.getenv("COSMOS_KEY", "")
DATABASE_NAME = "cloudmart"

# Initialize Cosmos DB client
# These will be None if env vars are not set (e.g., during testing)
client = None
database = None
products_container = None
cart_container = None
orders_container = None


def init_db():
    """Initialize database connections. Called at app startup."""
    global client, database, products_container, cart_container, orders_container
    
    if not COSMOS_ENDPOINT or not COSMOS_KEY:
        print("WARNING: COSMOS_ENDPOINT or COSMOS_KEY not set. Database features disabled.")
        return False
    
    try:
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        database = client.get_database_client(DATABASE_NAME)
        products_container = database.get_container_client("products")
        cart_container = database.get_container_client("cart")
        orders_container = database.get_container_client("orders")
        # Test connectivity
        database.read()
        print(f"Connected to Cosmos DB: {COSMOS_ENDPOINT}")
        return True
    except Exception as e:
        print(f"ERROR connecting to Cosmos DB: {e}")
        return False


def is_connected():
    """Check if database is connected."""
    if not client or not database:
        return False
    try:
        database.read()
        return True
    except Exception:
        return False
