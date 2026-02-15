#!/usr/bin/env python3
"""
Hyve Bistro - Premium Restaurant App
A gamified web challenge with multiple vulnerabilities
"""

from flask import Flask, request, render_template_string, jsonify, make_response
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'bistro_secret_key'

# Flag environment variables
FLAG_SQL_INJECTION = os.environ.get('FLAG_SQL_INJECTION', 'HYVE_CTF{sql_1nj3ct10n_b4s1c_HASH}')
FLAG_COOKIE_MANIP = os.environ.get('FLAG_COOKIE_MANIP', 'HYVE_CTF{c00k13_m4n1pul4t10n_HASH}')
FLAG_XSS = os.environ.get('FLAG_XSS', 'HYVE_CTF{xss_r3fl3ct3d_vuln_HASH}')
FLAG_IDOR = os.environ.get('FLAG_IDOR', 'HYVE_CTF{1d0r_pr1v_3sc4l4t10n_HASH}')
FLAG_SOURCE_DIVER = os.environ.get('FLAG_SOURCE_DIVER', 'HYVE_CTF{html_embedded_flag_HASH}')

# Memes
GIF_SUCCESS = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZ3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5/mm0JgrgE2LBXq/giphy.gif" # Hackerman
GIF_FAILURE = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZ3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5/vB6K45Q0uUqPa/giphy.gif" # Ah Ah Ah

# Layout CSS
COMMON_CSS = """
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; max-width: 900px; margin: 30px auto; padding: 20px; line-height: 1.6; }
    h1, h2, h3 { color: #ffcc00; text-transform: uppercase; letter-spacing: 2px; }
    .card { background: #1e1e1e; padding: 25px; margin: 20px 0; border: 1px solid #333; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .btn { background: #ffcc00; color: #000; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold; transition: 0.3s; cursor: pointer; border: none; }
    .btn:hover { background: #ffaa00; transform: translateY(-2px); }
    input { width: 100%; padding: 12px; margin: 10px 0; background: #2d2d2d; color: #fff; border: 1px solid #444; border-radius: 4px; }
    .meme { width: 100%; border-radius: 8px; margin-top: 15px; border: 1px solid #ffcc00; }
    .nav { margin-bottom: 30px; border-bottom: 2px solid #ffcc00; padding-bottom: 15px; }
    .nav a { color: #ffcc00; margin-right: 20px; text-decoration: none; font-weight: bold; }
    .nav a:hover { color: #fff; }
    .footer { margin-top: 50px; font-size: 0.8em; color: #666; text-align: center; }
"""

# Home Page Template
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hyve Bistro // High-End Dining</title>
    <style>""" + COMMON_CSS + """</style>
</head>
<body>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/menu">Menu & Order</a>
        <a href="/profile">My Loyalty</a>
        <a href="/staff-login">Staff Access</a>
    </div>
    <h1>Welcome to Hyve Bistro</h1>
    <div class="card">
        <h3>Today's Special: The 'Zero Day' Steak</h3>
        <p>A cut of meat so rare, it hasn't even been patched yet. Served with a side of encrypted greens.</p>
        <img src="https://images.pexels.com/photos/1267320/pexels-photo-1267320.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1" style="width:100%; border-radius:8px;">
    </div>
    <div class="card">
        <h3>Fast Delivery Guaranteed</h3>
        <p>Our couriers use cutting-edge routing protocols to bypass any traffic congestion.</p>
        <a href="/api/order/tracking/1001" class="btn">Track Last Order</a>
    </div>
    <div class="footer">
        © 2026 Hyve Bistro. All rights reserved. 
        <!-- HYVE_CTF{source_code_diver_FAKEHASH} -->
    </div>
</body>
</html>
"""

# Menu Template
MENU_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Menu // Hyve Bistro</title>
    <style>""" + COMMON_CSS + """</style>
</head>
<body>
    <div class="nav"><a href="/">Home</a></div>
    <h2>Bistro Menu</h2>
    <div class="card">
        <form action="/menu-search" method="GET">
            <input type="text" name="q" placeholder="Search for ingredients..." value="{{ query }}">
            <button type="submit" class="btn">Search Ingredients</button>
        </form>
    </div>
    {% if query %}
    <div class="card">
        <h3>Scan Results for: {{ query|safe }}</h3>
        <p>Searching our database for "{{ query|safe }}" related ingredients...</p>
    </div>
    {% endif %}
    <div class="card">
        <h3>Secret Recipe Inquiries?</h3>
        <!-- TODO: Secure our hidden ingredient list -->
        <a href="/secret-ingredients" class="btn">View Source Info</a>
    </div>
</body>
</html>
"""

