# CSP451 Milestone 3 — Submission
**Student Name:** YOUR NAME
**Student ID:** XXXXXXX
**GitHub Repo:** https://github.com/YOUR_USERNAME/CSP451-milestone3
**Live URL:** http://cloudmart-XXXXXXX.<your-region>.azurecontainer.io

---

## 1. Azure Login and Resource Verification

```bash
az group show --name Student-RG-XXXXXXX -o table
az resource list --resource-group Student-RG-XXXXXXX -o table
```

**Output:**
```
(paste your output here)
```

**Screenshot:** Resource group overview showing ACI + Cosmos DB + ACR

---

## 2. Cosmos DB Setup

```bash
az cosmosdb show --name cloudmart-db-XXXXXXX --resource-group Student-RG-XXXXXXX -o table
```

**Screenshot:** Data Explorer with products, cart, and orders containers

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
(paste your curl output here)
```

---

## 4. Docker Build and Test

```bash
docker build -t cloudmart-api .
docker run -p 8080:80 -e COSMOS_ENDPOINT="..." -e COSMOS_KEY="..." cloudmart-api
```

**Screenshot:** docker build output
**Screenshot:** App running locally at http://localhost:8080

---

## 5. Azure Deployment

```bash
az container show --resource-group $RESOURCE_GROUP --name cloudmart-app -o table
```

**Screenshot:** ACI details (running, IP, FQDN)
**Screenshot:** curl /health and /api/v1/products from live URL
**Screenshot:** CloudMart homepage via public URL
**Screenshot:** Container logs

---

## 6. CI/CD Pipeline

**Screenshot:** GitHub Secrets settings page (9 secrets configured)
**Screenshot:** GitHub Actions CI + CD passing
**Screenshot:** ACR repository with image tags

---

## 7. End-to-End Testing

### All 11 curl test outputs:

```bash
BASE_URL="http://cloudmart-XXXXXXX.<your-region>.azurecontainer.io"

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

# Test 9: Checkout
curl -X POST $BASE_URL/api/v1/orders | python3 -m json.tool

# Test 10: View orders
curl $BASE_URL/api/v1/orders | python3 -m json.tool

# Test 11: Empty cart (verify cleared)
curl $BASE_URL/api/v1/cart | python3 -m json.tool
```

**Output:**
```
(paste your full test session output here)
```

### 5 Browser Screenshots:
1. Homepage — full product catalog
2. Category filter — filtered products
3. Cart — items with total price
4. Order confirmation — successful placement
5. /health endpoint — JSON response

---

## 8. Reflection

### Q1: Security Model Comparison
How does the security model of a publicly exposed ACI container differ from the NSG-protected VMs in Milestone 1? What additional protections would you add in production?

*Your answer here (2-3 sentences)*

### Q2: Monitoring
How could you apply the monitoring techniques from Milestone 2 (flow logs, IDS alerts) to this containerized deployment?

*Your answer here (2-3 sentences)*

### Q3: Scaling
What is one thing you would change about this architecture if CloudMart had 10,000 concurrent users?

*Your answer here (2-3 sentences)*
