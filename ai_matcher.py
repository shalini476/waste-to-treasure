import joblib
import pandas as pd
from db_config import get_db_connection

MODEL_PATH = "models/ai_model.pkl"

def load_model():
    data = joblib.load(MODEL_PATH)
    return data['model'], data['vectorizer']

def suggest_all_matches(top_k=5):
    model, vectorizer = load_model()
    conn = get_db_connection()
    wastes = pd.read_sql("SELECT * FROM waste_items", conn)
    needs = pd.read_sql("SELECT * FROM need_items", conn)

    results = []
    for _, w in wastes.iterrows():
        # candidate needs - filter by same city first (fast)
        candidates = needs[needs['location'].str.lower() == w['location'].lower()]
        if candidates.empty:
            candidates = needs  # fallback

        # prepare combined texts
        texts = (w['category'].astype(str) + " " + w['description'].astype(str) + " " + candidates['category'].astype(str) + " " + candidates['description'].astype(str)).tolist()
        X = vectorizer.transform(texts)
        probs = model.predict_proba(X)[:,1]  # probability of matched==1
        candidates = candidates.copy()
        candidates['score'] = probs
        top = candidates.sort_values('score', ascending=False).head(top_k)
        for _, row in top.iterrows():
            results.append({
                'waste_id': int(w['id']),
                'need_id': int(row['id']),
                'score': float(row['score']),
                'waste_category': w['category'],
                'need_category': row['category'],
                'waste_location': w['location'],
                'need_location': row['location']
            })
    conn.close()
    return results

if __name__ == "__main__":
    matches = suggest_all_matches()
    print(matches[:10])
