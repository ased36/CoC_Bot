"""Telegram /koy and /tavsiye (Emre 02.11, 1A 2A): what the village is and what to do next, from what the bot reads on
screen (no game API): the whole builders menu once a day (Upgrader.read_village), builders / lab / potions (read_status),
storage, walls, and the game's max levels per Town Hall (assets/th_max.json)."""
import json, time, html
from pathlib import Path
from utils import Asset_Manager, Cache_Manager, Resource_Reader, Settings_Handler

# Rushed village: offence and the economy first, as the equipment / upgrade guides Emre keeps say for every account
OFFENCE = ("Laboratory", "Army Camp", "Clan Castle", "Barracks", "Dark Barracks", "Spell Factory", "Dark Spell Factory",
           "Hero Hall", "Pet House", "Blacksmith", "Workshop", "Barbarian King", "Archer Queen", "Grand Warden",
           "Royal Champion", "Minion Prince", "Dragon Duke")
ECONOMY = ("Gold Storage", "Elixir Storage", "Dark Elixir Storage", "Gold Mine", "Elixir Collector", "Dark Elixir Drill", "Builder's Hut")


def th_data():
    return json.loads(Path(Asset_Manager.resource_path("assets/th_max.json")).read_text(encoding="utf-8"))["th"]


def max_at(ths, th, name):
    """Max level of name at Town Hall th, or None when the game data does not know the name."""
    t = ths.get(str(th)) or {}
    key = name.lower() # the bot's name list writes "Builder'S Hut"
    for group in ("buildings", "traps", "heroes", "pets", "guardians"):
        for n, v in (t.get(group) or {}).items():
            if n.lower() == key: return v[1] if isinstance(v, list) else v
    return None


def town_hall(village=None):
    """(Town Hall level, how it is known). The panel value first (Genel → Köy), else the "Town Hall" row of the menu
    (its badge is the next level), else the lowest Town Hall that allows every level the menu offers."""
    ths = th_data()
    set_th = int(Settings_Handler.get("general", "th_level", 0) or 0)
    if set_th: return set_th, "panel"
    rows = (village or Cache_Manager.get("village") or {}).get("rows") or []
    for r in rows:
        if r["name"].lower() == "town hall" and r.get("level"): return r["level"], "menü"
    need = 0
    for r in rows:
        if not r.get("level"): continue
        nxt = r["level"] + 1 # the menu only offers upgrades the Town Hall allows
        for th in sorted(ths, key=int):
            m = max_at(ths, th, r["name"])
            if m is not None and m >= nxt:
                need = max(need, int(th))
                break
    return (need or None), "tahmin"


def behind(village, th):
    """Rows below their max at th: (name, count, level, max, missing levels in all)."""
    ths = th_data()
    out = []
    for r in village.get("rows") or []:
        if r["name"].lower() == "wall" or not r.get("level"): continue
        m = max_at(ths, th, r["name"])
        if m is None or m <= r["level"]: continue
        out.append((r["name"], r["count"], r["level"], m, (m - r["level"]) * r["count"]))
    return sorted(out, key=lambda x: -x[4])


def _short(v):
    if v is None: return "?"
    a = abs(v)
    return f"{a / 1e6:.2f} M".replace(".", ",") if a >= 1e6 else f"{a / 1e3:.0f} k" if a >= 1e3 else str(a)


def _age(t):
    h = (time.time() - t) / 3600
    return f"{int(h * 60)} dk önce" if h < 1 else f"{int(h)} saat önce" if h < 48 else f"{int(h // 24)} gün önce"


def koy_text():
    """/koy: Town Hall, how far the village is from its Town Hall's max, the furthest behind, walls."""
    esc = lambda s: html.escape(str(s), quote=False)
    v = Cache_Manager.get("village") or {}
    th, how = town_hall(v)
    profile = (Settings_Handler.current or {}).get("profile") or "Köy"
    lines = [f"🏰 <b>{esc(profile)}</b> · TH{th or '?'} <i>({how})</i>"]
    if not v.get("rows"):
        lines.append("\nKöy henüz okunmadı: bot usta menüsünü günde bir baştan sona okur (ilk turda).")
        return "\n".join(lines)
    lines.append(f"<i>Usta menüsü okuması {_age(v['t'])}</i>")
    if th:
        b = behind(v, th)
        total = sum(x[4] for x in b)
        lines += ["", f"📈 <b>TH{th} max'ına kalan</b>: {total} seviye, {len(b)} bina / tuzak / kahraman"]
        lines += [f"• {esc(n)}{f' ×{c}' if c > 1 else ''}: {lv} → {m}" for n, c, lv, m, _ in b[:8]]
        if len(b) > 8: lines.append(f"<i>   +{len(b) - 8} satır daha</i>")
    disc = [r for r in v["rows"] if r.get("discount")]
    if disc: lines += ["", f"🏷 <b>İndirimli</b>: {len(disc)} iş (etkinlik)"]
    w = Cache_Manager.get("walls") or {}
    if w.get("levels") and th:
        wall_max = max_at(th_data(), th, "Wall")
        total = int(Settings_Handler.get("walls", "total", 0) or 0)
        listed = sum(w["levels"].values())
        lv = " · ".join(f"Sv{k} {n}" for k, n in sorted(w["levels"].items(), key=lambda kv: int(kv[0])))
        top = f" · Sv{w.get('top')}+ {total - listed}" if total > listed else ""
        lines += ["", f"🧱 <b>Duvar</b> (TH{th} max Sv{wall_max}): {lv}{top}"]
    lines.append("\n<i>Ekipman ve cevher: Demirci okunmuyor (ölçüm bekliyor). /tavsiye ne yapılacağını söyler.</i>")
    return "\n".join(lines)


