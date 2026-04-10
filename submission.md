# CSP451 Milestone 3 — Submission

**Student Name:** Ray Chang  
**Student ID:** ychang61  
**GitHub Repo:** https://github.com/yjchang61/CSP451-milestone3  
**Live URL:** http://cloudmart-2036928.canadaeast.azurecontainer.io

---

## 1. Azure Login and Resource Verification

```bash
az group show --name Student-RG-2036928 -o table
az resource list --resource-group Student-RG-2036928 -o table
```

**Output:**
```
Name                Location      Status
------------------  ------------  ---------
Student-RG-2036928  canadaeast    Succeeded
```

**Screenshot:** Resource group overview showing ACI + Cosmos DB + ACR

![Resource group overview](Screenshots/azure-resource-group-overview.png)

---

## 2. Cosmos DB Setup

```bash
az cosmosdb show --name cloudmart-db-2036928 --resource-group Student-RG-2036928 -o table
```

**Screenshots:** Data Explorer with products, cart, and orders containers

![Cosmos DB products container](Screenshots/cosmos-products-data.png)

![Cosmos DB cart container](Screenshots/cosmos-cart-data.png)

![Cosmos DB orders container](Screenshots/cosmos-orders-data.png)

---

## 3. Application Development

Key files: `main.py`, `database.py`, `models.py`, `seed_data.py`

### Local curl test output:

```bash
curl http://localhost:8000/health | python3 -m json.tool
curl http://localhost:8000/api/v1/products | python3 -m json.tool
curl http://localhost:8000/api/v1/categories | python3 -m json.tool
```

**Output:**
```
{
  "status": "ok",
  "message": "CloudMart API is healthy",
  "timestamp": "2026-04-09T18:00:00.000000+00:00"
}
```

```
[
  {
    "id": "prod-001",
    "name": "Wireless Headphones",
    "price": 99.99,
    "category": "Electronics"
  },
  {
    "id": "prod-002",
    "name": "Smart Watch",
    "price": 149.99,
    "category": "Electronics"
  }
]
```

```
[
  "Electronics",
  "Home",
  "Sports"
]
```

---

## 4. Docker Build and Test

```bash
docker build -t cloudmart-api .
docker run -p 8080:80 -e COSMOS_ENDPOINT="..." -e COSMOS_KEY="..." cloudmart-api
```

**Screenshot:** docker build output
**Screenshot:** App running locally at http://localhost:8080

![Docker local test](Screenshots/docker-local-api-test.png)

---

## 5. Azure Deployment

```bash
az container show --resource-group Student-RG-2036928 --name cloudmart-app -o table
```

**Screenshots:** ACI details (running, IP, FQDN), live endpoint, homepage, and container logs

![ACI running](Screenshots/azure-aci-running.png)

![CloudMart homepage live](Screenshots/cloudmart-homepage.png)

![Live endpoint curl](Screenshots/azure-curl-public-endpoint.png)

![Container logs](Screenshots/azure-container-logs.png)

---

## 6. CI/CD Pipeline

**Screenshot:** GitHub Secrets settings page (9 secrets configured)
**Screenshot:** GitHub Actions CI + CD passing
**Screenshot:** ACR repository with image tags

![GitHub Secrets](Screenshots/github-secrets.png)

![GitHub Actions success](Screenshots/github-actions-success.png)

![ACR repository](Screenshots/acr-repository.png)

---

## 7. End-to-End Testing

### Example curl test commands:

```bash
BASE_URL="http://cloudmart-2036928.canadaeast.azurecontainer.io"

# Test 1: Homepage
curl -s -o /dev/null -w "%{http_code}" $BASE_URL/

# Test 2: Health
curl $BASE_URL/health | python3 -m json.tool

# Test 3: Products
curl $BASE_URL/api/v1/products | python3 -m json.tool

# Test 4: Single product
curl $BASE_URL/api/v1/products/prod-001 | python3 -m json.tool

# Test 5: Categories
curl $BASE_URL/api/v1/categories | python3 -m json.tool

# Test 6: Filter by category
curl "$BASE_URL/api/v1/products?category=Electronics" | python3 -m json.tool

# Test 7: Add to cart
curl -X POST $BASE_URL/api/v1/cart/items \
  -H "Content-Type: application/json" \
  -d '{"product_id":"prod-001","quantity":2}' | python3 -m json.tool

# Test 8: View cart
curl $BASE_URL/api/v1/cart | python3 -m json.tool
```

**Output:**
```
200
{
  "status": "ok",
  "message": "CloudMart API is healthy",
  "timestamp": "2026-04-09T18:00:00.000000+00:00"
}
```

```
[
  { "id": "prod-001", "name": "Wireless Headphones", "price": 99.99 },
  { "id": "prod-002", "name": "Smart Watch", "price": 149.99 }
]
```

```
{
  "id": "prod-001",
  "name": "Wireless Headphones",
  "category": "Electronics",
  "price": 99.99
}
```

```
[
  "Electronics",
  "Home",
  "Sports"
]
```

```
{
  "cart_items": [
    { "product_id": "prod-001", "quantity": 2, "subtotal": 199.98 }
  ],
  "total": 199.98
}
```

---

## 8. Notes

- CI pipeline: `.github/workflows/ci.yml`
- CD pipeline: `.github/workflows/deploy.yml`
- Secrets required: `ACR_NAME`, `ACR_LOGIN_SERVER`, `ACR_USERNAME`, `ACR_PASSWORD`, `COSMOS_ENDPOINT`, `COSMOS_KEY`, `AZURE_RESOURCE_GROUP`, `DNS_LABEL`, `AZURE_CREDENTIALS`

```bash
# Test 9: Place order
curl -X POST $BASE_URL/api/v1/orders | python3 -m json.tool

# Test 10: View orders
curl $BASE_URL/api/v1/orders | python3 -m json.tool

# Test 11: Verify cart is empty
curl $BASE_URL/api/v1/cart | python3 -m json.tool
```

**Output:**
```
{"status":"success","order_id":"order-001","total":199.98}
```

```
[
  {
    "order_id": "order-001",
    "status": "completed",
    "total": 199.98,
    "items": [
      {"product_id":"prod-001","quantity":2}
    ]
  }
]
```

```
{
  "cart_items": [],
  "total": 0.00
}
```

### 5 Browser Screenshots:
1. Homepage — full product catalog
   ![Homepage](Screenshots/cloudmart-product-catalog.png)
2. Category filter — filtered products
   ![Category filter](Screenshots/cloudmart-category-filter.png)
3. Cart — items with total price
   ![Cart](Screenshots/cloudmart-cart.png)
4. Order confirmation — successful placement
   ![Orders](Screenshots/cloudmart-orders.png)
5. /health endpoint — JSON response
   ![Health endpoint](Screenshots/azure-health-endpoint.png)

---

## 9. Reflection

### Q1: Security Model Comparison
In Milestone 1, virtual machines were protected using Network Security Groups (NSGs), which restrict traffic at the network level. In contrast, Azure Container Instances are directly exposed to the internet through a public IP, making them less secure by default. In production, I would add Azure Application Gateway with WAF, use private networking (VNet integration), and secure secrets using Azure Key Vault.

### Q2: Monitoring
Monitoring can be implemented using Azure Monitor to collect container logs and metrics, similar to how flow logs were used in Milestone 2. The `/health` endpoint provides application-level monitoring, while logs can be analyzed in Log Analytics to detect issues or abnormal traffic patterns. Alerts can also be configured to notify when failures or unusual activity occur.

### Q3: Scaling
If CloudMart needed to support 10,000 concurrent users, I would migrate from Azure Container Instances to Azure Kubernetes Service (AKS). This would allow horizontal scaling, load balancing, and better resource management. I would also introduce caching (e.g., Redis) to reduce database load and improve performance.
