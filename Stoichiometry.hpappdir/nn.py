"""Minimal neural network inference for HP Prime MicroPython.

Loads pre-trained weights from reaction_nn.weights and runs
forward passes to classify reaction types.  Uses only built-in
Python — no linalg needed for these small matrix sizes.

Designed for a network with architecture:
    input(18) -> Dense(24, ReLU) -> Dense(16, ReLU) -> Dense(7, softmax)
"""

from features import CATEGORIES, N_CLASSES
import math

# Module-level state — loaded once, reused for all predictions
_W1 = None
_b1 = None
_W2 = None
_b2 = None
_W3 = None
_b3 = None
_mean = None
_std = None
_loaded = False

_WEIGHTS_FILE = 'reaction_nn.weights'


def _dot(A, x, bias, rows, cols):
    """Matrix-vector multiply: result = A @ x + bias.

    A is stored as flat list (row-major), shape (rows, cols).
    x has length cols.  Returns list of length rows.
    """
    out = []
    idx = 0
    for r in range(rows):
        s = bias[r]
        for c in range(cols):
            s += A[idx] * x[c]
            idx += 1
        out.append(s)
    return out


def _relu(v):
    """In-place ReLU on a list."""
    for i in range(len(v)):
        if v[i] < 0.0:
            v[i] = 0.0
    return v


def _softmax(v):
    """Stable softmax, returns list of probabilities."""
    mx = v[0]
    for x in v:
        if x > mx:
            mx = x
    exps = []
    s = 0.0
    for x in v:
        e = math.exp(x - mx)
        exps.append(e)
        s += e
    return [e / s for e in exps]


def load():
    """Load weights from file.  Call once at startup.

    Returns True on success, False if file not found or corrupt.
    """
    global _W1, _b1, _W2, _b2, _W3, _b3, _mean, _std, _loaded
    global _n_feat, _h1, _h2, _n_cls

    try:
        f = open(_WEIGHTS_FILE, 'r')
    except:
        return False

    try:
        lines = f.readlines()
        f.close()

        if len(lines) < 9:
            return False

        # Line 0: dimensions
        dims = lines[0].split()
        _n_feat = int(dims[0])
        _h1 = int(dims[1])
        _h2 = int(dims[2])
        _n_cls = int(dims[3])

        # Line 1-2: normalization stats
        _mean = [float(x) for x in lines[1].split()]
        _std = [float(x) for x in lines[2].split()]

        # Line 3-8: weights and biases
        _W1 = [float(x) for x in lines[3].split()]
        _b1 = [float(x) for x in lines[4].split()]
        _W2 = [float(x) for x in lines[5].split()]
        _b2 = [float(x) for x in lines[6].split()]
        _W3 = [float(x) for x in lines[7].split()]
        _b3 = [float(x) for x in lines[8].split()]

        _loaded = True
        return True
    except:
        return False


def is_loaded():
    """Check if weights have been loaded."""
    return _loaded


def predict(features):
    """Run inference on a feature vector.

    Args:
        features: list of floats, length N_FEATURES

    Returns:
        (predicted_index, probabilities_list) where
        predicted_index is 0..N_CLASSES-1 and probabilities
        sum to 1.0.  Returns (None, None) if not loaded.
    """
    if not _loaded:
        return None, None

    # Normalize
    x = []
    for i in range(len(features)):
        x.append((features[i] - _mean[i]) / _std[i])

    # Forward pass
    z1 = _dot(_W1, x, _b1, _h1, _n_feat)
    a1 = _relu(z1)

    z2 = _dot(_W2, a1, _b2, _h2, _h1)
    a2 = _relu(z2)

    z3 = _dot(_W3, a2, _b3, _n_cls, _h2)
    probs = _softmax(z3)

    # Find argmax
    best = 0
    best_p = probs[0]
    for i in range(1, _n_cls):
        if probs[i] > best_p:
            best_p = probs[i]
            best = i

    return best, probs


def predict_category(features):
    """Convenience: returns (category_name, confidence, all_probs).

    Returns (None, 0.0, None) if not loaded.
    """
    idx, probs = predict(features)
    if idx is None:
        return None, 0.0, None
    return CATEGORIES[idx], probs[idx], probs
