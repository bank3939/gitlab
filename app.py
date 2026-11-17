import math
from flask import Flask, render_template, request

from dc_bias import analyze

app = Flask(__name__)

MODES = {
    "divider": "Voltage Divider Bias",
    "fixed": "Fixed Bias",
    "emitter": "Emitter Bias",
}
# fields per mode (in addition to common VCC, RC, beta, VBE)
MODE_FIELDS = {
    "divider": ["R1", "R2", "RE"],
    "fixed": ["RB"],
    "emitter": ["RB", "RE"],
}
COMMON_FIELDS = ["VCC", "RC", "beta", "VBE"]
ALL_FIELDS = ["VCC", "RC", "beta", "VBE", "R1", "R2", "RE", "RB"]
DEFAULTS = {
    "VCC": "12",
    "RC": "2200",
    "beta": "100",
    "VBE": "0.7",
    "R1": "100000",
    "R2": "22000",
    "RE": "1000",
    "RB": "1000000",
}


def _parse_value(raw, name):
    if raw is None or str(raw).strip() == "":
        raise ValueError(f"{name} จำเป็นต้องกรอก")
    try:
        num = float(str(raw).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if not math.isfinite(num):
        raise ValueError(f"{name} ต้องเป็นจำนวนจำกัด")
    return num


@app.route("/", methods=["GET", "POST"])
def index():
    mode = "divider"
    inputs = DEFAULTS.copy()
    result = None
    errors = []
    if request.method == "POST":
        mode = (request.form.get("mode") or "divider").strip().lower()
        # preserve all raw inputs for refill
        for f in ALL_FIELDS:
            inputs[f] = request.form.get(f, inputs.get(f, ""))
        inputs["mode"] = mode
        if mode not in MODES:
            errors.append("ไม่รู้จักโหมดวงจรที่เลือก")
        else:
            required = COMMON_FIELDS + MODE_FIELDS[mode]
            numeric = {}
            for field in required:
                raw = request.form.get(field, "")
                try:
                    numeric[field] = _parse_value(raw, field)
                except ValueError as e:
                    errors.append(str(e))
            # validate positive requirements per mode where applicable
            if not errors:
                # additional positivity checks aligned with lab
                for name in ["beta"]:
                    if numeric.get(name) is not None and numeric[name] <= 0:
                        errors.append(f"{name} ต้องมากกว่า 0")
                if mode == "fixed" and numeric.get("RB") is not None and numeric["RB"] <= 0:
                    errors.append("RB ต้องมากกว่า 0")
                if mode == "emitter":
                    if numeric.get("RB") is not None and numeric["RB"] <= 0:
                        errors.append("RB ต้องมากกว่า 0")
                    if numeric.get("RE") is not None and numeric["RE"] < 0:
                        errors.append("RE ต้องไม่เป็นค่าลบ")
                if mode == "divider":
                    if numeric.get("R1") is not None and numeric["R1"] <= 0:
                        errors.append("R1 ต้องมากกว่า 0")
                    if numeric.get("R2") is not None and numeric["R2"] <= 0:
                        errors.append("R2 ต้องมากกว่า 0")
                    if numeric.get("RE") is not None and numeric["RE"] < 0:
                        errors.append("RE ต้องไม่เป็นค่าลบ")
                if numeric.get("VCC") is not None and numeric["VCC"] < 0:
                    errors.append("VCC ต้องไม่เป็นค่าลบ")
                if numeric.get("RC") is not None and numeric["RC"] < 0:
                    errors.append("RC ต้องไม่เป็นค่าลบ")
                if numeric.get("VBE") is not None and numeric["VBE"] < 0:
                    errors.append("VBE ต้องไม่เป็นค่าลบ")
            if not errors:
                result = analyze(mode, numeric)
                # merge calculation errors into errors list display? keep separate
                if result.get("errors"):
                    errors.extend(result["errors"])
                    result = result  # still show result object for warnings/fields if any
    else:
        inputs["mode"] = mode

    return render_template(
        "index.html",
        mode=mode,
        modes=MODES,
        mode_fields=MODE_FIELDS,
        inputs=inputs,
        result=result,
        errors=errors,
    )


if __name__ == "__main__":
    app.run(debug=True)
