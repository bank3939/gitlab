import math
from flask import Flask, render_template, request

from bjt_bias import analyze_bjt_ce

app = Flask(__name__)

FIELDS = ["VCC", "R1", "R2", "RC", "RE", "beta", "VBE"]
DEFAULTS = {
    "VCC": "12",
    "R1": "40000",
    "R2": "10000",
    "RC": "2000",
    "RE": "1000",
    "beta": "100",
    "VBE": "0.7",
}


def _parse_inputs(form):
    values = {}
    errors = []
    for field in FIELDS:
        raw = (form.get(field) or "").strip()
        values[field] = raw
        if raw == "":
            errors.append(f"{field} is required.")
            continue
        try:
            num = float(raw)
        except (TypeError, ValueError):
            errors.append(f"{field} must be a number.")
            continue
        if not math.isfinite(num):
            errors.append(f"{field} must be a finite number.")
            continue
        values[field] = num
    return values, errors


@app.route("/", methods=["GET", "POST"])
def index():
    inputs = DEFAULTS.copy()
    result = None
    parse_errors = []
    if request.method == "POST":
        parsed, parse_errors = _parse_inputs(request.form)
        # keep raw strings for form re-fill when parsing fails
        inputs = {k: (str(v) if not isinstance(v, str) else v) for k, v in parsed.items()}
        if not parse_errors:
            numeric = {k: float(parsed[k]) for k in FIELDS}
            result = analyze_bjt_ce(**numeric)
        else:
            # still show form values entered
            for field in FIELDS:
                inputs[field] = request.form.get(field, "")
    return render_template(
        "index.html",
        inputs=inputs,
        result=result,
        parse_errors=parse_errors,
        fields=FIELDS,
    )


if __name__ == "__main__":
    app.run(debug=True)
