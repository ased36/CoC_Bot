import sys, json, time, copy
from pathlib import Path
try:
    import configs
except:
    import configs_build as configs

if getattr(sys, "frozen", False):
    DATA_DIR = Path.home() / ".CoC_Bot" / "data"
else:
    DATA_DIR = Path(__file__).parent.parent / "data"

# task name -> configs default (True = task enabled)
TASK_DEFAULTS = {
    "home_base": "UPGRADE_HOME_BASE",
    "heroes": "UPGRADE_HEROES",
    "home_lab": "UPGRADE_HOME_LAB",
    "pet_house": "UPGRADE_PETS",
    "builder_apprentice": "ASSIGN_BUILDER_APPRENTICE",
    "lab_assistant": "ASSIGN_LAB_ASSISTANT",
    "builder_base": "UPGRADE_BUILDER_BASE",
    "builder_lab": "UPGRADE_BUILDER_LAB",
    "home_attacks": "ATTACK_HOME_BASE",
    "builder_attacks": "ATTACK_BUILDER_BASE",
    "home_base_priority": "PRIORITY_HOME_BASE_UPGRADES",
    "home_lab_priority": "PRIORITY_HOME_LAB_UPGRADES",
    "pet_house_priority": "PRIORITY_PET_UPGRADES",
    "builder_base_priority": "PRIORITY_BUILDER_BASE_UPGRADES",
    "builder_lab_priority": "PRIORITY_BUILDER_LAB_UPGRADES",
}

EMPTY_STATS = {
    "since": 0,
    "rounds": 0,
    "upgrades_home": 0,
    "upgrades_home_lab": 0,
    "upgrades_pet": 0,
    "upgrades_builder": 0,
    "upgrades_builder_lab": 0,
    "walls": 0,
    "attacks_home": 0,
    "attacks_builder": 0,
    "errors": 0,
    "events": [],
}

def default_settings():
    return {
        "tasks": {k: bool(getattr(configs, v, False)) for k, v in TASK_DEFAULTS.items()},
        "general": {
            "check_interval": getattr(configs, "CHECK_INTERVAL", 5),
            "jitter_pct": 20,
            "hours_enabled": False,
            "hours_start": "08:00",
            "hours_end": "23:59",
            "close_game": True,
            # Play like a person (Emre 02.11, 2A): a break after a few attacks, a daily cap, a 24 hour grid (sleep).
            # Defaults are the advised values; every range is picked at random again each time
            "rest_enabled": True,
            "rest_after_min": 15, "rest_after_max": 25, # attacks before a break
            "rest_min": 20, "rest_max": 40, # break, minutes (the game is closed)
            "daily_min": 30, "daily_max": 45, # attacks a day, 0 = no cap; then wait for the next day
            "grid_enabled": True,
            "hours_grid": [not 2 <= h < 9 for h in range(24)], # hour h on = rounds may start in it (02-09 asleep)
        },
        "home": {
            "max_upgrades": getattr(configs, "MAX_UPGRADES_PER_CHECK", 10),
            "open_builders": getattr(configs, "OPEN_HOME_BUILDERS", 0),
            "town_hall": True,
            "excluded": [],
            "fallback": "cheapest", # when nothing on the priority list fits: cheapest / random
            "prefer_resource": "any", # any / gold / elixir
            "keep_gold": 0, # never start an upgrade that leaves less than this
            "keep_elixir": 0,
            "keep_dark": 0,
            "discount_first": True, # green tag rows before everything else
            "hero_priority": [], # panel Geliştirme -> Kahramanlar: [[name], ...] in order
            "heroes_first": False, # heroes before everything, discounts too
            "hero_builders": 0, # the last this many free builders go to heroes only
            "priority": copy.deepcopy(getattr(configs, "HOME_BASE_UPGRADE_PRIORITY", [])),
            "lab_priority": copy.deepcopy(getattr(configs, "HOME_LAB_UPGRADE_PRIORITY", [])),
            "pet_priority": copy.deepcopy(getattr(configs, "PET_HOUSE_UPGRADE_PRIORITY", [])),
        },
        "builder": {
            "open_builders": getattr(configs, "OPEN_BUILDER_BUILDERS", 0),
            "priority": copy.deepcopy(getattr(configs, "BUILDER_BASE_UPGRADE_PRIORITY", [])),
            "lab_priority": copy.deepcopy(getattr(configs, "BUILDER_LAB_UPGRADE_PRIORITY", [])),
        },
        "walls": {
            "enabled": False,
            "min_gold": 1_000_000,
            "min_elixir": 1_000_000,
            "max_per_round": 5,
            "levels": [], # walls at these levels go one level up; empty = any level
            "every_attacks": 3, # with attacks on: one wall pass, then this many attacks (the menu takes ~30 s)
            "start_gold": 0, # with attacks on: walls only once gold OR elixir reaches these (0 and 0 = use every_attacks)
            "start_elixir": 0,
            "total": 0, # walls in the village (Telegram wall count: the top level is not in the menu); 0 = unknown
        },
        "attack": {
            "min_gold": 400_000, # every non-zero minimum has to hold, 0 = no condition
            "min_elixir": 0,
            "min_dark": 0,
            "max_searches": 30, # then give up until the next round
            "lower_every": 15, # every this many searches the minimums drop...
            "lower_pct": 10, # ...by this % of the values above
            "end_after": 60, # end the battle this many seconds after everything is deployed (most loot comes early); 0 = play it out
        },
        # Panel Saldırı -> Dağıtım / Savaş sonu: these replace the same values in attacks/yayma.yaml
        "attack_style": {
            "style": "yayma", # attacks/<style>.yaml
            "count": 60, # super barbarians in the army
            "per_side_min": 13, "per_side_max": 15, # troops swept onto each of the four sides
            "red_line": True, # show the red area with one troop first, then drop by it
            "lead_first": 0, # % of attacks where the champion goes before the troops
            "bats": 11, # bat spells
            "loot_left_min": 50_000, "loot_left_max": 70_000, # leave once gold and elixir left are both under this; 0 = off
            "idle_seconds": 20, # end the battle when the loot has not moved for this long
        },
        "resources": {},
        "stats": dict(copy.deepcopy(EMPTY_STATS), since=time.time()),
    }

