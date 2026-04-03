from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- HASH FUNCTION ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- DB ----------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            age INTEGER,
            bp INTEGER,
            sugar INTEGER,
            risk TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------

@app.route('/')
def home():
    return render_template("login.html")

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = hash_password(request.form['password'])

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users VALUES (?,?)", (user, pwd))
            conn.commit()
            flash("Registration Successful! Please login.")
            return redirect('/')
        except:
            return "<h3>User already exists!</h3>"

    return render_template("register.html")

# LOGIN
@app.route('/login', methods=['POST'])
def login():
    user = request.form['username']
    pwd = hash_password(request.form['password'])

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
    result = cursor.fetchone()
    conn.close()

    if result:
        session['user'] = user
        return redirect('/dashboard')

    return "<h3>Invalid Login</h3>"

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template("dashboard.html", user=session['user'])

# PREDICT
@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect('/')

    try:
        age = int(request.form['age'])
        bp = int(request.form['bp'])
        sugar = int(request.form['sugar'])
    except:
        return "Invalid Input"

    risk = "Low"
    if bp > 140 or sugar > 150:
        risk = "High"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO history (username, age, bp, sugar, risk) VALUES (?,?,?,?,?)",
                   (session['user'], age, bp, sugar, risk))
    conn.commit()
    conn.close()

    return render_template("result.html", risk=risk, age=age, bp=bp, sugar=sugar)

# HISTORY
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT age, bp, sugar, risk FROM history WHERE username=?",
                   (session['user'],))
    data = cursor.fetchall()
    conn.close()

    return render_template("history.html", data=data)

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# RUN
if __name__ == "__main__":
    app.run(debug=True)
