"""
Cosmetic Production Management System - Flask Application
A complete production management system for cosmetic products

Author: Production Management System
Version: 1.0
Python: 3.8+
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'cosmetic-production-secret-key-2025'

# ============================================================================
# DATA MODELS
# ============================================================================

# Users Database
USERS = [
    {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
    {'username': 'sales', 'password': 'sales123', 'role': 'sales'},
    {'username': 'production', 'password': 'production123', 'role': 'production'},
    {'username': 'staff', 'password': 'staff123', 'role': 'staff'}
]

# Inventory Data
inventory = [
    {
        'id': 1,
        'sku': 'SHP-001',
        'name': 'Lavender Dreams Shampoo',
        'category': 'Shampoos',
        'quantity': 850,
        'min_quantity': 500,
        'price': 24.99,
        'supplier': 'Botanical Supplies Co',
        'expiry_date': '2026-08-15',
        'total_sold': 2450
    },
    {
        'id': 2,
        'sku': 'PRF-102',
        'name': 'Rose Garden Perfume',
        'category': 'Perfumes',
        'quantity': 320,
        'min_quantity': 200,
        'price': 89.99,
        'supplier': 'Essence International',
        'expiry_date': '2027-12-31',
        'total_sold': 1850
    },
    {
        'id': 3,
        'sku': 'CRM-203',
        'name': 'Vitamin C Face Cream',
        'category': 'Creams',
        'quantity': 0,
        'min_quantity': 300,
        'price': 45.99,
        'supplier': 'Derma Solutions Ltd',
        'expiry_date': '2026-03-20',
        'total_sold': 3200
    },
    {
        'id': 4,
        'sku': 'LOT-304',
        'name': 'Hydrating Body Lotion',
        'category': 'Lotions',
        'quantity': 1250,
        'min_quantity': 600,
        'price': 18.99,
        'supplier': 'Natural Ingredients Inc',
        'expiry_date': '2026-06-10',
        'total_sold': 4100
    },
    {
        'id': 5,
        'sku': 'SER-405',
        'name': 'Anti-Aging Serum',
        'category': 'Serums',
        'quantity': 180,
        'min_quantity': 150,
        'price': 125.99,
        'supplier': 'Premium Beauty Supply',
        'expiry_date': '2026-02-28',
        'total_sold': 1680
    }
]

# Production Lines
production_lines = [
    {
        'id': 1,
        'name': 'Shampoo Production Line',
        'product': 'Lavender Dreams Shampoo',
        'materials': [
            {'name': 'Lavender Extract', 'quantity': 50, 'unit': 'ml'},
            {'name': 'Surfactant Base', 'quantity': 200, 'unit': 'ml'},
            {'name': 'Preservatives', 'quantity': 5, 'unit': 'ml'}
        ],
        'output_rate': 450,
        'output_unit': 'bottles',
        'status': 'active',
        'efficiency': 92.5,
        'today_produced': 3325,
        'target_production': 3600
    },
    {
        'id': 2,
        'name': 'Perfume Blending Line',
        'product': 'Rose Garden Perfume',
        'materials': [
            {'name': 'Rose Essence', 'quantity': 30, 'unit': 'ml'},
            {'name': 'Alcohol Base', 'quantity': 40, 'unit': 'ml'},
            {'name': 'Fixative', 'quantity': 5, 'unit': 'ml'}
        ],
        'output_rate': 180,
        'output_unit': 'bottles',
        'status': 'active',
        'efficiency': 88.7,
        'today_produced': 1276,
        'target_production': 1440
    },
    {
        'id': 3,
        'name': 'Cream Manufacturing Line',
        'product': 'Vitamin C Face Cream',
        'materials': [
            {'name': 'Vitamin C Powder', 'quantity': 10, 'unit': 'g'},
            {'name': 'Emulsion Base', 'quantity': 45, 'unit': 'ml'}
        ],
        'output_rate': 300,
        'output_unit': 'jars',
        'status': 'maintenance',
        'efficiency': 0,
        'today_produced': 0,
        'target_production': 2400
    }
]

# Sales Orders
sales_orders = [
    {
        'id': 1,
        'order_number': 'ORD-2025-001',
        'client': 'BeautyMart Retail Chain',
        'products': [
            {'name': 'Lavender Dreams Shampoo', 'quantity': 500, 'price': 24.99},
            {'name': 'Coconut Oil Conditioner', 'quantity': 500, 'price': 28.99}
        ],
        'total_amount': 26990.00,
        'order_date': '2025-10-15',
        'due_date': '2025-10-30',
        'payment_status': 'Paid',
        'delivery_status': 'Delivered'
    },
    {
        'id': 2,
        'order_number': 'ORD-2025-002',
        'client': 'Luxury Spa International',
        'products': [
            {'name': 'Rose Garden Perfume', 'quantity': 200, 'price': 89.99}
        ],
        'total_amount': 17998.00,
        'order_date': '2025-10-18',
        'due_date': '2025-11-05',
        'payment_status': 'Pending',
        'delivery_status': 'Processing'
    },
    {
        'id': 3,
        'order_number': 'ORD-2025-003',
        'client': 'Online Beauty Store',
        'products': [
            {'name': 'Anti-Aging Serum', 'quantity': 150, 'price': 125.99}
        ],
        'total_amount': 18898.50,
        'order_date': '2025-10-10',
        'due_date': '2025-10-25',
        'payment_status': 'Overdue',
        'delivery_status': 'Shipped'
    }
]

# Security Alerts
alerts = [
    {
        'id': 1,
        'title': 'Unauthorized Access Detected',
        'description': 'Security cameras detected unauthorized personnel attempting to access Warehouse Section C.',
        'severity': 'Critical',
        'category': 'Theft',
        'location': 'Warehouse - Section C',
        'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
        'status': 'Active'
    },
    {
        'id': 2,
        'title': 'Fire Alarm Activated',
        'description': 'Smoke detected in Production Line 3 area. Automatic sprinkler system activated.',
        'severity': 'Critical',
        'category': 'Fire',
        'location': 'Production Floor - Line 3',
        'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
        'status': 'Active'
    },
    {
        'id': 3,
        'title': 'Shipment Discrepancy Alert',
        'description': 'Loading dock reported shipment leaving facility without matching order documentation.',
        'severity': 'Warning',
        'category': 'UnauthorizedShipment',
        'location': 'Loading Dock - Bay 2',
        'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
        'status': 'Resolved'
    }
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_inventory_status(item):
    """Get status of inventory item"""
    if item['quantity'] == 0:
        return 'Out of Stock'
    elif item['quantity'] < item['min_quantity']:
        return 'Low Stock'
    return 'In Stock'

def calculate_dashboard_stats():
    """Calculate dashboard statistics"""
    total_products = len(inventory)
    low_stock = sum(1 for item in inventory if get_inventory_status(item) == 'Low Stock')
    active_lines = sum(1 for line in production_lines if line['status'] == 'active')
    total_revenue = sum(order['total_amount'] for order in sales_orders)
    
    return {
        'total_products': total_products,
        'low_stock': low_stock,
        'active_lines': active_lines,
        'total_revenue': total_revenue
    }

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# ROUTES - AUTHENTICATION
# ============================================================================

@app.route('/')
def index():
    """Redirect to login or dashboard"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = next((u for u in USERS if u['username'] == username and u['password'] == password), None)
        
        if user:
            session['user'] = {'username': user['username'], 'role': user['role']}
            return jsonify({'success': True, 'role': user['role']})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('user', None)
    return redirect(url_for('login'))

