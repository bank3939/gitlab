# BJT Common-Emitter DC Bias Web App — Short Design (ENG29 2121)

**Approved:** 2026-11-10 (user: "ใช่ ทำเลย")

## Intent and why
Smallest working Flask web application for a short lab to compute the DC operating point of a BJT common-emitter voltage-divider bias circuit, with units, validation/region warnings, and comparison to an independent engineering calculation. Needed for a running localhost demo and GitHub commit today.

## Goals
- Separate Python engineering logic, Flask routes, HTML templates, CSS, and tests.
- Inputs: `VCC`, `R1`, `R2`, `RC`, `RE`, `beta`, `VBE`.
- Outputs: DC operating point with units, validation and region warnings.
- Compare results with an independent engineering calculation (documented hand/formula reference cases in tests).

## Non-goals / anti-goals
- No AC analysis, transient analysis, full circuit editor, or FET support.
- No JavaScript-heavy UI, plotting, or persistence.

## Constraints
- Must be a real Flask web app runnable on localhost.
- Keep implementation minimal and do not break existing DC-resistor lab files in this workspace.
- Use Thevenin equivalent voltage-divider bias analysis.

## Approaches considered
1. **Separated logic + Flask UI + tests (chosen):** `bjt_bias.py` pure calculation/validation, `app.py` routes only, Jinja template + CSS, tests with known hand-calculated values. *Trade-off:* a few files, but testable and meets required separation.
2. **Math in route/template:** smallest code count but untestable/mixed concerns and fails separation requirement. *Rejected.*
3. **SPA/AJAX or plotting app:** better UX but unnecessary complexity for short lab. *Rejected.*

## How (decided parts)
- **Engineering logic (`bjt_bias.py`)**: `analyze_bjt_ce(VCC,R1,R2,RC,RE,beta,VBE)` returns values with units context: `VTH,V,RTH,ohm,IB,A,IC,A,IE,A,VB,V,VE,V,VC,V,VCE,V,region,warnings,errors/valid`.
  - Formulas: `VTH = VCC*R2/(R1+R2)`, `RTH = R1*R2/(R1+R2)`, `IB = (VTH - VBE)/(RTH + (beta+1)*RE)`, `IC = beta*IB`, `IE = (beta+1)*IB`, `VB = VTH - IB*RTH`, `VE = IE*RE`, `VC = VCC - IC*RC`, `VCE = VC - VE`.
  - Validation: numeric/finite, `VCC>0`, `R1,R2,RC,RE>0`, `beta>0`, `VBE>=0`, `R1+R2>0`.
  - Region/warnings: cutoff if `IB <= 0` or emitter junction cannot turn on (`VTH <= VBE` effectively); saturation warning if `VCE <= 0.2 V` (`VCEsat` default 0.2 V); otherwise active/forward-active. Always report computed numbers and append warnings.
- **Routes (`app.py`)**: `GET/POST /` renders form, parses/validates input presence, calls logic, displays results or input errors.
- **UI (`templates/index.html`, `static/style.css`)**: single form, results table with units, validation/region warning banners.
- **Tests (`tests/test_bjt_bias.py`)**: independent hand-calculated reference case(s) (stepwise expected values), validation errors, cutoff and saturation cases.

## Left to the builder
- Exact formatting/rounding in UI, minor copy/layout, and concrete reference numeric example values chosen to be easy to verify by hand (documented in test).
