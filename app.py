import streamlit as st
import pickle
import re
import os
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Twitter Sentiment Analyzer",
    page_icon="🐦",
    layout="centered"
)
# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Main background gradient */
.stApp {
    background: linear-gradient(135deg, #d3d3d3, #1f77b4);
    background-attachment: fixed;
}

/* Text area styling */
textarea {
    border-radius: 10px !important;
    border: 1px solid #ccc !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #4a90e2, #0052cc);
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: bold;
    border: none;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0052cc, #003d99);
    color: white;
}

/* Title styling */
h1 {
    margin-top: 60px;
    color: #003d66;
    text-align: center;
}

/* Prediction Result Styling */

/* Make subheader cleaner */
h3 {
    color: white !important;
    margin-top: 40px !important;
}

/* Style all Streamlit alert boxes (success, error, info) */
div[data-testid="stAlert"] {
    background-color: black !important;
    border-radius: 15px !important;
    padding: 20px !important;
    border: 1px solid #333 !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
}

/* Remove default left colored border */
div[data-testid="stAlert"] > div {
    border-left: none !important;
}

/* Make text bigger & bold */
div[data-testid="stAlert"] p {
    font-size: 18px !important;
    font-weight: bold !important;
}

/* Positive (success) text color */
div[data-testid="stAlert"][kind="success"] {
    color: #00ff88 !important;
}

/* Negative (error) text color */
div[data-testid="stAlert"][kind="error"] {
    color: #ff4b4b !important;
}

/* Confidence info text */
div[data-testid="stAlert"][kind="info"] {
    color: #4da6ff !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "sentiment_model.pkl")
VEC_PATH = os.path.join(BASE_DIR, "model", "vectorizer.pkl")

model = pickle.load(open(MODEL_PATH, "rb"))
vectorizer = pickle.load(open(VEC_PATH, "rb"))

# ---------------- TEXT CLEANING ----------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text

# ---------------- UI ----------------
st.title("🐦 Twitter Sentiment Analysis")
st.write("Enter a tweet below to analyze its sentiment.")

user_input = st.text_area("✍ Enter Tweet Here")

if st.button("Analyze Sentiment"):

    if user_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        cleaned = clean_text(user_input)
        vectorized = vectorizer.transform([cleaned])
        prediction = model.predict(vectorized)[0]
        probabilities = model.predict_proba(vectorized)[0]

        st.subheader("🔍 Prediction Result")

        # If binary model
        if len(probabilities) == 2:
            confidence = np.max(probabilities) * 100

            if prediction == 0:
                st.error(f"Negative Sentiment 😡")
            else:
                st.success(f"Positive Sentiment 😊")

            st.info(f"Confidence: {confidence:.2f}%")

        else:
            # Multi-class case
            st.write(f"Predicted Class: {prediction}")
            st.write("Probabilities:", probabilities)