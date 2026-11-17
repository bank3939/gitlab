# Lab 03 — Browser / Form Validation (A1–A5)

**วิธีตรวจ:** ทดสอบผ่าน Flask `test_client` (ส่งฟอร์มจริงผ่าน route) และยืนยันด้วย unit tests (`tests/test_dc_bias.py`, `tests/test_app.py`) — เทียบเท่าการส่งฟอร์ม HTTP กับแอปจริง; สามารถทวนซ้ำด้วยเบราว์เซอร์ที่ `http://127.0.0.1:5000/`  
**ค่าร่วม:** VCC = 12 V, RC = 2.2 kΩ (2200 Ω), β = 100, VBE = 0.70 V  
**เกณฑ์เทียบ (ตามใบงาน):** |ΔIC| ≤ 0.01 mA, |ΔVCE| ≤ 0.02 V เทียบกับค่าอ้างอิงที่ยังไม่ปัดเศษ

## ค่าอ้างอิงอิสระ (คำนวณมือ/สมการจาก Engineering Electronics)

### A1 — Voltage Divider (R1=100 kΩ, R2=22 kΩ, RE=1 kΩ)
- VTH = VCC·R2/(R1+R2) = 12·22k/(122k) = 2.163934 V
- RTH = R1·R2/(R1+R2) = 18.032787 kΩ
- IB = (VTH−VBE)/(RTH+(β+1)RE) = (1.463934)/(18032.787+101000) = 12.2986 µA
- IC = βIB = 1.22986 mA, IE = (β+1)IB = 1.24216 mA
- VE = IERE = 1.24216 V, VB = VE+VBE = 1.94216 V
- VC = VCC−ICRC = 12−1.22986m·2200 = 9.29431 V, **VCE = VC−VE = 8.05216 V**

### A2 — Fixed Bias (RB=1 MΩ) *(ตัวอย่างกรณีโหมดใหม่)*
- IB = (VCC−VBE)/RB = (12−0.7)/1,000,000 = 11.3 µA
- IC = βIB = **1.13 mA**, IE = (β+1)IB = 1.1413 mA
- VE = 0 V, VB = VBE = 0.7 V
- VC = VCC−ICRC = 12−0.00113·2200 = 9.514 V, **VCE = 9.514 V**

### A3 — Emitter Bias (RB=1 MΩ, RE=1 kΩ)
- IB = (VCC−VBE)/(RB+(β+1)RE) = 11.3/(1,000,000+101,000) = 10.2634 µA
- **IC = 1.02634 mA**, IE = 1.03660 mA, VE = 1.03660 V, VB = 1.73660 V
- VC = 12−1.02634m·2200 = 9.74205 V, **VCE = 8.70545 V**

### A4 — Emitter Bias (RB=1 MΩ, RE=2 kΩ)
- **ทำนายก่อนรัน:** เมื่อเพิ่ม RE จาก 1 kΩ เป็น 2 kΩ (ค่าอื่นคงเดิม) ตัวหาร RB+(β+1)RE เพิ่มขึ้น → IB และ **IC จะลดลง** จาก A3
- IB = 11.3/(1,000,000+202,000) = 9.4010 µA
- **IC = 0.94010 mA** (ลดลง), IE = 0.94950 mA, VE = 1.89900 V, VB = 2.59900 V
- VC = 12−0.94010m·2200 = 9.93178 V, **VCE = 8.03278 V**

### A5 — Fixed Bias (RB=0 Ω)
- อินพุตผิด: RB ต้องมากกว่า 0 → ต้องแสดงข้อผิดพลาด, เว็บไม่ล่ม, ไม่แสดงผลคำนวณรอบนี้

## ตารางผล A1–A5

| กรณี | เลือกโหมดและกรอกค่า | คาดหมายก่อนรัน | เห็นจริง (จากแอป/ฟอร์ม) | วิธีตรวจ | สถานะ |
|---|---|---|---|---|---|
| A1 · โหมดเดิม | Divider · R1=100 kΩ, R2=22 kΩ, RE=1 kΩ (VCC=12, RC=2200, β=100, VBE=0.7) | IC 1.22986 mA · VCE 8.05216 V | IC 1.22986 mA · VCE 8.05216 V (โหมด Voltage Divider Bias) | Flask test_client / unit test | PASS |
| A2 · Fixed | Fixed · RB=1 MΩ (1000000 Ω) | IC 1.13000 mA · VCE 9.51400 V | IC 1.13 mA · VCE 9.514 V (VE 0 V) | Flask test_client / unit test | PASS |
| A3 · Emitter | Emitter · RB=1 MΩ, RE=1 kΩ | IC 1.02634 mA · VCE 8.70545 V | IC 1.02634 mA · VCE 8.70545 V | Flask test_client / unit test | PASS |
| A4 · เปลี่ยนค่าเดียว | Emitter · RB=1 MΩ, RE=2 kΩ (คงค่าอื่นเท่า A3) | IC ลดลงจาก A3 (RE มากขึ้น → IB,IC ลด), IC 0.94010 mA · VCE 8.03278 V | IC 0.94010 mA · VCE 8.03278 V (ลดลงจาก A3 ตามคาด) | Flask test_client / unit test | PASS |
| A5 · อินพุตผิด | Fixed · RB=0 Ω | แจ้งข้อผิดพลาดให้แก้ RB, เว็บไม่ล่ม, ไม่แสดงผลเดิม/ผลคำนวณรอบนี้ | แสดงข้อผิดพลาด "RB ต้องมากกว่า 0" ในหัวข้อข้อผิดพลาด (โหมด Fixed Bias), ไม่มีส่วน "ผลลัพธ์ DC Operating Point" | Flask test_client / unit test | PASS |

## หลักฐานการทดสอบอัตโนมัติ (รันจริง)
- `python -m unittest -v tests.test_dc_bias` — 6/6 OK (รวม A1–A5 และกรณี Divider เดิม)
- `python -m unittest -v tests.test_app` — 4/4 OK (GET, A1, A5 ไม่มีผลคำนวณค้าง, โหมดไม่รู้จัก)
- `python -m unittest -v tests.test_bjt_bias` — 4/4 OK, `python -m unittest -v test_electrical` — 2/2 OK

## หมายเหตุ
- ผลที่แสดงปัดด้วยรูปแบบ `%.6g` ในตารางผลเว็บ; ความต่างอยู่ในเกณฑ์ที่กำหนด (≤ 0.01 mA, ≤ 0.02 V)
- สามารถทดสอบซ้ำผ่านเบราว์เซอร์จริงได้ที่ `http://127.0.0.1:5000/` โดยเลือกโหมดและกรอกค่าตามตาราง
