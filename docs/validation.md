# Validation — Lab 03 (A1–A5) + Lab 04 (B1–B8)

## Environment
- Date: 2026-11-24
- Repo: https://github.com/bank3939/gitlab.git
- Python/Flask: per local environment
- ngspice: **NOT FOUND in current environment** (`ngspice` not in PATH/common locations) — SPICE real-run cases requiring engine are marked NOT RUN until ngspice is installed.

## Lab 03 Regression (A1–A5) — Analytical
| Case | Input | Expected | Observed | Status | Evidence |
|---|---|---:|---:|---|---|
| A1 Divider | VCC=12, RC=2200, beta=100, VBE=0.7, R1=100k, R2=22k, RE=1k | IC 1.22986 mA, VCE 8.05216 V | IC 1.22986 mA, VCE 8.05216 V | PASS | `tests/test_dc_bias.py`, `tests/test_app.py` |
| A2 Fixed | RB=1MΩ | IC 1.13 mA, VCE 9.514 V | matches | PASS | unit tests |
| A3 Emitter | RB=1MΩ, RE=1kΩ | IC 1.02634 mA, VCE 8.70545 V | matches | PASS | unit tests |
| A4 Emitter | RB=1MΩ, RE=2kΩ | IC 0.94010 mA, VCE 8.03278 V (IC ↓) | matches | PASS | unit tests |
| A5 Invalid | Fixed RB=0 | Error, no crash, no stale result | error shown, no result panel | PASS | unit tests |

## Lab 04 Browser/Simulation Acceptance (B1–B8)
| Case | Method | Expected/Check | Observed | Status | Evidence |
|---|---|---|---|---|---|
| B1 Regression | test_client/manual form | Lab 3 3 modes still work (A1-A5 values) | 16 tests pass incl. regression | PASS | automated tests run 2026-11-24 |
| B2 DC SPICE | Browser + ngspice | .op returns VB/VE/VC/VCE/IC with ngspice provenance | ngspice not installed in env | NOT RUN | app shows engine not ready; install ngspice to run |
| B3 Change RE | Browser + ngspice | changing RE changes OP/gain | blocked by missing ngspice | NOT RUN | — |
| B4 AC | Browser + ngspice | Bode plot from real .ac, axes/units | blocked by missing ngspice | NOT RUN | — |
| B5 Transient | Browser + ngspice | Vin/Vout vs time from real .tran | blocked by missing ngspice | NOT RUN | — |
| B6 Change Source | Browser + ngspice | waveform changes with amplitude/freq | blocked by missing ngspice | NOT RUN | — |
| B7 Invalid/Fail | code review/manual | invalid input or missing engine shows error, no fake success plot | missing ngspice returns explicit error, no success chart | PASS (error-path) | `spice_engine.py`/UI error handling |
| B8 UI responsive | Browser/manual | desktop/mobile readable, no critical cut-off | basic responsive CSS/layout in place; needs real browser screenshot on target machine | PARTIAL | visual smoke check recommended |

## Notes
- SPICE results must be labeled as `ngspice .op/.ac/.tran (real simulation)` and not mixed with analytical DC bias.
- When ngspice is installed, rerun B2–B6 and capture browser screenshots/logs into `docs/evidence/`.
