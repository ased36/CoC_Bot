r"""Max levels and counts per Town Hall, from the game's own data (ClashKingInc/ClashKingAssets static_data, the repo the bot
already reads its names from). Writes assets/th_max.json (read by the bot: Telegram /th) and docs/TH-MAX.md (to read).
Run again after a game update:  .venv\Scripts\python.exe scripts\th_max.py"""
import json, datetime, urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/ClashKingInc/ClashKingAssets/main/assets/static_data/"
ROOT = Path(__file__).resolve().parent.parent

def load(name):
    with urllib.request.urlopen(BASE + name + ".json", timeout=30) as r:
        return json.load(r)["items"]

def max_level(levels, th):
    ok = [l["level"] for l in levels if (l.get("required_townhall") or 0) <= th]
    return max(ok) if ok else 0

buildings = [b for b in load("buildings") if b.get("village") == "home"]
town_hall = next(b for b in buildings if b["name"] == "Town Hall")
groups = {"buildings": buildings, "traps": [t for t in load("traps") if t.get("village") == "home"], "heroes": load("heroes"),
          "pets": load("pets"), "guardians": load("guardians")}
top_th = max(l["level"] for l in town_hall["levels"])

out = {"source": "ClashKingInc/ClashKingAssets static_data", "made": datetime.date.today().isoformat(), "th": {}}
counts = {}
for th in range(1, top_th + 1):
    for u in next(l for l in town_hall["levels"] if l["level"] == th).get("unlocks") or []:
        counts[u["name"]] = counts.get(u["name"], 0) + u["quantity"]
    entry = {}
    for group, items in groups.items():
        rows = {}
        for item in items:
            if item["name"] == "Town Hall" or not item.get("levels"): continue
            level = max_level(item["levels"], th)
            if not level: continue
            rows[item["name"]] = [counts.get(item["name"], 1), level] if group in ("buildings", "traps") else level
        entry[group] = rows
    out["th"][str(th)] = entry
(ROOT / "assets" / "th_max.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

# Readable copy: walls for every Town Hall, then TH12 and up side by side
lines = [f"# Town Hall max seviyeleri", "", f"Kaynak: oyun verisi ({out['source']}), {out['made']}. Yeniden üretmek: `scripts/th_max.py`. Adet = Belediye açtıkça gelenler (oyunun listesi); 6. usta kulübesi gibi başka yoldan gelenler sayılmaz.",
         "", "## Duvar", "", "| TH | Adet | En yüksek seviye |", "|---|---|---|"]
for th in range(1, top_th + 1):
    c, lv = out["th"][str(th)]["buildings"].get("Wall", [0, 0])
    lines.append(f"| {th} | {c} | {lv} |")
ths = [str(t) for t in range(12, top_th + 1)]
for group, title in (("buildings", "Binalar (adet × seviye)"), ("traps", "Tuzaklar (adet × seviye)"), ("heroes", "Kahramanlar"), ("pets", "Evcil hayvanlar"), ("guardians", "Muhafızlar")):
    names = sorted({n for t in ths for n in out["th"][t][group]})
    lines += ["", f"## {title}", "", "| | " + " | ".join(f"TH{t}" for t in ths) + " |", "|---" * (len(ths) + 1) + "|"]
    for n in names:
        cells = []
        for t in ths:
            v = out["th"][t][group].get(n)
            cells.append("" if v is None else f"{v[0]}×{v[1]}" if isinstance(v, list) else str(v))
        lines.append(f"| {n} | " + " | ".join(cells) + " |")
(ROOT / "docs" / "TH-MAX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("TH", top_th, "written")
