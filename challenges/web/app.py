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

# Flag environment variables (Baselines)
BASE_SQL_INJECTION = "sql_1nj3ct10n_b4s1c"
BASE_COOKIE_MANIP = "c00k13_m4n1pul4t10n"
BASE_XSS = "xss_r3fl3ct3d_vuln"
BASE_IDOR = "1d0r_pr1v_3sc4l4t10n"
BASE_SOURCE_DIVER = "html_embedded_flag"

from utils.flag_gen import get_flag

def get_current_team_id():
    # In a real CTFd deployment with a reverse proxy, we'd get this from a header
    # or the CTFd session. For simulation/testing, we'll use a cookie or param.
    return request.args.get('team_id') or request.cookies.get('team_id', '1')

# Memes
GIF_SUCCESS = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZ3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5/mm0JgrgE2LBXq/giphy.gif" # Hackerman
GIF_FAILURE = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZ3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5/vB6K45Q0uUqPa/giphy.gif" # Ah Ah Ah

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
    .footer { font-size: 0.8em; color: #666; text-align: center; margin-top: 50px; }
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
        <!-- {{ fake_flag }} -->
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
    <div class="footer">Team ID: {{ team_id }} (Used for dynamic flag generation)</div>
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

# Secret Template
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
    <!-- {{ fake_flag }} -->
    <div id="ingredient-vault" data-recipe-secret="{{ flag }}" class="hidden"></div>
    <script>
        console.log("Vault loaded. Key in container metadata.");
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    team_id = get_current_team_id()
    fake_flag = get_flag("source_code_diver", team_id) + "_FAKE"
    return render_template_string(INDEX_TEMPLATE, fake_flag="HYVE_CTF{source_code_diver_FAKEHASH}")

@app.route('/menu')
def menu_page():
    return render_template_string(MENU_TEMPLATE, query="")

@app.route('/menu-search')
def menu_search():
    query = request.args.get('q', '')
    team_id = get_current_team_id()
    if '<script>' in query.lower() and ('alert' in query.lower() or 'console.log' in query.lower()):
        flag = get_flag(BASE_XSS, team_id)
        return f"""
        <html><head><style>{COMMON_CSS}</style></head>
        <body>
            <div class="card" style="text-align:center;">
                <h2>XSS ALERT! BISTRO HACKED!</h2>
                <p>Waitstaff alerted. Reward token revealed for Team {team_id}:</p>
                <div style="font-size: 1.5em; color: lime;">{flag}</div>
                <img src="{GIF_SUCCESS}" class="meme">
                <br><br><a href="/" class="btn">ABORT</a>
            </div>
        </body></html>
        """
    return render_template_string(MENU_TEMPLATE, query=query)

@app.route('/staff-login', methods=['GET', 'POST'])
def staff_login():
    team_id = get_current_team_id()
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
            flag = get_flag(BASE_SQL_INJECTION, team_id)
            message = f"Welcome back, Captain. Here is your bypass token: {flag}"
            return render_template_string(STAFF_LOGIN_TEMPLATE, message=message, success=True)
        else:
            message = "ACCESS DENIED: Credentials mismatch. Magic word needed?"
            return render_template_string(STAFF_LOGIN_TEMPLATE, message=message, success=False, gif=GIF_FAILURE)
    except Exception as e:
        return render_template_string(STAFF_LOGIN_TEMPLATE, message=f"DB Error: {str(e)}", success=False, gif=GIF_FAILURE)

@app.route('/profile')
def profile_page():
    team_id = get_current_team_id()
    role = request.cookies.get('role', 'user')
    is_admin = (role == 'admin')
    flag = get_flag(BASE_COOKIE_MANIP, team_id)
    gif = GIF_SUCCESS if is_admin else GIF_FAILURE
    
    response = make_response(
        render_template_string(
            PROFILE_TEMPLATE,
            role=role,
            is_admin=is_admin,
            flag=flag,
            gif=gif,
            team_id=team_id
        )
    )
    if not request.cookies.get('role'):
        response.set_cookie('role', 'user')
    if not request.cookies.get('team_id'):
        response.set_cookie('team_id', team_id)
    return response

@app.route('/secret-ingredients')
def secret_ingredients():
    team_id = get_current_team_id()
    flag = get_flag(BASE_SOURCE_DIVER, team_id)
    return render_template_string(SECRET_TEMPLATE, flag=flag, fake_flag="HYVE_CTF{you_found_it}_FAKEHASH")

@app.route('/api/order/tracking/<int:order_id>')
def track_order(order_id):
    team_id = get_current_team_id()
    # IDOR VULNERABLE
    try:
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, secret FROM users WHERE id=?", (order_id,))
        record = cursor.fetchone()
        conn.close()
        if record:
            if record[0] == 1: # Admin Order
                flag = get_flag(BASE_IDOR, team_id)
                return jsonify({
                    'order_id': order_id,
                    'customer': record[1],
                    'email': record[2],
                    'secret_note': flag 
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
    # Initialize DB with some fake data if not exists
    if not os.path.exists('ctf.db'):
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT, secret TEXT)")
        cursor.execute("INSERT INTO users VALUES (1, 'admin', 'complex_password_123', 'admin@hyvebistro.ctf', 'HYVE_CTF{placeholder}')")
        cursor.execute("INSERT INTO users VALUES (1001, 'guest', 'guest', 'guest@example.com', 'No secrets here')")
        conn.commit()
        conn.close()
    app.run(host='0.0.0.0', port=8080, debug=True)