def merge(base, update):
    """Recursively merge update into base (dicts merge, everything else replaces)."""
    for k, v in update.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            merge(base[k], v)
        else:
            base[k] = v
    return base

def settings_path(id):
    return DATA_DIR / f"{id}.json"

# Profiles (Emre 02.11, 1A): every profile keeps its own copy of these sections. general (check interval, breaks,
# daily cap, hour grid), resources and stats belong to the account and are shared (2A). On disk:
# {"active_profile": name, "profiles": {name: {section: ...}}, "general": ..., "resources": ..., "stats": ...};
# in memory the active profile is flattened over the shared part, so the bot reads the same keys as before
PROFILE_SECTIONS = ("tasks", "home", "builder", "walls", "attack", "attack_style")
FIRST_PROFILE = "Ganimet" # a file from before profiles becomes this profile (4A)

def compose(shared, profile, name):
    """Effective settings: defaults, then the shared part, then the profile; "profile" names it."""
    settings = default_settings()
    merge(settings, copy.deepcopy({k: v for k, v in shared.items() if k not in PROFILE_SECTIONS}))
    merge(settings, copy.deepcopy(profile))
    settings["profile"] = name
    return settings

def load_all(id):
    """(effective settings, {name: profile sections}, active name)"""
    raw = {}
    path = settings_path(id)
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    profiles = raw.pop("profiles", None)
    active = raw.pop("active_profile", None)
    if not isinstance(profiles, dict) or not profiles:
        profiles = {FIRST_PROFILE: {k: raw[k] for k in PROFILE_SECTIONS if k in raw}}
    if active not in profiles: active = next(iter(profiles))
    settings = compose(raw, profiles[active], active)
    profiles[active] = {k: copy.deepcopy(settings[k]) for k in PROFILE_SECTIONS}
    return settings, profiles, active

def load(id):
    return load_all(id)[0]

def save(id, settings, profiles, active):
    """Writes the effective settings back: the profile sections into profiles[active], the rest shared."""
    profiles[active] = {k: copy.deepcopy(settings[k]) for k in PROFILE_SECTIONS}
    data = {k: v for k, v in settings.items() if k not in PROFILE_SECTIONS and k != "profile"}
    data["active_profile"] = active
    data["profiles"] = profiles
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = settings_path(id)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def exclusions(settings):
    return sorted(k for k, v in settings["tasks"].items() if not v)
