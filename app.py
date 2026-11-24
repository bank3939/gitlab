import math
from flask import Flask, render_template, request

from dc_bias import analyze
from spice_engine import find_ngspice, get_ngspice_version, run_simulation, validate_params

app = Flask(__name__)

MODES = {
    "divider": "Voltage Divider Bias",
    "fixed": "Fixed Bias",
    "emitter": "Emitter Bias",
}
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
SPICE_DEFAULTS = {
    "spice_VCC": "12",
    "spice_R1": "100000",
    "spice_R2": "22000",
    "spice_RC": "2200",
    "spice_RE": "1000",
    "spice_RL": "10000",
    "spice_Cin_uF": "10",
    "spice_Cout_uF": "10",
    "spice_amp_mV": "10",
    "spice_freq_hz": "1000",
    "spice_analysis": "op",
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


def _handle_dc_post(form):
    mode = (form.get("mode") or "divider").strip().lower()
    inputs = DEFAULTS.copy()
    inputs["mode"] = mode
    result = None
    errors = []
    for f in ALL_FIELDS:
        inputs[f] = form.get(f, inputs.get(f, ""))
    if mode not in MODES:
        errors.append("ไม่รู้จักโหมดวงจรที่เลือก")
    else:
        required = COMMON_FIELDS + MODE_FIELDS[mode]
        numeric = {}
        for field in required:
            raw = form.get(field, "")
            try:
                numeric[field] = _parse_value(raw, field)
            except ValueError as e:
                errors.append(str(e))
        if not errors:
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
            if result.get("errors"):
                errors.extend(result["errors"])
    return mode, inputs, result, errors


def _handle_spice_post(form):
    spice = SPICE_DEFAULTS.copy()
    for k in SPICE_DEFAULTS:
        spice[k] = form.get(k, spice[k])
    errors = []
    result = None
    analysis = (form.get("spice_analysis") or "op").strip().lower()
    spice["spice_analysis"] = analysis
    if analysis not in ("op", "ac", "tran"):
        errors.append("ไม่รู้จักโหมดการวิเคราะห์ SPICE")
    params = None
    if not errors:
        try:
            params = {
                "VCC": _parse_value(spice["spice_VCC"], "VCC"),
                "R1": _parse_value(spice["spice_R1"], "R1"),
                "R2": _parse_value(spice["spice_R2"], "R2"),
                "RC": _parse_value(spice["spice_RC"], "RC"),
                "RE": _parse_value(spice["spice_RE"], "RE"),
                "RL": _parse_value(spice["spice_RL"], "RL"),
                "Cin": _parse_value(spice["spice_Cin_uF"], "Cin (uF)") * 1e-6,
                "Cout": _parse_value(spice["spice_Cout_uF"], "Cout (uF)") * 1e-6,
                "amp_mV": _parse_value(spice["spice_amp_mV"], "Amplitude (mV)"),
                "freq_hz": _parse_value(spice["spice_freq_hz"], "Frequency (Hz)"),
            }
            validate_params(params)
        except ValueError as e:
            errors.append(str(e))
    if not errors and params is not None:
        result = run_simulation(analysis, params)
        if not result.get("ok"):
            errors.append(result.get("error") or "SPICE simulation failed")
    ng_ver, ng_err = get_ngspice_version()
    return spice, result, errors, {"version": ng_ver, "error": ng_err, "path": find_ngspice()}


@app.route("/", methods=["GET", "POST"])
def index():
    mode = "divider"
    inputs = DEFAULTS.copy()
    inputs["mode"] = mode
    result = None
    errors = []
    spice = SPICE_DEFAULTS.copy()
    spice_result = None
    spice_errors = []
    if request.method == "POST":
        form_type = request.form.get("form_type", "dc")
        if form_type == "spice":
            spice, spice_result, spice_errors, _ = _handle_spice_post(request.form)
            # keep DC form defaults
        else:
            mode, inputs, result, errors = _handle_dc_post(request.form)
    ng_ver, ng_err = get_ngspice_version()
    ngspice_info = {"version": ng_ver, "error": ng_err, "path": find_ngspice()}
    return render_template(
        "index.html",
        mode=mode,
        modes=MODES,
        mode_fields=MODE_FIELDS,
        inputs=inputs,
        result=result,
        errors=errors,
        spice=spice,
        spice_result=spice_result,
        spice_errors=spice_errors,
        ngspice_info=ngspice_info,
    )


if __name__ == "__main__":
    app.run(debug=True)
