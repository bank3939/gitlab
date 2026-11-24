# Validation — Lab 03 (A1–A5) + Lab 04 (B1–B8)

## Environment
- Date: 2026-11-24
- Repo: https://github.com/bank3939/gitlab.git
- App: Flask local (`python app.py`, `http://127.0.0.1:5000/`)
- ngspice: **ngspice-47** installed at `C:\Spice64\bin\ngspice_con.exe` (detected by `spice_engine.find_ngspice()`)

## Lab 03 Regression (A1–A5) — Analytical
| Case | Input | Expected | Observed (browser, real) | Status | Evidence |
|---|---|---:|---:|---|---|
| A1 Divider | VCC=12, RC=2200, beta=100, VBE=0.7, R1=100k, R2=22k, RE=1k | IC 1.22986 mA, VCE 8.05216 V | IC 1.22986 mA, VCE 8.05216 V | PASS | browser form submit + `tests/test_dc_bias.py` |
| A2 Fixed | RB=1MΩ | IC 1.13 mA, VCE 9.514 V | IC 1.13 mA, VCE 9.514 V | PASS | browser + unit tests |
| A3 Emitter | RB=1MΩ, RE=1kΩ | IC 1.02634 mA, VCE 8.70545 V | IC 1.02634 mA, VCE 8.70545 V | PASS | browser + unit tests |
| A4 Emitter | RB=1MΩ, RE=2kΩ | IC 0.94010 mA, VCE 8.03278 V | IC 0.94010 mA, VCE 8.03278 V | PASS | browser + unit tests |
| A5 Invalid | Fixed RB=0 | Error, no crash, no stale result | "RB ต้องมากกว่า 0", no result panel | PASS | browser + unit tests |

## Lab 04 Browser/Simulation Acceptance (B1–B8)
| Case | Method | Expected/Check | Observed (real browser + ngspice) | Status | Evidence |
|---|---|---|---|---|---|
| B1 Regression | Browser form | Lab 3 3 modes still work (A1-A5) | A1-A5 all match expected values/errors | PASS | browser run 2026-11-24 |
| B2 DC SPICE | Browser + ngspice `.op` | VB/VE/VC/VCE/IC with ngspice provenance | VB=2.00367 V, VE=1.33288 V, VC=9.08722 V, VCE=7.75434 V, IC≈1.42396 mA, badge `ngspice .op (real simulation)` | PASS | browser run 2026-11-24 |
| B3 Change RE | Browser + ngspice `.op` | changing RE changes OP | RE=1k: VCE=7.75434 V, IC=1.42396 mA; RE=2k: VCE=9.03153 V, IC=0.803643 mA (OP changed) | PASS | browser run 2026-11-24 |
| B4 AC | Browser + ngspice `.ac` | Bode plot from real .ac, axes/units/reference clear | 201 points, Bode 2-panel: Gain Magnitude `|V(vout)/V(vin)| (dB)`, Phase `∠V(vout)/V(vin) (deg)`, Frequency Hz log; ref `Av(f)=V(vout)/V(vin)` shown | PASS | browser run 2026-11-24 |
| B5 Transient | Browser + ngspice `.tran` | Vin/Vout vs time from real .tran | 2 datasets (Vin/Vout), 1008 points each, badge `ngspice .tran (real simulation)` | PASS | browser run 2026-11-24 |
| B6 Change Source | Browser + ngspice `.tran` | waveform changes with amplitude/freq | amp/freq changed (10mV/1kHz → 50mV/2kHz), tran rerun produced real waveform result (1008 points) | PASS | browser run 2026-11-24 |
| B7 Invalid/Fail | Browser/manual | invalid input or missing engine shows error, no fake success plot | R1=-1 => "R1 ต้องมากกว่า 0" error panel, no SPICE result/graph | PASS | browser run 2026-11-24 |
| B8 UI responsive | Browser/manual | desktop/mobile readable, no critical cut-off | Desktop layout verified; mobile/narrow viewport screenshot not yet captured in this session | PARTIAL | needs mobile screenshot in `docs/evidence/` |

## Notes
- SPICE results are labeled as `ngspice .op/.ac/.tran (real simulation)` and kept separate from analytical DC bias.
- AC parser bug (wrdata 7-column mapping) was fixed; Bode plot now uses correct gain/phase data.
- For full submission evidence, capture and store browser screenshots/logs in `docs/evidence/` (B2 op, B3 RE compare, B4 bode, B5 tran, B6 changed source, B7 error, B8 desktop+mobile).