# ENG29 2121 — BJT DC Bias & CE Amplifier Simulator (Lab 03 + Lab 04 v1)

เว็บ Flask สำหรับ:
- **Lab 03:** คำนวณ DC Operating Point ของ BJT (NPN, Common Emitter) 3 โหมด — Voltage Divider, Fixed Bias, Emitter Bias (analytical, Python)
- **Lab 04 v1:** จำลอง CE Voltage Divider อ้างอิงด้วย **ngspice จริง** (`.op`, `.ac`, `.tran`) พร้อมกราฟและสถานะ engine

## โครงสร้างหลัก
- `dc_bias.py` — analytical DC bias 3 โหมด (Lab 3, เก็บเป็น reference)
- `spice_engine.py` — สร้าง netlist, เรียก `ngspice` ผ่าน `subprocess` (batch), parse ผล `.op/.ac/.tran`
- `app.py` — Flask routes, validation, dispatch analytical/SPICE
- `templates/index.html`, `static/style.css` — UI ฟอร์ม, ผลลัพธ์, กราฟ Chart.js
- `tests/` — unit tests (Lab 3 regression + spice engine validation/error path)
- `docs/validation.md` — ตารางตรวจ A1–A5, B1–B8

## ติดตั้งและรัน
### 1) Python dependencies
```bash
pip install -r requirements.txt
```

### 2) ngspice (external dependency สำหรับ Lab 04 จริง)
ติดตั้ง ngspice และให้เรียกได้จาก PATH (ตรวจด้วย `ngspice --version`)
- Windows: ดาวน์โหลดจาก https://ngspice.sourceforge.io/download.html (เช่น Spice64) แล้วเพิ่ม `...\Spice64\bin` เข้า PATH

หากไม่มี ngspice แอปยังรันได้ แต่ส่วน SPICE จะแสดงสถานะ “ไม่พร้อมใช้งาน” และไม่สร้างกราฟปลอม

### 3) รันเว็บ
```bash
python app.py
# หรือ
python -m flask --app app run
```
เปิด `http://127.0.0.1:5000/`

## ทดสอบ
```bash
python -m unittest discover -v -s tests
python -m unittest -v test_electrical
```

## หมายเหตุวิศวกรรม
- **แยกที่มาของผล:** Analytical (Python `dc_bias.py`) vs SPICE (`ngspice` real run) ไม่ปะปนกัน
- **Lab 3 คงไว้:** โหมด Fixed/Emitter/Voltage Divider และกรณี A1–A5 ยังทำงานเหมือนเดิม
- **SPICE v1 scope:** CE Voltage Divider อ้างอิง, ไม่มี Cbypass baseline, โมเดล BJT generic 2N3904-like เพื่อให้รันซ้ำได้ (ระบุใน UI/log)
- ห้าม commit `.env`, credentials, `.venv/`, ไฟล์ run ชั่วคราวขนาดใหญ่

## Evidence
ดู `docs/validation.md` และเพิ่ม screenshots/logs จริงหลังรัน ngspice ใน `docs/evidence/`.
