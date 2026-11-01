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
        },
        "home": {
            "max_upgrades": getattr(configs, "MAX_UPGRADES_PER_CHECK", 10),
            "open_builders": getattr(configs, "OPEN_HOME_BUILDERS", 0),
            "town_hall": True,
            "excluded": [],
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

def load(id):
    settings = default_settings()
    path = settings_path(id)
    if path.exists():
        try:
            merge(settings, json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            pass
    return settings

def save(id, settings):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = settings_path(id)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def exclusions(settings):
    return sorted(k for k, v in settings["tasks"].items() if not v)
