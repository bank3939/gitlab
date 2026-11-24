# UI / Impeccable Evidence (Lab 04)

## Before (ก่อนปรับ AC graph)
- Commit อ้างอิง: `fce0d01` (Lab 04 v1)
- AC plot แบบเดิม: กราฟเดียวรวม Gain และ Phase สองแกน y ใน canvas เดียว, label/reference ไม่ชัด, parser AC มี bug (wrdata 7-column mapping ผิด ทำให้ gain/phase ถูกอ่านเป็น frequency)

## After (หลังปรับ)
- Commits: `36ba310` (prefer `ngspice_con.exe`), `accd728` (fix AC wrdata parsing + improve Bode plot UI)
- แก้ parser ใน `spice_engine.py` ให้รองรับรูปแบบ wrdata 7 คอลัมน์จริง: `f, f, 0, f, gain_db, f, phase`
- ปรับ UI เป็น Bode Plot 2 แผง (Magnitude / Phase) พร้อม reference ชัด:
  - `Av(f) = V(vout) / V(vin)`
  - `Magnitude = 20·log10(|Av|) (dB)`
  - `Phase = ∠Av (deg)`
  - `Frequency (Hz, log scale)`
- เพิ่ม tooltip, grid, styling, และแยก provenance SPICE/analytical ชัดเจน

## Evidence files
- `B4_ac_bode.jpg` — หลังปรับ (Bode 2 แผง, reference ชัด)
- `B2_op.jpg`, `B3_op_RE2k.jpg`, `B5_tran.jpg`, `B6_tran_changed.jpg`, `B7_error.jpg`
- `B8_desktop.jpg`, `B8_mobile_simulated.jpg` (mobile เป็นการจำลองความกว้าง 390px ไม่ใช่ device emulation จริง)

## Checklist
- [x] ผล SPICE แสดง provenance จริง (`ngspice .op/.ac/.tran (real simulation)`)
- [x] Error/invalid input แสดงข้อความชัด และไม่แสดงกราฟ/ผลสำเร็จปลอม
- [x] AC มี reference/แกน/หน่วยชัด
- [x] ไม่กระทบผลคำนวณ Lab 3 (A1–A5 ผ่าน)
- [ ] เก็บ screenshot "before" จริงจาก commit เก่าเพิ่มเติม (ถ้าต้องการหลักฐานภาพก่อนหน้า)