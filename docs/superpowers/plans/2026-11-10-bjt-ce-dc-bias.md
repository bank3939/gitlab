# BJT Common-Emitter DC Bias Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest working Flask web app that computes and displays the DC operating point of a BJT common-emitter voltage-divider bias circuit with units, validation/region warnings, and tests compared to an independent engineering calculation.

**Architecture:** Pure Python engineering logic in `bjt_bias.py` performs validation and Thevenin-bias DC calculations; `app.py` contains only Flask routes/input parsing and rendering. A single Jinja template and CSS present inputs/results/warnings. Tests verify logic against hand-calculated reference values and edge conditions.

**Tech Stack:** Python 3.12, Flask, Jinja2 templates, CSS, pytest/unittest (`python -m pytest` or `unittest`).

**Spec:** `docs/superpowers/specs/2026-11-10-bjt-ce-dc-bias-design.md`

## Global Constraints
- Inputs exactly: `VCC, R1, R2, RC, RE, beta, VBE`.
- Outputs: DC operating point with units, validation and region warnings.
- Separate Python engineering logic, Flask routes, HTML templates, CSS and tests.
- No AC, transient, full circuit editor, or FET.
- Keep existing workspace files (`electrical.py`, `test_electrical.py`, `README.md`) intact.
- `VCEsat = 0.2 V` for saturation warning (default).

## Review Focus
- Non-numeric/blank inputs: show clear validation error, no crash/500.
- Non-physical values (e.g. `R1<=0`, `beta<=0`, `VCC<=0`): rejected with warning/error.
- Cutoff condition (`VTH <= VBE` or `IB <= 0`): region reported as cutoff with warning, values shown consistently.
- Saturation condition (`VCE <= 0.2 V`): saturation warning while still reporting computed operating point.
- Divider edge cases (`R1+R2` issues avoided by validation): no divide-by-zero.

---

### Task 1: Engineering logic and unit tests

**Files:**
- Create: `bjt_bias.py`
- Create: `tests/test_bjt_bias.py`

**Interfaces:**
- Consumes: numeric inputs `(VCC, R1, R2, RC, RE, beta, VBE)` as floats.
- Produces: `analyze_bjt_ce(VCC, R1, R2, RC, RE, beta, VBE) -> dict` with keys `VTH,RTH,IB,IC,IE,VB,VE,VC,VCE,region,warnings,errors` (numeric values in base SI units: V, ohm, A) suitable for UI formatting with units.

- [ ] **Step 1: Write the failing tests (independent hand calculation + cases)**

```python
# tests/test_bjt_bias.py
import math
import unittest
from bjt_bias import analyze_bjt_ce

class TestBjtBias(unittest.TestCase):
    def test_active_region_reference_case(self):
        # Independent hand calc: VCC=12,R1=40k,R2=10k,RC=2k,RE=1k,beta=100,VBE=0.7
        # VTH=12*10/(40+10)=2.4V, RTH=40k||10k=8k
        # IB=(2.4-0.7)/(8000+101000)=1.7/109000=1.559633e-5A
        # IC=1.559633e-3A, IE=1.575229e-3A
        # VE=1.575229V, VC=12-3.119266=8.880734V, VCE=7.305505V
        r = analyze_bjt_ce(12, 40000, 10000, 2000, 1000, 100, 0.7)
        self.assertAlmostEqual(r["VTH"], 2.4, places=6)
        self.assertAlmostEqual(r["RTH"], 8000.0, places=6)
        self.assertAlmostEqual(r["IB"], 1.7/109000, places=10)
        self.assertAlmostEqual(r["IC"], 100*1.7/109000, places=9)
        self.assertAlmostEqual(r["IE"], 101*1.7/109000, places=9)
        self.assertAlmostEqual(r["VCE"], 12 - (100*1.7/109000)*2000 - (101*1.7/109000)*1000, places=6)
        self.assertEqual(r["region"], "active")
        self.assertFalse(r["errors"])

    def test_saturation_warning(self):
        r = analyze_bjt_ce(5, 10000, 10000, 10000, 100, 200, 0.7)
        self.assertEqual(r["region"], "saturation")
        self.assertTrue(any("saturation" in w.lower() for w in r["warnings"]))

    def test_cutoff_warning(self):
        r = analyze_bjt_ce(12, 100000, 1000, 2000, 1000, 100, 0.7)
        self.assertEqual(r["region"], "cutoff")
        self.assertTrue(r["warnings"])

    def test_invalid_inputs(self):
        r = analyze_bjt_ce(12, 0, 10000, 2000, 1000, 100, 0.7)
        self.assertTrue(r["errors"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_bjt_bias.py -v` (or `python -m unittest tests.test_bjt_bias -v`)
