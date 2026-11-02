import sys
from pathlib import Path

if hasattr(sys, "_MEIPASS"):
    path = Path(sys._MEIPASS) / "gui_server"
else:
    path = Path(__file__).parent.resolve()
    sys.path.append(str(path.parent))

sys.path.append(str(path))

import os
import json
import time
import threading
from flask import Flask, render_template, jsonify, abort, request, send_from_directory
try:
    from configs import *
except:
    from configs_build import *
import settings as settings_store
from log_translate import parse_lines, translate_message
import icons

app = Flask(__name__)
bot_pipe = None
settings_lock = threading.Lock()

if getattr(sys, "frozen", False):
    LOG_DIR = Path.home() / ".CoC_Bot" / "debug"
else:
    LOG_DIR = Path("debug")
VOCAB_PATH = settings_store.DATA_DIR / "vocab.json"

UPGRADE_KINDS = {
    "home": ("upgrades_home", "Ana köy"),
    "home_lab": ("upgrades_home_lab", "Laboratuvar"),
    "pet": ("upgrades_pet", "Evcil hayvan"),
    "builder": ("upgrades_builder", "Usta üssü"),
    "builder_lab": ("upgrades_builder_lab", "Usta laboratuvarı"),
}

class Instance:
    def __init__(self, id=None):
        self.id = id if id is not None else ""
        self.run_status = ""
        self.end_time = 0
        self.next_check = 0
        self.active = True # False: the bot process idles until the Start button (only reads the village when asked)
        self.scan_requested = False
        self.search_requested = False
        self.settings, self.profiles, self.profile = settings_store.load_all(self.id)
        self.save()

    @property
    def exclusions(self):
        return settings_store.exclusions(self.settings)

    def save(self):
        settings_store.save(self.id, self.settings, self.profiles, self.profile)

    def switch_profile(self, name):
        # The bot reads the settings at the start of every round: the next round plays with this profile
        self.save()
        self.settings = settings_store.compose(self.settings, self.profiles[name], name)
        self.profile = name
        self.save()

    @property
    def mode(self):
        # run: full rounds · scan: read the village once, touch nothing · search: search only, no attack · paused / idle: wait
        if self.end_time > time.time(): return "paused"
        if self.active: return "run"
        if self.scan_requested: return "scan"
        if self.search_requested: return "search"
        return "idle"

    def add_event(self, text):
        events = self.settings["stats"]["events"]
        now = time.time()
        if events and events[-1]["text"] == text:
            events[-1]["count"] = events[-1].get("count", 1) + 1
            events[-1]["t"] = now
        else:
            events.append({"t": now, "text": text})
        del events[:-50]

instances = {}

def get_instance(id):
    instance = instances.get(id)
    if not instance: abort(404)
    return instance

@app.route("/", methods=["GET"])
def home():
    return render_template(
        "home.html",
        ids=sorted(list(instances.keys())),
    )

@app.route("/instances/<id>", methods=["GET"])
def handle_instance(id):
    get_instance(id)
    return render_template("instance.html", id=id)

@app.route("/instance_action", methods=["POST"])
def handle_instance_start_stop():
    data = request.json
    action = data.get("action", "")
    id = data.get("id", "")
    if action == "start":
        if id not in INSTANCE_IDS:
            return jsonify(0)
        if id not in instances:
            # new instance from the home page: start its bot process, idle until Start
            instances[id] = Instance(id)
            instances[id].active = False
            instances[id].scan_requested = True
            bot_pipe.send({"action": "start", "id": id})
            return jsonify(1)
        instance = instances[id]
        instance.active = True
        instance.next_check = 0
        return jsonify(1)
    elif action == "stop":
        instance = instances.get(id)
        if instance:
            instance.active = False
            instance.next_check = 0
        return jsonify(1)
    return jsonify(0)

@app.route("/current_time", methods=["GET"])
def handle_current_time():
    return {"current_time": time.time()}

@app.route("/instances/<id>/end_time", methods=["GET", "POST"])
def handle_end_time(id):
    instance = get_instance(id)
    if request.method == "POST":
        data = request.json.get("time", 0)
        instance.end_time = int(data) * 60 + time.time()
    return {"end_time": instance.end_time}

@app.route("/instances/<id>/running", methods=["GET"])
def handle_running(id):
    instance = get_instance(id)
    return {"running": instance.mode in ("run", "scan", "search")}