def tavsiye_text():
    """/tavsiye: a few things to do now, each with why. Only from what the bot has read; nothing is guessed."""
    esc = lambda s: html.escape(str(s), quote=False)
    now = time.time()
    v = Cache_Manager.get("village") or {}
    st = Cache_Manager.get("status") or {}
    r = Resource_Reader.good_values()
    th, _ = town_hall(v)
    tips = []
    # 1) Idle builders and what they can start now
    free = r.get("builders_free")
    if free:
        can = [x for x in v.get("rows") or [] if x.get("cost") and x["name"] != "Wall" and (r.get(x["resource"]) or 0) >= x["cost"]]
        can.sort(key=lambda x: (x["name"].lower() not in {n.lower() for n in OFFENCE}, x["cost"]))
        what = ", ".join(f"{esc(x['name'])} ({_short(x['cost'])})" for x in can[:3])
        tips.append(f"👷 <b>{free} usta boşta.</b> " + (f"Parası yeten: {what}." if what else "Parası yeten iş görünmüyor; saldırıyla kaynak topla."))
    # 2) A potion running while builders / the lab sit idle wastes it
    for kind, name, idle in (("builders", "İnşaatçı iksiri", bool(free)), ("lab", "Araştırma iksiri", not any(b["end"] > now for b in st.get("lab") or []))):
        p = st.get(f"{kind}_potion") or {}
        if p.get("end", 0) > now and idle: tips.append(f"⚡ <b>{name} boşa akıyor</b>: {'usta' if kind == 'builders' else 'laboratuvar'} boş, iksir sürüyor.")
    # 3) The laboratory
    if st.get("t") and not any(b["end"] + b.get("prec", 0) > now for b in st.get("lab") or []):
        tips.append("🔬 <b>Laboratuvar boş.</b> Araştırma başlat (bot laboratuvarı geliştirme görevi açıksa kendisi seçer).")
    # 4) Full storage: walls
    w = (Settings_Handler.current or {}).get("walls") or {}
    for k, label in (("gold", "altın"), ("elixir", "iksir")):
        start = w.get(f"start_{k}") or 0
        if start and (r.get(k) or 0) >= start:
            tips.append(f"🧱 <b>{label.capitalize()} {_short(r.get(k))}</b>, duvar başlama değeri {_short(start)} geçildi: duvara harca"
                        + ("" if w.get("enabled") else " (duvar görevi kapalı, Geliştirme sekmesinden aç)") + ".")
            break
    # 5) An event discount: the expensive ones first
    disc = sorted((x for x in v.get("rows") or [] if x.get("discount") and x.get("cost")), key=lambda x: -x["cost"])
    if disc:
        tips.append("🏷 <b>İndirim sürüyor.</b> Pahalılar önce: " + ", ".join(f"{esc(x['name'])} ({_short(x['cost'])})" for x in disc[:3]) + ".")
    # 6) Rushed: offence buildings furthest behind first
    if th and v.get("rows"):
        off = [x for x in behind(v, th) if x[0].lower() in {n.lower() for n in OFFENCE}][:3]
        if off:
            tips.append(f"⚔️ <b>Önce saldırı tarafı</b> (TH{th} max'ına göre en geride): "
                        + ", ".join(f"{esc(n)} {lv}→{m}" for n, _, lv, m, _ in off) + ". Ordu güçlenince ganimet de artar.")
        eco = [x for x in behind(v, th) if x[0].lower() in {n.lower() for n in ECONOMY}][:2]
        if eco: tips.append("💰 <b>Ekonomi</b>: " + ", ".join(f"{esc(n)}{f' ×{c}' if c > 1 else ''} {lv}→{m}" for n, c, lv, m, _ in eco) + ".")
    if not tips: tips.append("✅ Şu an yapılacak belirgin bir şey yok.")
    old = [f"usta menüsü {_age(v['t'])}" for _ in [0] if v.get("t") and now - v["t"] > 36 * 3600]
    foot = f"\n<i>Kaynak: botun ekrandan okudukları{' · ' + ', '.join(old) if old else ''}. Ekipman tavsiyesi Demirci okununca gelir.</i>"
    return "💡 <b>Tavsiye</b>\n\n" + "\n\n".join(tips) + foot
