import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for Flask
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64
from sklearn.metrics import confusion_matrix, classification_report
from src.data_loader import load_data


def fig_to_base64(fig):
    """Convert a matplotlib Figure to a base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def plot_training_curves(history_data):
    """Return base64 PNG of accuracy & loss curves."""
    epochs = history_data["epochs"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    fig.patch.set_facecolor("#0f0f1a")
    for ax in axes:
        ax.set_facecolor("#1a1a2e")
        ax.tick_params(colors="white")
        ax.title.set_color("white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        for spine in ax.spines.values():
            spine.set_color("#333355")

    axes[0].plot(epochs, history_data["accuracy"],     label="Train", color="#7c3aed")
    axes[0].plot(epochs, history_data["val_accuracy"], label="Val",   color="#06b6d4")
    axes[0].set_title("Accuracy"); axes[0].set_xlabel("Epoch")
    axes[0].legend(facecolor="#0f0f1a", labelcolor="white"); axes[0].grid(True, alpha=0.2)

    axes[1].plot(epochs, history_data["loss"],     label="Train", color="#f59e0b")
    axes[1].plot(epochs, history_data["val_loss"], label="Val",   color="#10b981")
    axes[1].set_title("Loss"); axes[1].set_xlabel("Epoch")
    axes[1].legend(facecolor="#0f0f1a", labelcolor="white"); axes[1].grid(True, alpha=0.2)

    plt.tight_layout()
    return fig_to_base64(fig)


def plot_confusion_matrix(model):
    """Return base64 PNG of a confusion matrix evaluated on MNIST test set."""
    _, (x_test, y_test_cat), y_test_raw = load_data()
    y_pred = np.argmax(model.predict(x_test, verbose=0), axis=1)

    cm = confusion_matrix(y_test_raw, y_pred)
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#0f0f1a")
    ax.set_facecolor("#1a1a2e")
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=range(10), yticklabels=range(10), ax=ax)
    ax.set_title("Confusion Matrix", color="white")
    ax.set_xlabel("Predicted", color="white")
    ax.set_ylabel("True", color="white")
    ax.tick_params(colors="white")
    plt.tight_layout()
    return fig_to_base64(fig)


def get_classification_report(model):
    """Return classification report as a string."""
    _, (x_test, _), y_test_raw = load_data()
    y_pred = np.argmax(model.predict(x_test, verbose=0), axis=1)
    return classification_report(y_test_raw, y_pred, digits=4)
