import math

VCE_SAT = 0.2


def _num(value, name, positive=False, allow_zero=False):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} ต้องเป็นตัวเลข")
    if not math.isfinite(value):
        raise ValueError(f"{name} ต้องเป็นจำนวนจำกัด")
    if positive:
        if allow_zero:
            if value <= 0 and not (allow_zero and value == 0):
                raise ValueError(f"{name} ต้องมากกว่า 0")
        else:
            if value <= 0:
                raise ValueError(f"{name} ต้องมากกว่า 0")
    if not positive and allow_zero is False:
        pass
    return float(value)


def _base_result(mode):
    return {
        "mode": mode,
        "vb_v": None,
        "ve_v": None,
        "vc_v": None,
        "vce_v": None,
        "ic_ma": None,
        "ib_a": None,
        "ic_a": None,
        "ie_a": None,
        "vth_v": None,
        "rth_ohm": None,
        "warnings": [],
        "errors": [],
        "model_ok": True,
    }


def _apply_forward_active_check(result, ib_a, vce_v):
    if ib_a <= 0:
        result["warnings"].append("แบบจำลอง Forward Active อาจใช้ไม่ได้ (I_B ≤ 0)")
        result["model_ok"] = False
    if vce_v is not None and vce_v <= VCE_SAT:
        result["warnings"].append("แบบจำลอง Forward Active อาจใช้ไม่ได้ (V_CE ≤ 0.2 V)")
        result["model_ok"] = False


def calculate_fixed_bias(vcc, rc, beta, vbe, rb):
    result = _base_result("fixed")
    try:
        vcc = _num(vcc, "VCC")
        rc = _num(rc, "RC")
        beta = _num(beta, "beta", positive=True)
        vbe = _num(vbe, "VBE")
        rb = _num(rb, "RB", positive=True)
        if vcc < 0:
            raise ValueError("VCC ต้องไม่เป็นค่าลบ")
        if rc < 0:
            raise ValueError("RC ต้องไม่เป็นค่าลบ")
        if vbe < 0:
            raise ValueError("VBE ต้องไม่เป็นค่าลบ")
    except ValueError as e:
        result["errors"].append(str(e))
        result["model_ok"] = False
        return result

    ib = (vcc - vbe) / rb
    ic = beta * ib
    ie = (beta + 1) * ib
    ve = 0.0
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve
    result.update({
        "vb_v": vb, "ve_v": ve, "vc_v": vc, "vce_v": vce,
        "ic_ma": ic * 1000.0, "ib_a": ib, "ic_a": ic, "ie_a": ie,
    })
    _apply_forward_active_check(result, ib, vce)
    return result


def calculate_emitter_bias(vcc, rc, beta, vbe, rb, re):
    result = _base_result("emitter")
    try:
        vcc = _num(vcc, "VCC")
        rc = _num(rc, "RC")
        beta = _num(beta, "beta", positive=True)
        vbe = _num(vbe, "VBE")
        rb = _num(rb, "RB", positive=True)
        re = _num(re, "RE")
        if vcc < 0:
            raise ValueError("VCC ต้องไม่เป็นค่าลบ")
        if rc < 0:
            raise ValueError("RC ต้องไม่เป็นค่าลบ")
        if re < 0:
            raise ValueError("RE ต้องไม่เป็นค่าลบ")
        if vbe < 0:
            raise ValueError("VBE ต้องไม่เป็นค่าลบ")
    except ValueError as e:
        result["errors"].append(str(e))
        result["model_ok"] = False
        return result

    denom = rb + (beta + 1) * re
    if denom == 0:
        result["errors"].append("ตัวหารสำหรับคำนวณ I_B เป็นศูนย์")
        result["model_ok"] = False
        return result
    ib = (vcc - vbe) / denom
    ic = beta * ib
    ie = (beta + 1) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve
    result.update({
        "vb_v": vb, "ve_v": ve, "vc_v": vc, "vce_v": vce,
        "ic_ma": ic * 1000.0, "ib_a": ib, "ic_a": ic, "ie_a": ie,
    })
    _apply_forward_active_check(result, ib, vce)
    return result


def calculate_voltage_divider_bias(vcc, rc, beta, vbe, r1, r2, re):
    result = _base_result("divider")
    try:
        vcc = _num(vcc, "VCC")
        rc = _num(rc, "RC")
        beta = _num(beta, "beta", positive=True)
        vbe = _num(vbe, "VBE")
        r1 = _num(r1, "R1", positive=True)
        r2 = _num(r2, "R2", positive=True)
        re = _num(re, "RE")
        if vcc < 0:
            raise ValueError("VCC ต้องไม่เป็นค่าลบ")
        if rc < 0:
            raise ValueError("RC ต้องไม่เป็นค่าลบ")
        if re < 0:
            raise ValueError("RE ต้องไม่เป็นค่าลบ")
        if vbe < 0:
            raise ValueError("VBE ต้องไม่เป็นค่าลบ")
        if (r1 + r2) == 0:
            raise ValueError("R1 + R2 ต้องมากกว่า 0")
    except ValueError as e:
        result["errors"].append(str(e))
        result["model_ok"] = False
        return result

    vth = vcc * r2 / (r1 + r2)
    rth = (r1 * r2) / (r1 + r2)
    denom = rth + (beta + 1) * re
    if denom == 0:
        result["errors"].append("ตัวหารสำหรับคำนวณ I_B เป็นศูนย์")
        result["model_ok"] = False
        result.update({"vth_v": vth, "rth_ohm": rth})
        return result
    ib = (vth - vbe) / denom
    ic = beta * ib
    ie = (beta + 1) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve
    result.update({
        "vb_v": vb, "ve_v": ve, "vc_v": vc, "vce_v": vce,
        "ic_ma": ic * 1000.0, "ib_a": ib, "ic_a": ic, "ie_a": ie,
        "vth_v": vth, "rth_ohm": rth,
    })
    _apply_forward_active_check(result, ib, vce)
    return result


def analyze(mode, values):
    mode = (mode or "").strip().lower()
    if mode in ("divider", "voltage_divider", "voltage-divider"):
        return calculate_voltage_divider_bias(
            values.get("VCC"), values.get("RC"), values.get("beta"), values.get("VBE"),
            values.get("R1"), values.get("R2"), values.get("RE"),
        )
    if mode in ("fixed", "fixed_bias", "fixed-bias"):
        return calculate_fixed_bias(
            values.get("VCC"), values.get("RC"), values.get("beta"), values.get("VBE"),
            values.get("RB"),
        )
    if mode in ("emitter", "emitter_bias", "emitter-bias"):
        return calculate_emitter_bias(
            values.get("VCC"), values.get("RC"), values.get("beta"), values.get("VBE"),
            values.get("RB"), values.get("RE"),
        )
    result = _base_result(mode or "unknown")
    result["errors"].append("ไม่รู้จักโหมดวงจรที่เลือก")
    result["model_ok"] = False
    return result
