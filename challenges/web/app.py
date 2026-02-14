#!/usr/bin/env python3
"""
CTF Web Challenges Application
Contains 4 vulnerable endpoints for educational purposes
"""

from flask import Flask, request, render_template_string, jsonify, make_response
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'insecure_secret_key'

# Flag environment variables
FLAG_SQL_INJECTION = os.environ.get('FLAG_SQL_INJECTION', 'FLAG{sql_1nj3ct10n_b4s1c}')
FLAG_COOKIE_MANIP = os.environ.get('FLAG_COOKIE_MANIP', 'FLAG{c00k13_m4n1pul4t10n}')
FLAG_XSS = os.environ.get('FLAG_XSS', 'FLAG{xss_r3fl3ct3d_vuln}')
FLAG_IDOR = os.environ.get('FLAG_IDOR', 'FLAG{1d0r_pr1v_3sc4l4t10n}')

# Index page template
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hivye CTF 2026 - Web Challenges</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .challenge { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .challenge h3 { margin-top: 0; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Hivye CTF 2026 - Web Challenges</h1>
    
    <div class="challenge">
        <h3>Challenge 1: Login Bypass (200 points)</h3>
        <p>SQL Injection vulnerability</p>
        <a href="/login">Go to Login Page</a>
    </div>
    
    <div class="challenge">
        <h3>Challenge 2: Cookie Monster (200 points)</h3>
        <p>Cookie manipulation challenge</p>
        <a href="/profile">Go to Profile Page</a>
    </div>
    
    <div class="challenge">
        <h3>Challenge 3: Script Injection (300 points)</h3>
        <p>Reflected XSS vulnerability</p>
        <a href="/search?q=test">Go to Search Page</a>
    </div>
    
    <div class="challenge">
        <h3>Challenge 4: Object Reference (300 points)</h3>
        <p>IDOR (Insecure Direct Object Reference)</p>
        <a href="/api/user/2">View API Endpoint</a>
    </div>
</body>
</html>
"""

# Login page template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Hivye CTF</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
        h2 { color: #333; }
        form { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #0066cc; color: white; border: none; cursor: pointer; }
        button:hover { background: #0052a3; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <h2>Login</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    {% if message %}
    <p class="{{ 'success' if success else 'error' }}">{{ message }}</p>
    {% endif %}
    <p><a href="/">Back to Home</a></p>
</body>
</html>
"""

# Profile page template
PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Profile - Hivye CTF</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 100px auto; padding: 20px; }
        h2 { color: #333; }
        .info { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .admin { background: #d4edda; border: 2px solid #28a745; }
    </style>
</head>
<body>
    <h2>User Profile</h2>
    <div class="info {{ 'admin' if is_admin else '' }}">
        <p><strong>Role:</strong> {{ role }}</p>
        {% if is_admin %}
        <p><strong>Congratulations!</strong></p>
        <p><strong>Flag:</strong> {{ flag }}</p>
        {% else %}
        <p>You need admin privileges to view sensitive information.</p>
        {% endif %}
    </div>
    <p><a href="/">Back to Home</a></p>
</body>
</html>
"""

# Search page template
SEARCH_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Search - Hivye CTF</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 100px auto; padding: 20px; }
        h2 { color: #333; }
        form { margin: 20px 0; }
        input[type="text"] { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #0066cc; color: white; border: none; cursor: pointer; }
        .results { background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <h2>Search</h2>
    <form method="GET">
        <input type="text" name="q" placeholder="Enter search query..." value="{{ query }}">
        <button type="submit">Search</button>
    </form>
    {% if query %}
    <div class="results">
        <p>Search results for: {{ query }}</p>
    </div>
    {% endif %}
    <p><a href="/">Back to Home</a></p>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with links to all challenges"""
    return INDEX_TEMPLATE

@app.route('/login', methods=['GET', 'POST'])
def login():
    """SQL Injection vulnerable login endpoint"""
    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE)
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    try:
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        
        # VULNERABLE: SQL Injection through f-string
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            message = f"Login successful! Flag: {FLAG_SQL_INJECTION}"
            return render_template_string(LOGIN_TEMPLATE, message=message, success=True)
        else:
            message = "Invalid credentials"
            return render_template_string(LOGIN_TEMPLATE, message=message, success=False)
    except Exception as e:
        message = f"Error: {str(e)}"
        return render_template_string(LOGIN_TEMPLATE, message=message, success=False)

@app.route('/profile')
def profile():
    """Cookie manipulation vulnerable endpoint"""
    role = request.cookies.get('role', 'user')
    is_admin = (role == 'admin')
    
    response = make_response(
        render_template_string(
            PROFILE_TEMPLATE,
            role=role,
            is_admin=is_admin,
            flag=FLAG_COOKIE_MANIP
        )
    )
    
    # Set a default cookie if none exists
    if not request.cookies.get('role'):
        response.set_cookie('role', 'user')
    
    return response

@app.route('/search')
def search():
    """Reflected XSS vulnerable search endpoint"""
    query = request.args.get('q', '')
    
    # Check if XSS payload with alert is present
    if '<script>' in query.lower() and 'alert' in query.lower():
        # Return flag if XSS is detected
        response = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Search - Hivye CTF</title></head>
        <body>
            <h2>XSS Detected!</h2>
            <p>Congratulations! You found the XSS vulnerability.</p>
            <p><strong>Flag:</strong> {FLAG_XSS}</p>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
        """
        return response
    
    # VULNERABLE: Reflects user input without sanitization
    return render_template_string(SEARCH_TEMPLATE, query=query)

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    """IDOR vulnerable API endpoint"""
    try:
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        
        # VULNERABLE: No authorization check
        cursor.execute("SELECT id, username, email, secret FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'secret': user[3]
            })
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
