import os
from tensorflow import keras
from src.data_loader import load_data
from src.model import build_model

MODELS_DIR = "models"


def train_model(epochs=15, batch_size=128):
    """
    Train the CNN on MNIST.
    Returns (model, history, test_accuracy, test_loss).
    """
    os.makedirs(MODELS_DIR, exist_ok=True)

    (x_train, y_train), (x_test, y_test_cat), y_test_raw = load_data()

    model = build_model()

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=3, restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=2, verbose=0
        ),
        keras.callbacks.ModelCheckpoint(
            os.path.join(MODELS_DIR, "best_mnist_model.keras"),
            save_best_only=True,
            monitor="val_accuracy",
        ),
    ]

    history = model.fit(
        x_train,
        y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=1,
    )

    test_loss, test_acc = model.evaluate(x_test, y_test_cat, verbose=0)

    model.save(os.path.join(MODELS_DIR, "mnist_model_final.keras"))

    return model, history, round(test_acc * 100, 2), round(test_loss, 4)


def get_history_data(history):
    """Convert Keras history to JSON-serialisable dict."""
    return {
        "accuracy": [round(v, 4) for v in history.history["accuracy"]],
        "val_accuracy": [round(v, 4) for v in history.history["val_accuracy"]],
        "loss": [round(v, 4) for v in history.history["loss"]],
        "val_loss": [round(v, 4) for v in history.history["val_loss"]],
        "epochs": list(range(1, len(history.history["accuracy"]) + 1)),
    }


# 🔹 This part actually runs training
if __name__ == "__main__":
    print("Starting MNIST training...\n")

    model, history, acc, loss = train_model()

    print("\nTraining finished")
    print(f"Test Accuracy: {acc}%")
    print(f"Test Loss: {loss}")