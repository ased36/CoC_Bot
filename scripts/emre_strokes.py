"""Emre's troop drag strokes from his recorded attacks -> assets/emre_strokes.json (Emre 02.11, 1A: the bot sweeps the
way his hand did). Recordings: X:/CoC/kayit/<time>/olaylar.txt (getevent -lt) + saat.txt (host time <-> device uptime),
made with X:/CoC/araclar/saldiri_kaydi.py.

A stroke is kept when one finger stayed still at least 0.3 s (a drop: a finger that moves at once moves the view) and
then went around the village (path over 400 px, angle range over 120 degrees). Strokes less than 20 s apart are one
attack ("plan"). Each stroke is stored as seen from the screen point (0.48, 0.47): its start angle, the angle it went
since the start over time, and the hand's wobble (the radius minus its 0.8 s moving mean, as a part of the screen width).
The slow part of the radius is the map's shape and is not kept: the bot lays the stroke on each village's red line.

Usage: python scripts/emre_strokes.py X:/CoC/kayit/20261101_185832 X:/CoC/kayit/20261101_203309 X:/CoC/kayit/20261101_203803
"""
import json, re, sys
from pathlib import Path
import numpy as np

CX, CY = 0.48 * 1920, 0.47 * 1080


def touches(folder):
    """[{t0, pts [[t, x, y]], fingers}] from getevent protocol A (SYN_MT_REPORT; an empty report = finger up)."""
    folder = Path(folder)
    maps = [(float(s[1]), float(s[3])) for s in (l.split() for l in open(folder / "saat.txt")) if s[3] != "*"]
    rx = re.compile(r"\[\s*([\d.]+)\] /dev/input/event4: (\S+)\s+(\S+)\s+([0-9a-f]+)")
    strokes, cur, frame, pos, offset = [], None, [], {}, 0.0
    for line in open(folder / "olaylar.txt", errors="replace"):
        if line.startswith("### getevent"):
            host = float(line.split()[-1])
            m = min(maps, key=lambda m: abs(m[0] - host))
            offset = m[0] - m[1]
            continue
        mm = rx.search(line)
        if not mm: continue
        t, code, val = float(mm[1]) + offset, mm[3], int(mm[4], 16)
        if code == "ABS_MT_POSITION_X": pos["x"] = val / 32767
        elif code == "ABS_MT_POSITION_Y": pos["y"] = val / 32767
        elif code == "SYN_MT_REPORT":
            if "x" in pos and "y" in pos: frame.append((pos["x"], pos["y"]))
            pos = {}
        elif code == "SYN_REPORT":
            if frame:
                if cur is None: cur = {"t0": t, "pts": [], "fingers": 1}
                cur["fingers"] = max(cur["fingers"], len(frame))
                cur["pts"].append([t, frame[0][0], frame[0][1]])
            elif cur is not None:
                strokes.append(cur)
                cur = None
            frame = []
    return strokes


def stroke(s):
    p = np.array(s["pts"])
    t, x, y = p[:, 0] - p[0, 0], p[:, 1] * 1920, p[:, 2] * 1080
    moved = np.hypot(x - x[0], y - y[0])
    still = t[np.argmax(moved > 12)] if (moved > 12).any() else t[-1]
    a = np.degrees(np.unwrap(np.arctan2(y - CY, x - CX)))
    if s["fingers"] != 1 or len(p) < 10 or still < 0.3 or np.hypot(np.diff(x), np.diff(y)).sum() < 400 or np.ptp(a) < 120: return None
    # 20 points a second
    grid = np.arange(0, t[-1], 0.05)
    a, r = np.interp(grid, t, a), np.interp(grid, t, np.hypot(x - CX, y - CY))
    k = 16 # 0.8 s
    slow = np.convolve(np.pad(r, k // 2, mode="edge"), np.ones(k) / k, mode="same")[k // 2:-(k // 2)]
    wob = np.clip((r - slow[:len(r)]) / 1920, -0.02, 0.02)
    return {"still": round(float(still), 2), "a0": round(float(a[0]) % 360, 1), "dur": round(float(t[-1]), 2),
            "da": [round(float(v - a[0]), 1) for v in a], "wob": [round(float(v), 4) for v in wob]}


def main(folders):
    plans = []
    for folder in folders:
        last = None
        for s in sorted(touches(folder), key=lambda s: s["t0"]):
            st = stroke(s)
            if st is None: continue
            if last is None or s["t0"] - last[1] > 20:
                plans.append({"src": f"{Path(folder).name} {s['t0']:.0f}", "strokes": []})
                st["gap"] = 0.0
            else:
                st["gap"] = round(s["t0"] - last[1], 2)
            plans[-1]["strokes"].append(st)
            last = (s["t0"], s["t0"] + st["dur"])
    # round: one stroke all the way round (Emre's idea, 02.11 23:33); halves: two strokes (01.11). A plan that covers
    # less than 300 degrees in all leaves a side empty and is dropped
    def cover(st): return max(st["da"]) - min(st["da"])
    for p in plans: p["kind"] = "round" if len(p["strokes"]) == 1 and cover(p["strokes"][0]) >= 300 else "halves"
    plans = [p for p in plans if sum(cover(st) for st in p["strokes"]) >= 300]
    out = Path(__file__).resolve().parents[1] / "assets" / "emre_strokes.json"
    json.dump({"made": "kayıt " + ", ".join(Path(f).name for f in folders), "center": [0.48, 0.47], "plans": plans},
              open(out, "w", encoding="utf-8"), separators=(",", ":"))
    for p in plans:
        print(p["src"], p["kind"], " + ".join(f"{s['dur']}s {s['a0']:.0f}°{s['da'][-1]:+.0f}" for s in p["strokes"]))
    print(len(plans), "plans ->", out)


if __name__ == "__main__":
    main(sys.argv[1:])