@app.route("/instances/<id>/mode", methods=["GET"])
def handle_mode(id):
    return {"mode": get_instance(id).mode}

@app.route("/instances/<id>/scan", methods=["POST"])
def handle_scan(id):
    instance = get_instance(id)
    instance.scan_requested = True
    return {"mode": instance.mode}

@app.route("/instances/<id>/search", methods=["POST"])
def handle_search(id):
    # Only while stopped; a running bot searches as part of its attack
    instance = get_instance(id)
    if not instance.active: instance.search_requested = True
    return {"mode": instance.mode}

@app.route("/instances/<id>/status", methods=["GET", "POST"])
def handle_status(id):
    instance = get_instance(id)
    if request.method == "POST":
        data = request.json
        instance.run_status = data.get("status", "")
    return {"status": instance.run_status}

@app.route("/instances/<id>/state", methods=["GET"])
def handle_state(id):
    # Everything the bottom bar needs in one request
    instance = get_instance(id)
    return {
        "current_time": time.time(),
        "active": instance.active,
        "mode": instance.mode,
        "scan_requested": instance.scan_requested,
        "search_requested": instance.search_requested,
        "status": instance.run_status,
        "end_time": instance.end_time,
        "next_check": instance.next_check,
        "resources": instance.settings.get("resources", {}),
    }

@app.route("/instances/<id>/exclude", methods=["GET", "POST"])
def handle_exclude(id):
    instance = get_instance(id)
    if request.method == "POST":
        data = request.json
        action = data.get("action", "")
        item = data.get("item", "")
        if item in instance.settings["tasks"]:
            with settings_lock:
                if action == "add":
                    instance.settings["tasks"][item] = False
                elif action == "remove":
                    instance.settings["tasks"][item] = True
                instance.save()
    return {"exclusions": instance.exclusions}

@app.route("/instances/<id>/settings", methods=["GET", "POST"])
def handle_settings(id):
    instance = get_instance(id)
    if request.method == "POST":
        update = request.json or {}
        update.pop("stats", None)
        update.pop("resources", None)
        update.pop("profile", None) # changed only through /profiles
        with settings_lock:
            settings_store.merge(instance.settings, update)
            instance.save()
    return instance.settings

def attack_styles():
    """attacks/*.yaml the scripted attack can play (step styles and the drag format; super-barbar.yaml is the old one)."""
    import yaml
    folder = (Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else path.parent.parent) / "attacks"
    names = []
    for f in sorted(folder.glob("*.yaml")):
        try:
            style = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            if style.get("steps") or style.get("troops", {}).get("mode") == "drag": names.append(f.stem)
        except Exception:
            pass
    return names

@app.route("/instances/<id>/profiles", methods=["GET", "POST"])
def handle_profiles(id):
    # Panel top bar: pick, new (a copy of the active one), rename, delete (not the active one, not the last one)
    instance = get_instance(id)
    if request.method == "POST":
        data = request.json or {}
        action = data.get("action", "")
        name = str(data.get("name", "")).strip()
        new_name = " ".join(str(data.get("new_name", "")).split())[:24]
        with settings_lock:
            profiles = instance.profiles
            if action in ("new", "rename"):
                if not new_name: return {"error": "Ad boş olamaz"}, 400
                if new_name in profiles: return {"error": f"\"{new_name}\" adında profil var"}, 400
            if action == "switch" and name in profiles:
                instance.switch_profile(name)
            elif action == "new":
                instance.save()
                profiles[new_name] = json.loads(json.dumps(profiles[instance.profile]))
                instance.switch_profile(new_name)
            elif action == "rename" and name in profiles:
                instance.profiles = {new_name if k == name else k: v for k, v in profiles.items()}
                if instance.profile == name:
                    instance.profile = instance.settings["profile"] = new_name
                instance.save()
            elif action == "delete" and name in profiles:
                if name == instance.profile: return {"error": "Seçili profil silinemez, önce başka profile geç"}, 400
                if len(profiles) == 1: return {"error": "Son profil silinemez"}, 400
                del profiles[name]
                instance.save()
            else:
                return {"error": "Profil bulunamadı"}, 400
    return {"active": instance.profile, "names": list(instance.profiles), "styles": attack_styles()}

