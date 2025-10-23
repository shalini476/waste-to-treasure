from flask import Flask, render_template, request, redirect, session, jsonify
from db_config import get_db_connection
import bcrypt
import ai_matcher

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret"

# Helper: get user by email
def get_user_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        location = request.form['location']
        role = request.form['role']

        if get_user_by_email(email):
            return "Email already exists", 400

        pw_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name,email,password_hash,location,role) VALUES (%s,%s,%s,%s,%s)",
                    (name,email,pw_hash,location,role))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        user = get_user_by_email(email)
        if user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            return redirect('/dashboard')
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# Add waste item
@app.route('/add_waste', methods=['POST'])
def add_waste():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO waste_items (user_id, category, description, quantity, location) VALUES (%s,%s,%s,%s,%s)",
                (user_id, data['category'], data['description'], data['quantity'], data['location']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/dashboard')

# Add need item
@app.route('/add_need', methods=['POST'])
def add_need():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO need_items (user_id, category, description, quantity, location) VALUES (%s,%s,%s,%s,%s)",
                (user_id, data['category'], data['description'], data['quantity'], data['location']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/dashboard')

# Endpoint to get AI-suggested matches (returns JSON)
@app.route('/suggest_matches')
def suggest_matches():
    if 'user_id' not in session:
        return jsonify({"error":"login required"}), 401
    # ai_matcher will return a list of tuples or dicts
    matches = ai_matcher.suggest_all_matches()
    return jsonify(matches)

# Endpoint for logging whether a suggested match succeeded (label)
@app.route('/log_match', methods=['POST'])
def log_match():
    data = request.json  # {waste_id, need_id, matched: 0/1}
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO match_logs (waste_id, need_id, matched) VALUES (%s,%s,%s)",
                (data['waste_id'], data['need_id'], data['matched']))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(debug=True)
