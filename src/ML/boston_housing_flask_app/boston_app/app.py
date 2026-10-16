"""
app.py
------
Flask front-end for the completed "Predicting Boston Housing Prices"
project. Run with:

    python app.py

then open http://127.0.0.1:5000 in a browser.
"""

import io

from flask import Flask, render_template, request, send_file, abort

import model
import visuals

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "index.html",
        stats=model.STATS,
        optimal_depth=model.OPTIMAL_DEPTH,
        test_r2=model.TEST_R2,
        clients=model.CLIENTS,
    )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        rm = float(request.form["rm"])
        lstat = float(request.form["lstat"])
        ptratio = float(request.form["ptratio"])
    except (KeyError, ValueError):
        abort(400, "Please provide numeric values for RM, LSTAT and PTRATIO.")

    price, sensitivity = model.predict_price(rm, lstat, ptratio)

    return render_template(
        "result.html",
        rm=rm,
        lstat=lstat,
        ptratio=ptratio,
        price=price,
        trials=sensitivity["prices"],
        price_range=sensitivity["range"],
        stats=model.STATS,
    )


def _figure_response(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@app.route("/plot/learning.png")
def plot_learning():
    fig = visuals.ModelLearning(model.features, model.prices)
    return _figure_response(fig)


@app.route("/plot/complexity.png")
def plot_complexity():
    fig = visuals.ModelComplexity(model.X_train, model.y_train)
    return _figure_response(fig)


if __name__ == "__main__":
    app.run(debug=True)
