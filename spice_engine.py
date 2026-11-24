import csv
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

DEFAULT_MODEL = """* Generic NPN 2N3904-like model (for educational simulation)
.model Q2N3904 NPN(IS=6.734f BF=416.4 NF=1 VAF=74.03 IKF=0.06678 ISE=6.734f
+ NE=1.259 BR=0.7371 NR=1 VAR=0 RB=10 RC=1 XTB=1.5 CJE=4.493p VJE=0.75 MJE=0.2593
+ CJC=3.638p VJC=0.75 MJC=0.3085 TF=301.2p XTF=2 VTF=4 ITF=0.4 TR=239.5n)"""

COMMON_NGSPICE_PATHS = [
    r"C:\Spice64\bin\ngspice.exe",
    r"C:\Program Files\Spice64\bin\ngspice.exe",
    r"C:\Program Files\ngspice\bin\ngspice.exe",
    r"C:\Program Files (x86)\Spice64\bin\ngspice.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Spice64\bin\ngspice.exe"),
]


def find_ngspice():
    exe = shutil.which("ngspice") or shutil.which("ngspice.exe")
    if exe:
        return exe
    for p in COMMON_NGSPICE_PATHS:
        if p and Path(p).exists():
            return p
    return None


def get_ngspice_version():
    exe = find_ngspice()
    if not exe:
        return None, "ngspice not found in PATH/common locations"
    try:
        cp = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=10)
        out = (cp.stdout or "") + "\n" + (cp.stderr or "")
        for line in out.splitlines():
            if "ngspice" in line.lower():
                return line.strip(), None
        return out.strip().splitlines()[0] if out.strip() else "ngspice (version unknown)", None
    except Exception as e:
        return None, str(e)


def _f(name, value, positive=False, allow_zero=False):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise ValueError(f"{name} ต้องเป็นตัวเลขจำกัด")
    v = float(value)
    if positive and v <= 0:
        raise ValueError(f"{name} ต้องมากกว่า 0")
    if not positive and not allow_zero and v < 0:
        raise ValueError(f"{name} ต้องไม่เป็นค่าลบ")
    return v


def validate_params(p):
    params = {
        "VCC": _f("VCC", p.get("VCC", 12), positive=True),
        "R1": _f("R1", p.get("R1", 100000), positive=True),
        "R2": _f("R2", p.get("R2", 22000), positive=True),
        "RC": _f("RC", p.get("RC", 2200), positive=True),
        "RE": _f("RE", p.get("RE", 1000), positive=True),
        "RL": _f("RL", p.get("RL", 10000), positive=True),
        "Cin": _f("Cin", p.get("Cin", 10e-6), positive=True),
        "Cout": _f("Cout", p.get("Cout", 10e-6), positive=True),
        "amp_mV": _f("Amplitude (mV)", p.get("amp_mV", 10), positive=True),
        "freq_hz": _f("Frequency (Hz)", p.get("freq_hz", 1000), positive=True),
    }
    # keep simulation reasonable
    if params["freq_hz"] > 1e7:
        raise ValueError("Frequency (Hz) สูงเกินขอบเขตที่รองรับ")
    if params["amp_mV"] > 5000:
        raise ValueError("Amplitude (mV) สูงเกินขอบเขตที่รองรับ")
    return params


def build_netlist(params, analysis, workdir):
    p = validate_params(params)
    amp_v = p["amp_mV"] / 1000.0
    freq = p["freq_hz"]
    # node names: vin, b, c, e, vout
    net = [
        "* CE Voltage Divider Amplifier - ENG29 2121 Lab 04",
        DEFAULT_MODEL,
        f"VCC vcc 0 DC {p['VCC']}",
        f"Vin vin 0 DC 0 AC 1 SIN(0 {amp_v} {freq})",
        f"Cin vin b {p['Cin']}",
        f"R1 vcc b {p['R1']}",
        f"R2 b 0 {p['R2']}",
        f"RC vcc c {p['RC']}",
        f"RE e 0 {p['RE']}",
        f"Q1 c b e Q2N3904",
        f"Cout c vout {p['Cout']}",
        f"RL vout 0 {p['RL']}",
    ]
    if analysis == "op":
        # write op to file
        out_file = (Path(workdir) / "op.txt").as_posix()
        net += [
            ".control",
            "set noaskquit",
            "op",
            f"print v(b) v(e) v(c) v(c,e) i(VCC) > {out_file}",
            "quit",
            ".endc",
            ".end",
        ]
    elif analysis == "ac":
        out_file = (Path(workdir) / "ac.csv").as_posix()
        fstart = max(1, freq / 100.0)
        fstop = max(freq * 100.0, 1e6)
        net += [
            ".control",
            "set noaskquit",
            f"ac dec 40 {fstart} {fstop}",
            "let gain_db = db(v(vout)/v(vin))",
            "let phase = 180/pi*ph(v(vout)/v(vin))",
            f"wrdata {out_file} frequency gain_db phase",
            "quit",
            ".endc",
            ".end",
        ]
    elif analysis == "tran":
        out_file = (Path(workdir) / "tran.csv").as_posix()
        period = 1.0 / freq
        tstop = period * 5.0
        tstep = period / 200.0
        net += [
            ".control",
            "set noaskquit",
            f"tran {tstep} {tstop} 0 {tstep}",
            f"wrdata {out_file} time v(vin) v(vout)",
            "quit",
            ".endc",
            ".end",
        ]
    else:
        raise ValueError("Unknown analysis")
    return "\n".join(net) + "\n", p


