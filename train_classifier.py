#!/usr/bin/env python3
"""Train a reaction-type classifier from equations.lib.

Reads the equation library, extracts features using the same feature
extractor that runs on the HP Prime, trains a small neural network,
and exports the weights to a file that the calculator can load.

Usage:
    pip install numpy
    cd Stoichiometry.hpappdir
    python ../train_classifier.py

Produces: reaction_nn.weights  (loaded by nn.py on the HP Prime)
"""

import sys
import os
import numpy as np

# Add the app directory so we can import parser and features
sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                'Stoichiometry.hpappdir'))
from parser import parse_equation
from features import extract, CATEGORIES, N_FEATURES, N_CLASSES

# ---------------------------------------------------------------------------
# 1. Load training data from equations.lib
# ---------------------------------------------------------------------------
LIB_PATH = os.path.join(os.path.dirname(__file__),
                        'Stoichiometry.hpappdir', 'equations.lib')

def load_data():
    """Load equations and extract features + labels."""
    X = []
    y = []
    skipped = 0
    with open(LIB_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) < 3:
                skipped += 1
                continue
            category = parts[0]
            equation = parts[2]

            if category not in CATEGORIES:
                print(f"  [WARN] Unknown category '{category}', skipping")
                skipped += 1
                continue

            label = CATEGORIES.index(category)

            try:
                lhs, rhs = parse_equation(equation)
                feat = extract(lhs, rhs)
                X.append(feat)
                y.append(label)
            except Exception as e:
                print(f"  [WARN] Parse error for '{equation}': {e}")
                skipped += 1

    print(f"Loaded {len(X)} equations, skipped {skipped}")
    return np.array(X, dtype=np.float64), np.array(y, dtype=np.int32)


# ---------------------------------------------------------------------------
# 2. Neural network  (numpy only — no pytorch/tensorflow needed)
# ---------------------------------------------------------------------------

class TinyNN:
    """2-hidden-layer neural network: N_FEATURES -> h1 -> h2 -> N_CLASSES.

    Uses ReLU activations and softmax output.  Trained with SGD +
    cross-entropy loss.
    """
    def __init__(self, h1=24, h2=16, seed=42):
        rng = np.random.RandomState(seed)
        s1 = np.sqrt(2.0 / N_FEATURES)
        s2 = np.sqrt(2.0 / h1)
        s3 = np.sqrt(2.0 / h2)
        self.W1 = rng.randn(N_FEATURES, h1) * s1
        self.b1 = np.zeros(h1)
        self.W2 = rng.randn(h1, h2) * s2
        self.b2 = np.zeros(h2)
        self.W3 = rng.randn(h2, N_CLASSES) * s3
        self.b3 = np.zeros(N_CLASSES)

    def forward(self, X):
        """Forward pass.  X shape: (batch, N_FEATURES)."""
        self.z1 = X @ self.W1 + self.b1
        self.a1 = np.maximum(0, self.z1)  # ReLU
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = np.maximum(0, self.z2)  # ReLU
        self.z3 = self.a2 @ self.W3 + self.b3
        # Stable softmax
        exp_z = np.exp(self.z3 - np.max(self.z3, axis=1, keepdims=True))
        self.probs = exp_z / np.sum(exp_z, axis=1, keepdims=True)
        return self.probs

    def loss(self, probs, y):
        """Cross-entropy loss."""
        n = len(y)
        log_p = -np.log(probs[np.arange(n), y] + 1e-12)
        return np.mean(log_p)

    def backward(self, X, y, lr=0.01):
        """Backprop + SGD update."""
        n = len(y)
        # Gradient of softmax + cross-entropy
        dz3 = self.probs.copy()
        dz3[np.arange(n), y] -= 1
        dz3 /= n

        dW3 = self.a2.T @ dz3
        db3 = np.sum(dz3, axis=0)

        da2 = dz3 @ self.W3.T
        dz2 = da2 * (self.z2 > 0)  # ReLU grad

        dW2 = self.a1.T @ dz2
        db2 = np.sum(dz2, axis=0)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * (self.z1 > 0)  # ReLU grad

        dW1 = X.T @ dz1
        db1 = np.sum(dz1, axis=0)

        # SGD
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W3 -= lr * dW3
        self.b3 -= lr * db3

    def predict(self, X):
        probs = self.forward(X)
        return np.argmax(probs, axis=1)


# ---------------------------------------------------------------------------
# 3. Feature normalization (z-score)
# ---------------------------------------------------------------------------

def normalize(X_train):
    """Compute mean/std and normalize. Returns (X_norm, mean, std)."""
    mean = np.mean(X_train, axis=0)
    std = np.std(X_train, axis=0)
    std[std < 1e-8] = 1.0  # avoid division by zero for constant features
    return (X_train - mean) / std, mean, std


# ---------------------------------------------------------------------------
# 4. Training loop
# ---------------------------------------------------------------------------

