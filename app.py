from flask import Flask, render_template, request, redirect, session, jsonify, flash
from db_config import get_db_connection
import bcrypt
import ai_matcher

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret"


# ---------------- Helper ----------------
def get_user_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


# ---------------- Routes ----------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        location = request.form['location']
        role = request.form['role']

        if get_user_by_email(email):
            flash("Email already registered!", "danger")
            return redirect('/register')

        pw_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash, location, role) VALUES (%s, %s, %s, %s, %s)",
            (name, email, pw_hash, location, role)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Registered successfully! Please log in.", "success")
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        user = get_user_by_email(email)

        if user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            return redirect('/dashboard')

        flash("Invalid credentials!", "danger")
        return redirect('/login')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('dashboard.html', user=user)

# ---------------- Add Waste ----------------
@app.route('/add_waste', methods=['POST'])
def add_waste():
    if 'user_id' not in session:
        return redirect('/login')
    data = request.form
    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO waste_items (user_id, category, description, quantity, location)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, data['category'], data['description'], data['quantity'], data['location']))
    conn.commit()
    cur.close()
    conn.close()

    flash("Waste added successfully!", "success")
    return redirect('/dashboard')


# ---------------- Add Need ----------------
@app.route('/add_need', methods=['POST'])
def add_need():
    if 'user_id' not in session:
        return redirect('/login')
    data = request.form
    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO need_items (user_id, category, description, quantity, location)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, data['category'], data['description'], data['quantity'], data['location']))
    conn.commit()
    cur.close()
    conn.close()

    flash("Need added successfully!", "success")
    return redirect('/dashboard')


# ---------------- Suggest Matches (AI + fallback) ----------------
@app.route('/suggest_matches')
def suggest_matches():
    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    if not user:
        return jsonify([])

    # Database-based matching
    if user['role'] == 'giver':
        query = """
        SELECT w.id AS waste_id, n.id AS need_id, w.category AS waste_category, 
               n.category AS need_category, w.location AS waste_location, 
               n.location AS need_location,
               (w.category = n.category) AS score
        FROM waste_items w
        JOIN need_items n ON w.category = n.category
        WHERE w.user_id = %s
        """
        cur.execute(query, (user_id,))
    elif user['role'] == 'receiver':
        query = """
        SELECT w.id AS waste_id, n.id AS need_id, w.category AS waste_category, 
               n.category AS need_category, w.location AS waste_location, 
               n.location AS need_location,
               (w.category = n.category) AS score
        FROM need_items n
        JOIN waste_items w ON w.category = n.category
        WHERE n.user_id = %s
        """
        cur.execute(query, (user_id,))
    else:
        cur.execute("""
        SELECT w.id AS waste_id, n.id AS need_id, w.category AS waste_category, 
               n.category AS need_category, w.location AS waste_location, 
               n.location AS need_location,
               (w.category = n.category) AS score
        FROM waste_items w
        JOIN need_items n ON w.category = n.category
        """)

    matches = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(matches)


# ---------------- Log match feedback ----------------
@app.route('/log_match', methods=['POST'])
def log_match():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO match_logs (waste_id, need_id, matched) VALUES (%s, %s, %s)",
        (data['waste_id'], data['need_id'], data['matched'])
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"})


# ---------------- Logout ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
