import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# ---------------- DATASET ----------------
data = [
    # FAKE (scam / clickbait / misleading)
    ("Earn $5000 fast from home", "Fake"),
    ("Click here to win a free iPhone", "Fake"),
    ("Breaking: shocking secret they don't want you to know", "Fake"),
    ("You have been selected for a reward", "Fake"),
    ("Make money instantly with this trick", "Fake"),
    ("Lose weight in 2 days guaranteed", "Fake"),
    ("Congratulations! You won a lottery", "Fake"),
    ("This investment doubles money overnight", "Fake"),
    ("Secret government conspiracy exposed", "Fake"),
    ("Act now before it's too late!!!", "Fake"),

    # REAL (normal human sentences)
    ("The sun is bright today", "Real"),
    ("I am going to school", "Real"),
    ("Hello how are you doing", "Real"),
    ("We have a meeting tomorrow", "Real"),
    ("The weather is nice today", "Real"),
    ("She is reading a book", "Real"),
    ("I will call you later", "Real"),
    ("This is a normal sentence", "Real"),
    ("We are studying for exams", "Real"),
    ("He is playing football", "Real"),

    # MORE REAL (important for balance)
    ("The report was submitted yesterday", "Real"),
    ("Our class starts at 9am", "Real"),
    ("I enjoy listening to music", "Real"),
    ("We are having lunch now", "Real"),
    ("The project deadline is next week", "Real"),

    # MORE FAKE (balance dataset)
    ("Win cash prizes instantly now", "Fake"),
    ("You won’t believe what happened next", "Fake"),
    ("Free money offer limited time", "Fake"),
    ("Get rich quick scheme revealed", "Fake"),
    ("Doctors hate this trick", "Fake"),
]

df = pd.DataFrame(data, columns=["text", "label"])

# ---------------- SPLIT DATA ----------------
X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42
)

# ---------------- VECTORIZER ----------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),   # BIG improvement (captures phrases)
    max_features=5000
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# ---------------- MODEL ----------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

# ---------------- EVALUATION ----------------
y_pred = model.predict(X_test_vec)
print("\nMODEL PERFORMANCE:\n")
print(classification_report(y_test, y_pred))

# ---------------- SAVE ----------------
joblib.dump(model, "text_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("\nModel trained and saved successfully!")