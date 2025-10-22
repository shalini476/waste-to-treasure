from flask import Flask, render_template, request, jsonify
from db_config import get_db_connection
from sklearn.metrics.pairwise import euclidean_distances
import pandas as pd

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# --------------------- USER LOGIN ---------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "message": "Login successful!"})
    else:
        return jsonify({"status": "error", "message": "Invalid email or password."})


# --------------------- REGISTER ---------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data['name']
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        return jsonify({"status": "success", "message": "Registration successful!"})
    except:
        conn.rollback()
        return jsonify({"status": "error", "message": "Email already exists."})
    finally:
        conn.close()


# --------------------- PROVIDER FORM ---------------------
@app.route('/provider', methods=['POST'])
def provider():
    data = request.json
    waste_type = data['waste_type']
    quantity = data['quantity']
    location = data['location']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO waste_providers (waste_type, quantity, location) VALUES (%s, %s, %s)",
                   (waste_type, quantity, location))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Waste provider data saved!"})


# --------------------- RECEIVER FORM ---------------------
@app.route('/receiver', methods=['POST'])
def receiver():
    data = request.json
    resource_needed = data['resource_needed']
    quantity = data['quantity']
    location = data['location']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO resource_receivers (resource_needed, quantity, location) VALUES (%s, %s, %s)",
                   (resource_needed, quantity, location))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Resource receiver data saved!"})


# --------------------- AI MATCHING ENGINE ---------------------
@app.route('/match', methods=['GET'])
def match_resources():
    conn = get_db_connection()
    provider_df = pd.read_sql("SELECT * FROM waste_providers", conn)
    receiver_df = pd.read_sql("SELECT * FROM resource_receivers", conn)
    conn.close()

    if provider_df.empty or receiver_df.empty:
        return jsonify({"status": "error", "message": "Not enough data for matching."})

    # Simple AI-based Matching: match closest quantities (simulate optimization)
    matches = []
    for _, prov in provider_df.iterrows():
        receiver_df['diff'] = abs(receiver_df['quantity'] - prov['quantity'])
        best_match = receiver_df.sort_values(by='diff').iloc[0]
        matches.append({
            "provider": prov['waste_type'],
            "provider_qty": prov['quantity'],
            "receiver": best_match['resource_needed'],
            "receiver_qty": best_match['quantity'],
            "location": f"{prov['location']} → {best_match['location']}"
        })

    return jsonify({"status": "success", "matches": matches})


if __name__ == '__main__':
    app.run(debug=True)
