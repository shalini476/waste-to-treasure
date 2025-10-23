import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib

def train(csv_path="matches.csv", model_path="models/ai_model.pkl"):
    df = pd.read_csv(csv_path)

    # Use only labeled rows for supervised learning (matched == 0/1)
    labeled = df[df['matched'].isin([0,1])]

    X = labeled['combined'].astype(str)
    y = labeled['matched']

    # Vectorize
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X_vec = vectorizer.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42, stratify=y)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    # Save both
    joblib.dump({'model': model, 'vectorizer': vectorizer}, model_path)
    print("Saved model to", model_path)

if __name__ == "__main__":
    train()