# ============================================================================
# ROUTES - PAGES
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    if session['user']['role'] != 'admin':
        return redirect(url_for('inventory_page'))
    
    stats = calculate_dashboard_stats()
    return render_template('dashboard.html', user=session['user'], stats=stats)

@app.route('/inventory')
@login_required
def inventory_page():
    """Inventory management page"""
    return render_template('inventory.html', user=session['user'])

@app.route('/production')
@login_required
def production_page():
    """Production management page"""
    return render_template('production.html', user=session['user'])

@app.route('/sales')
@login_required
def sales_page():
    """Sales management page"""
    return render_template('sales.html', user=session['user'])

@app.route('/alerts')
@login_required
def alerts_page():
    """Security alerts page (admin only)"""
    if session['user']['role'] != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('alerts.html', user=session['user'])

# ============================================================================
# API ROUTES - INVENTORY
# ============================================================================

@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    """Get all inventory items"""
    items_with_status = []
    for item in inventory:
        item_copy = item.copy()
        item_copy['status'] = get_inventory_status(item)
        items_with_status.append(item_copy)
    return jsonify(items_with_status)

@app.route('/api/inventory', methods=['POST'])
@login_required
def add_inventory():
    """Add new inventory item"""
    if session['user']['role'] not in ['admin']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    new_id = max([item['id'] for item in inventory]) + 1 if inventory else 1
    
    new_item = {
        'id': new_id,
        'sku': data['sku'],
        'name': data['name'],
        'category': data['category'],
        'quantity': int(data['quantity']),
        'min_quantity': int(data['min_quantity']),
        'price': float(data['price']),
        'supplier': data['supplier'],
        'expiry_date': data.get('expiry_date', ''),
        'total_sold': 0
    }
    
    inventory.append(new_item)
    return jsonify({'success': True, 'item': new_item})

