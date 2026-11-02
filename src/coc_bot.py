from utils import *
try:
    from configs import *
except:
    from configs_build import *
from upgrader import Upgrader
from attacker import Attacker

def in_working_hours(general):
    from datetime import datetime
    grid = general.get("hours_grid") or []
    if general.get("grid_enabled") and len(grid) == 24: return bool(grid[datetime.now().hour]) # 24 hour grid (2A)
    if not general.get("hours_enabled"): return True
    now = datetime.now().strftime("%H:%M")
    start, end = general.get("hours_start", "00:00"), general.get("hours_end", "23:59")
    if start <= end: return start <= now < end
    return now >= start or now < end # overnight window, e.g. 22:00-06:00

def next_check_delay(general):
    import random
    jitter = max(0, min(90, general.get("jitter_pct", 0))) / 100
    # The panel's interval (it used to be ignored: the configs value was always used); 0 = next round right away
    return 60 * general.get("check_interval", configs.CHECK_INTERVAL) * (1 + random.uniform(-jitter, jitter))

class CoC_Bot:
    def __init__(self):
        self.upgrader = Upgrader()
        self.attacker = Attacker()
        self.attacks_since_walls = None # None = walls first (a full storage wastes loot)
        self.was_running = False
        self.last_profile = None # panel profile (1A): logged when it changes

    # Today's attacks, the session (attacks since the last break) and the rest: in the disk cache, so closing and
    # opening the bot neither resets the daily cap nor ends a break early
    @property
    def day(self):
        return dict(Cache_Manager.get("play") or {"date": None, "attacks": 0, "gold": 0, "elixir": 0, "dark": 0})

    @day.setter
    def day(self, value):
        Cache_Manager["play"] = value

    @staticmethod
    def _short(v):
        """1.234.567 -> 1,23 M; 45.600 -> 46 k (Telegram messages)."""
        if v is None: return "?"
        sign = "-" if v < 0 else "+"
        v = abs(v)
        return sign + (f"{v / 1e6:.2f} M".replace(".", ",") if v >= 1e6 else f"{v / 1e3:.0f} k" if v >= 1e3 else str(v))

    def _day_rollover(self, general):
        """On a new day: yesterday's summary to Telegram, counters back to zero, today's random cap."""
        import random
        from datetime import date
        today = date.today().isoformat()
        d = self.day
        if d.get("date") == today: return
        if d.get("date") and d.get("attacks"):
            send_notification(f"📊 {d['date']} özeti: {d['attacks']} saldırı, {self._short(d['gold'])} altın, "
                              f"{self._short(d['elixir'])} iksir, {self._short(d['dark'])} kara iksir")
        lo, hi = sorted((int(general.get("daily_min", 0) or 0), int(general.get("daily_max", 0) or 0)))
        self.day = {"date": today, "attacks": 0, "gold": 0, "elixir": 0, "dark": 0, "cap": random.randint(lo, hi) if hi else 0,
                    "session": d.get("session", 0), "session_target": d.get("session_target"), "rest_until": d.get("rest_until", 0)}

    def _rest(self, general):
        """Play like a person (2A): (until, status, text) when no attack should start now, else None.
        A break after rest_after_min..max attacks (rest_min..max minutes), and today's cap (then the next day)."""
        import time, random
        from datetime import datetime, timedelta
        if not general.get("rest_enabled"): return None
        self._day_rollover(general)
        d = self.day
        if d.get("rest_until", 0) > time.time():
            return d["rest_until"], d.get("rest_kind", "rest"), None
        if d.get("cap") and d["attacks"] >= d["cap"]:
            tomorrow = datetime.combine(datetime.now().date() + timedelta(days=1), datetime.min.time())
            until = tomorrow.timestamp() + random.uniform(5, 30) * 60
            d.update(rest_until=until, rest_kind="daily")
            self.day = d
            return until, "daily", f"Günlük sınır doldu: bugün {d['attacks']} saldırı. Devam: yarın {datetime.fromtimestamp(until).strftime('%H:%M')}"
        lo, hi = sorted((int(general.get("rest_after_min", 15) or 1), int(general.get("rest_after_max", 25) or 1)))
        if not d.get("session_target"):
            d["session_target"] = random.randint(max(lo, 1), max(hi, 1))
            self.day = d
        if d.get("session", 0) >= d["session_target"]:
            lo_m, hi_m = sorted((int(general.get("rest_min", 20) or 0), int(general.get("rest_max", 40) or 0)))
            until = time.time() + random.uniform(lo_m, hi_m) * 60
            text = f"Mola: {d['session']} saldırıdan sonra {int((until - time.time()) / 60)} dk. Devam: {datetime.fromtimestamp(until).strftime('%H:%M')}"
            d.update(rest_until=until, rest_kind="rest", session=0, session_target=random.randint(max(lo, 1), max(hi, 1)))
            self.day = d
            return until, "rest", text
        return None

    @staticmethod
    def _close_for_rest():
        """A person closes the game for a break or the night (left open, the game asks "anyone there?" anyway)."""
        try:
            # BlueStacks crashed while waiting (02.11 04:09): nothing to close, and asking ADB would start it again for the night
            if Emulator_Manager.PROCESS_NAMES and not Emulator_Manager.check(): return
            if ADB_Manager.adbutils_device.shell("pidof com.supercell.clashofclans").strip():
                stop_coc(sleep=configs.SUSPEND_EMULATOR_ON_IDLE)
        except (KeyboardInterrupt, SystemExit): raise
        except Exception as e:
            logger.warning(f"Could not close the game for the rest: {e}")

    def _count_attack(self, gain):
        d = self.day
        d["attacks"] = d.get("attacks", 0) + 1
        d["session"] = d.get("session", 0) + 1
        for k, v in gain.items():
            if v is not None and v > 0: d[k] = d.get(k, 0) + v
        self.day = d
        return d

    def _attack_message(self, before, seconds):
        """After a home attack (back home): loot won (storage before / after) and the results screen as a picture.
        Silent on the phone: one comes every ~2 minutes."""
        after = Resource_Reader.read() or {}
        gain = {k: (after.get(k) - before.get(k)) if None not in (after.get(k), before.get(k)) else None for k in ("gold", "elixir", "dark")}
        d = self._count_attack(gain)
        store = lambda k: self._short(after.get(k)).lstrip("+")
        cap = f"/{d['cap']}" if d.get("cap") else ""
        profile = f" · {p}" if (p := (Settings_Handler.current or {}).get("profile")) else ""
        text = (f"⚔️ Saldırı{profile} (bugün {d['attacks']}{cap}.): {self._short(gain['gold'])} altın · {self._short(gain['elixir'])} iksir"
                f" · {self._short(gain['dark'])} kara\nDepo: {store('gold')} / {store('elixir')} / {store('dark')} · tur {int(seconds)} sn")
        send_notification(text, photo=self.attacker.last_result, silent=True)
        # Panel "Son saldırılar" table (Emre 02.11, design A)
        report("loot", **gain, searches=getattr(self.attacker, "last_searches", None), seconds=int(seconds))

    @staticmethod
    def _when(t):
        """An end time for Telegram: 14:20 today, yarın 09:05, 04.11 18:00 later."""
        from datetime import datetime, date, timedelta
        d = datetime.fromtimestamp(t)
        if d.date() == date.today(): return d.strftime("%H:%M")
        if d.date() == date.today() + timedelta(days=1): return "yarın " + d.strftime("%H:%M")
        return d.strftime("%d.%m %H:%M")

    @staticmethod
    def _th_text(arg=None):
        """Telegram /th (Emre 02.11): without a level the walls of every Town Hall and this village's walls; "/th 16" the
        max levels at that Town Hall. From assets/th_max.json, made from the game's data by scripts/th_max.py."""
        import json, html
        data = json.loads(Path(Asset_Manager.resource_path("assets/th_max.json")).read_text(encoding="utf-8"))
        ths = data["th"]
        if arg and arg.isdigit() and arg in ths:
            t = ths[arg]
            lines = [f"🏛 <b>TH{arg} en yüksek seviyeler</b> (adet × seviye)"]
            for group, title in (("buildings", "Binalar"), ("traps", "Tuzaklar"), ("heroes", "Kahramanlar"), ("pets", "Evcil"), ("guardians", "Muhafızlar")):
                rows = t.get(group) or {}
                if not rows: continue
                cell = lambda v: f"{v[0]}×{v[1]}" if isinstance(v, list) else str(v)
                lines += ["", f"<b>{title}</b>", ", ".join(f"{html.escape(n, quote=False)} {cell(v)}" for n, v in sorted(rows.items()))]
            lines.append(f"\n<i>Oyun verisi, {data['made']}</i>")
            return "\n".join(lines)
        lines = ["🧱 <b>Duvar: TH başına adet ve en yüksek seviye</b>"]
        lines += [f"TH{n}: {ths[n]['buildings']['Wall'][0]} duvar · Sv{ths[n]['buildings']['Wall'][1]}" for n in sorted(ths, key=int) if int(n) >= 9 and "Wall" in ths[n]["buildings"]]
        w = Cache_Manager.get("walls") or {}
        if w.get("levels"): lines += ["", "Köyünde (son okuma): " + " · ".join(f"Sv{k}: {v}" for k, v in sorted(w["levels"].items(), key=lambda kv: int(kv[0])))]
        lines.append("\n<i>Bir TH'nin bütün max seviyeleri: /th 16</i>")
        return "\n".join(lines)

    def _last_look(self):
        """Emre 02.11: Stop keeps one last look at the village (builders, laboratory, potions, storage) for /ozet while the
        bot waits. Only on the open village screen (the round has just ended there); menus are opened and closed, nothing
        is tapped inside them."""
        import time
        Cache_Manager["stopped_at"] = None
        try:
            if Emulator_Manager.PROCESS_NAMES and not Emulator_Manager.check(): return logger.info("Last look skipped: emulator closed")
            if not ADB_Manager.adbutils_device.shell("pidof com.supercell.clashofclans").strip(): return logger.info("Last look skipped: game closed")
            if not in_home_base(): return logger.info("Last look skipped: not on the home village")
            logger.info("Last look before stopping")
            TEMP_CACHE["location"] = "home_base"
            Resource_Reader.read()
            if time.time() - (Cache_Manager.get("status") or {}).get("t", 0) > 600: self.upgrader.read_status()
            Cache_Manager["stopped_at"] = time.time() # /ozet: "the rows below were read when stopping"
        except (KeyboardInterrupt, SystemExit): raise
        except Exception: logger.exception("CoC_Bot._last_look:")

    @staticmethod
    def _walls_lines():
        """Emre 02.11 (2A): "🧱 Duvar · bugün 14" and the levels from the start of the day to now, "Sv13: 200 → 186". The
        walls at the top level are not in the builders menu: they are the panel's total minus the rows read."""
        from datetime import date
        w = Cache_Manager.get("walls") or {}
        if not w.get("levels"): return []
        day = w.get("day") or {}
        today = day.get("date") == date.today().isoformat()
        start = (day.get("start") if today else None) or w["levels"]
        top = min(t for t in (w.get("top"), day.get("start_top") if today else None) if t) # lowest level the unlisted walls can be at
        total = int(Settings_Handler.get("walls", "total", 0) or 0)
        def groups(levels):
            g = {int(k): v for k, v in levels.items() if int(k) < top}
            return g, (total - sum(g.values()) if total else None)
        (a, a_top), (b, b_top) = groups(start), groups(w["levels"])
        change = lambda x, y: f"{x} → {y}" if x != y else str(y)
        parts = [f"Sv{k}: {change(a.get(k, 0), b.get(k, 0))}" for k in sorted(set(a) | set(b)) if a.get(k, 0) or b.get(k, 0)]
        parts.append(f"Sv{top}+: " + (change(a_top, b_top) if total else "?"))
        lines = [f"🧱 <b>Duvar</b> · bugün {day.get('count', 0) if today else 0}", " · ".join(parts)]
        if not total: lines.append("<i>   En üst seviye için toplam duvar sayısını panele girin (Köy → Duvar).</i>")
        return lines

    def _summary(self):
        """The Telegram /ozet answer (Emre 02.11: everything at a glance, with emojis since Telegram has no colors): profile,
        what the bot is doing, today's attacks and loot, storage, each builder and laboratory with its time left and end,
        the pet house. HTML (bold headings)."""
        import time, html
        from datetime import datetime, date
        now = time.time()
        esc = html.escape
        hm = lambda t: datetime.fromtimestamp(t).strftime("%H:%M")
        d = self.day if self.day.get("date") == date.today().isoformat() else {"attacks": 0, "gold": 0, "elixir": 0, "dark": 0}
        status = TEMP_CACHE.get("status")
        rest_until = d.get("rest_until", 0) or 0
        doing = {"now": "⚔️ Turda (geliştirme / saldırı)", "paused": "⏸ Duraklatıldı", "idle": "⏹ Durdu, Başlat bekleniyor",
                 "hours": "🌙 Çalışma saatleri dışında", "error": "⚠️ Son turda hata, 1 dk sonra yeniden",
                 "rest": f"☕ Molada, devam {hm(rest_until)}", "daily": f"📵 Günlük sınır doldu, devam {self._when(rest_until)}"}.get(status)
        if isinstance(status, (int, float)): doing = f"🟢 Çalışıyor, sonraki tur {hm(status)}"
        stopped_at = Cache_Manager.get("stopped_at")
        if status in ("idle", "paused") and stopped_at:
            doing += f" ({hm(stopped_at)}; aşağıdakiler durdurulurken okundu)"
        # A value the last read missed (02.11 16:20 elixir "?") is the last good one
        r = Resource_Reader.good_values()
        store = lambda k: self._short(r.get(k)).lstrip("+")
        profile = (Settings_Handler.current or {}).get("profile")
        cap = f"/{d['cap']}" if d.get("cap") else ""
        lines = [f"🏰 <b>{esc(profile or 'Köy')}</b> · {hm(now)}", doing or "❔ Durum bilinmiyor", "",
                 f"⚔️ <b>Bugün</b> · {d['attacks']}{cap} saldırı" + (f" · ☕ mola {d.get('session', 0)}/{d['session_target']}" if d.get("session_target") else ""),
                 f"🟡 {self._short(d['gold'])}   🟣 {self._short(d['elixir'])}   ⚫ {self._short(d['dark'])}"]
        if r:
            gems = f"{r['gems']:,}".replace(",", ".") if isinstance(r.get("gems"), int) else "?"
            lines += ["", "🏦 <b>Depo</b>", f"🟡 {store('gold')}   🟣 {store('elixir')}   ⚫ {store('dark')}   💎 {gems}"]
        if walls := self._walls_lines(): lines += [""] + walls
        st = Cache_Manager.get("status") or {}
        # 02.11 16:20 the 05:13 reading was shown as if it were now ("Royal Champion bitti" while it was upgrading again):
        # an old reading says so, and the builder count comes from the live counter on the village screen
        old = st.get("t") and now - st["t"] > 2 * 3600
        if old: lines += ["", f"⚠️ <b>Usta / lab listesi {self._when(st['t'])} okuması</b> ({int((now - st['t']) // 3600)} saat önce); bot bir sonraki turda okuyunca güncellenir"]
        fmt = self.upgrader.fmt_left
        def mmss(s): return f"{int(s) // 3600}h {int(s) % 3600 // 60}m" if s >= 3600 else f"{int(s) // 60}m {int(s) % 60}s"
        def section(kind, title, total, potion_name):
            rows = st.get(kind)
            if rows is None: return
            running = sorted((b for b in rows if b["end"] + b.get("prec", 0) > now), key=lambda b: b["end"])
            done = [b for b in rows if b["end"] + b.get("prec", 0) <= now]
            free = r.get("builders_free") if kind == "builders" else None
            busy_n = total - free if total and free is not None else len(running)
            busy = f" · {busy_n}/{total} dolu" if total else ""
            lines.extend(["", f"{title}{busy}"])
            # A running potion (Emre 02.11): its time left, its speed, and every end below counted with it
            potion = st.get(f"{kind}_potion") or {}
            p_left = potion.get("end", 0) - now
            if p_left > 0:
                speed = potion.get("speed", 10)
                lines.append(f"⚡ <b>{potion_name}</b> · {mmss(p_left)} kaldı · <b>{speed} kat hız</b> · {self._when(potion['end'])}'e kadar")
                lines.append(f"<i>   İksir sürerken 1 dk = {speed} dk iş: {speed} saatlik iş 1 saatte biter. Bitişler buna göre.</i>")
            for b in running:
                left = max(0, b["end"] - now)
                dot = "🟢" if left <= 3600 else "🟡" if left <= 6 * 3600 else "🟠" if left <= 86400 else "🔴"
                line = f"{dot} {esc(b['name'])} · {fmt(left)} · {self._when(b['end'] + b.get('prec', 0) / 2)}"
                if p_left > 0 and "left" in b:
                    # The work still to do now, as the menu would show it: potion speed since the reading, then normal
                    e, p0 = now - st["t"], potion["end"] - st["t"]
                    work = max(0, b["left"] - speed * min(e, p0) - max(0, e - p0))
                    line += f" ⚡ <i>(iksirsiz {fmt(work)})</i>"
                lines.append(line)
            lines.extend((f"❔ {esc(b['name'])} bitmiş olmalı (yeniden okunmadı)" if old else f"✅ {esc(b['name'])} bitti") for b in done)
            if total and busy_n < total: lines.append(f"🔨 {total - busy_n} boş")
        section("builders", "👷 <b>Ustalar</b>", r.get("builders_total"), "İnşaatçı iksiri")
        section("lab", "🔬 <b>Laboratuvar</b>", None, "Araştırma iksiri")
        if "pet_busy" in st: lines += ["", "🐾 <b>Evcil hayvan</b> · " + ("meşgul" if st["pet_busy"] else "boş")]
        if st.get("t"): lines += ["", f"<i>Usta / lab okuma {hm(st['t'])} · 🟢 ≤1 sa 🟡 ≤6 sa 🟠 ≤1 gün 🔴 daha uzun</i>"]
        return "\n".join(lines)

    def _status_events(self):
        """Emre 02.11 (1A): a message when a builder or the laboratory gets free (the end the menu allowed is past) and the
        summary at 09:00 and 21:00. Cheap (no game), called every loop."""
        import time, html
        from datetime import datetime, date
        now = time.time()
        st = Cache_Manager.get("status") or {}
        done = set(Cache_Manager.get("status_done") or [])
        new = []
        for kind, what in (("builders", "usta boşaldı"), ("lab", "laboratuvar boşaldı")):
            for b in st.get(kind) or []:
                key = f"{kind}|{b['name']}|{int(b['end'])}"
                if key not in done and b["end"] + b.get("prec", 0) <= now:
                    done.add(key)
                    new.append(f"✅ <b>{html.escape(b['name'])}</b> bitti, {what}")
        if new:
            Cache_Manager["status_done"] = sorted(done)[-60:]
            send_notification("\n".join(new), html=True)
        hour = datetime.now().hour
        if hour in (9, 21) and Cache_Manager.get("summary_slot") != (slot := f"{date.today()} {hour}"):
            Cache_Manager["summary_slot"] = slot
            send_notification(self._summary(), html=True, silent=True)

    def _telegram_commands(self):
        """Emre 02.11: /ozet in Telegram gets the summary at once. Long polling on its own thread; only the chat the bot
        already writes to is answered, messages sent while the bot was closed are skipped."""
        import time, re, unicodedata, requests
        if not TELEGRAM_BOT_TOKEN: return
        api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        offset = None
        try:
            requests.post(f"{api}/setMyCommands", json={"commands": [{"command": "ozet", "description": "Anlık özet"}, {"command": "koy", "description": "Köy: TH, max'a kalan, en geride"}, {"command": "tavsiye", "description": "Şimdi ne yapılmalı"}, {"command": "th", "description": "TH max seviyeleri (/th 16)"}]}, timeout=(5, 10))
            old = requests.get(f"{api}/getUpdates", params={"offset": -1, "timeout": 0}, timeout=(5, 10)).json().get("result", [])
            if old: offset = old[-1]["update_id"] + 1
        except (KeyboardInterrupt, SystemExit): raise
        except Exception: pass
        while True:
            try:
                res = requests.get(f"{api}/getUpdates", params={"offset": offset, "timeout": 50, "allowed_updates": '["message"]'}, timeout=(5, 65)).json()
                for u in res.get("result", []):
                    offset = u["update_id"] + 1
                    msg = u.get("message") or {}
                    if str(msg.get("chat", {}).get("id")) != str(Cache_Manager.get("telegram_chat_id")): continue
                    # "Özet", "özet." or an ö typed as o + two dots (phone keyboards) all count
                    text = unicodedata.normalize("NFC", msg.get("text") or "").replace("İ", "i").lower()
                    words = re.sub(r"[^\w/@ ]", " ", text).split()
                    cmd = words[0].split("@")[0] if words else ""
                    if cmd in ("/ozet", "/özet", "ozet", "özet"): send_notification(self._summary(), html=True)
                    elif cmd in ("/th", "th"): send_notification(self._th_text(words[1] if len(words) > 1 else None), html=True)
                    elif cmd in ("/koy", "/köy", "koy", "köy"):
                        import advice
                        send_notification(advice.koy_text(), html=True)
                    elif cmd in ("/tavsiye", "tavsiye"):
                        import advice
                        send_notification(advice.tavsiye_text(), html=True)
                    elif cmd in ("/start", "/help", "/yardim", "/yardım"): send_notification("Komutlar:\n/ozet — anlık özet\n/koy — köy: TH, max'a kalan, en geride\n/tavsiye — şimdi ne yapılmalı\n/th — duvar tablosu, /th 16 — TH16 max seviyeleri")
            except (KeyboardInterrupt, SystemExit): raise
            except Exception:
                time.sleep(30) # no network: try again later

    def scan(self, general):
        import time

        # Read the village without touching anything (on startup and on the panel's "read village" button)
        logger.info("Reading village")
        started, res = start_coc(detailed=True)
        if started:
            update_status("now")
            to_home_base(ref_cache=True)
            Resource_Reader.read()
            if general.get("close_game", True):
                stop_coc(sleep=configs.SUSPEND_EMULATOR_ON_IDLE)
            update_status(time.time())
        else:
            logger.warning("Could not read village: CoC did not start")
            update_status("error" if res == "error" else "idle")
        report("scan_done")

    def search_only(self, general):
        import time

        # Panel's "search only" button: read loot and press Next, never deploy anything
        logger.info("Search only: looking for a village without attacking")
        started, res = start_coc(detailed=True)
        if started:
            update_status("now")
            to_home_base(ref_cache=True)
            self.attacker.run_search_only()
            Resource_Reader.read()
            if general.get("close_game", True):
                stop_coc(sleep=configs.SUSPEND_EMULATOR_ON_IDLE)
            update_status(time.time())
        else:
            logger.warning("Could not search: CoC did not start")
            update_status("error" if res == "error" else "idle")
        report("search_done")

    def run(self):
        import time, threading
        from datetime import datetime

        threading.Thread(target=self._telegram_commands, daemon=True).start()
        waiting_logged = None
        while True:
            try:
                if not online():
                    time.sleep(1)
                    continue
                try: self._status_events()
                except (KeyboardInterrupt, SystemExit): raise
                except Exception: logger.exception("CoC_Bot._status_events:")

                mode = bot_mode()
                if mode in ("paused", "idle"):
                    if waiting_logged != mode:
                        logger.info("Paused, waiting" if mode == "paused" else "Waiting for Start")
                        update_status(mode)
                        if self.was_running:
                            self._last_look()
                            send_notification(("⏸ Bot duraklatıldı" if mode == "paused" else "⏹ Bot durduruldu (panelden)")
                                              + " · son okuma bitti, oyuna geçebilirsin; /ozet bunu gösterir")
                    self.was_running = False
                    waiting_logged = mode
                    time.sleep(5)
                    continue

                all_settings = Settings_Handler.load()
                general = all_settings["general"]
                if mode == "scan":
                    waiting_logged = None
                    self.scan(general)
                    continue
                if mode == "search":
                    waiting_logged = None
                    self.search_only(general)
                    continue

                if not in_working_hours(general):
                    if waiting_logged != "hours":
                        logger.info("Outside working hours, waiting")
                        update_status("hours")
                        self._close_for_rest()
                        if self.was_running: send_notification("🌙 Çalışma saatleri dışında, bot bekliyor", silent=True)
                    waiting_logged = "hours"
                    time.sleep(60)
                    continue

                # Play like a person (2A): a break every few attacks, a daily cap. The loop keeps looking at the panel
                # every 5 s, so Stop still works during a break
                rest = self._rest(general) if all_settings.get("tasks", {}).get("home_attacks") else None
                if rest:
                    until, kind, text = rest
                    if waiting_logged != kind:
                        logger.info(f"Resting until {datetime.fromtimestamp(until).strftime('%d.%m %H:%M')} ({kind})")
                        update_status(kind)
                        report("rest", next_check=until, text=text or "")
                        self._close_for_rest()
                        if text: send_notification(("☕ " if kind == "rest" else "📊 ") + text, silent=kind == "rest")
                    waiting_logged = kind
                    time.sleep(5)
                    continue
                waiting_logged = None

                if not self.was_running:
                    send_notification("▶️ Bot başladı")
                    self.was_running = True
                    Cache_Manager["stopped_at"] = None
                if (profile := all_settings.get("profile")) and profile != self.last_profile:
                    logger.info(f"Profile: {profile}")
                    if self.last_profile is not None: send_notification(f"🔀 Profil: {profile}", silent=True)
                    self.last_profile = profile
                round_start = time.time()
                # Emre 02.11 "the bot is slow": one line per round with how long each part took
                timing, mark = [], [round_start]
                def lap(name):
                    now = time.time()
                    timing.append(f"{name} {now - mark[0]:.0f}s")
                    mark[0] = now
                    report("step", done=name) # panel "Şu an" strip
                started, res = start_coc(detailed=True)
                if started:
                    lap("start")
                    update_status("now")
                    report("round_start")

                    Task_Handler.get_exclusions()
                    exclude_home_base = Task_Handler.excluded("home_base", use_cached=True)
                    exclude_home_lab = Task_Handler.excluded("home_lab", use_cached=True)
                    exclude_pets = Task_Handler.excluded("pet_house", use_cached=True)
                    # Walls, apprentice and lab assistant run in the same step, so it runs when any of them is on
                    skip_home_base_upgrades = exclude_home_base and exclude_home_lab and exclude_pets \
                        and Task_Handler.excluded("heroes", use_cached=True) \
                        and not Settings_Handler.get("walls", "enabled", False) \
                        and Task_Handler.excluded("builder_apprentice", use_cached=True) and Task_Handler.excluded("lab_assistant", use_cached=True)
                    exclude_home_attacks = Task_Handler.excluded("home_attacks", use_cached=True)

                    exclude_builder_base = Task_Handler.excluded("builder_base", use_cached=True)
                    exclude_builder_lab = Task_Handler.excluded("builder_lab", use_cached=True)
                    skip_builder_base_upgrades = exclude_builder_base and exclude_builder_lab
                    exclude_builder_attacks = Task_Handler.excluded("builder_attacks", use_cached=True)

                    # Check home base
                    to_home_base(ref_cache=True)
                    Resource_Reader.read()
                    report("scan_done")
                    lap("village")

                    # Stop pressed in the panel: finish the current step, skip the rest of the round
                    def stopped():
                        if bot_mode() == "run": return False
                        logger.info("Stopped from panel, skipping the rest of the round")
                        return True

                    if not skip_home_base_upgrades and not stopped():
                        logger.info("Upgrading home base")
                        # With attacks on, walls run once every N attacks (walls, N attacks, walls, ...), always before an attack
                        # or, when the panel sets a gold / elixir level, only once either one reaches it (attack until then)
                        walls_now = True
                        start_gold = Settings_Handler.get("walls", "start_gold", 0) or 0
                        start_elixir = Settings_Handler.get("walls", "start_elixir", 0) or 0
                        # The start levels hold with attacks off too (02.11 19:22: attacks off, 631 k gold, the wall menu
                        # was read every 25 s round for nothing)
                        if start_gold or start_elixir:
                            have = Resource_Reader.last
                            walls_now = bool(start_gold and (have.get("gold") or 0) >= start_gold) or bool(start_elixir and (have.get("elixir") or 0) >= start_elixir)
                            if not walls_now and Settings_Handler.get("walls", "enabled", False): logger.info("Walls wait: gold and elixir below the start levels")
                        if not exclude_home_attacks:
                            if not (start_gold or start_elixir):
                                every = max(1, int(Settings_Handler.get("walls", "every_attacks", 3) or 1))
                                walls_now = self.attacks_since_walls is None or self.attacks_since_walls >= every
                            if walls_now: self.attacks_since_walls = 0
                        self.upgrader.run_home_base(exclude_home_base, exclude_home_lab, exclude_pets, walls=walls_now)
                        lap("upgrades")
                    if not exclude_home_attacks and not stopped():
                        logger.info("Attacking home base")
                        report("attack", base="home")
                        self._day_rollover(general)
                        before, attack_start = dict(Resource_Reader.read() or Resource_Reader.last), time.time()
                        self.attacker.last_result = None
                        self.attacker.run_home_base(restart=not skip_home_base_upgrades or not skip_builder_base_upgrades)
                        self.attacks_since_walls = (self.attacks_since_walls or 0) + 1
                        if self.attacker.last_result is not None and in_home_base(): # an attack was played (not only searched)
                            self._attack_message(before, time.time() - attack_start)
                        lap("attack")

                    # Check builder base
                    builder_base_stopped = stopped()
                    went_builder = (not skip_builder_base_upgrades or not exclude_builder_attacks) and not builder_base_stopped
                    if went_builder:
                        to_builder_base(ref_cache=True)

                    if not skip_builder_base_upgrades and not builder_base_stopped:
                        logger.info("Upgrading builder base")
                        self.upgrader.collect_builder_attack_elixir()
                        self.upgrader.run_builder_base(exclude_builder_base, exclude_builder_lab)
                    if not exclude_builder_attacks and not builder_base_stopped and not stopped():
                        logger.info("Attacking builder base")
                        report("attack", base="builder")
                        self.attacker.run_builder_base()

                    to_home_base()
                    # The attack message has just read the storage (1-2 s): no second read right after it
                    if went_builder or time.time() - Resource_Reader.read_at > 15: Resource_Reader.read()
                    if general.get("close_game", True):
                        stop_coc(sleep=configs.SUSPEND_EMULATOR_ON_IDLE)
                    update_status(time.time())
                    lap("end")
                    logger.info("Round timing: " + ", ".join(timing))
                elif res == "error":
                    update_status("error")

                delay = next_check_delay(general)
                # Interval 0 = attack after attack; with no attack in the round it only re-read the menus every ~25 s
                if started and res != "error" and exclude_home_attacks and exclude_builder_attacks: delay = max(delay, 120)
                next_check = time.time() + delay
                if started:
                    logger.info(f"Round finished in {int(time.time() - round_start)}s, next check at {datetime.fromtimestamp(next_check).strftime('%H:%M')}")
                    report("round_end", duration=time.time() - round_start, next_check=next_check)
                time.sleep(delay)

            except (KeyboardInterrupt, SystemExit): raise
            except Exception as e:
                logger.exception("CoC_Bot.run:")
                send_notification(f"❌ Turda hata: {type(e).__name__}: {str(e)[:200]} — 1 dk sonra yeni tur", key="round_error", every=900)
                stop_coc()
                update_status("error")
                time.sleep(60) # the next round starts the emulator again if it closed (it used to wait the whole check interval)
