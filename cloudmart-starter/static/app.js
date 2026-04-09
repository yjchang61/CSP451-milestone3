/**
 * CloudMart — Frontend JavaScript
 * Handles product display, cart, orders via the /api/v1/ endpoints.
 * CSP451 Milestone 3
 */

const API_BASE = '/api/v1';
let allProducts = [];

// ─── Initialization ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    loadCart();
});

// ─── Section Navigation ─────────────────────────────────────────────
function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

    // Show selected
    const sectionEl = document.getElementById(`${section}-section`);
    if (sectionEl) sectionEl.classList.add('active');

    // Highlight nav link
    const links = document.querySelectorAll('.nav-link');
    const index = section === 'shop' ? 0 : section === 'cart' ? 1 : 2;
    if (links[index]) links[index].classList.add('active');

    // Reload data when switching
    if (section === 'cart') loadCart();
    if (section === 'orders') loadOrders();
}

// ─── Products ────────────────────────────────────────────────────────
async function loadProducts() {
    try {
        const res = await fetch(`${API_BASE}/products`);
        allProducts = await res.json();
        renderProducts(allProducts);
        loadCategories();
    } catch (err) {
        document.getElementById('products-grid').innerHTML =
            '<p class="empty-message">⚠️ Could not load products. Check the API connection.</p>';
    }
}

function renderProducts(products) {
    const grid = document.getElementById('products-grid');
    if (!products.length) {
        grid.innerHTML = '<p class="empty-message">No products found.</p>';
        return;
    }
    grid.innerHTML = products.map(p => `
        <div class="product-card">
            <div class="product-image">
                <img src="${p.image_url || 'https://img.icons8.com/3d-fluency/94/box.png'}"
                     alt="${p.name}"
                     onerror="this.src='https://img.icons8.com/3d-fluency/94/box.png'">
            </div>
            <div class="product-info">
                <div class="product-category">${p.category}</div>
                <div class="product-name">${p.name}</div>
                <div class="product-desc">${p.description}</div>
                <div class="product-footer">
                    <span class="product-price">$${p.price.toFixed(2)}</span>
                    <button class="btn btn-primary" onclick="addToCart('${p.id}')">
                        + Add
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

async function loadCategories() {
    try {
        const res = await fetch(`${API_BASE}/categories`);
        const categories = await res.json();
        const container = document.getElementById('category-filters');
        container.innerHTML = `
            <button class="filter-btn active" onclick="filterProducts('all')">All</button>
            ${categories.map(c => `<button class="filter-btn" onclick="filterProducts('${c}')">${c}</button>`).join('')}
        `;
    } catch (err) {
        console.error('Failed to load categories', err);
    }
}

function filterProducts(category) {
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    if (category === 'all') {
        renderProducts(allProducts);
    } else {
        renderProducts(allProducts.filter(p => p.category === category));
    }
}

// ─── Cart ────────────────────────────────────────────────────────────
async function addToCart(productId) {
    try {
        const res = await fetch(`${API_BASE}/cart/items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });
        const data = await res.json();
        if (res.ok) {
            showToast(`✅ ${data.item.product_name} added to cart!`);
            updateCartBadge();
        } else {
            showToast(`❌ ${data.detail || 'Error adding to cart'}`);
        }
    } catch (err) {
        showToast('❌ Network error — could not add to cart');
    }
}

async function loadCart() {
    try {
        const res = await fetch(`${API_BASE}/cart`);
        const items = await res.json();
        renderCart(items);
        updateCartBadgeWithCount(items.length);
    } catch (err) {
        console.error('Failed to load cart', err);
    }
}

function renderCart(items) {
    const container = document.getElementById('cart-items');
    const summary = document.getElementById('cart-summary');

    if (!items.length) {
        container.innerHTML = '<p class="empty-message">Your cart is empty. Start shopping!</p>';
        summary.style.display = 'none';
        return;
    }

    let total = 0;
    container.innerHTML = items.map(item => {
        total += item.subtotal;
        return `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.product_name}</div>
                    <div class="cart-item-meta">Qty: ${item.quantity} × $${item.price.toFixed(2)}</div>
                </div>
                <div class="cart-item-subtotal">$${item.subtotal.toFixed(2)}</div>
                <button class="btn btn-danger" onclick="removeFromCart('${item.id}')">✕</button>
            </div>
        `;
    }).join('');

    document.getElementById('cart-total').textContent = `$${total.toFixed(2)}`;
    summary.style.display = 'block';
}

async function removeFromCart(itemId) {
    try {
        await fetch(`${API_BASE}/cart/items/${itemId}`, { method: 'DELETE' });
        showToast('🗑️ Item removed from cart');
        loadCart();
    } catch (err) {
        showToast('❌ Error removing item');
    }
}

async function updateCartBadge() {
    try {
        const res = await fetch(`${API_BASE}/cart`);
        const items = await res.json();
        updateCartBadgeWithCount(items.length);
    } catch (err) { /* ignore */ }
}

function updateCartBadgeWithCount(count) {
    document.getElementById('cart-badge').textContent = count;
}

// ─── Orders ──────────────────────────────────────────────────────────
async function placeOrder() {
    try {
        const res = await fetch(`${API_BASE}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (res.ok) {
            showToast('🎉 Order placed successfully!');
            loadCart();
            showSection('orders');
        } else {
            showToast(`❌ ${data.detail || 'Error placing order'}`);
        }
    } catch (err) {
        showToast('❌ Network error — could not place order');
    }
}

async function loadOrders() {
    try {
        const res = await fetch(`${API_BASE}/orders`);
        const orders = await res.json();
        renderOrders(orders);
    } catch (err) {
        document.getElementById('orders-list').innerHTML =
            '<p class="empty-message">⚠️ Could not load orders.</p>';
    }
}

function renderOrders(orders) {
    const container = document.getElementById('orders-list');
    if (!orders.length) {
        container.innerHTML = '<p class="empty-message">No orders yet. Place your first order!</p>';
        return;
    }

    container.innerHTML = orders.map(order => `
        <div class="order-card">
            <div class="order-header">
                <span class="order-id">Order #${order.id.substring(0, 8)}...</span>
                <span class="order-status">${order.status}</span>
            </div>
            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item-row">
                        <span>${item.product_name} × ${item.quantity}</span>
                        <span>$${item.subtotal.toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
            <div class="order-footer">
                <span class="order-date">${new Date(order.created_at).toLocaleString()}</span>
                <span class="order-total">Total: $${order.total.toFixed(2)}</span>
            </div>
        </div>
    `).join('');
}

// ─── Toast Notification ──────────────────────────────────────────────
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}
