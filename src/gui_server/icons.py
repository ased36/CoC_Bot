"""Panel icons from the ClashKingAssets repository (the same place the name lists come from).
Downloaded once into data/icons (data/ is not in git: Supercell pictures stay out of the public fork)."""
import json, re, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import settings as settings_store

REPO = "ClashKingInc/ClashKingAssets"
CATEGORIES = ["buildings/home-village", "traps/home-village", "heroes", "troops", "spells", "pets"]
ICON_DIR = settings_store.DATA_DIR / "icons"
INDEX_PATH = ICON_DIR / "index.json"

_lock = threading.Lock()
_last_try = 0

def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "CoC_Bot panel"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def _format_name(stem):
    # Same as utils.get_vocab, so icon names match the panel's name lists
    return stem.replace("_", " ").title()

def _slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

def _pick_files(paths):
    """{name: repo path}: icon.webp when there is one, else the highest level picture; spells are plain files."""
    best = {}
    for cat in CATEGORIES:
        prefix = f"assets/{cat}/"
        for p in paths:
            if not p.startswith(prefix) or not p.endswith(".webp"): continue
            parts = p[len(prefix):].split("/")
            if len(parts) == 1: # assets/spells/rage_spell.webp
                name, rank = _format_name(parts[0][:-5]), 10**6
            elif len(parts) == 2:
                name = _format_name(parts[0])
                if parts[1] == "icon.webp": rank = 10**6
                elif (m := re.fullmatch(r"level_(\d+)\.webp", parts[1])): rank = int(m.group(1))
                else: continue
            else: continue
            if name not in best or rank > best[name][0]: best[name] = (rank, p)
    return {name: p for name, (rank, p) in best.items()}

def load_index():
    try: return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except Exception: return {"icons": {}, "complete": False}

def ensure_icons():
    """Download the missing icons. One GitHub API request (the repo tree), the pictures come from raw.githubusercontent.com."""
    if not _lock.acquire(blocking=False): return
    try:
        index = load_index()
        if index.get("complete"): return
        repo = json.loads(_get(f"https://api.github.com/repos/{REPO}"))
        branch = repo.get("default_branch", "main")
        tree = json.loads(_get(f"https://api.github.com/repos/{REPO}/git/trees/{branch}?recursive=1"))
        files = _pick_files([e["path"] for e in tree.get("tree", []) if e.get("type") == "blob"])
        ICON_DIR.mkdir(parents=True, exist_ok=True)
        icons = dict(index.get("icons", {}))

        def fetch(item):
            name, path = item
            target = ICON_DIR / f"{_slug(name)}.webp"
            if not target.exists() or target.stat().st_size == 0:
                target.write_bytes(_get(f"https://raw.githubusercontent.com/{REPO}/{branch}/{path}"))
            return name, target.name

        failed = []
        with ThreadPoolExecutor(8) as pool:
            for item, result in zip(files.items(), pool.map(lambda i: _safe(fetch, i), files.items())):
                if result: icons[result[0]] = result[1]
                else: failed.append(item[0])
        INDEX_PATH.write_text(json.dumps({"icons": icons, "complete": not failed, "failed": failed}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass # no internet: tiles show initials, the next panel start tries again
    finally:
        _lock.release()

def _safe(fn, arg):
    try: return fn(arg)
    except Exception: return None

def start_background_download():
    # At most every 10 minutes: the GitHub API allows 60 requests an hour without a token
    global _last_try
    if time.time() - _last_try < 600: return
    _last_try = time.time()
    threading.Thread(target=ensure_icons, daemon=True).start()
