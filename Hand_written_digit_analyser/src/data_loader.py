import numpy as np
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical


def load_data():
    """Load and preprocess the MNIST dataset."""
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    x_train = x_train.astype("float32") / 255.0
    x_test  = x_test.astype("float32")  / 255.0

    x_train = x_train.reshape(-1, 28, 28, 1)
    x_test  = x_test.reshape(-1, 28, 28, 1)

    y_train_cat = to_categorical(y_train, 10)
    y_test_cat  = to_categorical(y_test,  10)

    return (x_train, y_train_cat), (x_test, y_test_cat), y_test
