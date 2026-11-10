# Task 1 Report: Engineering logic and unit tests (BJT CE DC bias)

## Status
Implemented and verified. Commit created.

## What was implemented
- Created `bjt_bias.py` with `analyze_bjt_ce(VCC, R1, R2, RC, RE, beta, VBE) -> dict`.
- Returns DC operating-point values in base SI units (V, ohm, A) with keys: `VTH, RTH, IB, IC, IE, VB, VE, VC, VCE, region, warnings, errors`.
- Input validation collects errors into `errors` (no exceptions raised for UI-facing invalid inputs) and returns numeric outputs as `None` when invalid.
- Uses Thevenin equivalent: `VTH = VCC*R2/(R1+R2)`, `RTH = R1||R2`.
- Uses `VCE_SAT = 0.2 V`.
- Region/warning logic:
  - **cutoff** when base drive is insufficient (`VTH <= VBE` or computed IB <= 0): currents zeroed, `VB=VTH`, `VE=0`, `VC=VCC`, `VCE=VCC`, warning added.
  - **saturation** when active-formula `VCE <= VCE_SAT`: region set to `saturation` with warning.
  - **active** otherwise.

## Files changed
- `bjt_bias.py` (new): pure engineering logic module.
- `tests/test_bjt_bias.py` (new): unit tests per brief.
- Existing files not modified: `electrical.py`, `test_electrical.py`, `README.md`.

## TDD evidence

### RED (tests first, failing as expected)
Command:
```powershell
python -m unittest tests.test_bjt_bias -v
```
Result summary (before implementation): failed during import because module did not exist.
Key output:
- `ImportError: Failed to import test module: test_bjt_bias`
- `ModuleNotFoundError: No module named 'bjt_bias'`
- `Ran 1 test in 0.000s` / `FAILED (errors=1)`

### GREEN (minimal implementation, tests pass)
Command:
```powershell
python -m unittest tests.test_bjt_bias -v
```
Result summary: all 4 tests passed.
Key output:
- `test_active_reference ... ok`
- `test_cutoff ... ok`
- `test_invalid_r1_zero ... ok`
- `test_saturation_warning ... ok`
- `Ran 4 tests in 0.000s` / `OK`

Notes: PowerShell reported a native-command nonzero exit code in this environment due to verbose unittest output on stderr, but the unittest result itself is `OK` with 4/4 passing.

## Tests added (per brief)
- **Active reference** (independent hand calc): `VCC=12,R1=40000,R2=10000,RC=2000,RE=1000,beta=100,VBE=0.7` -> `VTH=2.4V`, `RTH=8000ohm`, `IB=1.7/109000 A`, `IC=100*IB`, `IE=101*IB`, expected node/`VCE` values, `region='active'`, no errors/warnings.
- **Saturation warning**: `VCC=5,R1=10000,R2=10000,RC=10000,RE=100,beta=200,VBE=0.7` -> `region='saturation'`, warnings include `saturation`.
- **Cutoff**: `VCC=12,R1=100000,R2=1000,RC=2000,RE=1000,beta=100,VBE=0.7` -> `region='cutoff'`, warnings present.
- **Invalid input**: `R1=0` -> `errors` present.

## Commit
- `e8aaa01` — `feat: add BJT CE DC bias logic and tests`
- Staged/committed only: `bjt_bias.py`, `tests/test_bjt_bias.py`

## Self-review
- **Correctness:** Active-case math matches the independent hand calculation in the brief (Thevenin divider/parallel, base loop with `(beta+1)*RE`, collector/emitter currents and voltages, `VCE`).
- **API/shape:** Function name, parameters, and required output keys match spec; outputs are base SI numeric values suitable for later UI unit formatting.
- **Validation:** Collects errors for non-finite/non-numeric and invalid parameter ranges (including `R1<=0`) instead of raising.
- **Separation:** Pure logic only in `bjt_bias.py`; tests isolated in `tests/test_bjt_bias.py`; no Flask/routes/templates/css added.
- **Scope:** No AC, transient, full circuit editor, or FET features; existing files left intact.

## Issues/concerns
- Saturation is detected and reported as a warning/region based on `VCE <= 0.2V` using the active-region equations; a more physically detailed saturation model would clamp/recompute currents differently, but that is beyond the stated DC-bias operating-point/warning scope.
- In cutoff, returned `VB=VTH`, `VE=0`, `VC=VCC`, `VCE=VCC` represent the no-conduction DC state consistent with the warning; this matches expected behavior for the specified case.
- No broader regression suite was run beyond the new task tests (existing repo tests unchanged).

## Verification commands
```powershell
python -m unittest tests.test_bjt_bias -v
& 'C:\Users\B6821241\AppData\Local\Programs\Git\cmd\git.exe' --no-pager log -1 --oneline
```
