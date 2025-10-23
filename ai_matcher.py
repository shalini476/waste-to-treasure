# ai_matcher.py
from sentence_transformers import SentenceTransformer, util
import mysql.connector

# Load semantic model once (small + fast)
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # update if needed
        database="waste_to_treasure"
    )

def suggest_all_matches():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Fetch data
    cur.execute("SELECT * FROM waste_items")
    wastes = cur.fetchall()

    cur.execute("SELECT * FROM need_items")
    needs = cur.fetchall()

    results = []

    for w in wastes:
        w_text = f"{w['category']} {w['description']}"
        w_emb = model.encode(w_text, convert_to_tensor=True)

        best_match = None
        best_score = 0.0

        for n in needs:
            n_text = f"{n['category']} {n['description']}"
            n_emb = model.encode(n_text, convert_to_tensor=True)

            score = util.cos_sim(w_emb, n_emb).item()

            if score > best_score:
                best_score = score
                best_match = n

        if best_match:
            results.append({
                "waste_id": w['id'],
                "need_id": best_match['id'],
                "waste_category": w['category'],
                "need_category": best_match['category'],
                "waste_location": w['location'],
                "need_location": best_match['location'],
                "score": round(best_score, 2)
            })

    cur.close()
    conn.close()
    return results
