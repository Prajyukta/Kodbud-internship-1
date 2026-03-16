# MNIST Digit Recognizer — Flask App

A full-stack web application for training and testing a CNN on the MNIST handwritten digit dataset.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open browser
http://localhost:5000
```

## Pages

| URL | Description |
|-----|-------------|
| `/` | Draw or upload a digit → get prediction |
| `/train` | Configure & launch model training |
| `/evaluate` | Training curves, confusion matrix, classification report |

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/train` | Start training `{ epochs, batch_size }` |
| GET  | `/api/train/status` | Poll training progress |
| GET  | `/api/model/status` | Check if model is loaded |
| POST | `/api/predict` | Predict from canvas `{ image: dataURL }` |
| POST | `/api/predict/upload` | Predict from uploaded image file |

## Project Structure

```
mnist-flask/
├── app.py                  ← Flask app + all routes
├── requirements.txt
├── models/                 ← Saved .keras model files
├── src/
│   ├── data_loader.py      ← Load & preprocess MNIST
│   ├── model.py            ← CNN architecture
│   ├── train.py            ← Training loop + callbacks
│   ├── predict.py          ← Inference logic
│   └── evaluate.py         ← Plots + metrics
├── templates/
│   ├── base.html
│   ├── index.html          ← Predict page
│   ├── train.html          ← Training page
│   └── evaluate.html       ← Evaluation page
└── static/
    ├── css/style.css
    └── js/
        ├── main.js
        ├── canvas.js       ← Drawing logic
        ├── predict.js      ← Prediction API calls
        └── train.js        ← Training polling
```
