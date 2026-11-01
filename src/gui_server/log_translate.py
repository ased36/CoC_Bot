import re

WORDS = {
    "home": "binalar", "lab": "laboratuvar", "pet": "evcil hayvan",
    "gold": "altın", "elixir": "iksir", "dark": "kara iksir",
    "discount": "indirimli", "priority": "öncelik listesi", "cheapest": "en ucuz", "random": "rastgele", "town hall": "Belediye binası",
}
tr = lambda word: WORDS.get(word, word)

# English log message -> Turkish panel text. First match wins; {0}, {1}... are regex groups.
TRANSLATIONS = [
    (r"Starting CoC\.\.\.", "Oyun açılıyor…"),
    (r"CoC started", "Oyun açıldı"),
    (r"Stopping CoC\.\.\.", "Oyun kapatılıyor…"),
    (r"CoC stopped", "Oyun kapandı"),
    (r"No update available", "Oyun güncel"),
    (r"Connected to ADB\.", "Emülatöre bağlanıldı"),
    (r"Failed to connect to ADB\. Retrying\.\.\.", "Emülatöre bağlanılamadı, yeniden deneniyor…"),
    (r"Upgrading home base", "Ana köy geliştiriliyor"),
    (r"Upgrading builder base", "Usta üssü geliştiriliyor"),
    (r"Attacking home base", "Ana köyde saldırı"),
    (r"Attacking builder base", "Usta üssünde saldırı"),
    (r"Failed to confirm attack", "Saldırı onaylanamadı"),
    (r"Battle ended after (\d+)s, returned home", "Savaş {0} sn sürdü, köye dönüldü"),
    (r"Return Home not found within (\d+)s, restarting CoC instead", "{0} sn içinde \"Return Home\" bulunamadı, oyun yeniden başlatılıyor"),
    (r"Encountered an error while attempting to upgrade home base\. Retrying\.\.\.", "Ana köy geliştirmesinde hata, yeniden deneniyor"),
    (r"Encountered an error while attempting to upgrade builder base\. Retrying\.\.\.", "Usta üssü geliştirmesinde hata, yeniden deneniyor"),
    (r"Encountered an error while attempting to upgrade home lab\. Retrying\.\.\.", "Laboratuvar geliştirmesinde hata, yeniden deneniyor"),
    (r"Encountered an error while attempting to upgrade builder lab\. Retrying\.\.\.", "Usta laboratuvarı geliştirmesinde hata, yeniden deneniyor"),
    (r"Upgrader\.get_home_builders: Failed to get home builders", "Boş usta sayısı okunamadı"),
    (r"Upgrader\.get_builder_builders: Failed to get builder builders", "Usta üssünde boş usta sayısı okunamadı"),
    (r"Resources: gold=(\S+) elixir=(\S+) dark=(\S+) gems=(\S+) builders=(\S+)", "Kaynaklar — altın {0} · iksir {1} · kara iksir {2} · mücevher {3} · boş usta {4}"),
    (r"Resources could not be read", "Kaynaklar okunamadı"),
    (r"Started upgrading (.+) \((home|home_lab|pet|builder|builder_lab)\)", "Geliştirme başladı: {0}"),
    (r"Upgraded wall", "Duvar geliştirildi"),
    (r"Menu (\w+): (\d+) rows, (\d+) affordable, (\d+) unread, (\d+)s", lambda k, n, a, u, t: f"Menü ({tr(k)}): {n} satır okundu, {a} tanesine kaynak yetiyor" + (f", {u} maliyet okunamadı" if u != "0" else "") + f" ({t} sn)"),
    (r"No upgrade fits \((\w+)\)", lambda k: f"Uygun geliştirme yok ({tr(k)})"),
    (r"Chosen \(([\w ]+)\): (\w+) (\S+)( discounted)?", lambda r, res, c, d: f"Seçildi ({tr(r)}): {c} {tr(res)}" + (" — indirimli" if d else "")),
    (r"Chosen upgrade not found again \((\w+) (\S+)\)", lambda res, c: f"Seçilen geliştirme ({c} {tr(res)}) menüde yeniden bulunamadı"),
    (r"Skipped (.+): blocked in the panel", "{0} atlandı: panelde engelli"),
    (r"Dry run, not confirming: wall with (\w+) (\S+)", lambda res, c: f"Deneme: duvar {c} {tr(res)} ile ödenecekti, onaylanmadı"),
    (r"Dry run, not confirming: (.+)", "Deneme: {0} seçildi, onaylanmadı"),
    (r"Wall (\w+) button not found", lambda res: f"Duvarın {tr(res)} düğmesi bulunamadı"),
    (r"Encountered an error while attempting to upgrade walls", "Duvar geliştirmesinde hata"),
    (r"Walls skipped: disabled", "Duvar kapalı (Köy → Duvar), duvar yapılmıyor"),
    (r"Walls skipped: resources unknown", "Duvar atlandı: kaynaklar okunamadı"),
    (r"Walls skipped: gold (\S+) min (\S+), elixir (\S+) min (\S+)", "Uygun duvar yok: maliyet düşülünce altın {0} (en az {1}) ve iksir {2} (en az {3}) sınırın altına iniyor"),
    (r"Settings loaded", "Ayarlar okundu"),
    (r"Round finished in (\d+)s, next check at (\S+)", "Tur bitti ({0} sn), sonraki tur {1}"),
    (r"Outside working hours \((\S+)-(\S+)\), waiting", "Çalışma saatleri dışında ({0}–{1}), bekleniyor"),
    (r"Paused, waiting", "Duraklatıldı, bekleniyor"),
    (r"Waiting for Start", "Bekliyor — geliştirme ve saldırı Başlat'a basınca başlar"),
    (r"Reading village", "Köy okunuyor (hiçbir şeye dokunulmaz)"),
    (r"Could not read village: CoC did not start", "Köy okunamadı: oyun açılmadı"),
    (r"Stopped from panel, skipping the rest of the round", "Panelden durduruldu, turun kalanı atlanıyor"),
    (r"CoC_Bot\.run:", "Turda beklenmeyen hata"),
    (r"start_coc:", "Oyun açılırken hata"),
]
_COMPILED = [(re.compile(rf"^{p}$"), t) for p, t in TRANSLATIONS]

_LINE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) \| (\w+) \| (.*)$")

LEVELS = {"INFO": "bilgi", "WARNING": "uyarı", "ERROR": "hata", "DEBUG": "ayrıntı", "SUCCESS": "bilgi", "CRITICAL": "hata"}

def translate_message(msg):
    msg = msg.strip()
    for pattern, text in _COMPILED:
        m = pattern.match(msg)
        if m: return text(*m.groups()) if callable(text) else text.format(*m.groups())
    return msg

def parse_lines(lines):
    """Turn raw log lines into entries; lines without a timestamp (tracebacks) attach to the previous entry."""
    entries = []
    for line in lines:
        line = line.rstrip("\r\n")
        if not line: continue
        m = _LINE.match(line)
        if m:
            date, clock, level, msg = m.groups()
            entries.append({
                "date": date,
                "time": clock,
                "level": LEVELS.get(level, level.lower()),
                "text": translate_message(msg),
                "detail": [],
            })
        elif entries:
            entries[-1]["detail"].append(line)
    return entries
