import math

VCE_SAT = 0.2


def analyze_bjt_ce(VCC, R1, R2, RC, RE, beta, VBE):
    """Analyze a BJT common-emitter DC bias circuit.

    Inputs: VCC, R1, R2, RC, RE, beta, VBE (numeric).
    Returns dict with keys:
      VTH, RTH, IB, IC, IE, VB, VE, VC, VCE, region, warnings, errors
    Values in base SI units (V, ohm, A). On invalid input, errors are collected
    and numeric outputs may be None.
    """
    errors = []
    warnings = []
    result = {
        "VTH": None,
        "RTH": None,
        "IB": None,
        "IC": None,
        "IE": None,
        "VB": None,
        "VE": None,
        "VC": None,
        "VCE": None,
        "region": "unknown",
        "warnings": warnings,
        "errors": errors,
    }

    params = {
        "VCC": VCC,
        "R1": R1,
        "R2": R2,
        "RC": RC,
        "RE": RE,
        "beta": beta,
        "VBE": VBE,
    }

    for name, value in params.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{name} must be a finite number.")
            continue
        if not math.isfinite(value):
            errors.append(f"{name} must be a finite number.")

    if errors:
        return result

    # Basic physical/validity constraints
    if VCC < 0:
        errors.append("VCC must be non-negative.")
    if R1 <= 0:
        errors.append("R1 must be greater than zero.")
    if R2 <= 0:
        errors.append("R2 must be greater than zero.")
    if RC < 0:
        errors.append("RC must be non-negative.")
    if RE < 0:
        errors.append("RE must be non-negative.")
    if beta <= 0:
        errors.append("beta must be greater than zero.")
    if VBE < 0:
        errors.append("VBE must be non-negative.")
    if R1 + R2 == 0:
        errors.append("R1 + R2 must be greater than zero.")

    if errors:
        return result

    vth = VCC * R2 / (R1 + R2)
    rth = (R1 * R2) / (R1 + R2)

    # Determine cutoff by base-emitter loop feasibility (Thevenin view)
    vbe_on = VBE
    ib = 0.0
    ic = 0.0
    ie = 0.0
    cutoff = vth <= vbe_on

    denom = rth + (beta + 1) * RE
    if not cutoff and denom <= 0:
        errors.append("Invalid bias network (non-positive Thevenin denominator).")
        return result

    if not cutoff:
        ib_calc = (vth - vbe_on) / denom
        if ib_calc <= 0:
            cutoff = True
        else:
            ib = ib_calc
            ic = beta * ib
            ie = (beta + 1) * ib

    vb = vth - ib * rth
    ve = ie * RE
    vc = VCC - ic * RC
    vce = vc - ve

    if cutoff:
        ib = 0.0
        ic = 0.0
        ie = 0.0
        vb = vth
        ve = 0.0
        vc = VCC
        vce = VCC
        region = "cutoff"
        warnings.append("Transistor is in cutoff (insufficient base drive).")
    else:
        # Active/saturation determination using VCEsat
        if vce <= VCE_SAT:
            region = "saturation"
            warnings.append(f"Transistor is in saturation (VCE <= {VCE_SAT} V).")
        else:
            region = "active"

    result.update(
        {
            "VTH": vth,
            "RTH": rth,
            "IB": ib,
            "IC": ic,
            "IE": ie,
            "VB": vb,
            "VE": ve,
            "VC": vc,
            "VCE": vce,
            "region": region,
            "warnings": warnings,
            "errors": errors,
        }
    )
    return result
