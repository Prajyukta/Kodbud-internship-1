import os
import pandas as pd
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# =========================
# Path setup
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "tweets.csv")

# =========================
# Load dataset (no header)
# =========================
data = pd.read_csv(
    DATA_PATH,
    sep=",",
    encoding="latin-1",
    header=None,
    quotechar='"',
    engine="python"
)

# Rename columns
data.columns = ["sentiment", "id", "date", "query", "user", "tweet"]

# Keep only needed columns
data = data[["sentiment", "tweet"]]

# Convert labels: 0 = negative, 4 = positive → convert 4 to 1
data["sentiment"] = data["sentiment"].apply(lambda x: 1 if x == 4 else 0)

# Remove missing tweets if any
data.dropna(subset=["tweet"], inplace=True)

# =========================
# Text Cleaning
# =========================
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)   # remove URLs
    text = re.sub(r"@\w+", "", text)            # remove mentions
    text = re.sub(r"#", "", text)               # remove hashtags
    text = re.sub(r"[^a-zA-Z\s]", "", text)     # remove special chars
    return text.strip()

data["tweet"] = data["tweet"].apply(clean_text)

# =========================
# Features & Labels
# =========================
X = data["tweet"]
y = data["sentiment"]

# =========================
# TF-IDF Vectorization
# =========================
vectorizer = TfidfVectorizer(max_features=5000)
X_vectorized = vectorizer.fit_transform(X)

# =========================
# Train/Test Split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y   # keeps class balance
)

# =========================
# Train Logistic Regression
# =========================
model = LogisticRegression(max_iter=1000, solver="liblinear")
model.fit(X_train, y_train)

# =========================
# Evaluate
# =========================
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# =========================
# Save model safely
# =========================
with open("sentiment_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅Model trained and saved successfully!")