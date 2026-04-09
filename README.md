# CloudMart — CSP451 Milestone 3

A cloud-native e-commerce application built with **FastAPI**, **Azure Cosmos DB**, and deployed to **Azure Container Instances (ACI)** via **GitHub Actions CI/CD**.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Repository                                       │
│  ├── Push to main → CI Pipeline (test + build)          │
│  └── Push to main → CD Pipeline (push ACR + deploy ACI) │
└────────────────────┬────────────────────────────────────┘
                     │
           ┌─────────▼──────────┐
           │  Azure Container    │
           │  Registry (ACR)     │
           │  cloudmartacrXXX    │
           └─────────┬──────────┘
                     │
           ┌─────────▼──────────┐       ┌──────────────────┐
           │  Azure Container    │       │  Azure Cosmos DB  │
           │  Instances (ACI)    │◄─────►│  (NoSQL)          │
           │  cloudmart-app      │       │  canadacentral    │
           │  Public IP + FQDN   │       └──────────────────┘
           └────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | Python 3.11 + FastAPI |
| Database | Azure Cosmos DB (NoSQL) |
| Container Registry | Azure Container Registry (ACR) |
| Hosting | Azure Container Instances (ACI) |
| CI/CD | GitHub Actions |
| Frontend | Vanilla HTML/CSS/JS |

## API Endpoints (11 total)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage (static HTML) |
| GET | `/health` | Health check + DB status |
| GET | `/api/v1/products` | List all products |
| GET | `/api/v1/products?category=X` | Filter by category |
| GET | `/api/v1/products/{id}` | Get single product |
| GET | `/api/v1/categories` | List categories |
| GET | `/api/v1/cart` | View cart |
| POST | `/api/v1/cart/items` | Add item to cart |
| DELETE | `/api/v1/cart/items/{id}` | Remove from cart |
| POST | `/api/v1/orders` | Place order (checkout) |
| GET | `/api/v1/orders` | List orders |

## Quick Start — Local Development

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run locally (without Cosmos DB — health endpoint will show "degraded")
uvicorn app.main:app --reload --port 8000

# 4. Open http://localhost:8000
```

## Run with Cosmos DB

```bash
# Set environment variables
export COSMOS_ENDPOINT="https://your-cosmos-account.documents.azure.com:443/"
export COSMOS_KEY="your-primary-key"

# Start the app
uvicorn app.main:app --reload --port 8000

# Seed initial products (run once)
python -m app.seed_data
```

## Run Tests

```bash
pytest tests/ -v
```

## Docker

```bash
# Build
docker build -t cloudmart-api .

# Run locally
docker run -p 8080:80 \
  -e COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
  -e COSMOS_KEY="$COSMOS_KEY" \
  cloudmart-api

# Open http://localhost:8080
```

## Deploy to Azure (ACR + ACI)

```bash
# Push to ACR (cloud build — no Docker Desktop needed)
az acr build --registry $ACR_NAME --image cloudmart-api:latest .

# Deploy to ACI
az container create \
  --resource-group $RESOURCE_GROUP \
  --name cloudmart-app \
  --image $ACR_NAME.azurecr.io/cloudmart-api:latest \
  --registry-login-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_NAME \
  --registry-password $ACR_PASSWORD \
  --cpu 1 --memory 1.5 \
  --ports 80 --dns-name-label $DNS_LABEL \
  --environment-variables \
    COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_KEY="$COSMOS_KEY" \
  --restart-policy OnFailure
```

## Project Structure

```
cloudmart/
├── .github/workflows/
│   ├── ci.yml              # CI: test + build Docker image
│   └── deploy.yml          # CD: push to ACR + deploy to ACI
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app — routes + static serving
│   ├── models.py           # Pydantic request/response models
│   ├── database.py         # Cosmos DB client initialization
│   └── seed_data.py        # Populate initial product catalog
├── static/
│   ├── index.html          # Storefront HTML
│   ├── style.css           # Modern responsive CSS
│   └── app.js              # Frontend JavaScript (API calls)
├── tests/
│   └── test_api.py         # Pytest unit tests
├── Dockerfile              # Production container image
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Pytest configuration
├── submission.md           # Your submission document
├── README.md               # This file
└── .gitignore
```

## GitHub Secrets Required (9)

| Secret | Description |
|--------|-------------|
| `ACR_NAME` | ACR registry name |
| `ACR_LOGIN_SERVER` | `<acr-name>.azurecr.io` |
| `ACR_USERNAME` | ACR admin username |
| `ACR_PASSWORD` | ACR admin password |
| `COSMOS_ENDPOINT` | Cosmos DB endpoint URL |
| `COSMOS_KEY` | Cosmos DB primary key |
| `AZURE_RESOURCE_GROUP` | Your Student-RG name |
| `AZURE_CREDENTIALS` | Service principal JSON |
| `DNS_LABEL` | ACI DNS name label |

## License

Educational project for Seneca Polytechnic CSP451 — Cloud Computing.
