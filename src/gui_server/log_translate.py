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
    (r"Search only: looking for a village without attacking", "Yalnız arama: rakip köylere bakılıyor, saldırılmayacak"),
    (r"Could not search: CoC did not start", "Arama yapılamadı: oyun açılmadı"),
    (r"Search (\d+): gold=(\S+) elixir=(\S+) dark=(\S+) min=(\S+)/(\S+)/(\S+)", lambda n, g, e, d, mg, me, md: f"Arama {n}: altın {g} · iksir {e} · kara iksir {d} — şart " + " · ".join(f"{a} ≥ {v}" for a, v in (("altın", mg), ("iksir", me), ("kara", md)) if v not in ("0", "-")) if any(v not in ("0", "-") for v in (mg, me, md)) else f"Arama {n}: altın {g} · iksir {e} · kara iksir {d} — şart yok"),
    (r"Village found after (\d+) searches", "Uygun köy bulundu ({0}. arama)"),
    (r"No village in (\d+) searches, trying again next round", "{0} aramada uygun köy çıkmadı, sonraki turda yeniden"),
    (r"Village did not load", "Rakip köy yüklenmedi"),
    (r"Next button not found", "Next düğmesi bulunamadı"),
    (r"Battle button not found", "Battle düğmesi bulunamadı (ana köy ekranı değil), arama yapılmadı"),
    (r"Failed to click find a match button", "\"Find a Match\" düğmesi bulunamadı"),
    (r"End Battle not found on the search screen", "Arama ekranında End Battle bulunamadı"),
    (r"Did not get back home from the search screen", "Arama ekranından köye dönülemedi"),
    (r"Error in run_search_only\(\):", "Yalnız aramada beklenmeyen hata"),
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
    (r"Upgraded (\d+) wall\(s\)", "{0} duvar geliştirildi"),
    (r"Walls: selected wall count unclear \((\S+), wanted (\d+)\)", "Duvar: seçilen duvar sayısı okunamadı ({0}, istenen {1}), geliştirilmedi"),
    (r"Dry run, not confirming: (\d+) wall\(s\) with (\S+), (\S+) each", "Deneme: {0} duvar, {1} ile, tanesi {2} — onaylanmadı"),
    (r"Upgraded wall", "Duvar geliştirildi"),
    (r"(\d+)s after the deploy, ending the battle", "Askerler indikten {0} sn sonra savaş bitiriliyor"),
    (r"Walls skipped: not enough gold or elixir for a wall", "Duvar atlandı: altın ya da iksir bir duvara yetmiyor"),
    (r"Walls after the attack:", "Saldırıdan sonra duvar adımında hata"),
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
    (r"Walls: the upgrade menu did not open", "Duvar: inşaat menüsü açılmadı (ekran debug/main_wall_fail.png)"),
    (r"Walls: could not go back to the wall row \((\S+)\)", "Duvar: {0} maliyetli satıra geri dönülemedi (ekran debug/main_wall_fail.png)"),
    (r"Walls: confirm button not found", "Duvar: onay düğmesi bulunamadı (ekran debug/main_wall_fail.png)"),
    (r"Walls: paid with (\S+) but it did not go down \((\S+) -> (\S+)\)", "Duvar: {0} ile ödendi ama kaynak azalmadı ({1} → {2})"),
    (r"Wall level (\S+) not chosen \((\S+)\)", "Duvar seviyesi {0} seçili değil ({1}), geçildi"),
    (r"No wall of the chosen levels \((.*)\)", "Seçili seviyelerde ({0}) duvar yok"),
    (r"No affordable wall in the menu \((\d+) rows read\)", "Menüde parası yeten duvar yok ({0} satır okundu)"),
    (r"Emulator is not running, starting it again","BlueStacks kapanmış, yeniden açılıyor"),
    (r"Emulator back after (\d+)s", "BlueStacks yeniden açıldı ({0} sn)"),
    (r"Emulator started but Android did not finish booting", "BlueStacks açıldı ama Android yüklenmedi"),
    (r"ensure_emulator:", "BlueStacks yeniden açılırken hata"),
    (r"Attack (\S+): cards (.*)", "Saldırı ({0}): kartlar {1}"),
    (r"Bottom corner: view moved up, (\d+) points", "Alt köşe: görüntü yukarı kaydırıldı, {0} nokta"),
    (r"Leftover troops: (\d+) more taps, card empty", "Elde kalan askerler {0} dokunuşla bırakıldı"),
    (r"Leftover troops: (\d+) more taps, card still not empty", "Elde kalan askerler: {0} dokunuş, kart hâlâ boş değil"),
    (r"Siege already on the field, its card is not touched", "Kuşatma zaten sahada, kartına dokunulmadı"),
    (r"(\S+) did not land, trying further out", "{0} inmedi, daha dışarıdan yeniden"),
    (r"(\S+) could not be deployed", "{0} indirilemedi"),
    (r"Loot unchanged for (\d+)s, ending the battle", "Ganimet {0} sn değişmedi, savaş bitiriliyor"),
    (r"Battle over, back home", "Savaş bitti, köye dönüldü"),
    (r"Return Home not found, restarting CoC instead", "Return Home bulunamadı, oyun yeniden açılıyor"),
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
