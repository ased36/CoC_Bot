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
    (r"CoC already open", "Oyun zaten açık, köyde (yeniden açılmadı)"),
    (r"Round timing: (.+)", "Tur süreleri: {0}"),
    (r"Home steps: (.+)", "Geliştirme adımı süreleri: {0}"),
    (r"Clan castle (\S+): (\d+) taps", "Klan kalesi büyüsü ({0}): {1} dokunuş"),
    (r"Walls dialog: (.*)", "Duvar penceresi: {0}"),
    (r"Walls paused after an unpaid pass, next look at (.+)", "Duvar ödenmedi, duvar {0}'e kadar bekliyor (saldırılar sürüyor)"),
    (r"Walls skipped: paused after an unpaid pass", "Duvar bekliyor: son duvar turu ödenmedi"),
    (r"Status out of date \((\d+) rows running, (\d+) builders busy(, an end passed)?\), next look at (.+)", lambda a, b, p, t: f"Usta listesi eskimiş (listede {a} süren iş, köyde {b} usta meşgul{', bir bitiş geçti' if p else ''}), yeniden okunuyor"),
    (r"Status (builders|lab): wrong menu on screen \((.*)\), kept the last read", lambda k, t: f"{'Usta' if k == 'builders' else 'Lab'} durumu: ekranda başka menü vardı ({t}), eski okuma tutuldu"),
    (r"Village read: (\d+) rows, (\d+) without a level, next look at (.+)", "Köy okundu: usta menüsünde {0} satır ({1} satırın seviyesi okunamadı), sonraki okuma {2}"),
    (r"Village read: (nothing|the menu did not open), next look at (.+)", lambda w, t: f"Köy okunamadı ({'menü açılmadı' if w.startswith('the') else 'satır yok'}), yeniden {t}"),
    (r"Last look before stopping", "Durdurmadan önce son okuma (ustalar, lab, iksirler, depo)"),
    (r"Last look skipped: (.+)", "Son okuma yapılmadı: {0}"),
    (r"Walls read: nothing, next look at (.+)", "Duvar satırı okunamadı (sonraki okuma {0})"),
    (r"Walls read: (.+), next look at (.+)", "Duvarlar okundu: {0} (sonraki okuma {1})"),
    (r"Stopping CoC\.\.\.", "Oyun kapatılıyor…"),
    (r"CoC stopped", "Oyun kapandı"),
    (r"No update available", "Oyun güncel"),
    (r"Connected to ADB\.", "Emülatöre bağlanıldı"),
    (r"Failed to connect to ADB\. Retrying\.\.\.", "Emülatör bekleniyor…"),
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
    (r"Status builders \(potion (.+) left, x(\d+)\): (.+)", "Ustalar (inşaatçı iksiri {0} kaldı, {1} kat): {2}"),
    (r"Status lab \(potion (.+) left, x(\d+)\): (.+)", "Laboratuvar (araştırma iksiri {0} kaldı, {1} kat): {2}"),
    (r"Status builders: (.+)", "Ustalar: {0}"),
    (r"Status lab: (.+)", "Laboratuvar: {0}"),
    (r"Status read, next look at (.+)", "Usta / lab durumu okundu, sonraki okuma {0}"),
    (r"Pet upgrade did not start, next look at (.+)","Evcil hayvan geliştirmesi başlamadı (kara iksir düşmedi), sonraki bakış {0}"),
    (r"(.+): (gold|elixir|dark) did not drop \((\S+) -> (\S+), cost (\S+)\), not started", lambda n, r, a, b, c: f"{n} başlamadı: {tr(r)} düşmedi ({a} → {b}, maliyet {c})"),
    (r"Pet house busy, next look at (.+)","Evcil hayvan evi meşgul, sonraki bakış {0}"),
    (r"Pet upgrade started, next look at (.+)", "Evcil hayvan geliştirmesi başladı, sonraki bakış {0}"),
    (r"No pet upgrade to start, next look at (.+)", "Evcil hayvanda başlatılacak geliştirme yok, sonraki bakış {0}"),
    (r"Builder apprentice assigned, next look at (.+)", "Çırak atandı, sonraki bakış {0}"),
    (r"No builder apprentice to assign, next look at (.+)", "Atanacak çırak yok, sonraki bakış {0}"),
    (r"Lab assistant assigned, next look at (.+)", "Lab asistanı atandı, sonraki bakış {0}"),
    (r"No lab assistant to assign, next look at (.+)", "Atanacak lab asistanı yok, sonraki bakış {0}"),
    (r"Profile: (.+)", "Profil: {0}"),
    (r"Upgraded (\d+) wall\(s\)", "{0} duvar geliştirildi"),
    (r"Walls: selected wall count unclear \((\S+), wanted (\d+)\)", "Duvar: seçilen duvar sayısı okunamadı ({0}, istenen {1}), geliştirilmedi"),
    (r"Dry run, not confirming: (\d+) wall\(s\) with (\S+), (\S+) each", "Deneme: {0} duvar, {1} ile, tanesi {2} — onaylanmadı"),
    (r"Upgraded wall", "Duvar geliştirildi"),
    (r"Walls wait: gold and elixir below the start levels", "Duvar bekliyor: altın ve iksir başlama değerinin altında"),
    (r"Storage full: the attack brought no gold or elixir", "Depo dolu: saldırı altın / iksir getirmedi"),
    (r"Spent by hand since the last round \((.*)\): walls counted again", "Elle harcama görüldü ({0}): duvarlar bu turda yeniden sayılıyor"),
    (r"Walls: the tap selected something else \((.*)\)", "Duvar: menüde dokunulan satır duvar değil ({0}), ödeme yapılmadı (ekran debug/main_wall_fail.png)"),
    (r"Attack skipped: storage full.*", "Saldırı atlandı: depolar dolu (harcanınca devam eder)"),
    (r"Walls paused: upgrade button not found, next look at (.+)", "Duvar geliştirme düğmesi bulunamadı, duvar {0}'e kadar bekliyor (ekran debug/main_wall_fail.png)"),
    (r"(\S+): ability used right after the drop", "{0}: atılır atılmaz yeteneği kullanıldı"),
    (r"(\S+): ability used \(step\)", "{0}: yeteneği kullanıldı (stil adımı)"),
    (r"Spells: (\S+) x(\d+) into the village", "Büyü: {0} × {1} köyün içine"),
    (r"(\S+) not in the bar or already down, skipped", "{0} çubukta yok ya da zaten indi, atlandı"),
    (r"Attack style (\S+) has errors, not attacking: (.+)", "Saldırı stili {0} hatalı, saldırı yapılmıyor: {1}"),
    (r"Attack style (\S+) not found, using yayma", "Saldırı stili {0} bulunamadı, yayma kullanılıyor"),
    (r"(\d+)s after the first drop, ending the battle", "Saldırı başladıktan {0} sn sonra savaş bitiriliyor"),
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
    (r"Outside working hours, waiting", "Çalışma saatleri dışında, bekleniyor"),
    (r"Resting until (\S+ \S+) \(rest\)", "Mola, devam: {0}"),
    (r"Resting until (\S+ \S+) \(daily\)", "Günlük sınır doldu, devam: {0}"),
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
    (r"(\S+) did not land, trying again", "{0} inmedi, yeniden deneniyor"),
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
