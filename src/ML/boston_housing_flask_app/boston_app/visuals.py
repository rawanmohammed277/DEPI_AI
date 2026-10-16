"""
visuals.py
----------
Supplementary plotting code for the Boston Housing project, ported to work
with a current scikit-learn/matplotlib install and to return Figure objects
(so a Flask route can render them as PNG bytes) instead of calling
`pl.show()`, which only makes sense inside a notebook.

Fixes applied to the version supplied with the notebook:
  - `pl` was used but never imported -> use `matplotlib.pyplot as plt`.
  - `curves.validation_curve` referenced a module that doesn't exist
    -> `from sklearn.model_selection import validation_curve`.
  - `ShuffleSplit(..., n_iter=10, ...)` is the old (pre-0.18) scikit-learn
    API -> `ShuffleSplit(n_splits=10, ...)`.
"""

import warnings

import matplotlib
matplotlib.use("Agg")  # no display server available on the server
import matplotlib.pyplot as plt
import numpy as np
from sklearn.exceptions import UndefinedMetricWarning

# The smallest learning-curve training size can be a single sample, for
# which R^2 is mathematically undefined (matches the original notebook's
# behaviour) - silence that specific, harmless warning.
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

from sklearn.model_selection import (
    ShuffleSplit,
    learning_curve,
    validation_curve,
    train_test_split,
)
from sklearn.tree import DecisionTreeRegressor


def ModelLearning(X, y):
    """Calculates the performance of several models with varying sizes of
    training data. The learning and testing scores for each model are
    plotted, one subplot per max_depth in (1, 3, 6, 10)."""

    cv = ShuffleSplit(n_splits=10, test_size=0.2, random_state=0)
    train_sizes = np.rint(np.linspace(1, X.shape[0] * 0.8 - 1, 9)).astype(int)

    fig = plt.figure(figsize=(10, 7))

    for k, depth in enumerate([1, 3, 6, 10]):
        sizes, train_scores, test_scores = learning_curve(
            DecisionTreeRegressor(max_depth=depth, random_state=0),
            X,
            y,
            cv=cv,
            train_sizes=train_sizes,
            scoring="r2",
        )
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)

        ax = fig.add_subplot(2, 2, k + 1)
        ax.plot(sizes, train_mean, "o-", color="r", label="Training Score")
        ax.plot(sizes, test_mean, "o-", color="g", label="Testing Score")
        ax.fill_between(
            sizes, train_mean - train_std, train_mean + train_std, alpha=0.15, color="r"
        )
        ax.fill_between(
            sizes, test_mean - test_std, test_mean + test_std, alpha=0.15, color="g"
        )
        ax.set_title(f"max_depth = {depth}")
        ax.set_xlabel("Number of Training Points")
        ax.set_ylabel("Score")
        ax.set_xlim([0, X.shape[0] * 0.8])
        ax.set_ylim([-0.05, 1.05])
        ax.legend(loc="lower right", fontsize=8)

    fig.suptitle("Decision Tree Regressor Learning Performances", fontsize=16, y=1.02)
    fig.tight_layout()
    return fig


def ModelComplexity(X, y):
    """Calculates the performance of the model as model complexity
    (max_depth) increases, and plots training/validation curves."""

    cv = ShuffleSplit(n_splits=10, test_size=0.2, random_state=0)
    max_depth = np.arange(1, 11)

    train_scores, test_scores = validation_curve(
        DecisionTreeRegressor(random_state=0),
        X,
        y,
        param_name="max_depth",
        param_range=max_depth,
        cv=cv,
        scoring="r2",
    )

    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)

    fig = plt.figure(figsize=(7, 5))
    plt.title("Decision Tree Regressor Complexity Performance")
    plt.plot(max_depth, train_mean, "o-", color="r", label="Training Score")
    plt.plot(max_depth, test_mean, "o-", color="g", label="Validation Score")
    plt.fill_between(
        max_depth, train_mean - train_std, train_mean + train_std, alpha=0.15, color="r"
    )
    plt.fill_between(
        max_depth, test_mean - test_std, test_mean + test_std, alpha=0.15, color="g"
    )
    plt.legend(loc="lower right")
    plt.xlabel("Maximum Depth")
    plt.ylabel("Score")
    plt.ylim([-0.05, 1.05])
    return fig


def PredictTrials(X, y, fitter, data):
    """Performs 10 trials of fitting and predicting `data` (a single point)
    on different train/test shuffles, returning the list of predicted
    prices and the range between the highest and lowest prediction."""

    prices = []
    for k in range(10):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=k
        )
        reg = fitter(X_train, y_train)
        pred = reg.predict([data[0]])[0]
        prices.append(pred)
        print(f"Trial {k + 1}: ${pred:,.2f}")

    print(f"\nRange in prices: ${max(prices) - min(prices):,.2f}")
    return prices