# Profile Template
PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Loyalty // Hyve Bistro</title>
    <style>""" + COMMON_CSS + """ .gold { color: #ffcc00; font-weight: bold; border: 2px solid #ffcc00; padding: 10px; } </style>
</head>
<body>
    <div class="nav"><a href="/">Home</a></div>
    <h2>Membership Status</h2>
    <div class="card">
        <p><strong>Current Tier:</strong> {{ role }}</p>
        {% if is_admin %}
        <div class="gold">
            <p>🌟 GOLD STATUS ACHIEVED! 🌟</p>
            <p>Welcome, Valued Guest. Here is your early-access coupon code:</p>
            <p>Code: <strong>{{ flag }}</strong></p>
            <img src="{{ gif }}" class="meme">
        </div>
        {% else %}
        <p>Spend $500 more to unlock <strong>Gold Membership</strong> rewards.</p>
        <img src="{{ gif }}" class="meme">
        {% endif %}
    </div>
</body>
</html>
"""

# Staff Login Template
STAFF_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Staff Portal // Hyve Bistro</title>
    <style>""" + COMMON_CSS + """</style>
</head>
<body>
    <div class="nav"><a href="/">Home</a></div>
    <h2>Waitstaff Login</h2>
    <div class="card">
        <form method="POST">
            <input type="text" name="username" placeholder="Employee ID" required>
            <input type="password" name="password" placeholder="Access Code" required>
            <button type="submit" class="btn">Log In</button>
        </form>
        {% if message %}
        <p style="color: {{ 'lime' if success else 'red' }}; margin-top:20px;">{{ message }}</p>
        {% if not success %}<img src="{{ gif }}" class="meme">{% endif %}
        {% endif %}
    </div>
</body>
</html>
"""

# Source/Secret Template
SECRET_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Secrets // Hyve Bistro</title>
    <style>""" + COMMON_CSS + """ .hidden { display: none; } </style>
</head>
<body>
    <div class="nav"><a href="/">Home</a></div>
    <h2>Ingredient Sources</h2>
    <p>We source only the finest local components.</p>
    <div class="card">
        <ul>
            <li>Organic Buffer Overflows</li>
            <li>Hand-picked SQL Tokens</li>
            <li>Artisanal Cookies</li>
        </ul>
    </div>
    <!-- HYVE_CTF{you_found_it}_FAKEHASH -->
    <div id="ingredient-vault" data-recipe-secret="{{ flag }}" class="hidden"></div>
    <script>
        console.log("Vault loaded. Key in container metadata.");
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return INDEX_TEMPLATE

@app.route('/menu')
def menu_page():
    return render_template_string(MENU_TEMPLATE)

@app.route('/menu-search')
def menu_search():
    query = request.args.get('q', '')
    if '<script>' in query.lower() and 'alert' in query.lower():
        return f"""
        <html><head><style>{COMMON_CSS}</style></head>
        <body>
            <div class="card" style="text-align:center;">
                <h2>XSS ALERT! BISTRO HACKED!</h2>
                <p>Waitstaff alerted. Reward token revealed:</p>
                <div style="font-size: 1.5em; color: lime;">{FLAG_XSS}</div>
                <img src="{GIF_SUCCESS}" class="meme">
                <br><br><a href="/" class="btn">ABORT</a>
            </div>
        </body></html>
        """
    return render_template_string(MENU_TEMPLATE, query=query)

@app.route('/staff-login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'GET':
        return render_template_string(STAFF_LOGIN_TEMPLATE)
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    try:
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        # VULNERABLE TO SQLI
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            message = f"Welcome back, Captain. Here is your bypass token: {FLAG_SQL_INJECTION}"
            return render_template_string(STAFF_LOGIN_TEMPLATE, message=message, success=True)
        else:
            message = "ACCESS DENIED: Credentials mismatch. Magic word needed?"
            return render_template_string(STAFF_LOGIN_TEMPLATE, message=message, success=False, gif=GIF_FAILURE)
    except Exception as e:
        return render_template_string(STAFF_LOGIN_TEMPLATE, message=f"DB Error: {str(e)}", success=False, gif=GIF_FAILURE)

@app.route('/profile')
def profile_page():
    role = request.cookies.get('role', 'user')
    is_admin = (role == 'admin')
    gif = GIF_SUCCESS if is_admin else "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZ3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5/vB6K45Q0uUqPa/giphy.gif"
    
    response = make_response(
        render_template_string(
            PROFILE_TEMPLATE,
            role=role,
            is_admin=is_admin,
            flag=FLAG_COOKIE_MANIP,
            gif=gif
        )
    )
    if not request.cookies.get('role'):
        response.set_cookie('role', 'user')
    return response

@app.route('/secret-ingredients')
def secret_ingredients():
    return render_template_string(SECRET_TEMPLATE, flag=FLAG_SOURCE_DIVER)

@app.route('/api/order/tracking/<int:order_id>')
def track_order(order_id):
    # IDOR VULNERABLE
    try:
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, secret FROM users WHERE id=?", (order_id,))
        record = cursor.fetchone()
        conn.close()
        if record:
            # Mask sensitive data for non-admins, but the IDOR logic allows viewing ID=1 (Admin)
            if record[0] == 1:
                return jsonify({
                    'order_id': order_id,
                    'customer': record[1],
                    'email': record[2],
                    'secret_note': record[3] # THE FLAG
                })
            else:
                return jsonify({
                    'order_id': order_id,
                    'customer': record[1],
                    'status': 'In Transit',
                    'note': 'Order contains extra napkins.'
                })
        return jsonify({'error': 'Order not found'}), 404
    except:
        return jsonify({'error': 'Server Error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
