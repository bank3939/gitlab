# Task 2 Report: Flask app, templates, and CSS (BJT CE DC bias)

## Status
DONE

## What implemented
- **`app.py`**: Flask app with `GET/POST /`.
  - Defines the 7 input fields `VCC, R1, R2, RC, RE, beta, VBE` with sensible defaults.
  - `_parse_inputs` parses POST form values to floats, treats empty as required error, and rejects non-numeric/non-finite values gracefully (collects parse errors instead of raising).
  - On successful parse, calls `analyze_bjt_ce(**numeric)` from `bjt_bias.py` and renders results.
  - Re-renders form with entered values and separate `parse_errors` block when input parsing fails; displays logic `result.errors`/`result.warnings` and results when analysis runs.
- **`templates/index.html`**: Labeled inputs for all 7 parameters with submit button; results panel showing `Region`, results table with columns `VTH (V), RTH (Ω), IB (A), IC (A), IE (A), VB (V), VE (V), VC (V), VCE (V)`, and separate warning/error blocks for parse errors, validation errors, and warnings. Renders `—` for `None` numeric outputs.
- **`static/style.css`**: Simple readable layout (grid form, card panels, styled table, distinct error/warning styling).
- **`tests/test_app.py`**: Smoke/app tests using Flask `test_client`:
  - `GET /` returns 200 and response contains `VCC`.
  - `POST /` with valid reference inputs computes and response contains `VCE`.

## TDD evidence

### RED (failing before implementation)
Command:
```powershell
python -m unittest tests.test_app 2>&1 | Select-Object -Last 40
```
Result summary (FAILED, errors=2): `ModuleNotFoundError: No module named 'app'` for both `test_get_index_contains_vcc` and `test_post_computes_and_contains_vce`. (2 tests ran, 0.003s)

### GREEN (after implementation)
Commands:
```powershell
python -m unittest tests.test_app 2>&1 | Select-Object -Last 30
python -m unittest tests.test_bjt_bias 2>&1 | Select-Object -Last 30
python -c "from app import app; c=app.test_client(); r=c.get('/'); print(r.status_code, 'VCC' in r.get_data(as_text=True)); r=c.post('/', data={'VCC':'12','R1':'40000','R2':'10000','RC':'2000','RE':'1000','beta':'100','VBE':'0.7'}); print(r.status_code, 'VCE' in r.get_data(as_text=True))"
```
Results:
- `tests.test_app`: `Ran 2 tests in 0.307s` — **OK**
- `tests.test_bjt_bias`: `Ran 4 tests in 0.000s` — **OK**
- Manual smoke via test_client (localhost-equivalent request cycle): `200 True` (GET contains VCC), `200 True` (POST computes and contains VCE)

Notes: In this PowerShell environment, unittest/print output routed through stderr/warnings caused non-zero exit codes when captured with `2>&1`, but the test summaries and smoke output show all assertions passing.

## Tests run and results (summary)
| Command | Result |
|---|---|
| `python -m unittest tests.test_app` | 2 tests, OK |
| `python -m unittest tests.test_bjt_bias` | 4 tests, OK |
| Inline `test_client` GET/POST smoke | `200 True`, `200 True` (VCC/VCE present) |

## Files changed
- Created: `app.py`
- Created: `templates/index.html`
- Created: `static/style.css`
- Created: `tests/test_app.py`

## Commit
- `f5dcb70` — `feat: add Flask UI for BJT CE DC bias calculator` (4 files changed, 201 insertions)

## Self-review findings
- Requirements met: 7 labeled inputs and submit; results table with requested headers/units `VTH(V),RTH(Ω),IB(A),IC(A),IE(A),VB(V),VE(V),VC(V),VCE(V)`; region and warning/error blocks displayed; POST parses to floats and handles non-numeric/empty/non-finite gracefully via parse errors; logic errors/warnings from `analyze_bjt_ce` surfaced in UI.
- Separation of concerns preserved: analysis in `bjt_bias.py`, routes in `app.py`, view in `templates/index.html`, styling in `static/style.css`, tests in `tests/`.
- Existing files (`electrical.py`, `test_electrical.py`, `README.md`, `bjt_bias.py`, existing tests) not modified.
- `analyze_bjt_ce` may return `region="unknown"` with `None` numeric outputs on invalid input; template handles this by showing `—` and error/warning blocks.

## Issues / concerns
- **Flask not preinstalled**: installed via `python -m pip install flask` (Flask 3.1.3) to complete implementation; install emitted PATH warning for user scripts and a pip update notice.
- **No `pytest` installed**: existing/project tests run successfully with `unittest` as shown; `python -m pytest` unavailable in environment.
- **Raw numeric display**: results render Python float/string values without fixed formatting/scientific notation; values are correct but can be long (e.g. small currents). Acceptable for base SI-unit output but could be formatted for readability in future.
- **No live server smoke**: did not start a persistent `localhost` dev server process; verified equivalent request/response behavior via Flask `test_client` GET/POST (and app is runnable via `python app.py`).
- Unrelated untracked paths (`.superpowers/`, `docs/`) left untouched and uncommitted as required.