@app.route("/instances/<id>/stats/reset", methods=["POST"])
def handle_stats_reset(id):
    instance = get_instance(id)
    with settings_lock:
        instance.settings["stats"] = dict(json.loads(json.dumps(settings_store.EMPTY_STATS)), since=time.time())
        instance.save()
    return instance.settings["stats"]

@app.route("/instances/<id>/report", methods=["POST"])
def handle_report(id):
    instance = get_instance(id)
    data = request.json or {}
    kind = data.get("type", "")
    if kind == "vocab":
        settings_store.DATA_DIR.mkdir(parents=True, exist_ok=True)
        VOCAB_PATH.write_text(json.dumps(data.get("vocab", {}), ensure_ascii=False), encoding="utf-8")
        return jsonify(1)
    with settings_lock:
        stats = instance.settings["stats"]
        if kind == "resources":
            instance.settings["resources"] = dict(data.get("values", {}), t=time.time())
        elif kind == "round_start":
            stats["rounds"] += 1
            instance.next_check = 0
            instance.add_event("Tur başladı")
        elif kind == "scan_done":
            if instance.scan_requested: instance.add_event("Köy okundu")
            instance.scan_requested = False
        elif kind == "search_done":
            if instance.search_requested: instance.add_event("Yalnız arama bitti")
            instance.search_requested = False
        elif kind == "round_end":
            instance.next_check = data.get("next_check", 0)
            instance.add_event(f"Tur bitti ({int(data.get('duration', 0))} sn)")
        elif kind == "rest": # a break or today's cap (2A): the status shows when the next round starts
            instance.next_check = data.get("next_check", 0)
            if data.get("text"): instance.add_event(data["text"])
        elif kind == "upgrade":
            key, label = UPGRADE_KINDS.get(data.get("kind"), (None, ""))
            if key:
                stats[key] += 1
                instance.add_event(f"Geliştirme başladı: {data.get('name', '?')} ({label})")
        elif kind == "wall":
            count = int(data.get("count", 1) or 1)
            stats["walls"] += count
            instance.add_event(f"{count} duvar geliştirildi" if count > 1 else "Duvar geliştirildi")
        elif kind == "attack":
            base = data.get("base")
            if base in ("home", "builder"):
                stats[f"attacks_{base}"] += 1
                instance.add_event("Saldırı: " + ("ana köy" if base == "home" else "usta üssü"))
        elif kind == "error":
            stats["errors"] += 1
            instance.add_event("Hata: " + translate_message(data.get("text", "")))
        elif kind == "event":
            instance.add_event(translate_message(data.get("text", "")))
        else:
            return jsonify(0)
        instance.save()
    return jsonify(1)

@app.route("/instances/<id>/log", methods=["GET"])
def handle_log(id):
    get_instance(id)
    n = min(int(request.args.get("n", 300)), 2000)
    log_path = LOG_DIR / f"{id}.log"
    if not log_path.exists(): return {"entries": []}
    with open(log_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - 400_000))
        lines = f.read().decode("utf-8", errors="replace").splitlines()
    if size > 400_000: lines = lines[1:]
    return {"entries": parse_lines(lines)[-n:]}

@app.route("/vocab", methods=["GET"])
def handle_vocab():
    if VOCAB_PATH.exists():
        try: return json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
        except Exception: pass
    return {}

@app.route("/icons/index", methods=["GET"])
def handle_icon_index():
    index = icons.load_index()
    if not index.get("complete"): icons.start_background_download() # no-op while a download runs
    return {"icons": index.get("icons", {}), "complete": bool(index.get("complete"))}

@app.route("/icons/<path:name>", methods=["GET"])
def handle_icon(name):
    return send_from_directory(icons.ICON_DIR, name, max_age=7 * 24 * 3600)

def start_server(pipe, port, id=None, debug=False):
    global bot_pipe
    bot_pipe = pipe

    if not debug:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    if id is not None:
        instances[id] = Instance(id)
        instances[id].active = False # actions start from the panel's Start button
        instances[id].scan_requested = True # but read the village right away

    icons.start_background_download() # once; the server does not wait for it
    app.run(port=port, debug=debug, threaded=True)

if __name__ == "__main__":
    from multiprocessing import Pipe
    parent_conn, child_conn = Pipe()
    start_server(child_conn, port=1234)