def train(X, y, epochs=2000, lr=0.05, lr_decay=0.999):
    """Train the network and return (model, mean, std)."""
    X_norm, mean, std = normalize(X)

    model = TinyNN(h1=24, h2=16)

    best_acc = 0
    for epoch in range(epochs):
        probs = model.forward(X_norm)
        loss = model.loss(probs, y)
        model.backward(X_norm, y, lr=lr)
        lr *= lr_decay

        if (epoch + 1) % 100 == 0 or epoch == 0:
            preds = np.argmax(probs, axis=1)
            acc = np.mean(preds == y)
            if acc > best_acc:
                best_acc = acc
            print(f"  Epoch {epoch+1:4d}  loss={loss:.4f}  "
                  f"acc={acc:.1%}  lr={lr:.5f}")

    # Final accuracy
    preds = model.predict(X_norm)
    acc = np.mean(preds == y)
    print(f"\nFinal training accuracy: {acc:.1%}")

    # Per-class accuracy
    for i, cat in enumerate(CATEGORIES):
        mask = y == i
        if mask.sum() == 0:
            continue
        cat_acc = np.mean(preds[mask] == y[mask])
        print(f"  {cat:25s} {mask.sum():3d} samples  acc={cat_acc:.1%}")

    return model, mean, std


# ---------------------------------------------------------------------------
# 5. Export weights to HP-Prime-readable format
# ---------------------------------------------------------------------------

WEIGHTS_FILE = os.path.join(os.path.dirname(__file__),
                            'Stoichiometry.hpappdir', 'reaction_nn.weights')

def _fmt(val):
    """Format float compactly."""
    return f"{val:.6g}"


def export_weights(model, mean, std):
    """Export weights to a simple text file.

    Weight matrices are **transposed** before export so that the
    HP Prime inference code can use simple ``W @ x`` (matrix-vector
    multiply) instead of ``x @ W``.

    Format:
        Line 1: n_features h1 h2 n_classes
        Line 2: mean values (space-separated)
        Line 3: std values (space-separated)
        Line 4: W1^T flattened row-major  (shape h1 x n_features)
        Line 5: b1
        Line 6: W2^T flattened row-major  (shape h2 x h1)
        Line 7: b2
        Line 8: W3^T flattened row-major  (shape n_classes x h2)
        Line 9: b3
    """
    h1 = model.W1.shape[1]
    h2 = model.W2.shape[1]

    with open(WEIGHTS_FILE, 'w') as f:
        f.write(f"{N_FEATURES} {h1} {h2} {N_CLASSES}\n")
        f.write(' '.join(_fmt(v) for v in mean) + '\n')
        f.write(' '.join(_fmt(v) for v in std) + '\n')
        # Transpose weight matrices: numpy does X @ W, but the
        # calculator does W^T @ x  (simple mat-vec multiply).
        f.write(' '.join(_fmt(v) for v in model.W1.T.flatten()) + '\n')
        f.write(' '.join(_fmt(v) for v in model.b1) + '\n')
        f.write(' '.join(_fmt(v) for v in model.W2.T.flatten()) + '\n')
        f.write(' '.join(_fmt(v) for v in model.b2) + '\n')
        f.write(' '.join(_fmt(v) for v in model.W3.T.flatten()) + '\n')
        f.write(' '.join(_fmt(v) for v in model.b3) + '\n')

    # Report file size
    size = os.path.getsize(WEIGHTS_FILE)
    n_params = (N_FEATURES * h1 + h1 +
                h1 * h2 + h2 +
                h2 * N_CLASSES + N_CLASSES +
                N_FEATURES * 2)  # mean + std
    print(f"\nExported {n_params} parameters to {WEIGHTS_FILE}")
    print(f"File size: {size} bytes ({size/1024:.1f} KB)")


# ---------------------------------------------------------------------------
# 6. Confusion matrix (text)
# ---------------------------------------------------------------------------

def show_confusion(model, X, y, mean, std):
    """Print a text confusion matrix."""
    X_norm = (X - mean) / std
    preds = model.predict(X_norm)

    matrix = np.zeros((N_CLASSES, N_CLASSES), dtype=int)
    for true, pred in zip(y, preds):
        matrix[true][pred] += 1

    # Header
    short = ['Com', 'Syn', 'DRe', 'SRe', 'Neu', 'Red', 'Dec']
    print("\nConfusion Matrix (rows=true, cols=predicted):")
    print(f"{'':>15s}", end='')
    for s in short:
        print(f"{s:>5s}", end='')
    print()
    for i in range(N_CLASSES):
        print(f"{CATEGORIES[i]:>15s}", end='')
        for j in range(N_CLASSES):
            print(f"{matrix[i][j]:5d}", end='')
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("=== Reaction Type Classifier Training ===\n")

    print("Loading data...")
    X, y = load_data()

    print(f"\nFeatures: {N_FEATURES}")
    print(f"Classes:  {N_CLASSES}")
    print(f"Samples:  {len(X)}")

    # Class distribution
    print("\nClass distribution:")
    for i, cat in enumerate(CATEGORIES):
        n = np.sum(y == i)
        print(f"  {cat:25s} {n:3d}")

    print("\nTraining...")
    model, mean, std = train(X, y, epochs=3000, lr=0.05)

    show_confusion(model, X, y, mean, std)

    print("\nExporting weights...")
    export_weights(model, mean, std)

    print("\nDone!")
