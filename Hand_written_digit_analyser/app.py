
import os
import threading
from flask import Flask, request, jsonify, render_template, session

from tensorflow import keras

from src.train   import train_model, get_history_data
from src.predict import predict_from_canvas, predict_digit
from src.evaluate import (
    plot_training_curves,
    plot_confusion_matrix,
    get_classification_report,
)

# ── App setup ────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "mnist-secret-key-change-in-production"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # 5 MB upload limit

MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# ── Global state (simple; use Redis/DB for production) ───────
_model         = None
_history_data  = None
_train_status  = {"running": False, "progress": 0, "message": "Not started"}
_test_acc      = None
_test_loss     = None


def get_model():
    """Load model from disk if not in memory."""
    global _model
    if _model is None:
        path = os.path.join(MODELS_DIR, "mnist_model_final.keras")
        if os.path.exists(path):
            _model = keras.models.load_model(path)
    return _model


# ── Pages ─────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/train")
def train_page():
    return render_template("train.html")


@app.route("/evaluate")
def evaluate_page():
    model = get_model()
    if model is None:
        return render_template("evaluate.html", error="No trained model found. Train first.")

    curves_img = plot_training_curves(_history_data) if _history_data else None
    cm_img     = plot_confusion_matrix(model)
    report     = get_classification_report(model)

    return render_template(
        "evaluate.html",
        curves_img=curves_img,
        cm_img=cm_img,
        report=report,
        test_acc=_test_acc,
        test_loss=_test_loss,
    )


# ── API — Model Status ────────────────────────────────────────
@app.route("/api/model/status")
def model_status():
    model = get_model()
    return jsonify({
        "loaded":    model is not None,
        "test_acc":  _test_acc,
        "test_loss": _test_loss,
    })


# ── API — Train ───────────────────────────────────────────────
def _run_training(epochs, batch_size):
    global _model, _history_data, _train_status, _test_acc, _test_loss
    _train_status = {"running": True, "progress": 0, "message": "Loading MNIST…"}
    try:
        _train_status["message"] = "Training…"
        model, history, acc, loss = train_model(epochs=epochs, batch_size=batch_size)
        _model        = model
        _history_data = get_history_data(history)
        _test_acc     = acc
        _test_loss    = loss
        _train_status = {
            "running": False, "progress": 100,
            "message": f"Done! Test Accuracy: {acc}%"
        }
    except Exception as e:
        _train_status = {"running": False, "progress": 0, "message": f"Error: {str(e)}"}


@app.route("/api/train", methods=["POST"])
def api_train():
    global _train_status
    if _train_status["running"]:
        return jsonify({"error": "Training already in progress"}), 409

    data       = request.get_json(silent=True) or {}
    epochs     = int(data.get("epochs", 15))
    batch_size = int(data.get("batch_size", 128))

    thread = threading.Thread(target=_run_training, args=(epochs, batch_size), daemon=True)
    thread.start()

    return jsonify({"message": "Training started", "epochs": epochs})


@app.route("/api/train/status")
def train_status():
    return jsonify(_train_status)


# ── API — Predict (canvas) ────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
def api_predict():
    model = get_model()
    if model is None:
        return jsonify({"error": "Model not trained yet"}), 400

    data     = request.get_json(silent=True) or {}
    data_url = data.get("image")
    if not data_url:
        return jsonify({"error": "No image data provided"}), 400

    try:
        result = predict_from_canvas(model, data_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── API — Predict (file upload) ───────────────────────────────
@app.route("/api/predict/upload", methods=["POST"])
def api_predict_upload():
    model = get_model()
    if model is None:
        return jsonify({"error": "Model not trained yet"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        image_bytes = file.read()
        result      = predict_digit(model, image_bytes)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