def _run_ngspice(netlist_text, workdir, timeout=30):
    exe = find_ngspice()
    if not exe:
        return {
            "ok": False,
            "error": "ไม่พบ ngspice ในระบบ (ติดตั้ง ngspice และให้อยู่ใน PATH หรือตำแหน่งมาตรฐาน)",
            "engine": None,
            "stdout": "",
            "stderr": "",
            "log": "",
        }
    version, ver_err = get_ngspice_version()
    net_path = Path(workdir) / "circuit.cir"
    log_path = Path(workdir) / "run.log"
    net_path.write_text(netlist_text, encoding="utf-8")
    cmd = [exe, "-b", "-o", str(log_path), str(net_path)]
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=workdir)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"ngspice timeout หลัง {timeout}s", "engine": version, "stdout": "", "stderr": "", "log": ""}
    except Exception as e:
        return {"ok": False, "error": f"เรียก ngspice ไม่สำเร็จ: {e}", "engine": version, "stdout": "", "stderr": "", "log": ""}
    log = ""
    if log_path.exists():
        try:
            log = log_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            log = ""
    stdout = cp.stdout or ""
    stderr = cp.stderr or ""
    combined = "\n".join([stdout, stderr, log]).lower()
    if cp.returncode != 0:
        return {"ok": False, "error": f"ngspice exited with code {cp.returncode}", "engine": version, "stdout": stdout, "stderr": stderr, "log": log}
    if "fatal" in combined or "error" in combined and "no. of errors" not in combined:
        # keep simple: detect obvious fatal; ngspice sometimes prints warnings
        if "fatal error" in combined or "run simulation(s) aborted" in combined:
            return {"ok": False, "error": "ngspice รายงานข้อผิดพลาดระหว่างรัน (ดู log)", "engine": version, "stdout": stdout, "stderr": stderr, "log": log}
    return {"ok": True, "error": None, "engine": version, "stdout": stdout, "stderr": stderr, "log": log}


def _parse_wrdata(path):
    rows = []
    p = Path(path)
    if not p.exists():
        return rows
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        # wrdata format: index value index value ... or sometimes index value value depending
        nums = []
        for x in parts:
            try:
                nums.append(float(x))
            except Exception:
                pass
        if nums:
            rows.append(nums)
    return rows


def run_op(params):
    with tempfile.TemporaryDirectory(prefix="ngspice_op_") as wd:
        net, p = build_netlist(params, "op", wd)
        run = _run_ngspice(net, wd)
        result = {"ok": False, "analysis": "op", "params": p, "engine": run.get("engine"), "model": "Q2N3904", "log": run.get("log", ""), "error": run.get("error")}
        if not run["ok"]:
            return result
        out_path = Path(wd) / "op.txt"
        text = out_path.read_text(encoding="utf-8", errors="replace") if out_path.exists() else ""
        # parse key=value style from print output
        values = {}
        import re
        for m in re.finditer(r"([A-Za-z\(\),_]+)\s*=\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)", text):
            values[m.group(1).strip().lower()] = float(m.group(2))
        # ngspice naming can vary; try common forms
        def pick(*keys):
            for k in keys:
                if k.lower() in values:
                    return values[k.lower()]
            # partial match
            for vk, vv in values.items():
                for k in keys:
                    if k.lower() in vk:
                        return vv
            return None
        vb = pick("v(b)")
        ve = pick("v(e)")
        vc = pick("v(c)")
        vce = pick("v(c,e)", "v(c)-v(e)")
        icc = pick("i(vcc)")
        ic_ma = None
        if icc is not None:
            # current through VCC source is usually negative into source
            ic_ma = abs(icc) * 1000.0
        # fallback for vce
        if vce is None and vc is not None and ve is not None:
            vce = vc - ve
        result.update({
            "ok": True,
            "error": None,
            "vb_v": vb, "ve_v": ve, "vc_v": vc, "vce_v": vce,
            "ic_ma": ic_ma,
            "raw_op_text": text,
            "parsed_values": values,
            "provenance": "ngspice .op (real simulation)",
        })
        if any(v is None for v in [vb, ve, vc, vce]):
            result["ok"] = False
            result["error"] = "Parse ผล .op ไม่ครบ (ตรวจ log/netlist)"
        return result


