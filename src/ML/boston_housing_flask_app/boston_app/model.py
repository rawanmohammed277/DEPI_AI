"""
model.py
--------
This module completes every TODO from `boston_housing.ipynb`
(Model Evaluation & Validation - Predicting Boston Housing Prices) and
exposes the trained model + dataset statistics for the Flask app.

Sections map directly onto the notebook:
  1. Load data                       -> load_data()
  2. Data Exploration / statistics   -> STATS
  3. performance_metric (R^2)        -> performance_metric()
  4. Shuffle & split data            -> X_train / X_test / y_train / y_test
  5. fit_model (GridSearchCV)        -> fit_model()
  6. Predicting selling prices       -> CLIENT_PREDICTIONS
  7. PredictTrials (sensitivity)     -> predict_trials()
"""

import os
import numpy as np
import pandas as pd

from sklearn.metrics import r2_score, make_scorer
from sklearn.model_selection import train_test_split, ShuffleSplit, GridSearchCV
from sklearn.tree import DecisionTreeRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "housing.csv")


# ---------------------------------------------------------------------------
# 1. Load the data
# ---------------------------------------------------------------------------
def load_data():
    data = pd.read_csv(CSV_PATH)
    prices = data["MEDV"]
    features = data.drop("MEDV", axis=1)
    return data, features, prices


# ---------------------------------------------------------------------------
# 3. Performance metric (coefficient of determination, R^2)
# ---------------------------------------------------------------------------
def performance_metric(y_true, y_predict):
    """Calculates and returns the R^2 score between true and predicted values."""
    return r2_score(y_true, y_predict)


# ---------------------------------------------------------------------------
# 5. Fit model using grid search over max_depth, validated with ShuffleSplit
# ---------------------------------------------------------------------------
def fit_model(X, y, random_state=0):
    """Performs grid search over 'max_depth' for a DecisionTreeRegressor."""
    cv_sets = ShuffleSplit(n_splits=10, test_size=0.20, random_state=random_state)
    regressor = DecisionTreeRegressor(random_state=random_state)
    params = {"max_depth": list(range(1, 11))}
    scoring_fnc = make_scorer(performance_metric)
    grid = GridSearchCV(regressor, params, scoring=scoring_fnc, cv=cv_sets)
    grid = grid.fit(X, y)
    return grid.best_estimator_


# ---------------------------------------------------------------------------
# 7. Sensitivity trials: refit on 10 different shuffles and see how much a
#    single client's predicted price wobbles.
# ---------------------------------------------------------------------------
def predict_trials(features, prices, client_point, n_trials=10, max_depth=None):
    """Fits a DecisionTreeRegressor (fixed max_depth) on 10 different
    train/test shuffles and predicts the price for `client_point` each time.
    Mirrors the notebook's PredictTrials, but reuses a fixed max_depth
    (found once by grid search) instead of re-running GridSearchCV on every
    trial, which keeps a web request fast without changing the idea being
    demonstrated: how much the prediction moves as the training data changes.
    """
    point_df = pd.DataFrame([client_point], columns=features.columns)
    trial_prices = []
    for k in range(n_trials):
        X_train, X_test, y_train, y_test = train_test_split(
            features, prices, test_size=0.2, random_state=k
        )
        reg = DecisionTreeRegressor(max_depth=max_depth, random_state=k)
        reg.fit(X_train, y_train)
        pred = float(reg.predict(point_df)[0])
        trial_prices.append(pred)
    return {
        "prices": trial_prices,
        "range": max(trial_prices) - min(trial_prices),
    }


# ---------------------------------------------------------------------------
# Train everything once, at import time, and expose it as module-level state
# ---------------------------------------------------------------------------
data, features, prices = load_data()

STATS = {
    "n_points": data.shape[0],
    "n_features": features.shape[1],
    "min_price": float(prices.min()),
    "max_price": float(prices.max()),
    "mean_price": float(prices.mean()),
    "median_price": float(prices.median()),
    "std_price": float(prices.std()),
}

X_train, X_test, y_train, y_test = train_test_split(
    features, prices, test_size=0.2, random_state=1
)

REGRESSOR = fit_model(X_train, y_train)
OPTIMAL_DEPTH = REGRESSOR.get_params()["max_depth"]
TEST_R2 = performance_metric(y_test, REGRESSOR.predict(X_test))

# 6. Predicting selling prices for the three sample clients from the notebook
CLIENTS = [
    {"name": "Client 1", "RM": 5, "LSTAT": 17, "PTRATIO": 15},
    {"name": "Client 2", "RM": 4, "LSTAT": 32, "PTRATIO": 22},
    {"name": "Client 3", "RM": 8, "LSTAT": 3, "PTRATIO": 12},
]
for c in CLIENTS:
    point = [c["RM"], c["LSTAT"], c["PTRATIO"]]
    point_df = pd.DataFrame([point], columns=features.columns)
    c["price"] = float(REGRESSOR.predict(point_df)[0])


def predict_price(rm, lstat, ptratio):
    """Single prediction using the trained (optimal) regressor."""
    point = [rm, lstat, ptratio]
    point_df = pd.DataFrame([point], columns=features.columns)
    price = float(REGRESSOR.predict(point_df)[0])
    sensitivity = predict_trials(features, prices, point, max_depth=OPTIMAL_DEPTH)
    return price, sensitivity


if __name__ == "__main__":
    # Quick sanity check when run directly: python model.py
    print(f"Dataset: {STATS['n_points']} points, {STATS['n_features']} features")
    print(f"Price range: ${STATS['min_price']:,.2f} - ${STATS['max_price']:,.2f}")
    print(f"Mean: ${STATS['mean_price']:,.2f}  Median: ${STATS['median_price']:,.2f}  "
          f"Std: ${STATS['std_price']:,.2f}")
    print(f"Optimal max_depth: {OPTIMAL_DEPTH}  (test R^2 = {TEST_R2:.3f})")
    for c in CLIENTS:
        print(f"{c['name']}: RM={c['RM']} LSTAT={c['LSTAT']} PTRATIO={c['PTRATIO']} "
              f"-> ${c['price']:,.2f}")
