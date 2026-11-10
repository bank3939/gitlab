# Task 2: Flask app, templates, and CSS

**Files:**
- Create: `app.py`
- Create: `templates/index.html`
- Create: `static/style.css`
- Create: `tests/test_app.py`

**Interfaces:**
- Consumes: `analyze_bjt_ce` from `bjt_bias.py`.
- Produces: running Flask app at `/` with form inputs VCC,R1,R2,RC,RE,beta,VBE, results table with units, and validation/region warnings.

**Steps:**
1. Write failing app/smoke tests in `tests/test_app.py` (GET / 200 contains VCC; POST computes and response contains VCE).
2. Run tests to verify fail.
3. Implement `app.py` (parse POST to floats, call analyze_bjt_ce, handle non-numeric gracefully), `templates/index.html` (labeled 7 inputs, submit, results table VTH(V),RTH(Ω),IB(A),IC(A),IE(A),VB(V),VE(V),VC(V),VCE(V), region, warning/error blocks), `static/style.css` (simple readable layout).
4. Run all tests and manual localhost check.
5. Commit.

**Global Constraints:** inputs VCC,R1,R2,RC,RE,beta,VBE; outputs with units, validation/region warnings; separate logic/routes/templates/css/tests; keep existing files intact.
