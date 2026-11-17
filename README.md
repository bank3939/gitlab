# ENG29 2121 — Lab 03: BJT DC Bias Web App

เว็บ Flask สำหรับคำนวณ **DC Operating Point** ของวงจรไบอัสทรานซิสเตอร์ BJT (NPN, Common Emitter) 3 โหมด: **Voltage Divider Bias**, **Fixed Bias**, **Emitter Bias (แหล่งจ่ายเดียว)**

## โครงสร้างโปรเจกต์
- `dc_bias.py` — ฟังก์ชันคำนวณทางวิศวกรรมแยกตามโหมด (`calculate_fixed_bias`, `calculate_emitter_bias`, `calculate_voltage_divider_bias`) และตัวเลือกโหมด `analyze(...)`
- `app.py` — Flask routes, รับ/ตรวจอินพุตตามโหมด, เลือกฟังก์ชันคำนวณ, ส่งผลให้เทมเพลต
- `templates/index.html` — ฟอร์มเลือกโหมด, แสดงช่องอินพุตตามโหมด, แสดงผล/ข้อผิดพลาด/คำเตือน
- `static/style.css` — สไตล์หน้าเว็บ
- `tests/test_dc_bias.py`, `tests/test_app.py` — เทสต์กรณี A1–A5 และการทำงานของเว็บ
- `docs/validation.md` — ค่าอ้างอิงอิสระและตารางผล A1–A5
- `bjt_bias.py`, `tests/test_bjt_bias.py`, `test_electrical.py` — โมดูล/เทสต์เดิมที่ยังคงอยู่

## วิธีรัน
ต้องมี Python 3 และ Flask

```bash
# ติดตั้ง dependency (ถ้าจำเป็น)
pip install flask

# รันเว็บแอป
python -m flask --app app run
# หรือ
python app.py
```

เปิดเบราว์เซอร์ที่ URL ที่ Flask แสดง (เช่น `http://127.0.0.1:5000/`)

## วิธีทดสอบ
```bash
python -m unittest -v test_electrical
python -m unittest -v tests.test_bjt_bias
python -m unittest -v tests.test_dc_bias
python -m unittest -v tests.test_app
```

## สมการและผลลัพธ์ (สรุป)
- อินพุตร่วม: `VCC, RC, β, VBE` | Fixed: `RB` | Emitter: `RB, RE` | Divider: `R1, R2, RE`
- Fixed: `IB=(VCC−VBE)/RB`, `VE=0`  
- Emitter: `IB=(VCC−VBE)/(RB+(β+1)RE)`  
- Divider: `VTH=VCC·R2/(R1+R2)`, `RTH=R1||R2`, `IB=(VTH−VBE)/(RTH+(β+1)RE)`
- ร่วม: `IC=βIB`, `IE=(β+1)IB`, `VE=IE·RE` (Fixed=0), `VB=VE+VBE`, `VC=VCC−IC·RC`, `VCE=VC−VE`
- หน่วยคำนวณ: Ω, A (ผลแสดง `IC` เป็น mA และแรงดันเป็น V). เตือนเมื่อ `IB ≤ 0` หรือ `VCE ≤ 0.2 V` (แบบจำลอง Forward Active อาจใช้ไม่ได้)

## หมายเหตุ
- งาน Lab 03: เพิ่ม 3 โหมด, เลือกฟังก์ชันตามโหมด, ตรวจอินพุตรายโหมด, แสดงผล/คำเตือน, คงผล Divider กรณีเดิม (A1) ได้
- ค่าอ้างอิงอิสระและตาราง A1–A5 ดูที่ `docs/validation.md`