def run_ac(params):
    with tempfile.TemporaryDirectory(prefix="ngspice_ac_") as wd:
        net, p = build_netlist(params, "ac", wd)
        run = _run_ngspice(net, wd, timeout=45)
        result = {"ok": False, "analysis": "ac", "params": p, "engine": run.get("engine"), "model": "Q2N3904", "log": run.get("log", ""), "error": run.get("error")}
        if not run["ok"]:
            return result
        # wrdata can create file or file with suffix in some versions; search
        files = list(Path(wd).glob("ac.csv*"))
        rows = []
        for f in files:
            rows = _parse_wrdata(f)
            if rows:
                break
        freq, gain_db, phase = [], [], []
        for r in rows:
            # expected patterns: [idx,f,idx,g,idx,p] or [f,g,p] or [idx,f,g,p]
            vals = r
            # wrdata commonly outputs: freq gain_db freq phase? Or index freq index gain_db index phase
            # We'll handle common case: 6 values => f,g,f,p? Actually wrdata vec1 vec2 vec3 -> n1 v1 n2 v2 n3 v3
            if len(vals) >= 6:
                f = vals[1]; g = vals[3]; ph = vals[5]
            elif len(vals) >= 3:
                f, g, ph = vals[0], vals[1], vals[2]
            else:
                continue
            if math.isfinite(f) and math.isfinite(g) and math.isfinite(ph) and f > 0:
                freq.append(f); gain_db.append(g); phase.append(ph)
        # de-duplicate by frequency
        if freq:
            merged = {}
            for f, g, ph in zip(freq, gain_db, phase):
                merged[f] = (g, ph)
            freq = sorted(merged.keys())
            gain_db = [merged[f][0] for f in freq]
            phase = [merged[f][1] for f in freq]
        result.update({
            "ok": len(freq) > 0,
            "error": None if len(freq) > 0 else "Parse ผล .ac ไม่สำเร็จ (ตรวจ log/wrdata)",
            "frequency_hz": freq,
            "gain_db": gain_db,
            "phase_deg": phase,
            "provenance": "ngspice .ac (real simulation)",
        })
        return result


def run_tran(params):
    with tempfile.TemporaryDirectory(prefix="ngspice_tran_") as wd:
        net, p = build_netlist(params, "tran", wd)
        run = _run_ngspice(net, wd, timeout=45)
        result = {"ok": False, "analysis": "tran", "params": p, "engine": run.get("engine"), "model": "Q2N3904", "log": run.get("log", ""), "error": run.get("error")}
        if not run["ok"]:
            return result
        files = list(Path(wd).glob("tran.csv*"))
        rows = []
        for f in files:
            rows = _parse_wrdata(f)
            if rows:
                break
        t, vin, vout = [], [], []
        for r in rows:
            vals = r
            if len(vals) >= 6:  # idx t idx vin idx vout
                tt, vi, vo = vals[1], vals[3], vals[5]
            elif len(vals) >= 3:
                tt, vi, vo = vals[0], vals[1], vals[2]
            else:
                continue
            if all(math.isfinite(x) for x in [tt, vi, vo]):
                t.append(tt); vin.append(vi); vout.append(vo)
        if t:
            merged = {}
            for tt, vi, vo in zip(t, vin, vout):
                merged[tt] = (vi, vo)
            t = sorted(merged.keys())
            vin = [merged[x][0] for x in t]
            vout = [merged[x][1] for x in t]
        result.update({
            "ok": len(t) > 0,
            "error": None if len(t) > 0 else "Parse ผล .tran ไม่สำเร็จ (ตรวจ log/wrdata)",
            "time_s": t,
            "vin_v": vin,
            "vout_v": vout,
            "provenance": "ngspice .tran (real simulation)",
        })
        return result


def run_simulation(analysis, params):
    analysis = (analysis or "").lower().strip()
    if analysis == "op":
        return run_op(params)
    if analysis == "ac":
        return run_ac(params)
    if analysis == "tran":
        return run_tran(params)
    return {"ok": False, "error": "Unknown analysis mode", "analysis": analysis}
