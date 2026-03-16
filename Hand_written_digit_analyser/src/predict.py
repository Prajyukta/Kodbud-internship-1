import numpy as np
from PIL import Image
import io
import base64


def preprocess_image(image_bytes):
    """
    Accept raw image bytes (PNG/JPG/etc.),
    resize to 28×28 grayscale, normalize.
    Returns a (1, 28, 28, 1) float32 array.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("L")  # grayscale
    img = img.resize((28, 28), Image.LANCZOS)

    arr = np.array(img).astype("float32")

    # If image is light-on-dark, invert (MNIST is white digit on black)
    if arr.mean() > 127:
        arr = 255.0 - arr

    arr = arr / 255.0
    return arr.reshape(1, 28, 28, 1)


def predict_digit(model, image_bytes):
    """
    Run inference on raw image bytes.
    Returns dict with digit, confidence, and all class probabilities.
    """
    arr = preprocess_image(image_bytes)
    probs = model.predict(arr, verbose=0)[0]

    digit      = int(np.argmax(probs))
    confidence = float(probs[digit]) * 100

    return {
        "digit":        digit,
        "confidence":   round(confidence, 2),
        "probabilities": {str(i): round(float(p) * 100, 2) for i, p in enumerate(probs)},
    }


def predict_from_canvas(model, data_url):
    """
    Accept a base64 data URL from an HTML canvas element.
    Returns same dict as predict_digit().
    """
    # Strip 'data:image/png;base64,' prefix
    header, encoded = data_url.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    return predict_digit(model, image_bytes)