@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
@login_required
def update_inventory(item_id):
    """Update inventory item"""
    if session['user']['role'] not in ['admin']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    item = next((i for i in inventory if i['id'] == item_id), None)
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    item.update({
        'sku': data['sku'],
        'name': data['name'],
        'category': data['category'],
        'quantity': int(data['quantity']),
        'min_quantity': int(data['min_quantity']),
        'price': float(data['price']),
        'supplier': data['supplier'],
        'expiry_date': data.get('expiry_date', '')
    })
    
    return jsonify({'success': True, 'item': item})

@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@login_required
def delete_inventory(item_id):
    """Delete inventory item"""
    if session['user']['role'] not in ['admin']:
        return jsonify({'error': 'Permission denied'}), 403
    
    global inventory
    inventory = [i for i in inventory if i['id'] != item_id]
    return jsonify({'success': True})

# ============================================================================
# API ROUTES - PRODUCTION
# ============================================================================

@app.route('/api/production', methods=['GET'])
@login_required
def get_production():
    """Get all production lines"""
    return jsonify(production_lines)

@app.route('/api/production', methods=['POST'])
@login_required
def add_production():
    """Add new production line"""
    if session['user']['role'] not in ['admin', 'production']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    new_id = max([line['id'] for line in production_lines]) + 1 if production_lines else 1
    
    new_line = {
        'id': new_id,
        'name': data['name'],
        'product': data['product'],
        'materials': data.get('materials', []),
        'output_rate': int(data['output_rate']),
        'output_unit': data['output_unit'],
        'status': data['status'],
        'efficiency': float(data['efficiency']),
        'today_produced': int(data['today_produced']),
        'target_production': int(data['target_production'])
    }
    
    production_lines.append(new_line)
    return jsonify({'success': True, 'line': new_line})

@app.route('/api/production/<int:line_id>', methods=['PUT'])
@login_required
def update_production(line_id):
    """Update production line"""
    if session['user']['role'] not in ['admin', 'production']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    line = next((l for l in production_lines if l['id'] == line_id), None)
    
    if not line:
        return jsonify({'error': 'Line not found'}), 404
    
    line.update({
        'name': data['name'],
        'product': data['product'],
        'output_rate': int(data['output_rate']),
        'output_unit': data['output_unit'],
        'status': data['status'],
        'efficiency': float(data['efficiency']),
        'today_produced': int(data['today_produced']),
        'target_production': int(data['target_production'])
    })
    
    return jsonify({'success': True, 'line': line})

# ============================================================================
# API ROUTES - SALES
# ============================================================================

@app.route('/api/sales', methods=['GET'])
@login_required
def get_sales():
    """Get all sales orders"""
    return jsonify(sales_orders)

@app.route('/api/sales', methods=['POST'])
@login_required
def add_sales():
    """Add new sales order"""
    if session['user']['role'] not in ['admin', 'sales']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    new_id = max([order['id'] for order in sales_orders]) + 1 if sales_orders else 1
    
    new_order = {
        'id': new_id,
        'order_number': data['order_number'],
        'client': data['client'],
        'products': data.get('products', []),
        'total_amount': float(data['total_amount']),
        'order_date': data['order_date'],
        'due_date': data['due_date'],
        'payment_status': data['payment_status'],
        'delivery_status': data['delivery_status']
    }
    
    sales_orders.append(new_order)
    return jsonify({'success': True, 'order': new_order})

@app.route('/api/sales/<int:order_id>', methods=['PUT'])
@login_required
def update_sales(order_id):
    """Update sales order"""
    if session['user']['role'] not in ['admin', 'sales']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    order = next((o for o in sales_orders if o['id'] == order_id), None)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    order.update({
        'order_number': data['order_number'],
        'client': data['client'],
        'total_amount': float(data['total_amount']),
        'order_date': data['order_date'],
        'due_date': data['due_date'],
        'payment_status': data['payment_status'],
        'delivery_status': data['delivery_status']
    })
    
    return jsonify({'success': True, 'order': order})

# ============================================================================
# API ROUTES - ALERTS
# ============================================================================

@app.route('/api/alerts', methods=['GET'])
@login_required
def get_alerts():
    """Get all alerts (admin only)"""
    if session['user']['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return jsonify(alerts)

@app.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """Resolve an alert"""
    if session['user']['role'] != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    alert = next((a for a in alerts if a['id'] == alert_id), None)
    if alert:
        alert['status'] = 'Resolved'
        return jsonify({'success': True, 'alert': alert})
    
    return jsonify({'error': 'Alert not found'}), 404

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🎨 Cosmetic Production Management System - Python/Flask")
    print("=" * 70)
    print("\n✅ Server starting...")
    print("\n📍 Open your browser and go to: http://localhost:5000")
    print("\n🔑 Login credentials:")
    print("   • Admin:      admin / admin123")
    print("   • Sales:      sales / sales123")
    print("   • Production: production / production123")
    print("   • Staff:      staff / staff123")
    print("\n⏹  Press CTRL+C to stop the server")
    print("=" * 70)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
