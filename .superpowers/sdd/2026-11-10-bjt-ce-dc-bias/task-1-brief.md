# Task 1: Engineering logic and unit tests

**Files:**
- Create: `bjt_bias.py`
- Create: `tests/test_bjt_bias.py`

**Interfaces:**
- Consumes: numeric inputs `(VCC, R1, R2, RC, RE, beta, VBE)` as floats.
- Produces: `analyze_bjt_ce(VCC, R1, R2, RC, RE, beta, VBE) -> dict` with keys `VTH,RTH,IB,IC,IE,VB,VE,VC,VCE,region,warnings,errors` (numeric values in base SI units: V, ohm, A) suitable for UI formatting with units.

**Steps:**
1. Write failing tests in `tests/test_bjt_bias.py` (independent hand calculation + cases).
   - Active reference (independent hand calc): VCC=12,R1=40000,R2=10000,RC=2000,RE=1000,beta=100,VBE=0.7
     VTH=12*10/(40+10)=2.4V, RTH=40k||10k=8000ohm
     IB=(2.4-0.7)/(8000+101000)=1.7/109000 A
     IC=100*IB, IE=101*IB
     VCE=12 - IC*2000 - IE*1000, region "active", no errors.
   - Saturation warning: e.g. VCC=5,R1=10000,R2=10000,RC=10000,RE=100,beta=200,VBE=0.7 => region "saturation", warnings contain "saturation".
   - Cutoff: e.g. VCC=12,R1=100000,R2=1000,RC=2000,RE=1000,beta=100,VBE=0.7 => region "cutoff", warnings present.
   - Invalid: R1=0 => errors present.
2. Run tests to verify fail.
3. Implement `bjt_bias.py`: `analyze_bjt_ce` with input validation (collect errors, do not raise for UI), Thevenin calculations, VCEsat=0.2, region/warnings logic, return all DC values in base units.
4. Run tests to verify pass.
5. Commit: `git add bjt_bias.py tests/test_bjt_bias.py && git commit -m "feat: add BJT CE DC bias logic and tests"`

**Global Constraints:** inputs VCC,R1,R2,RC,RE,beta,VBE; outputs DC operating point with units, validation and region warnings; separate logic/routes/templates/css/tests; no AC/transient/editor/FET; keep existing files intact; VCEsat=0.2V.
