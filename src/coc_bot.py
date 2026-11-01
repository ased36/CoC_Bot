from utils import *
try:
    from configs import *
except:
    from configs_build import *
from upgrader import Upgrader
from attacker import Attacker

def in_working_hours(general):
    from datetime import datetime
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
        self.day = {"date": None, "attacks": 0, "gold": 0, "elixir": 0, "dark": 0} # today's attacks for Telegram
        self.was_running = False

    @staticmethod
    def _short(v):
        """1.234.567 -> 1,23 M; 45.600 -> 46 k (Telegram messages)."""
        if v is None: return "?"
        sign = "-" if v < 0 else "+"
        v = abs(v)
        return sign + (f"{v / 1e6:.2f} M".replace(".", ",") if v >= 1e6 else f"{v / 1e3:.0f} k" if v >= 1e3 else str(v))

    def _day_rollover(self):
        """At the first attack of a new day: yesterday's summary to Telegram, counters back to zero."""
        from datetime import date
        today = date.today().isoformat()
        d = self.day
        if d["date"] and d["date"] != today and d["attacks"]:
            send_notification(f"📊 {d['date']} özeti: {d['attacks']} saldırı, {self._short(d['gold'])} altın, "
                              f"{self._short(d['elixir'])} iksir, {self._short(d['dark'])} kara iksir")
        if d["date"] != today:
            self.day = {"date": today, "attacks": 0, "gold": 0, "elixir": 0, "dark": 0}

    def _attack_message(self, before, seconds):
        """After a home attack (back home): loot won (storage before / after) and the results screen as a picture.
        Silent on the phone: one comes every ~2 minutes."""
        after = Resource_Reader.read() or {}
        gain = {k: (after.get(k) - before.get(k)) if None not in (after.get(k), before.get(k)) else None for k in ("gold", "elixir", "dark")}
        self.day["attacks"] += 1
        for k, v in gain.items():
            if v is not None and v > 0: self.day[k] += v
        store = lambda k: self._short(after.get(k)).lstrip("+")
        text = (f"⚔️ Saldırı (bugün {self.day['attacks']}.): {self._short(gain['gold'])} altın · {self._short(gain['elixir'])} iksir"
                f" · {self._short(gain['dark'])} kara\nDepo: {store('gold')} / {store('elixir')} / {store('dark')} · tur {int(seconds)} sn")
        send_notification(text, photo=self.attacker.last_result, silent=True)

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
        import time
        from datetime import datetime

        waiting_logged = None
        while True:
            try:
                if not online():
                    time.sleep(1)
                    continue

                mode = bot_mode()
                if mode in ("paused", "idle"):
                    if waiting_logged != mode:
                        logger.info("Paused, waiting" if mode == "paused" else "Waiting for Start")
                        update_status(mode)
                        if self.was_running:
                            send_notification("⏸ Bot duraklatıldı" if mode == "paused" else "⏹ Bot durduruldu (panelden)")
                    self.was_running = False
                    waiting_logged = mode
                    time.sleep(5)
                    continue

                general = Settings_Handler.load()["general"]
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
                        logger.info(f"Outside working hours ({general['hours_start']}-{general['hours_end']}), waiting")
                        update_status("hours")
                    waiting_logged = "hours"
                    time.sleep(60)
                    continue
                waiting_logged = None

                if not self.was_running:
                    send_notification("▶️ Bot başladı")
                    self.was_running = True
                round_start = time.time()
                started, res = start_coc(detailed=True)
                if started:
                    update_status("now")
                    report("round_start")

                    Task_Handler.get_exclusions()
                    exclude_home_base = Task_Handler.excluded("home_base", use_cached=True)
                    exclude_home_lab = Task_Handler.excluded("home_lab", use_cached=True)
                    exclude_pets = Task_Handler.excluded("pet_house", use_cached=True)
                    # Walls, apprentice and lab assistant run in the same step, so it runs when any of them is on
                    skip_home_base_upgrades = exclude_home_base and exclude_home_lab and exclude_pets \
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
                        if not exclude_home_attacks:
                            start_gold = Settings_Handler.get("walls", "start_gold", 0) or 0
                            start_elixir = Settings_Handler.get("walls", "start_elixir", 0) or 0
                            if start_gold or start_elixir:
                                have = Resource_Reader.last
                                walls_now = bool(start_gold and (have.get("gold") or 0) >= start_gold) or bool(start_elixir and (have.get("elixir") or 0) >= start_elixir)
                                if not walls_now: logger.info("Walls wait: gold and elixir below the start levels")
                            else:
                                every = max(1, int(Settings_Handler.get("walls", "every_attacks", 3) or 1))
                                walls_now = self.attacks_since_walls is None or self.attacks_since_walls >= every
                            if walls_now: self.attacks_since_walls = 0
                        self.upgrader.run_home_base(exclude_home_base, exclude_home_lab, exclude_pets, walls=walls_now)
                    if not exclude_home_attacks and not stopped():
                        logger.info("Attacking home base")
                        report("attack", base="home")
                        self._day_rollover()
                        before, attack_start = dict(Resource_Reader.read() or Resource_Reader.last), time.time()
                        self.attacker.last_result = None
                        self.attacker.run_home_base(restart=not skip_home_base_upgrades or not skip_builder_base_upgrades)
                        self.attacks_since_walls = (self.attacks_since_walls or 0) + 1
                        if self.attacker.last_result is not None and in_home_base(): # an attack was played (not only searched)
                            self._attack_message(before, time.time() - attack_start)

                    # Check builder base
                    builder_base_stopped = stopped()
                    if (not skip_builder_base_upgrades or not exclude_builder_attacks) and not builder_base_stopped:
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
                    Resource_Reader.read()
                    if general.get("close_game", True):
                        stop_coc(sleep=configs.SUSPEND_EMULATOR_ON_IDLE)
                    update_status(time.time())
                elif res == "error":
                    update_status("error")

                delay = next_check_delay(general)
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