Expected: FAIL (module/function missing).

- [ ] **Step 3: Implement `bjt_bias.py`**

Implement `analyze_bjt_ce` with input validation (collect errors, do not raise for UI), Thevenin calculations, `VCEsat=0.2`, region/warnings logic, and return all DC values in base units. Ensure math uses floats and handles edge cases safely.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_bjt_bias.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add bjt_bias.py tests/test_bjt_bias.py
git commit -m "feat: add BJT CE DC bias logic and tests"
```

### Task 2: Flask app, templates, and CSS

**Files:**
- Create: `app.py`
- Create: `templates/index.html`
- Create: `static/style.css`
- Create: `tests/test_app.py` (minimal route/smoke test)

**Interfaces:**
- Consumes: `analyze_bjt_ce` from `bjt_bias.py`.
- Produces: running Flask app at `/` with form inputs `VCC,R1,R2,RC,RE,beta,VBE`, results table with units, and validation/region warnings.

- [ ] **Step 1: Write failing app/smoke tests**

```python
# tests/test_app.py
import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'VCC', resp.data)

    def test_post_computes(self):
        resp = self.client.post('/', data=dict(VCC='12',R1='40000',R2='10000',RC='2000',RE='1000',beta='100',VBE='0.7'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'VCE', resp.data)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_app.py -v`
Expected: FAIL (app missing).

- [ ] **Step 3: Implement `app.py`, `templates/index.html`, `static/style.css`**

- `app.py`: parse POST form to floats, call `analyze_bjt_ce`, pass inputs/results/errors/warnings; handle non-numeric input gracefully.
- Template: labeled form fields for all 7 inputs, submit, results table showing `VTH (V), RTH (Ω), IB (A), IC (A), IE (A), VB (V), VE (V), VC (V), VCE (V)` and region, warning/error blocks.
- CSS: simple readable layout.

- [ ] **Step 4: Run all tests and manual localhost check**

Run: `python -m pytest -q` (and/or `python -m unittest discover -v`)
Expected: PASS. Then run `python app.py` (or `flask --app app run`) and verify page loads at localhost.

- [ ] **Step 5: Commit**

```bash
git add app.py templates/index.html static/style.css tests/test_app.py
git commit -m "feat: add Flask UI for BJT CE DC bias calculator"
```

### Task 3: Final verification, demo readiness, and GitHub commit

**Files:**
- Modify (if needed): `README.md` (brief run/test instructions for this lab, without removing prior content intent) — optional/minimal.

**Interfaces:**
- Produces: verified test run output, localhost demo readiness, and final commit(s) pushed/prepared as repo state allows.

- [ ] **Step 1: Run full verification**

Run: `python -m pytest -q`
Expected: all tests pass, including reference-case comparison.

- [ ] **Step 2: Smoke-run localhost app**

Run: `python app.py` and confirm form + results/warnings render.
Expected: working demo on localhost.

- [ ] **Step 3: Final commit and report**

```bash
git add -A
git status
git commit -m "chore: finalize BJT CE DC bias lab app" (if needed)
```
Note: if no git remote/repo configured, report status and provide commit hash/readiness.
