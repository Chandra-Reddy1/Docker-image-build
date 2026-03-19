from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = "welcome-app-secret-key"

# Demo users (username: password)
USERS = {
    "admin": "admin123",
    "alice": "alice123",
    "bob":   "chnadra",
}

# ─── HTML Templates ──────────────────────────────────────────────────────────

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Login — Welcome App</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        }
        .card {
            background: #fff;
            border-radius: 24px;
            padding: 52px 44px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.4);
            text-align: center;
        }
        .logo { font-size: 56px; margin-bottom: 18px; }
        h1 { color: #1a1a2e; font-size: 1.75rem; font-weight: 700; margin-bottom: 6px; }
        .sub { color: #999; font-size: 0.92rem; margin-bottom: 36px; }
        .form-group { text-align: left; margin-bottom: 18px; }
        label { display: block; font-size: 0.82rem; font-weight: 600; color: #555; margin-bottom: 7px; letter-spacing: 0.4px; text-transform: uppercase; }
        .input-wrap { position: relative; }
        input {
            width: 100%;
            padding: 13px 42px 13px 16px;
            border: 2px solid #e8e8e8;
            border-radius: 11px;
            font-size: 0.97rem;
            outline: none;
            transition: border-color 0.2s;
            color: #1a1a2e;
            background: #fafafa;
        }
        input:focus { border-color: #6c63ff; background: #fff; }
        .eye-btn {
            position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
            background: none; border: none; cursor: pointer; font-size: 18px; padding: 0;
        }
        .btn {
            width: 100%;
            padding: 14px;
            margin-top: 8px;
            background: linear-gradient(135deg, #6c63ff, #4b44cc);
            color: #fff;
            border: none;
            border-radius: 11px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            letter-spacing: 0.3px;
            transition: opacity 0.2s, transform 0.15s;
        }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }
        .btn:active { transform: translateY(0); }
        .error {
            background: #fff0f0;
            border: 1px solid #ffb3b3;
            color: #d63031;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 0.88rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .hint { margin-top: 22px; font-size: 0.8rem; color: #bbb; }
        .hint span { color: #6c63ff; font-weight: 600; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">🙌</div>
        <h1>Welcome to my world</h1>
        <p class="sub">Sign in to access your dashboard</p>

        {% if error %}
        <div class="error">⚠️ {{ error }}</div>
        {% endif %}

        <form method="POST" action="/login">
            <div class="form-group">
                <label>Username</label>
                <div class="input-wrap">
                    <input type="text" name="username" placeholder="Enter your username"
                           value="{{ username or '' }}" required autofocus/>
                </div>
            </div>
            <div class="form-group">
                <label>Password</label>
                <div class="input-wrap">
                    <input type="password" name="password" id="pwdInput" placeholder="Enter your password" required/>
                    <button type="button" class="eye-btn" onclick="togglePwd()">👁</button>
                </div>
            </div>
            <button type="submit" class="btn">Sign In →</button>
        </form>

        <p class="hint">Demo users: <span>admin</span> / <span>alice</span> / <span>bob</span></p>
    </div>
    <script>
        function togglePwd() {
            const inp = document.getElementById('pwdInput');
            inp.type = inp.type === 'password' ? 'text' : 'password';
        }
    </script>
</body>
</html>
"""

WELCOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Welcome to my page, {{ username }}!</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            padding: 20px;
        }
        .card {
            background: #fff;
            border-radius: 24px;
            padding: 56px 44px;
            width: 100%;
            max-width: 480px;
            text-align: center;
            box-shadow: 0 30px 80px rgba(0,0,0,0.4);
            animation: popIn 0.5s ease;
        }
        @keyframes popIn {
            from { opacity: 0; transform: scale(0.94) translateY(16px); }
            to   { opacity: 1; transform: scale(1) translateY(0); }
        }
        .avatar {
            width: 90px; height: 90px;
            background: linear-gradient(135deg, #6c63ff, #4b44cc);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 40px;
            margin: 0 auto 24px;
            box-shadow: 0 8px 24px rgba(108,99,255,0.35);
        }
        h1 { color: #1a1a2e; font-size: 2rem; font-weight: 700; margin-bottom: 8px; }
        .greeting { color: #6c63ff; font-size: 1rem; font-weight: 600; margin-bottom: 6px; }
        .time { color: #aaa; font-size: 0.85rem; margin-bottom: 36px; }
        .info-grid {
            display: grid; grid-template-columns: 1fr 1fr;
            gap: 14px; margin-bottom: 32px;
        }
        .info-box {
            background: #f7f7ff;
            border: 1px solid #ebebff;
            border-radius: 14px;
            padding: 18px 14px;
        }
        .info-box .label { font-size: 0.75rem; color: #999; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 6px; }
        .info-box .value { font-size: 1rem; font-weight: 700; color: #1a1a2e; }
        .btn-logout {
            width: 100%;
            padding: 13px;
            background: linear-gradient(135deg, #ff6b6b, #c0392b);
            color: #fff;
            border: none;
            border-radius: 11px;
            font-size: 0.97rem;
            font-weight: 700;
            cursor: pointer;
            transition: opacity 0.2s;
            text-decoration: none;
            display: block;
        }
        .btn-logout:hover { opacity: 0.88; }
    </style>
</head>
<body>
    <div class="card">
        <div class="avatar">{{ username[0].upper() }}</div>
        <p class="greeting">{{ greeting }},</p>
        <h1>{{ username.capitalize() }}! 🎉</h1>
        <p class="time">{{ now }}</p>

        <div class="info-grid">
            <div class="info-box">
                <div class="label">Status</div>
                <div class="value">✅ Active</div>
            </div>
            <div class="info-box">
                <div class="label">Role</div>
                <div class="value">{{ "Admin" if username == "admin" else "User" }}</div>
            </div>
            <div class="info-box">
                <div class="label">Logged in</div>
                <div class="value">Just now</div>
            </div>
            <div class="info-box">
                <div class="label">Session</div>
                <div class="value">🟢 Live</div>
            </div>
        </div>

        <a href="/logout" class="btn-logout">Sign Out</a>
    </div>
</body>
</html>
"""

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("welcome"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username in USERS and USERS[username] == password:
            session["username"] = username
            return redirect(url_for("welcome"))
        else:
            error = "Invalid username or password. Please try again."
    return render_template_string(LOGIN_HTML, error=error, username=username)

@app.route("/welcome")
def welcome():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    now = datetime.now().strftime("%A, %d %B %Y — %I:%M %p")
    return render_template_string(WELCOME_HTML, username=username, greeting=greeting, now=now)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "app": "Welcome Login App", "version": "1.0.0"})

# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 App running at http://localhost:5000")
    print("👤 Demo users: admin/admin123 | alice/alice123 | bob/bob456")
    app.run(host="0.0.0.0", port=5000, debug=True)