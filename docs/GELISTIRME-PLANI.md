# Geliştirme planı (ased36/CoC_Bot)

MyBot.run'ın ayar grupları örnek alındı (kaynak: MyBotRun/MyBot `develop` dalı, `COCBot/GUI/*.au3`).
Kod kopyalanmadı, yalnızca hangi ayarların olduğuna bakıldı.

Zorluk işaretleri:
- ✅ yalnızca kod, canlı oyunda ayar gerekmez
- 🟨 oyun ekranından yeni resim / okuma bölgesi gerekir, canlı denenmeli
- 🟥 mümkün ama yavaş ya da riskli

Bir ayar panele **çalıştığı denendikten sonra** eklenir. Çalışmayan düğme konmaz.

## 0. Altyapı (önce bu)

| İş | Not | |
|---|---|---|
| Ayar deposu | `data/<id>.json`: görev aç/kapa + ayarlar + istatistik; panelden değişir, bot her tur başında okur | ✅ |
| Bot → panel raporu | `/instances/<id>/report`: kaynaklar, saldırı, geliştirme, tur | ✅ |
| Kayıt akışı | panel `debug/<id>.log` dosyasını okur, Türkçe'ye çevirerek gösterir | ✅ |
| Kaynak okuma | sağ üst: altın, iksir, kara iksir, mücevher (easyocr, ~0,1 sn/kaynak); bölgeler 1920×1080'de ölçüldü, mücevher bölgesi rozet yüzünden daraltılacak | ✅ |

## 1. Panel (Türkçe, koyu tema, geniş pencere)

Sekmeler: **Kayıt · Köy · Duvarlar · Saldırı · Usta üssü · Bakım · İstatistik · Genel**
Alt şerit: Başlat / Durdur / Duraklat (5-15-30-özel) · altın · iksir · kara iksir · mücevher · usta · son okuma saati.

## 2. Genel

| Ayar | Seçenek | Varsayılan | |
|---|---|---|---|
| Kontrol aralığı | dakika | 5 | ✅ |
| Rastgele bekleme payı | ± % (insan gibi) | 20 | ✅ |
| Çalışma saatleri | başlangıç–bitiş | her zaman | ✅ |
| Tur sonunda oyunu kapat | aç/kapa | açık | ✅ |
| Telegram bildirimi | aç/kapa + anahtar | kapalı | ✅ (kod var) |

## 3. Köy geliştirme (ana köy)

| Ayar | Seçenek | Varsayılan | |
|---|---|---|---|
| Binalar / Kahramanlar / Laboratuvar / Evcil / Usta çırağı / Lab asistanı | aç/kapa | açık | ✅ (var) |
| **Seçim yöntemi** | Öncelik listesi · En ucuz · Rastgele · En kısa süre | Öncelik, listede yoksa en ucuz | Öncelik ✅ · En ucuz ✅ 2. oturum ("Listede uygun yoksa: En ucuz / Rastgele") · En kısa süre 🟥 (her aday için pencere açılır) |
| Öncelik listesi | panelde düzenlenir (satır = öncelik seviyesi) | configs'teki liste | ✅ |
| Kaynak tercihi | Altınla olanlar önce · İksirle olanlar önce · Fark etmez | fark etmez | ✅ 2. oturum (simge rengi) |
| Geliştirmeden sonra kalacak en az | altın / iksir / kara iksir | 0 | ✅ 2. oturum |
| Boşta bırakılacak usta | sayı | 0 | ✅ (var: OPEN_HOME_BUILDERS) |
| Tur başına en fazla geliştirme | sayı | 10 | ✅ (var) |
| Belediye binası | aç/kapa | açık | ✅ |
| Hariç tutulacak binalar | liste | boş | ✅ |
| İndirimli (yeşil etiket) önce | aç/kapa | açık | 🟨 kodu var ve açık (`green_tag` satırda aranır); **henüz indirimli satır görülmedi, denenmedi** → panelde düğme yok |

## 4. Duvarlar

| Ayar | Seçenek | Varsayılan | |
|---|---|---|---|
| Otomatik duvar | aç/kapa | kapalı | ✅ 2. oturum (tur sonunda ayrı geçiş, deneme kipinde denendi) |
| Kaynak | Altın · İksir · Önce iksir sonra altın | önce iksir | ✅ 2. oturum yalnız "önce iksir sonra altın" (seçenek panelde yok) |
| Kalacak en az altın / iksir | sayı | 1 000 000 / 1 000 000 | ✅ 2. oturum: maliyet düşülerek |
| Tur başına en fazla duvar | sayı | 5 | ✅ 2. oturum |
| Duvara 1 usta ayır | aç/kapa | kapalı | ❌ gereksiz: duvar usta istemiyor (01.11 canlı: ustalar 0/5 iken duvar onay penceresi açıldı, süre "None") |

## 5. Saldırı (ana köy) — şu an KAPALI (01.11, Emre isteği)

| Ayar | Seçenek | Varsayılan | |
|---|---|---|---|
| Saldır | aç/kapa | kapalı | ✅ |
| Arama şartı | en az altın · en az iksir · en az kara iksir · birleşim VE / VEYA / TOPLAM | 400k / 0 / 0, VE (0 = sayılmaz) | ✅ 4. oturum, yalnız VE |
| En fazla Belediye seviyesi | sayı | sınırsız | 🟨 |
| Şartları düşür | her X aramada %Y | 15 / 10 | ✅ 4. oturum (panel değerinin yüzdesi, birikmez) |
| En fazla arama | sayı, sonra: ilk köye saldır · vazgeç | 30, vazgeç | ✅ 4. oturum (yalnız vazgeç) |
| Depolar doluysa saldırma | aç/kapa | açık | 🟨 (depo çubuğunun doluluğu) |
| Kahramanları bekle | aç/kapa | kapalı | 🟨 |
| Klan askerlerini kullan | aç/kapa | kapalı | ✅ (var) |
| Asker yerleştirme süresi | sn | 2 | ✅ (var) |

## 6. Savaş sonu

| Ayar | Seçenek | Varsayılan | |
|---|---|---|---|
| Savaşın bitmesini bekle (Return Home) | aç/kapa | açık | ✅ yazıldı, **saldırı açılınca denenecek** |
| X sn yeni ganimet yoksa bitir | sn | 20 | 🟨 (savaş içi ganimet okuma) |
| % X'i geçince bitir · 1/2 yıldızda bitir | seçim | kapalı | 🟨 |

## 7. Usta üssü

| Ayar | Seçenek | Varsayılan | |
|---|---|---|---|
| Binalar / Laboratuvar / öncelik | aç/kapa | açık | ✅ (var) |
| Saldırı | aç/kapa | kapalı | ✅ |
| Yalnızca yıldız bonusu varken saldır | aç/kapa | açık | 🟨 |

## 8. Bakım

| Ayar | | |
|---|---|---|
| Toplayıcılardan topla | aç/kapa | 🟨 (`collect` resmi var) |
| Maden arabası | aç/kapa | 🟨 |
| Mezar taşı / engel temizle | aç/kapa | 🟨 |

## 9. İstatistik

Tur sayısı · saldırı (ana/usta) · başlayan geliştirmeler (ana/usta) · kazanılan ganimet (saldırı öncesi/sonrası kaynak farkı) · hata sayısı · son 50 olay · sıfırla düğmesi. ✅

## Emre'nin kararları (01.11)

- Geliştirme seçimi varsayılanı: **öncelik listesi, listede uygun yoksa en ucuz** (en ucuz kısmı 2. oturumda, o zamana kadar listede yoksa rastgele).
- Duvar kaynağı: **önce iksir, yetmezse altın**.
- Duvarlara harcarken kalacak en az: **altın 1 000 000 / iksir 1 000 000**, panelden (Köy → Duvar) değiştirilebilir (01.11, 1. oturum).
- Saldırılar kapalı kalacak; savaş sonu: bekle + Return Home; tur sonunda oyun kapansın; orijinal yazara PR şimdilik yok.

## Emre'nin kararları (01.11, 1. oturum sonu — ClashFarmer araştırmasından sonra)

- **Açılış:** bot açılınca yalnızca köyü okur (oyunu açar, kaynak/usta okur, kapatır), geliştirme ve saldırı **Başlat'a basınca** başlar. Durdur = elindeki adımı bitirip bekler (programı öldürmez). Alt şeritte "Köyü oku" düğmesi. ✅ yapıldı
- **Duvar:** ayrı aç/kapa anahtarı, **kapalı başlar** ✅ yapıldı. Mantık **MyBot gibi (1A):** her turun en sonunda; önce açık bina/lab geliştirmelerinin parası ayrılır, kalandan duvar; "kalan − maliyet ≥ en az" oldukça devam; seviye seçimi; duvara 1 usta ayır → 3. oturum.
- **Mola saatleri (2A):** ClashFarmer'daki gibi 24 saatlik ızgara, Genel sekmesinde; şimdiki başlangıç–bitiş saatinin yerine geçer.
- **Ordu (3A):** oyunun Quick Train tarifleri 1/2/3 (asker asker kurma yok).
- **Yeni gruplar (4: hepsi):** bakım genişlemesi (hazine, engel/mücevher kutusu, başarı ödülleri) · asker isteme + bağış · güçlendirmeler (saat ızgarası) · klan oyunları + klan başkenti · Telegram bildirim + uzaktan komut · günlük rastgele saldırı sınırı.
- **Oturum sırası (5A) aynı kalır:** 2 maliyet okuma → 3 duvar → 4 saldırı → 5 bakım; yeni gruplar 6. oturumdan sonra (sırası o zaman konuşulur).

## Oturum sırası

1. Altyapı + panel + kaynak okuma + istatistik + Genel + Köy'ün ✅ satırları + öncelik listesi düzenleme — **yapıldı 01.11** (aşağıda "1. oturum")
2. Menüde maliyet okuma → En ucuz, kaynak tercihi, kalacak en az, indirimli önce — **yapıldı 01.11** (aşağıda "2. oturum"); duvarın maliyetli hali de bu oturumda yapıldı
3. Duvarlar
4. Saldırı arama şartları + savaş sonu şartları (saldırı açılınca)
5. Bakım, usta üssü saldırı ayarları, en kısa süre
6+. ClashFarmer/MyBot'tan eklenenler (Ek bölümü): mola ızgarası, bakım genişlemesi, asker isteme/bağış, güçlendirmeler, klan oyunları + başkent, Telegram, günlük saldırı sınırı

## Bilinen hatalar / notlar

- ~~`upgrader.py` "heros" yazım hatası~~ ve ~~`launch.py` `cmd_launch` `utils` tanımsız~~ — 1. oturumda düzeltildi.

## 1. oturum (01.11) — ne yapıldı

- **Ayar deposu** `src/settings.py` → `data/<id>.json` (gitignore'da). Tek yazan panel sunucusu; bot her tur başında `GET /instances/<id>/settings` ile okur (`Settings_Handler.load`), panel yoksa dosyadan. Görev aç/kapa (`tasks`), Genel, Köy, Usta üssü, duvar sınırları, son kaynaklar ve istatistik aynı dosyada. Eski paneldeki görev ayarları bot yeniden başlayınca sıfırlanıyordu; artık kalıcı.
- **Bot → panel raporu** `POST /instances/<id>/report` (`utils.report`): `round_start`, `round_end`, `resources`, `upgrade` (home/home_lab/pet/builder/builder_lab), `wall`, `attack`, `error` (loguru ERROR sink), `vocab` (bina adı listesi → `data/vocab.json`, paneldeki ad önerileri için).
- **Kaynak okuma** `utils.Resource_Reader` + `OCR_Handler.read_digits`: beyaz yazı ayıklanır, kenar eklenir, 2× büyütülür, easyocr rakam listesiyle okunur. Ham görüntüde "1 939" → "939", "6 900 507" → "900 507" kaçırıyordu; bu yöntemle 5/5 doğru. Bölgeler (1920×1080 oranı): altın 0.835–0.955 × 0.030–0.080, iksir × 0.098–0.148, kara 0.865– × 0.165–0.215, mücevher 0.905– × 0.233–0.283 (rozetten sonra), usta 0.885–0.935 × 0.750–0.790 ("0/5"; eğik çizgi bazen 7 okunur → ilk ve son rakam). Tur başında, sonunda ve her ana köy geliştirmesinden sonra okunur.
- **Panel** (`templates/instance.html`, `static/panel.css`): Kayıt (Türkçe çeviri `gui_server/log_translate.py`, yalnız uyarı/hata süzgeci, hata ayrıntısı) · Köy (görevler, Belediye binası, sınırlar, duvar, hariç binalar, 5 öncelik listesi düzenleyici) · Genel (aralık, ± bekleme payı, çalışma saatleri, oyunu kapat) · İstatistik (sayaçlar, son 50 olay, sıfırla). Alt şerit: Başlat/Durdur, Duraklat 5/15/30/özel + Devam et, durum, kaynaklar. Pencere 1180×800, boyutlanabilir.
- **Duraklat** eski panelde hiç çalışmıyordu (`running()` web uygulaması yoksa hep True dönüyordu) → yerel panele soruyor.
- **Duvar alt sınırı** (Emre: 1 000 000 / 1 000 000, panelden değişir): altın ya da iksir sınırın altındaysa ya da okunamadıysa "Wall" hem öncelik listesinden hem rastgele seçimden çıkar. Maliyet okunmadığı için kaba; tam hali 2. oturumda.
- **Hariç binalar + Belediye binası anahtarı**: öncelik listesinden çıkarılır, rastgele seçimde geçersiz satır sayılır, adı okunduktan sonra yine engellenir.
- Küçük düzeltmeler: `pet_house_priority` → `PRIORITY_PET_UPGRADES` (yanlış ad), kahraman adı karşılaştırması küçük harfle (hiç tutmuyordu), `Cache_Manager.get("vocab", get_vocab())` her çağrıda GitHub'a gidiyordu → `get("vocab") or get_vocab()`.
- Eski panelde düğme **yanıyorsa görev kapalıydı**; 01.11 04:45'te 14 görevin hepsi kapalı kalmış, bot oyunu açıp hemen kapatıyordu. Yeni panelde yeşil = açık.
- Ana köy saldırısında 01.11'de "Failed to confirm attack" görüldü (`confirm_attack` resmi tutmadı).
- `attacker.py`: savaş sonu bekleme (`WAIT_FOR_BATTLE_END`) yazıldı, commit'lenmedi. 01.11 04:33 usta üssü denemesi: **"Return Home" 300 sn'de bulunamadı**, yedek yol (oyunu yeniden başlat) çalıştı. `_click_return_home` gri ton + prefilter'sız eşik 0,9 arıyor; savaş sonu ekran görüntüsüyle ölçülüp düzeltilecek (renkli + prefilter dene).

## 2. oturum (01.11) — ne yapıldı

**Emre'nin kararları:** 1A deneme kipinde canlı deneme (ustalar 0/5 doluydu) · 2A en ucuz bina + laboratuvar + evcil hayvanda · 3A "en ucuz" = maliyet ÷ depodaki miktar · 4A indirimli her şeyden önce · 5A duvar alt sınırı (aşağıda: hangi kaynakla ödeneceği bilinince "önce iksir, yetmezse altın" ile kesinleşti).
Emre'nin hedefi: 4 usta hep geliştirmede, 1'i savaş + duvar için. **Bulgu:** duvar da saldırı da usta kullanmıyor; "Boşta bırakılacak usta" **0 kalır** (Emre 01.11: "default 0 kalsın").

- **Menü tarama** (`upgrader.py` → `_open_menu`, `_scan_menu`, `_read_rows`): menü açılır, başlık ("Suggested upgrades" / pet'te "Assigned") en üste kaydırılır, sonra sayfa sayfa aşağı. Satır = sağdaki kaynak simgesi: x 0.981–0.991'de altın (R>200 G>150 B<90), iksir (R>140 G<110 B>150), kara (hepsi <70) en az 6 px dolu şerit; kara damladaki parlaklık şeridi ikiye bölüyor → 0.02 içinde birleştirilir. Maliyet x 0.840–0.979, simgenin ±0.016'sı: beyaz yazı = kaynak yetiyor (OCR ile okunur), kırmızı = yetmiyor (okunmaz). Ad satırı maliyetin 0.025 üstünde; ad şablonu yalnız satır başında (x < 0.79, pet 0.82) sayılır → "Barracks" "Dark Barracks"ı tutmaz. Yeşil ad = yeni bina, atlanır. 8 ekran görüntüsünde bütün maliyetler doğru okundu.
- **Sayfa kayması:** ilk hâli (alt−0.075 → üst) sayfalar arasında satır kaçırıyordu (8 sayfa, en alttaki 800 altınlık Bomb hiç görülmedi); kaydırma üst+0.15'e kısaldı, sayfalar ~2 satır örtüşüyor (10 sayfa, ana köy taraması ~33 sn, lab ~13 sn).
- **Seçilen satıra gitme:** seçilen satır ekrandaki sayfada değilse menü kapatılıp açılır, aynı kaydırmalar tekrarlanır, satır maliyet + kaynakla yeniden bulunur.
- **Seçim sırası** (`_choose_row`): indirimli → öncelik listesi seviyeleri (seviye içinde en ucuz) → "Listede uygun yoksa" (en ucuz / rastgele) → Belediye binası en son. Hepsinde kaynak tercihi önce, "kalacak en az" tutmayan satır atlanır. Crafting Station, hariç binalar, (kapalıysa) kahramanlar ve duvar bina seçiminden çıkar.
- **Duvar** (`wall_upgrade`, `run_walls`): ana köy turunun en sonunda, bina/lab/pet'ten artan kaynakla; en ucuz duvar; önce iksir (iksir − maliyet ≥ en az iksir), olmazsa altın. Düğme fiyatın yanındaki simge renginden bulunur (eski `upgrade.png` şablonu tutmuyordu; ortadaki mavi düğme Wall Ring, ona basılmaz). Kaynak düşmezse sayılmaz ve durur.
- **Usta üssü "boş usta okunamadı":** iksir arabası penceresi kapanırken 1 sn yetmiyordu → araba sonrası 1 sn bekleme, okuma süresi 5 sn.
- **Panel Köy:** "Seçim" kartı (listede uygun yoksa, kaynak tercihi, kalacak en az altın / iksir / kara iksir), Duvar'a "tur başına en fazla duvar". Kayıt çevirileri eklendi.
- **Deneme kipi:** `Upgrader.dry_run = True` seçer, menüde satırı açar, onaya basmaz (yalnız geliştirici denemesi, panelde yok).
- **Canlı deneme (01.11 05:40–05:52, deneme kipi, hiçbir şey onaylanmadı, kaynaklar aynı kaldı):** binalar → öncelik 1. seviyeden Grand Warden 5 040 000 iksir; "kalacak en az iksir 3 000 000" ile Warden elendi, en ucuz Bomb 800 altın; lab → Freeze Spell 2 400 000 iksir; pet → kaynak yetmiyor, seçim yok; duvar → en ucuz 1 200 000, iksirle (en az iksir 7 M yapılınca altınla) onay penceresi doğru açıldı.
- **Bekleyen:** indirimli (yeşil etiket) satır hiç görülmedi; Hammer Jam (01–15.11, 09:00'da başlıyor) menüyü nasıl gösteriyor (üstü çizili fiyat? etiket?) bakılacak, gerekirse ölçülüp panele düğme konacak. Gerçek (onaylı) geliştirme ilk boş ustada görülecek.

## 4. oturum kararları (01.11, Emre) — saldırı

Önce bu, 3. oturumun (duvar) çoğu 2. oturumda yapıldı. Saldırı **betikli** olacak: her stil `docs/SALDIRI-STILI.md`'de Türkçe anlatılır, Claude `attacks/<ad>.yaml` betiğine çevirir; ilk stil süper barbar + yıldırım (taslak belgede, boş satırları Emre dolduracak).

- **Ganimet şartı (1A):** altın / iksir / kara iksir alt sınırlarının **hepsi** tutmalı; **0 yazılan şart sayılmaz** (Emre: altın 400 000, iksir 0).
- **Kara iksir (2B):** panelde ayrı alt sınır.
- **Arama (3A):** en fazla 30 "Next", bulamazsa vazgeç, sonraki turda yeniden.
- **Yıldırım (4A):** 4 sondaya 3 + 3 + 3 + 2 = 11; az bulunursa bulunanlara bölünür, hiç bulunamazsa atılmaz. Sonda şablonu yok → arama denemesinde rakip köylerden toplanacak.
- **Yön (5B):** sağ / sol / alt / üst rastgele, art arda aynı gelmez.
- **Kahraman (6A):** ordunun arkasından aynı yönden, yetenek 8–12 sn sonra; klan askeri yok.
- **Ordu (7A):** Quick Train kayıtlı ordu (panelden 1/2/3 seçilir). MyBot gibi asker asker ordu yazma sonra.
- **İnsan gibi (Emre):** her saldırı farklı: dalgalı bırakma, rastgele beklemeler, dokunuş sapması, bazen bir taraf geç, bazen yıldırım biraz sapsın.
- **Deneme sırası:** önce "yalnız ara" (saldırmaz, ganimet okur, Next'e basar), sonra Emre'nin onayıyla tek gerçek saldırı. Bilinen kırıklar: `confirm_attack` ve `return_home` resimleri tutmuyor → canlıda ölçülecek.
- **Ek kararlar (01.11, 4. oturum başı):** 2B en fazla 30 arama + **her 15 aramada şartlar %10 düşer** (ikisi de panelden; Emre bazen %30 yapar) · 3A kara iksir şartı yok · 4A yıldırım ordudan önce · 5B **20 sn ganimet değişmezse savaşı bitir** · 6A ordu ekrandan okunur.

## 4. oturum (01.11) — ne yapıldı (yarım: arama bitti, saldırı betiği sırada)

- **Satın alma kazası (06:10):** deneme betiğimin kör tıklaması (sağ ortaya → Shop'un kenarı; sonra Battle yerine → mağazada TH15 Pack fiyat düğmesi) Google Play "Satın al ₺159,00" penceresini açtı; ekrana dokunmadan Android Geri tuşuyla kapatıldı, satın alma olmadı. Ders: kör koordinat yok. Botun Battle tıklaması da kördü → artık `_click_battle` önce ana köyü ve Battle düğmesinin resmini (`assets/attacker/battle.png`, eşik 0,97; köyde 1,0, mağazada 0,38) doğruluyor. Emre: Play'de satın alma şifresi açmayacak, ayrı bekçi istemedi.
- **Ölçümler (1920×1080):** Battle → savaş penceresi ("Find a Match 1400" — her arama ve Next 1 400 altın) → ordu penceresi, sağ altta yeşil "Attack!" = `confirm_attack` (resim tutuyor, güven 0,98; eski hata pencerenin 5 sn'den geç açılmasıydı → 10 sn) → bulutlar → rakip köy ~3,5 sn sonra. Rakip köy ekranı: sol üstte "Available Loot" altın (0.050, 0.118, 0.160, 0.165), iksir (…0.172–0.220), kara (…0.225–0.272) — beyaz rakam, `read_digits` ile okunur (2 köyde ekranla birebir karşılaştırıldı, 14 köyde değerler makul, tek tek bakılmadı); sağda **Next** (`assets/attacker/next.png`), solda End Battle. **"Battle starts in 30s"**: süre dolunca savaş başlar, Next kalkar → karar 30 sn içinde. Asker koymadan End Battle → onay sormadan doğrudan köy, saldırı sayılmaz.
- **Kod:** `attacker.py` → `search()` (ganimet oku, `loot_minimums` her `lower_every` aramada panel değerinin `lower_pct` %'si kadar düşürür, `loot_ok` 0 olmayan her şart tutmalı, okunamayan şart tutmaz; köyde 1,5–4 sn rastgele bakıp Next, dokunuşlar birkaç piksel sapmalı; bulamazsa End Battle ile döner), `run_search_only()`, eski `start_normal_attack` → `_open_search()`. `run_home_base` artık `search()` sonra eski kör asker bırakma (`complete_normal_attack`, betikle değişecek; saldırılar kapalı). Yalnız aramada her köy `debug/villages/`e kaydedilir (sonda şablonu için).
- **Panel:** Genel → "Saldırı — arama" kartı (ana köyde saldır anahtarı, en az altın/iksir/kara, en fazla arama, her N aramada %Y düşür); alt şeritte **"Yalnız ara"** düğmesi (bot dururken; kip `search`, bitince "Yalnız arama bitti"). Kayıt Türkçe ("Arama 3: altın … — şart altın ≥ 400.000").
- **Canlı deneme:** (1) gerçek şart 400 000: 1. köy 697 145 altın → "uygun", saldırmadan döndü (15 sn). (2) yol denemesi, şart bilerek 3 000 000 (30 arama + düşüş + vazgeçme görülsün diye; Emre 1 milyonluk köylerin geçilmesine şaşırdı — denemeden önce açıkça söylenmeli): 14 arama sorunsuz (~11 sn/arama), 15.'de **BlueStacks kapandı** (HD-Player süreci yok; Emre mi kapattı, çöktü mü belli değil), ADB koptu. Kayıp yok (~21 000 altın arama bedeli).
- **Sonda:** henüz bulunamadı. Gözle bakılan adaylar sonda değil: mor kristal yığını = Wizard Tower, şişeli siyah kule = TH15 Spell Tower, pembe tanklı pompa = iksir toplayıcı. 15 köy `debug/villages/`de → sonraki oturumda kara iksir sondası buradan bulunacak (sondayı dokunup adını görmek rakip köyde mümkün değil; gerekirse Emre kendi köyünde gösterir).
- **Sıradaki:** (1) 2A: panel ayarıyla (400 000 / 30 / 15 / %10) yalnız ara — bulunca durur, saldırmaz. (2) Sonda şablonu. (3) Saldırı betiği `attacks/super-barbar.yaml` + yıldırım + kahraman + 20 sn ganimet bekçisi + Return Home ölçümü. (4) Emre onayıyla tek gerçek saldırı. Hammer Jam henüz başlamamıştı (06:15, Wizard Tower düz fiyat 1 040 000) → etkinlik başlayınca menü fiyatı.

## 4. oturum devamı (01.11 öğle) — ne yapıldı

- **BlueStacks çökmeleri çözüldü:** `X:\BlueStacks_nxt\Dumps\HD-Player\` altındaki 4 dökümün (04:17, 04:19, 06:28, 12:37) hepsi `nvoglv64.dll+0x94a750` erişim hatası = NVIDIA OpenGL sürücüsü (RTX 3060, 610.88). 04:10'daki Vulkan → OpenGL geçişinden sonra başlamıştı. Emre BlueStacks ayarından **Vulkan**'a döndü (`graphics_renderer="vlcn"`), sonrasında çökme yok. 06:28'deki "BlueStacks kapandı" da buydu, Emre kapatmamıştı.
- **2A yalnız ara ✅ (12:40):** panel ayarı (400 000 / 30 / her 15'te %10); 1. aramada altın 512 563 / iksir 446 313 / kara 5 027 — ekranla birebir; saldırmadan End Battle ile döndü, 54 sn, tek bedel 1 400 altın.
- **Yanlışlıkla gerçek geliştirme (12:42):** yalnız aramadan sonra panelde Başlat'a basıldı → tam tur → **Mighty Yak (pet) 18 000 kara iksirle başladı**. Durdur birkaç saniye önce basılmıştı ama Durdur adım bitince işliyor. İptal edilmedi (yarısı yanar). Emre 12:43'te görevleri kapattı. → Başlat'a onay penceresi eklendi (aşağıda).
- **Bilinen davranış (kod değişmedi):** duvar, usta çırağı ve lab asistanı `run_home_base` içinde; Binalar, Laboratuvar ve Evcil hayvanların üçü kapalıysa bu adım hiç çalışmaz → onlar da çalışmaz. Panel özeti bunu yazıyor.
- **Panel yenilendi (Emre 1A 2A 3A):** sekmeler Durum · Geliştirme · Saldırı · Genel · İstatistik. Durum = "Başlat'a basınca bot şunları yapar" özeti (ayarlardan canlı; kaynak harcayan görev varsa sarı uyarı) + son 8 olay + kayıt. Başlat'a basınca aynı listeyle onay penceresi. Görevler "Bot neleri geliştirsin?" — her anahtarın altında ne yaptığı, "kaynak harcar" / "ücretsiz" etiketi; Kahraman ve Belediye "Binalar"ın alt satırı. Açılır listeler koyu tema (`color-scheme: dark`), altın/iksir/kara kutularında renk noktası, arama sınırı + düşürme tek kutuda, 500 px'de yana taşma giderildi.
- **Hammer Jam (12:53, salt okuma):** indirimli satırın sol üst köşesinde küçük yeşil etiket, fiyat üstü çizili değil (yalnız indirimli fiyat). Eski şablon etiketten büyük ve menü sınırının dışında kalıyordu → renkle bakılıyor (indirimli ~235 piksel, değil 0; 12 sayfa gözle doğrulandı). Hammer Jam'de Crafting Station dışında her bina indirimli. Kaynak çubuğu yarı saydam: altın bir kez 44.765.341 okundu → iki okuma tutmalı.
- **Sonda şablonu iptal:** Emre "sonda şart değil, saldırı insan gibi görünsün" — yıldırım rastgele yerlere (1B).
- **BlueStacks çökmesi Vulkan'da da sürdü (13:19, yine `nvoglv64.dll`):** BlueStacks pencereyi (arayüz) OpenGL ile çiziyordu. Emre Ayarlar → Grafikler → **Arayüz oluşturucu = DirectX** yaptı (`bst.qt_renderer="Direct3D11"`); sonraki denemelerde çökme yok (gözlem sürüyor).
- **Takılma (2 kez):** easyocr ilk okumada geç yükleniyordu, scipy yüklenirken kilitlendi → `OCR_Handler.load()` bot açılışında, ADB'den önce.
- **Ölçüm (13:34, asker konmadı):** tek uzaklaştırma yetiyor, bütün köy görünüyor; kırmızı çizgi RGB ~(206, 91, 35). Bırakma yeri: kırmızı piksellerin dışbükey zarfı + ekranın %2'si dışarı (bina arkası / HUD girintisi olmaz); alt köşe asker çubuğunun altında → görünen alt kenara. Kart şablonları `assets/attacker/cards/` (0,97–1,00).
- **Saldırı betiği yazıldı, denenmedi:** `attacks/super-barbar.yaml` + `Attacker.scripted_attack` (yıldırım → 4 köşe × 15 → kuşatma → kahramanlar → yetenekler 8–12 sn → 20 sn ganimet değişmezse bitir → Return Home; savaş görüntüleri `debug/attacks/`). Panelde saldırı hâlâ kapalı.
- **İlk gerçek saldırı (13:42, Emre onayı):** 3. aramada 1 203 479 altınlı köy; yıldırım + 60 barbar + kahramanlar 23 sn'de bırakıldı (barbarlar ~15 sn); sonuç **%67, 1 yıldız**, ganimet geldi (altın +~890 000). Sorunlar: (1) kuşatma kartı "!" görünümündeydi → şablon tutmadı; ama barbarlar bitince oyun seçimi sıradaki karta geçirdiği için "artan asker" dokunuşu kuşatmayı attı, savaş sırasında bir dokunuş da klan yıldırımını attı → artan dokunuşu kaldırıldı, her aşamadan sonra kart bırakılıyor (çubuğun boş sol ucu), `siege_b` şablonu eklendi. (2) Savaş bitti ama Return Home bulunamadı → 30 sn sonra oyun kapatıldı (sonuç sayıldı). Düğmeler artık 0,6–1,1 boyutlarında aranıyor (Surrender / End Battle 1,00; Okay / Return Home yokken ≤ 0,57), bulunamazsa kör dokunuş yok; sonuç ekranında 60 sn, 1 sn'de bir görüntü.
- **13:48 BlueStacks yine kapandı:** Emre orduyu doldururken "kapatılmak zorunda" penceresi çıktı (kayıtta Android "Unexpected shutdown / Power down", döküm yok, NVIDIA değil). Sebep bulunamadı; tekrarlarsa saat + Windows kayıtları.
- **2. gerçek saldırı (13:54): Zafer, 2 yıldız, %63** — 1 055 259 altın, 737 092 iksir, 10 976 kara + %93 bonus. Klan büyüsüne dokunulmadı (kart bırakma düzeltmesi çalıştı), End Battle? → Okay ölçekli şablonla basıldı. Eksikler: Return Home eski şablonla bulunamadı → sonuç ekranından yeni şablon (`return_home.png`, sonuç ekranında 1,00, savaşta ≤ 0,49); kuşatma kartı üçüncü bir resimle geldi → artık barbarla ilk kahraman arasındaki kart sayılıyor (Emre: "barbar kralın bir yanında"). Aramada iksir 10.376.176 okundu → ganimet de iki okumayla.
- **3. gerçek saldırı (14:00): 2 yıldız, %86, köyün bütün altını (1,42 M)** — kuşatma yerinden bulundu ve atıldı, **Return Home ile kendi döndü** (uçtan uca ilk tam saldırı). Sorun: büyük köyde alt kenar asker çubuğunun arkasında, zarf orada ekran kesiminde bitiyordu → "You cannot deploy troops on the red area!", 8 barbar kaldı. Düzeltme: zarf kenarı HUD'a / ekran kenarına yakınsa (yatay 0,015, aşağı 0,045) o yönde nokta seçilmez; köşenin eksik kalan askeri diğer köşelere. 4 köy görüntüsünde 4 × 15 nokta, alt köşe yalnız görünen kenarda.
- **Ordu:** Emre orduyu kendisi dolduruyor — Quick Train gerekmiyor (Emre 01.11).
- **4. gerçek saldırı (14:06): 3 yıldız, %100** — 549 873 altın, 515 251 iksir, 9 964 kara + %100 bonus (250 000 / 250 000 / 1 600). 60 barbarın hepsi indi (kart x0, kırmızı alan uyarısı yok), kuşatma x1, 11 yıldırım, klan büyüsüne dokunulmadı, ganimet bitince 20 sn kuralına gerek kalmadan savaş bitti, Return Home ile döndü. Saldırı betiği tamam.
- **Alt köşeye asker gitmiyordu (Emre 14:08):** alt uç asker çubuğu + "Boosted" yazılarının altında → güvenli nokta yok → asker diğer köşelere kayıyordu. Artık alt köşe en sona; önce kart bırakılır, görüntü parmakla yukarı kaydırılır (0,62 → 0,36, kart seçili değilken sürükleme asker bırakmaz), çizgi yeniden bulunur, 15 barbar alt köşeye; kuşatma ve kahramanlar kaydırılmış görüntüyle. Ekran kenarında kesilen zarf kenarına da nokta yok. Ölçüm (14:09, asker konmadı): köy ~185 px kaydı, alt uç göründü, 15 nokta çizginin dışında. Canlı saldırıda denenmedi.
- **5. gerçek saldırı (14:12):** alt köşe kaydırması çalıştı ("view moved up, 15 points"). Return Home'a basıldı ama köy 3 sn'de yüklenmemişti → bot 60 sn bekleyip oyunu kapattı → düzeltildi (Return Home'dan sonra 15 sn köy beklenir; döngüde köydeyse biter). Bırakma anında **7 barbar elde** ("cannot deploy on the red area"); 10 sn sonraki görüntüde x0 — kalanları neyin bıraktığı belli değil.
- **Emre'nin geri bildirimi (14:13) — SIRADAKİ OTURUMUN İLK İŞİ:**
  1. **Kuşatma makinesine ikinci kez basılmasın** (ikinci basış içindeki askerleri erken bırakıyor / patlatıyor). Kodda kuşatma kartına tek `tap_card` var; ikinci basışın kaynağını bul (5. saldırı görüntüleri `debug/attacks/20261101_141148/`; kart deployed'da "boşalt" simgesiyle, battle_003'te gri). Kuşatma indikten sonra kartına hiç dokunma.
  2. **Kahramanlar kırmızı alana atılıyor, inmiyor, sonra kartlarına basılıp duruluyor:** her kahramandan sonra kartın üstünde yeşil can çubuğu (y ≈ 0,80) var mı bak; yoksa daha dışarıda başka noktaya bir kez daha dene; yetenek yalnız inen kahramana.
  3. **8–10 barbar elde kalıyor:** bırakma payını büyüt (şimdi zarf + %2 + 0–%1 → ~%3,5 + 0–%1,5); köşeler bitince kart boş değilse (0,4 sn bekle, taze görüntü) kartı yeniden seç, kalanları daha dışarıya tek tek bırak, her dokunuştan önce 0,25 sn bekleyip kartın boşalıp boşalmadığına bak.
  Emre: "her seferinde elle izleyemem" → hedef gözetimsiz saldırı.
- **Sonra:** paneldeki "Ana köyde saldır" ile botun kendi turunda saldırı (panel sunucusu 400 000 şartını verir; Emre orduyu kendi doldurur — ordu yoksa ne olacağı denenmedi). Sonra: basılı tutarak bırakma, sonda (isteğe bağlı), log çevirileri (yeni İngilizce satırlar panelde Türkçe değil).

## Ek: ClashFarmer + MyBot'ta olup bizde olmayanlar (01.11 araştırması)

Kaynak: clashfarmer.com ekran görüntüleri (status/army/search/attack/clan/village/remote/other.png, resimler tek tek incelendi) + MyBot `develop` dalı GUI `.au3` dosyaları ve `functions/Village/UpgradeWall.au3`. Görüntüdeki değerler varsayılan olmayabilir.

**ClashFarmer sekmeleri:** Durum (bot kaydı + saldırı kaydı tablosu) · Ordu (oyunun Quick Train tarifi 1/2/3, süper birlik etkinleştirme) · Arama (en az altın/iksir/kara iksir, yalnız dolu toplayıcılı ölü köy, VE/VEYA, eşleşmede ses, "hiç arama yapma, yalnız köyü bakımla", altın şunun altındaysa arama) · Saldırı (dalga/asker hızı 1–9, klan askerleri, kahraman yeteneği N sn sonra, N sn ganimet gelmezse bitir, saldırı yönleri KB/KD/GB/GD, 1–3 dalga, kırmızı çizgiye yakın, sürükle-bırak asker sırası) · Klan (bağış, anahtar kelimeye göre bağış, asker iste) · Köy (altın/iksir/kara iksir topla, mezar taşı, maden arabası; başka cihaz bağlanınca N sn bekle; otomatik duvar: duvar seviyesi seçimi, "önce iksir sonra altın", kalacak en az) · Uzaktan (Telegram) · Diğer (açılışta otomatik başla — kapalı, 24 saatlik mola ızgarası, günlük rastgele 25–35 saldırı sınırı).
Alt şeritte her sekmede: **Start Bot · Search Only · Close Bot**. Bot Start'a basılmadan çalışmaz.

**MyBot duvar mantığı (kodda doğrulandı):** her boş turda en sona; en az 1 boş usta; önce açık bina/kahraman/lab geliştirmelerinin maliyetini ayırır, kalandan duvar; "kaynak − duvar maliyeti ≥ en az" oldukça döngü; seçilen seviye bitince bir üst seviye; Belediye seviyesi yetmiyorsa atlar; "duvara 1 usta ayır".

**İkisinde olup planımızda olmayanlar:** asker eğitimi (hızlı eğitim/özel ordu) · süper birlik · kahraman/büyü/klan askerini bekle · güçlendirmeler (kışla, kahraman; saat ızgarası) · asker isteme/bağış · hazine toplama, engel/mücevher kutusu, sihirli eşya, başarı/görev ödülleri · klan oyunları · klan başkenti · usta üssü yıldız bonusu · arama: savunma seviyesi süzgeci, kupa aralığı, ölü köy algılama, zorba modu · SmartZap (kara iksir sondajına şimşek) · kupa düşürme · tekrar paylaşımı · Telegram olay bildirimleri + uzaktan komut · çok hesap · Android'i N saatte yeniden başlat · istatistik CSV.

## 5. oturum (01.11 öğleden sonra) — Emre'nin 14:13 geri bildirimi

- **Görüntülerden bulgu:** inen kahraman/kuşatmanın kartının üstünde yeşil can çubuğu var (y 0,795–0,815, tam canda ~850–925 yeşil piksel, inmeyende 0). 5. saldırıda "deployed" anında Warden'da çubuk yoktu (inmemiş), sonra inmiş görünüyor; 3. saldırıda üç kahramanda çubuk gecikmeli çıktı → kontrol 2,5 sn bekleyerek. Kart konumları 5 saldırıda aynı (barbar 0,103, kuşatma 0,188, kahramanlar 0,271 / 0,346 / 0,421 / 0,496).
- **Kuşatmaya ikinci basış (1):** olası kaynak — ordu planlanan dokunuştan azsa barbar kartı biter, oyun kuşatmayı seçer, artan dokunuş onu barbar noktasına atar, sonra koddaki kuşatma kartı dokunuşu = boşalt. Düzeltme: barbarda her 4 dokunuşta kart boş mu bakılır (biterse durur); kuşatma kartına dokunmadan önce can çubuğu varsa hiç dokunulmaz; kartına yalnız bir kez dokunulur.
- **Kahraman (2):** her kahramandan sonra can çubuğu beklenir; yoksa aynı kart seçiliyken %6 sonra %9 dışarıya yeniden; inmeyen kahramana yetenek basılmaz (kartına bir daha dokunulmaz). Zaten inmiş görünen kahramanın kartına bırakmak için dokunulmaz, yalnız yeteneği zamanlanır.
- **Elde kalan barbar (3):** bırakma payı %2 + 0–%1 → %3,5 + 0–%1,5. Köşelerden sonra 0,4 sn bekleyip kart boş değilse kart yeniden seçilir, görünen köşelerde %6 dışarıdaki noktalara tek tek; her dokunuştan önce 0,25 sn + kart boş mu.
- **Panel yenilendi:** Inter + JetBrains Mono, renkler `:root` değişkenlerinde, Durum'da 5 büyük kaynak kutusu, kaynak şeridi üst çubukta, Başlat birincil (çalışırken kırmızı Durdur), 500 px'de taşma yok. API / ayar adları aynı.
- **Durum:** kod derlendi, kayıtlı görüntüde can çubuğu kontrolü doğru (Warden inmemiş); **canlı saldırıda denenmedi** — Emre onayıyla 6. saldırı.
- **6. gerçek saldırı (14:36, Emre onayı): Zafer, 1 yıldız, %77** — 996 754 altın, 242 998 iksir, 1 149 kara. İlk aramada 1 275 074 altınlı köy. "deployed" görüntüsünde: barbar x0 (60'ın hepsi indi, kalan barbar adımına gerek olmadı), kuşatma sahada ve kartı "boşalt" simgesinde kaldı (ikinci dokunuş yok, sonuçta x1), 4 kahramanın hepsi ilk denemede indi (yeniden deneme satırı yok). Sonuç ekranına gelindi (result_00).
- **14:37:45 BlueStacks yine çöktü** (Return Home'a basılmadan, sonuç ekranında): döküm `HD-Player.exe_2026-11-01_14-37-45.dmp`, yine `nvoglv64.dll+0x94a750` — ayarlar Vulkan + arayüz Direct3D11 olduğu halde. Saldırı sayıldı, kayıp yok. Bot ADB'yi yeniden aradı, BlueStacks'i kendisi açmadı (test betiği durduruldu).
- **Emre 1C 2A (14:40):** çökme için ayar değişmiyor, gözleniyor. **BlueStacks kendiliğinden kapanırsa bot yeniden açar:** `utils.ensure_emulator()` `start_coc` başında (tur, Köyü oku, Yalnız ara hepsi): süreç yoksa BlueStacks'i başlatır, ADB'ye bağlanır, `sys.boot_completed` 120 sn bekler; olmazsa tur "hata" ile biter, sonraki turda yeniden. Canlı denendi (14:42, çökmüş BlueStacks): 29 sn'de açıldı ve bağlandı, açıkken ikinci çağrı hiçbir şey yapmadı. Saldırı/BlueStacks kayıt satırları panelde Türkçe (`log_translate.py`).
- **"Beklenmeyen kapanma" (14:45, Emre botu bat ile açınca):** sebep çökme değil — bot açılışta BlueStacks'i yeniden başlatıyordu (`Emulator_Manager.init` → `restart` → `stop` = `adb shell reboot -p`); Android kapanınca BlueStacks "FATAL: Unexpected shutdown" penceresini açıp tıklanana kadar bekliyor (`X:\BlueStacks_nxt\Logs\Player.log` 14:45:32 "reboot: Power down"). 13:48'deki pencere de büyük olasılıkla bu (betik çıkışında `stop`). Düzeltme: açılışta `start()` (açık BlueStacks'e dokunulmaz); `stop()` kapanmayı 10 sn bekler, pencere açık kalırsa süreci sonlandırır.
- **Geliştirme sekmesi yenilendi (Emre 1A 2A 3A 4A, 14:55):** Binalar / Laboratuvar / Evcil hayvanlar anahtarı açılınca altında simgeli seçim alanı: tıklama sırası = öncelik (numara rozeti, ← → ile yer değiştirir), arama kutusu; binalarda "Sırala / Hariç tut" kipi (home.excluded); laboratuvarda usta üssü + süper askerler gizli ("Hepsini göster"). Veri biçimi aynı (her seçim ayrı seviye: [["Inferno Tower"],["X-Bow"]]; eski çok elemanlı satırlar ilk açılışta sırayla düzleşir) → bot kodu değişmedi. Simgeler ClashKingAssets'ten bir kez `data/icons/`a (gitignore, açık depoya girmez; 188 simge, 3,2 MB), `/icons/` adresinden. Eski ana köy öncelik kartları ve "Hariç tutulacak binalar" kartı kalktı.
- **Duvar seviyeleri:** panelde "Hangi seviyeler" 1–18 (`walls.levels`, boş = her seviye). **Bot tarafı henüz yok** — seçili duvarın seviyesinin ekranda nerede yazdığı ölçülecek (betik scratchpad `duvar_olc.py`, Geliştir'e basmaz).
- **Duvar / çırak / asistan artık tek başına çalışır:** `coc_bot.py` geliştirme adımını Binalar + Lab + Pet kapalı olsa da duvar açıksa ya da çırak / asistan açıksa çalıştırır; Başlat özetindeki "çalışmaz" uyarısı kalktı.
- **Bot açılmıyordu (15:10, `psutil.AccessDenied pid=19772`):** önbellekteki BlueStacks pid'i kapanmış bir BlueStacks'ten kalmıştı, Windows numarayı korumalı bir sürece vermişti → `wake()` erişim hatasıyla açılışı düşürdü. Düzeltme: `_Emulator_Manager.pid` numaranın süreç adını doğrular (BlueStacks `HD-Player.exe`), uymazsa yok sayar ve çalışan HD-Player'ı adından bulur; `wake` / `sleep` AccessDenied'ı yutar. Salt okuma denemesi: eski pid yok sayıldı, BlueStacks kapalı görüldü.

## Klan kalesi doldurma — Emre'nin kararları (01.11, 15:15)

- **1A:** her tur başında (saldırıdan önce) klan kalesi boşsa: **Klan Kalesi Pastası etkinse ücretsiz doldur**, değilse **klana istek at**.
- **2:** saldırı değişmez — klan askerleri kuşatma makinesinin içinde gidiyor, makine patlayınca iniyor (yani kale zaten kullanılıyor, her saldırıdan sonra boşalıyor).
- **3A:** pastayı Emre kendisi etkinleştirir (1 saat); bot yalnız etkin olduğu sürede ücretsiz doldurur, pastayı kendisi harcamaz.
- **Sırada:** bot kapalıyken ölçüm — ordu ekranı, klan kalesi bölümü, "Request" düğmesi, pasta etkinken doldurma düğmesi (hiçbirine basılmaz). Aynı ölçümde duvar seviyesi (`duvar_olc.py`). Sonra kod + Emre onayıyla canlı tur.
- **Pasta saati (Emre 1A):** pasta etkinken turlar arası bekleme yok (saldır → kaleyi bedava doldur → yeniden saldır); pasta bitince normal bekleme. Emre 1 inşaatçıyı hep boşta tutacak (panel "Boşta bırakılacak usta" = 1).
- **Ölçüm (15:24–15:38, Emre botu kapattı):**
  - **Duvar:** seçili duvarın üstünde "Wall (Level 12)" yazısı (yeri duvara göre değişir; 0,15–0,80 × 0,45–0,72 bölgesinde OCR, ")" bazen "1" okunuyor → "Level 131" = 13). Menüde 675 000 = 12. seviye (123 duvar), 900 000 = 13. seviye. Seçili duvarda **"Upgrade More"** düğmesi var (aynı seviyeden birkaç duvar birden — hız için sonra bakılacak).
  - **Duvar seviyesi kodu:** `wall_upgrade` panel seviyeleri seçiliyse duvar satırlarına ucuzdan pahalıya dokunur, seviyeyi okur (3 deneme × 0,7 sn — görüntü duvara kayarken okunmuyordu), seçili değilse geçer; maliyet → seviye oturum içinde hatırlanır. Deneme kipinde canlı: seviye 13 seçili → 12'yi geçti, 13'ü iksirle seçti, onay penceresinde durdu; kaynaklar aynı.
  - **Klan kalesi:** köydeki "Request" yazısı tıklanmıyor (dokunuş önündeki duvara gitti). Battle → Find a Match → ordu penceresinde klan kalesi bölümü (45/45 · 3/3 · 1/1, şu an dolu) ve sağında iki yeşil düğme: **mücevherli doldurma (ASLA basılmayacak)** ve kale + "+" = Request. Kale boşken istek penceresi ve pasta etkinken ücretsiz doldurma henüz görülmedi → bir saldırıdan sonra ölçülecek. Köyde Android Geri iki kez = "Confirm Exit" penceresi (Geri ile kapanır).
  - Kaynak okuma bir kez mücevheri 7.612 okudu (ekranda 1 612).
- **Çok hesap (köy 1 / köy 2):** konuşuldu, Emre vazgeçti (01.11 15:45). Seçenekler kayıtta kalsın: tek BlueStacks + Supercell ID ile geçiş (MyBot gibi, köy başına ayrı ayar) ya da ikinci BlueStacks kopyası.
- **Duvar onaylanmıyordu (17:27, "Walls: confirm button not found"):** `_click_home_confirm` `use_cached=True` ile arıyordu → onay penceresi açılmadan önceki görüntüye 5 sn boyunca bakıp Confirm'ü hiç görmüyordu (bina onayını da etkiliyordu). Taze görüntüyle aranıyor. Hammer Jam'de Confirm üstü çizili fiyatlı (1 500 000 → 675 000) ama resim yine tutuyor (kayıtlı ekranda denendi). Emre'nin "oyun kapandı" dediği büyük olasılıkla tur sonu kapatma (Genel → tur bitince oyunu kapat).
- **Hızlı duvar (Emre 17:30, "+1 tuşu var, ganimete göre bassın"):**
  - Seçili duvarda "Upgrade More" → düğmeler "-1 Remove Wall" · "+10 Add Wall" · "+1 Add Wall" (+1 Upgrade More'un yerinde, +10 bir düğme solunda x−0,108, −1 iki düğme solunda); başlık "Wall (Level 12) x N", Upgrade düğmeleri N × fiyat. Şablon `assets/upgrader/upgrade_more.png` (yalnız yazı, duvar resmi seviyeye göre değişiyor).
  - `wall_upgrade(max_walls)`: kaynak − kalacak en az ile kaç duvar alınabiliyorsa (ve tur sınırı) o kadar ekler, başlıktaki N okunur (OCR 1'i I / l / T okuyor → düzeltiliyor), N × fiyat sınırı aşmıyorsa tek onayla hepsi. `run_walls` "Tur başına en fazla duvar"ı artık duvar adedi sayar; panel istatistiği adet kadar artar.
  - Seçim artık sayfa sayfa: duvar satırı görüldüğü sayfada dokunulur, menü sonuna kadar taranmaz ve kapatılıp yeniden açılmaz (yeniden açma filtre penceresini açmıştı); seçim 70+ sn → 30 sn.
  - Deneme kipinde canlı (17:40): seviye 12, en fazla 12 → iksir 6,6 M − 300 k ile **9 duvar** seçildi, "x 9", 6 075 000; onaylanmadı, kaynaklar aynı.
- **17:41 yine çökme:** Emre BlueStacks'i kapattı (17:41:23 "Close clicked"), bot açtı (17:41:36), açılıştan 18 sn sonra `nvoglv64.dll+0x94a691` ile çöktü ("VM is about to shut down due to an unhandled exception"). Bugün 5. NVIDIA OpenGL çökmesi (12:37, 13:19, 14:37, 14:56, 17:41). Bot takılı kaldı çünkü `check()` süreç yokken ADB'ye sordu ve ölü emülatör "connected" dedi → artık BlueStacks süreci adından bulunamazsa kapalı sayılır, `ensure_emulator` yeniden açar.
- **Toplu duvar onaylanmıyordu (17:46):** birden çok duvarda oyun Confirm penceresi yerine "Upgrade Walls — Do you really want to upgrade the selected Walls for 3375000 Elixir? Cancel / Okay" soruyor. `_click_walls_confirm`: Okay = bölgedeki en büyük yeşil düğme + OCR "ok"; aynı yerdeki Okay "Confirm Exit" (oyundan çık) penceresinde de var → başlıkta "upgrade" olmalı, "confirm" olmamalı (OCR "Upgrade Walis" / "Confirm Exxit"). Kayıtlı ekranlarda: duvar penceresi bas, çıkış penceresi basma, köy basma. 17:47 "oyun kapandı" = tur sonu kapatma, yeni döküm yok.
- **Saldır → duvar → saldır (Emre 17:58):** saldırı açıksa tur sırası geliştirme (duvarsız) → saldırı → duvar (ganimetle); saldırı kapalıysa duvar eskisi gibi geliştirmenin sonunda. **Hata:** paneldeki "Kontrol aralığı" hiç kullanılmıyordu (`next_check_delay` hep `configs.CHECK_INTERVAL`) → artık panel değeri; 0 = beklemeden yeni tur (panelde en az 0).
- **Çökme deseni (6 döküm, hepsi `nvoglv64.dll`):** 12:37 ve 13:19 oyun açıldıktan hemen sonra, 14:37 saldırı sonucu, **14:56 ve 17:53 tam "Stopping CoC" (tur sonu oyun kapatma) saniyesinde**, 17:41 BlueStacks açılışı → oyunun açılıp kapanması tetikliyor. Öneri: "Tur sonunda oyunu kapat" kapalı + aralık 0 (oyun hep açık). 17:51'de bot çökmüş BlueStacks'i kendisi açtı ("Emulator back") — toparlama çalışıyor.
- **İlk gerçek toplu duvar (17:57): 5 duvar** iksirle (6 605 917 → 3 230 917), "Upgraded 5 wall(s)". Emre: yalnız iksirle → tur sınırı 5 iksirle doluyordu, altın sırası gelmiyordu; artık fazlası çok olan kaynak önce (altın dolu → altın). Oyun kapanması = "Tur sonunda oyunu kapat" hâlâ açık.
- **Duvar saldırıdan önce de (Emre 18:05, "depo fullken boş"):** tur = geliştirme + duvar → saldırı → duvar. Bilinen en ucuz duvara (oturumda görülen maliyetler) ne altın ne iksir yetmiyorsa menü hiç açılmaz (~30 sn kazanç).
- **Ölü köy:** Emre vazgeçti (01.11 18:10) — "saldırsın yeter". Yapılmayacak.
- **Duvar her N saldırıda bir (Emre 18:15, "3 saldırı 1 duvar"):** `walls.every_attacks` (varsayılan 3, panel Geliştirme → Duvar "Kaç saldırıda bir duvar"). Saldırı açıkken: duvar → N saldırı → duvar …; bot açılışta önce duvar (depo dolu olabilir). Duvar hep saldırıdan önce; saldırı sonrası ayrı duvar adımı kalktı. Sayaç bot açıkken bellekte.
- **Saldırıyı erken bitir (Emre 18:20, "ganimeti 1 dakikada alıyoruz"):** `attack.end_after` (varsayılan 60 sn, panel Saldırı → "Saldırıyı bitir, saniye", 0 = sonuna kadar). Askerler indikten (savaş döngüsü başı) bu kadar sonra, yetenekler basılmışsa Surrender → Okay; "ganimet 20 sn değişmezse" kuralı da duruyor.
- **18:05–18:15 canlı (yeni kod):** 1. saldırı askerler bitti ("Leftover troops: 11 more taps, card empty" — kalan barbar adımı ilk kez çalıştı), 18:08 BlueStacks çöktü; 2. saldırı 18:12 çöktü (ikisi de `nvoglv64.dll`, saldırı sırasında). Bot hata sonrası 5 dk bekliyordu → 60 sn. 18:10 duvar: 675 000'lik duvar "11" okundu → seviye 12 bulunamadı ve oturum boyunca atlanacaktı → seviye iki okuma aynıysa sayılır, yalnız onaylanan hatırlanır, onaylı seviyede yeniden okunmaz.
- **Önce düşük seviye (Emre 18:25):** seviye seçili değilken ilk görülen duvar seçiliyordu → menüde 13. seviye (900 000) 12'den (675 000) önce geldiği için yüksek seviye kasılıyordu. `_select_wall` artık önce bütün duvar satırlarını okur (sayfasıyla), sonra en ucuzdan (= en düşük seviye) başlayıp o sayfaya geri kaydırır (`_menu_swipe_back`), satırı maliyetle yeniden bulur. **Canlıda denenmedi** (bot çalışıyordu).
- **Grafik:** bu BlueStacks sürümünde Grafik oluşturucu yalnız "Vulkan ve OpenGL" / "Yalnızca OpenGL" — DirectX yok (önceki öneri yanlıştı). İşlemci Ryzen 7 5700X3D, yerleşik grafik yok → "Özel GPU" anahtarı çözüm değil. NVIDIA sürücüsü 610.88 (32.0.16.1088); sıradaki çare sürücü (temiz kurulum / önceki sürüm).
- **Saldırı sadeleşti (Emre 18:35):** yıldırım kalktı (`spells` yaml'da yorum satırı; 4A kararı değişti). Royal Champion (= `hero_2`, kart resimlerinden: hero_1 King, hero_2 Royal Champion, hero_3 Warden, hero_4 Minion Prince) atılır atılmaz kartına bir daha basılır (`heroes.ability_now`), diğerleri 8–12 sn. Sıra: barbarlar → kuşatma → kahramanlar → 60 sn sonra bitir. Çökünce BlueStacks'i bot açıyor (Emre: sürücüye dokunma, "önemli değil").
- **18:26 canlı (yeni kod):** duvar adımı altınla 5 duvar (11 027 827 → 7 652 827), sonra saldırı; Royal Champion yeteneği atılır atılmaz basıldı ("hero_2: ability used right after the drop"). 5'te durması ayar yüzünden: "Tur başına en fazla duvar" o anda 5'ti, Emre 40'ı 18:26:16'da kaydetti (duvar 18:26:13'te bitmişti). **Düzeltme (önceki not yanlış):** "Kontrol aralığı" panelden zaten uygulanıyordu (`Settings_Handler.apply` → `configs.CHECK_INTERVAL`); `next_check_delay` değişikliği zararsız ama gereksizdi. 18:23'te kuşatma + 3 kahraman "did not land" ve ardından BlueStacks çökmesi.
- **Önce altın, sonra iksir (Emre 18:45):** `_wall_payment` sabit sıra: altın en az sınırına kadar, sonra iksir (fazlası çok olan kuralı kalktı). Oyunsuz döngü denemesi (13,75 M / 10,5 M, en az 100 k, sınır 40): altın 20 duvar → iksir 15 duvar. Emre isteğiyle `walls.every_attacks = 1` (duvar her saldırıdan önce) data/main.json'a yazıldı.
- **60 sn bitirme çalışmıyor gibiydi (Emre 18:50):** sayaç askerler BİTTİKTEN sonra başlıyordu; asker atmak ~25–30 sn → 18:26 saldırısı 67. sn'de kendiliğinden bitti, sayaç dolmadı; 18:33'te 51. sn'de BlueStacks çöktü. Artık sayaç ilk asker atılırken başlar (`battle_start`), süre dolunca ganimet okunmadan (her okuma ~3 sn) bitirilir. Duvar sayısı ("x N") okunamadı (18:32, "count unclear") → 3 deneme.
- **Çökme sonrası dakikalarca "Emülatöre bağlanılamadı" (18:34–18:36):** her ADB çağrısı 60 sn bağlanmayı deniyordu, çökmüş BlueStacks'i ancak hata tur döngüsüne çıkınca açıyordu. Artık `ADB_Manager.connect` ilk başarısızlıkta BlueStacks süreci yoksa onu hemen yeniden açar ve 120 sn bekler; bekleme satırları INFO ("Emülatör bekleniyor…"), hata yalnız vazgeçince. Canlı çökmede denenmedi.
- **Duvar ganimet eşiğiyle (Emre 19:00, "5 M altın / 5 M iksir olunca"):** `walls.start_gold` / `walls.start_elixir` (panel Geliştirme → Duvar "Duvara başla: altın ≥ / iksir ≥", 0 = kapalı). Saldırı açıkken her saldırıdan önce: altın YA DA iksir eşiğe ulaştıysa duvar (önce altın, sonra iksir, en aza kadar), değilse doğrudan saldırı ("Walls wait…"). İkisi 0 ise "kaç saldırıda bir" geçerli. YA DA seçildi: biri dolarken diğerini beklemek dolan deponun ganimetini harcatır.
- **30 barbar elde kaldı (18:47, Noraima köyü):** bırakma sınırı "kırmızı piksellerin dışbükey zarfı" — normal köylerde bu zarf binalardaki kırmızı ayrıntılardan köyün çevresini veriyor, ama etkinlik süslemeli köyde (gökkuşağı şeritleri, kırmızı halılar) zarf ekran dışına taştı → sağ ve alt kenarda 0 nokta, kalan adımı 12 noktayla bitti. Kalan adımı güçlendirildi: bütün görünen kenarlar (spread 60°), pay %6 → %9 → %12, kart boşalana kadar en fazla 60 dokunuş. Denenen süzgeçler (kalın kırmızıyı at, en büyük parça, yön başına %95) normal köyleri bozdu → bırakılmadı. Önerilen sağlam yol: kart seçiliyken köy ortasına (binaya) bir dokunuş → oyun gerçek kırmızı sınırı yakar → önceki/sonraki görüntü farkı = yalnız sınır (süsleme farkta kaybolur). Canlı ölçüm gerekiyor.

## DEVİR 01.11 19:00 — Emre'nin elle saldırı kaydı (yeni sohbette devam)

- **Kayıt sürüyor:** `X:\CoC\kayit\20261101_185832\` — `olaylar.txt` (`getevent -lt`, bütün aygıtlar; dokunuş = "BlueStacks Virtual Touch" /dev/input/event4, ABS_MT_POSITION_X/Y 0–32767 → 1920×1080), `saat.txt` (bilgisayar saati ↔ cihaz açılış saniyesi; BlueStacks yeniden açılınca yeni satır, `### getevent basladi` işareti), `ekran/<bilgisayar saati>.jpg` (1,5 sn'de bir, 960×540). Araç `X:\CoC\araclar\saldiri_kaydi.py`, sohbetten bağımsız süreç; **durdurmak: `X:\CoC\kayit\DUR` dosyası oluştur** (araç kapanır, DUR'u siler; çıktı `X:\CoC\kayit\arac.log`).
- **Emre 8–10 saldırı yapıyor**, ordu: 60 süper barbar, kuşatma, 4 kahraman (hero_1 King, hero_2 Royal Champion, hero_3 Warden, hero_4 Minion Prince), **yıldırım yerine yarasa büyüsü** (kart şablonu yok → kayıttan çıkar). Hedef: "köye yayarak" saldırı düzenini çıkar (kenar dağılımı, dokunuş aralığı, sıra, kuşatma/kahraman/büyü yeri ve zamanı, yetenek zamanları) → `attacks/` yeni stil + kod; Emre: "hep öyle saldırsın".
- **Sonra:** kırmızı sınırı yaktırma ölçümü (Emre 1A): barbar kartı seçiliyken köy ortasındaki binaya bir dokunuş → oyun gerçek kırmızı sınırı gösterir → önceki/sonraki görüntü farkı = sınır (süslemeli köylerde zarf ekran dışına taşıyordu). Emre onayıyla bir saldırıda.
- Bot ayarları (data/main.json): duvar açık, en az 100 k / 100 k, tur başına 40, every_attacks 1 (Emre başlama eşiklerini panelden girecek, ör. 5 M / 5 M), saldırı açık, end_after 60, aralık 0, oyunu kapatma kapalı.
- **Kayıt BİTTİ (19:27, Claude durdurdu):** `X:\CoC\kayit\20261101_185832\` — 1 082 görüntü, 53 323 dokunuş konumu olayı, 174 MB. `notlar.txt` = Emre'nin saldırı başı/sonu saatleri: 9 saldırı 19:15–19:27 (4.'de ilk köy geçildi); öncesinde yarım saldırılar, BlueStacks 19:01:52 ve 19:13:33'te çöktü; 19:21 elle 20 duvar (10 altın + 10 iksir). Emre ölü olmayan köyleri geçiyor → köy seçimi de kayıttan incelenecek. NVIDIA App: BlueStacks için güç = maksimum performans, düşük gecikme kapalı (Emre); iş parçacıklı optimizasyon bulunamadı.

## 7. oturum (01.11 akşam) — kayıttan "yayma" stili, ilk canlı deneme

- **Kayıt incelemesi:** 10 saldırı (notlarda 9; 19:19'daki eksik), dokunuşlar `getevent` → vuruş (bas–kaldır). Bulgular `docs/SALDIRI-STILI.md` "Stil 2 — Yayma": Champion tek başına + yetenek hemen; barbarlar **basılı sürükleyerek** (iki yarım ya da tek tur, ~7,3 barbar/sn); kuşatma + King/Queen/Warden + 11 yarasa aynı noktaya; yetenek süreleri; 29–65 sn'de teslim. Köy seçimi ganimetle (saldırılan en zayıf 755 k / 624 k, geçilen en iyi 681 k / 104 k) → **panel şartı 700 000 / 600 000** (Emre 3A; kara iksir 400 aynı).
- **Ordu değişmişti:** Minion Prince → Archer Queen, yıldırım → yarasa. **Kartlar küçülmüş** (çubukta boş yuvalar, ~0,8 ölçek): `_find_cards` artık 0,75–1,05 ölçekte arıyor (en iyi üç kartın toplamıyla ölçek seçilir), kart ortası / can çubuğu (0,8'de y 0,837–0,845) / gri kart bandı ölçeğe göre. Kart resimleri adlandırıldı: king, queen (yeni), warden, champion, minion_prince, bat (yeni; kayıttaki 10 arama ekranının ortalamasından). Canlıda 7 kartın 7'si bulundu.
- **Kod:** `Input_Handler.drag_path` (minitouch ile basılı çok noktalı yol, 60 ms adım — her publish 50 ms uyuyor), `Attacker._deploy_spread` + `attacks/yayma.yaml` (ana köy saldırısı artık bu stil; eski köşe stili `_deploy_corners`, yaml'da `mode` yoksa), `_leftover_troops` ortak, sürüklemede ikinci iş parçacığı kartı izler (boşalınca parmak kalkar), savaş sonu `after_factor` 0,6–1,05.
- **Kırmızı sınır ölçümü (1A) — ÇALIŞMADI (19:57):** keşif ekranında barbar seçiliyken köy ortasına dokunmak sınırı yakmıyor, dokunulan binanın bilgisini (Wizard Tower menzilleri) açıyor; kart seçili karede de sınır çizilmiyor; Emre'nin kaydında hiçbir karede sınır yok. Adım koddan çıkarıldı. 1 köyde yapılabildi, sonra BlueStacks çöktü (19:57:19 dökümü; bugün 19:01, 19:13, 19:36, 19:57).
- **1. canlı saldırı (20:03, Emre onayı):** 3. aramada 899 k / 1,26 M. Champion + yetenek ✅, 11 yarasa ✅, ama **yalnız 11 barbar indi** (x49), kuşatma ve 3 kahraman inmedi, %22, 51. sn'de teslim; +155 k altın / +364 k iksir. **Sebep:** sürükleme sırasında görüntü kaydı (start → deployed 72 px sola, 140 px aşağı; `_view_shift` ile ölçüldü) → sonraki bütün noktalar eski görüntüye göre köyün içine gitti (60 kalan dokunuşu boşa). Olası tetikleyici: sürükleme kırmızı alanda / sınıra yakın başladı (Emre hep ekran kenarından başlıyor).
- **Düzeltme (canlıda denenmedi):** sürükleme köyden uzakta başlar (ilk %15'te +%5 pay), her sürüklemeden önce ve sonra ve kahramanlardan önce taze kare → kayma kaydı ("View moved …") + sınır ve noktalar yeniden; sürükleme sırasında kareler `debug/attacks/<saat>/hold_*.png` (oyunun ne yaptığı görülsün).
- **Betik notu:** betikten çalışırken `Settings_Handler.load()` şart (yoksa bütün şartlar 0 → ilk köye saldırır; 20:01 denemesi bu yüzden aramadan durduruldu). Betiği durdurmak onun açtığı BlueStacks'i de kapatır.

## DEVİR 01.11 20:30

- Sırada: Emre onayıyla 3. canlı saldırı (başta sabit basılı tutma denenecek) (scratchpad `saldiri_yayma.py`: parse_args → OCR → init_instance → ensure_emulator → start_coc → Settings_Handler.load → search → scripted_attack("yayma")). Bakılacak: "View moved" satırı, `hold_*.png` karelerinde barbarlar sürüklemede iniyor mu, kalan dokunuşlar kartı boşaltıyor mu, kahramanlar iniyor mu.
- Kayma sürerse seçenekler: sürüklemeyi tam ekran kenarından başlatmak (Emre gibi x ≈ 0,05–0,1), ya da önce kısa basılı tutup (tek nokta, kayma olmaz) sonra yürümek.
- Sınır tahmini hâlâ binalardaki kırmızılardan (bazı köylerde yol içeri giriyor). Sınırı bulmanın başka yolu düşünülecek (ör. çimen rengi dışındaki her şey = bina).
- **2. canlı saldırı (20:13, Emre 1A): 2 yıldız, %93**, +954 k altın / +750 k iksir (977 k / 973 k'lık köy, 2. arama). Kuşatma, King, Warden indi; 11 yarasa alt kenara. Sürüklemede yine **hiç barbar inmedi**: `hold_*.png` karelerinde 7,5 sn boyunca kart x60, köy ekranda kayıyor ("View moved -67, -44"). Barbarları kalan adımının 60 dokunuşu indirdi (46 indi, 14 elde).
- **Asıl sebep (kayıttan doğrulandı):** Emre'nin asker bırakan 23 sürüklemesinin hepsinde parmak önce **0,36–0,53 sn kıpırdamadan** duruyor, sonra yürüyor; hemen kıpırdayan sürüklemeler (19:03) kamera kaydırması. Botunki anında yürüyordu. **Düzeltme:** `drag_path(hold_start=…)`, yaml `hold_still: [0.35, 0.55]`. Canlıda denenmedi.
- **Pay büyütüldü (Emre 20:20, "hala dışlarıya atamıyorsun"):** sürükleme payı %3–4,5 → %5–7, kahraman/kuşatma noktası %3,5 → %5,5 (sınır binalardaki kırmızılardan dar tahmin ediliyor).
- **3. canlı saldırı (20:22, Emre 1A): 2 yıldız, %96, sürükleme ÇALIŞTI.** 1,6 M / 1,6 M'lik köy (2. arama), +1,38 M altın / +1,47 M iksir. Başta sabit basılı tutmayla tek tur: `hold_*.png`'de kart x60 → x45 → x25 → boş, görüntü kayması yok; kalan 10 dokunuşla kart boşaldı. Champion (sol, yetenek hemen), Queen (yetenek hemen), kuşatma, King, Warden sağdan indi, 11 yarasa sağa; 55. sn'de teslim.
- **"Beklenmeyen kapanma" penceresi (20:24) çökme değil:** deneme betiği bitince botun çıkış işleyicisi (`Exit_Handler` → emülatör `stop` → `reboot -p`) Android'i kapattı (Player.log 20:24:11 "Power down", döküm yok). Betik artık bunu kaldırıyor. Botun kendisi kapanırken de aynısını yapar (upstream davranışı) — değiştirilip değiştirilmeyeceği açık.
- **Sırada:** paneldeki "Ana köyde saldır" ile botun kendi turunda yayma stili (gözetimsiz); sınırı daha iyi bulma (çimen dışı = bina) isteğe bağlı.
- **4. canlı saldırı (20:30, botun kendi turu, panelden Başlat): tutmadı.** Sürüklemede kart 60 → 53, "You cannot deploy troops on the red area!" → sınır tahmini köyün içine giriyor. 3. saldırının tutması şanstı.
- **Emre'nin yeni kayıtları (20:33 ve 20:38, `X:\CoC\kayit\20261101_203309`, `…_203803`):** sürüklemeler kırmızı çizgiye yapışmıyor, haritanın dış çimen kuşağından geniş yaylarla gidiyor (ekranın en sol kenarından x 0,008 başlıyor); 1. saldırıda ortadan görüntüyü yukarı kaydırıp alt yarıyı ikinci yayla bitiriyor. 20:38'de **W / S** (BlueStacks: ortadan (0,52, 0,51) kısa dikey kaydırma): önce görüntüyü yukarı it → alt kenarı sürükle, aşağı indir → üstü sürükle. Kayıt aracı artık aralık alır (`saldiri_kaydi.py 0.5`; ekran alma ~2 sn sürüyor, gerçek aralık ~2 sn).
- **Kod (canlıda tam denenmedi):** sınır tahmini yerine **Emre'nin yolu**: iki kayıttaki 27 sürüklemenin ekran merkezinden (0,48, 0,47) 15° dilimlerde ortası (`EMRE_MID`: kahraman noktası, kalan barbarlar) ve dış çeyreği (`EMRE_OUTER`: sürükleme). Görüntü kayarsa halkalar ölçülen kaymayla taşınır. Kuru çalıştırmada 4 köyde yol köyün dışında. **`pan` seçeneği** (yaml, varsayılan kapalı): görüntü %30 yukarı → alt yarı → geri → üst yarı.
- **20:43 deneme (W/S'siz + W/S'li iki saldırı, Emre isteği):** 1. saldırıda sürükleme sırasında BlueStacks çöktü (20:43:21, döküm; 20:38:50'de de Emre'nin saldırısından sonra çökmüştü — bugün 6 çökme). Saldırı yarım kaldı, W/S'liye geçilmedi; sonuç görülemedi.

## DEVİR 01.11 20:50

- Sırada: Emre onayıyla yeniden iki deneme (`saldiri_yayma.py YALIN PAN`) → Emre hangisinin sağlıklı olduğuna karar verecek; sonra panelden botun kendi turu (duvar şu an kapalı, Emre açacak).
- BlueStacks çökmeleri (NVIDIA OpenGL) sıklaştı: 19:01, 19:13, 19:36, 19:57, 20:38, 20:43. Sürücü kararı Emre'de (önceden "dokunma" dedi).
- **Karşılaştırma (20:49–20:53, Emre 1A; Emre'nin yolu ile):**
  - **W/S'siz:** 1,55 M / 1,08 M'lik köy; sürükleme 7,9 sn, kalan 15 dokunuşla kart boş; kuşatma, King, Queen, Warden indi, yarasa atıldı. **1 yıldız %68**, +1,18 M altın / +0,68 M iksir.
  - **W/S'li:** görüntü −201 px (alt görünür) → alt yarı, +324 px → üst yarı; sürükleme 7,4 sn, kalan 12 dokunuş, kart boş; barbarlar + Champion + yarasa ile %52 (1 yıldız). **Kuşatma ve 3 kahraman inmedi:** geri kaydırma fazla geldi, alt kenar asker çubuğunun arkasında kaldı ve nokta seçimi görünmeyen kenarda eski noktaya düşüyordu → düzeltildi (görünmeyen kenarda başka görünen kenar). +672 k altın / +881 k iksir. Teslim penceresinde Okay bulunamadı, savaş kendiliğinden bitti.
  - "Find a Match" bulma hatası düzeltildi (resim arama sonucu boş satırlarla karışık gelince çöküyordu). 20:47 "Unable to attack Village! Try again later" = çöken saldırı sunucuda bitmemişti; birkaç dakika sonra düzeldi.
- **Emre 20:55 (1C 2A + geri bildirim):** W/S saldırıların %40'ında (`pan: 0.4`). "Köyün içine bırakıyorsun" → sürükleme dış halkanın 0–%3 dışında, kahraman noktası ve kalan barbarlar da dış halkada (orta halka bırakıldı). "Çok yavaş" → akış barbarlar → Champion + yetenek → kuşatma → King/Queen/Warden aynı noktaya → yarasa, can çubuğu beklenmeden (`quick`); inmeyenler en sonda bir kez yeniden, daha dışarıdan. Kart → saha 0,15–0,35 sn, kartlar arası 0,25–0,5 sn; kalan barbarlarda bekleme 0,25 → 0,05 sn (her dokunuştan önce kart yine kontrol: boşalınca sıradaki kuşatmayı bırakmasın). Sırada: panelden botun kendi turu.
- **Botun kendi turu (21:00, Emre Başlat; duvarı Emre panelden açtı: 3 M / 3 M eşik, 3 saldırıda bir):** önce 18 duvar (3 altın, 15 iksir). 1. tur aramada "Village did not load" (sebep görülmedi, tur hata verip yeniden). 2. tur 21:05: 8. aramada 2,32 M / 2,21 M'lik köy, **W/S'li**; sürükleme 7,7 sn, kalan 21 dokunuş, her şey indi; **1 yıldız %70, +2,19 M altın / +2,19 M iksir**. Emre: "inanılmaz saldırdı".
- **21:07 2. bot saldırısı:** 2 yıldız %86, +1,06 M / +0,6 M (ilk yarımda görüntü kaydı, kalan 38 dokunuş). **21:09 3. bot saldırısı bozuk:** sürüklemede kart x60, savaş başlamadı bile ("Next" duruyor) — 20:55'teki "daha dışarı" (dış halka + %0–3 + başlangıçta +%3) başlangıcı **haritanın dışına** (su / orman) attı; oyun harita dışında başlayan basışı yok sayıyor, bütün sürükleme boşa. Kahraman noktası da dışarıda, "daha dışarı" yeniden deneme daha da dışarı → kuşatma + 3 kahraman inmedi. **Düzeltme:** sürükleme dış halkanın %0–2,5 içi, başlangıçta ek pay yok; kahraman noktası ve kalan barbarlar orta halka + %3,5 (orta ile dış arası); inmeyince önce içeri (−%2,5) sonra dışarı (+%3). Kuru çalıştırmada 4 köyde başlangıç çimende.
- **Emre 21:17: "bu saldırı daha iyi"** (dış kenardan giden 0b9ca71 sürümü). O görünüm geri: sürükleme dış halkanın %0–3 dışında, ama **ilk noktası %3 içeride** (ilk %15'te açılır) → basış hep haritada başlar; kahraman noktası dış halka + %1, inmezse önce içeri (−%2,5) sonra dışarı; kalan barbarlar orta halka + %1,5–5,5 (dışta 60 dokunuş boşa gidiyordu). Kuru çalıştırmada 4 bot köyünde başlangıç çimende.
- **21:12–21:25 eski kodla (0b9ca71) bot turları:** 4. saldırı kalan 60 dokunuş boşa; 5. kalan 55 dokunuş; 6. kahramanlar ikinci denemede; 7. iyi; 8. sürükleme 11 barbar, kalan 49 inmedi (Emre gördü) — hepsi harita dışı başlangıç / harita dışı kalan dokunuşlar. Arada duvar turları (20 duvar).
- **21:25 Emre botu af91b57 ile yeniden açtı. 21:27 ilk saldırı: 2 yıldız %95**, köydeki altının tamamı (+710 k) ve iksirin neredeyse tamamı (+725 k); sürükleme 7,9 sn, kalan 18 dokunuş, kart boş, kahramanların hepsi indi. Emre: "harikaydı".

## DEVİR 01.11 21:30

- Yayma stili botun kendi turunda çalışıyor (af91b57). Ayarlar: arama 700 k / 600 k / 400, W/S %40, duvar açık (Emre: 3 M / 3 M eşik, 3 saldırıda bir), saldırı bitirme 60 × 0,6–1,05.
- Açık: ara sıra ilk yarım sürüklemede görüntü kayması (kalan dokunuşlar telafi ediyor), teslim penceresinde Okay bazen bulunamıyor, "Village did not load" bir kez, NVIDIA çökmeleri (Emre 2A: dokunma; bot BlueStacks'i kendisi açıyor). Bot kodu değişince Emre botu kapatıp `Botu-Baslat.bat` ile yeniden açmalı.
- **21:47–22:05 af91b57 ile bot turları, Emre: "hâlâ redline'da kaldı, 30 barbar kaldı, şampiyonu atamadın; bu saldırıları yapma, insansı yap, botun atamadığı belli".** 21:57: kuşatma + 3 kahraman inmedi; 22:00 (çok büyük köy, harita kenarına kadar dolu): sürükleme 29 barbar, kalan 60 dokunuş boşa (orta halka bu köyde köyün içinde), Champion üstte inmedi. **Sabit halka (Emre'nin yolu) bazı köylerde harita dışı, bazılarında köyün içi.** Bot 22:05'te panelden durduruldu (doğru komut: POST `/instance_action` `{"action":"stop","id":"main"}`; `id` olmadan etkisiz).
- **Ölçüm:** harita kenarı (çimen / orman) renkle 5 köyde bulundu ama köyden köye ~%8 (≈ 90 px) kayıyor (arama görüntüsü her köyde aynı yerde açılmıyor), karanlık temalı köyde renk tutmuyor → sabit dörtgen de güvenilir değil.

## DEVİR 01.11 22:10 — bot DURDURULDU, sırada asker bırakma yerini köye göre bulmak

- Asıl sorun: bırakılabilir kuşak (köyün kırmızı çizgisi ile harita kenarı arası) her köyde farklı yerde; sabit yol ~3 saldırıdan 1'inde ıskalıyor.
- Seçenekler (Emre'ye soruldu): (A) savaş başladıktan sonra (Champion indikten sonra) barbar seçiliyken köyün içine bir dokunuş → "You cannot deploy troops on the red area!" ile kırmızı çizgi yanıyor mu ölç (keşifte yanmıyordu; savaşta 20:30 karesinde uyarı göründü) → gerçek çizgi + biraz dışı; (B) harita kenarını her karede düz çizgilerle bul (dörtgen kenarları sabit eğimde); (C) sürüklemede kart sayısını izleyip inmeyen kısımda yolu dışarı / içeri kaydır.
- Bot `af91b57` ile durdu; Emre yeniden Başlat'a basarsa aynı kodla saldırır.
- **Kırmızı alan ölçümü (22:32, Emre 1A 2A): ÇALIŞTI.** Savaş başladıktan sonra barbar kartı seçiliyken köyün ortasına dokununca oyun ("You cannot deploy troops on the red area!") **bütün yasak alanı** hafif bir renkle gösteriyor: Lab a* kanalı köy üstünde ~5–10 düşüyor, kenarlar basamaklı ve keskin; 0,45 sn'de yok, 0,9 sn'de kısmen, 1,4 sn'de tamamı. (Keşif ekranında dokunuş bina seçiyordu, 19:57.) Kareler `debug/attacks/20261101_223209/red_*.png`. Bu saldırı: 2 yıldız, kalan 18 dokunuş.
- **Kod (canlıda denenmedi):** `_red_area_from(before, after)` (a* farkı < −2,5, HUD kutuları dışarıda, açma 5 + kapama 25, en büyük parça ≥ ekranın %8'i; HUD/ekran kenarına değen kenar noktaları "gizli" sayılıp komşulardan tamamlanır; 22°'lik dairesel ortanca) → halka. `_reveal_red_area`: ortaya dokun, 1,2 sn bekle, 1 sn içinde halka bulunana kadar kare. `_deploy_spread`: barbar seçilince önce haritanın en geniş yerine (EMRE_OUTER 0° ya da 180°, %5 içeri) **tek barbar** (savaşı başlatır), sonra kırmızı alan; bulunursa sürükleme çizginin %1,5–3,5 dışı, kahraman noktası %3, kalan barbarlar %3/5/7; bulunamazsa eski yol. Görüntü kayarsa halka da kayar. Yaml `troops.red_line` (varsayılan açık). Kuru çalıştırma: 22:32 köyünde yol köyün hemen dışında (sağ üstte hafif içeri kıvrım), 22:00 köyünde eski yol.
- **22:41 canlı deneme: "Red area not seen"** → eski yol (kalan 21 dokunuş, saldırı normal bitti). Sebep: kırmızı renk dokunuşla **beliriyor, ~1,5 sn'de sönüyor** (a* artar); 22:32'deki "önce" karesinde renk ilk sürüklemeden kalmıştı ve sönüşü ölçülmüştü (işaret ters). 22:41'de kare 1,2 sn bekleyip alındı → sönmüştü. **Düzeltme:** temiz kare savaşı başlatan barbardan önce, dokunuştan hemen sonra 1,2 sn boyunca kareler, a* artışı > 2,5. Kayıtlı 22:32 karelerinde (sıra çevrilerek) halka doğru.
- **22:47 canlı deneme: yine "not seen"** — bu sefer başlatıcı barbar inmedi (taş temalı harita, nokta harita dışı) → keşif ekranında kalındı, ortaya dokunuş bina seçti. Saldırı eski yolla bitti (kalan 22 dokunuş). **Düzeltme:** `_start_battle`: başlatıcı barbar sırayla dış halka %5 / %10 içeri (iki yan), sonra orta halka (4 yön); her dokunuştan sonra Next düğmesi kayboldu mu (= savaş başladı) bakılır; başlamazsa ölçüm atlanır, eski yol.
- **22:51 canlı deneme: "Battle did not start"** — başlatıcı barbarın bütün noktaları büyük köyün kırmızı alanında kaldı (keşifte reddedilen dokunuş uyarı göstermiyor); eski yolla sürükleme 13 barbar, kalan 47 dokunuş. **Düzeltme:** başlatıcı önce ekranın sol / sağ kenarı (Emre'nin sürüklemelerinin başladığı yer), sonra dış halka.
- **Emre 22:53:** "3. saldırıda en aşağı barbar gitmedi; her kenara 13–15 at, çok barbar kalıyor, zaman kaybı." → `troops.per_side: [13, 15]`: dört kenar (sağ üst, sol üst, sol alt, sağ alt) ayrı kısa sürükleme (~1,9 sn), önce üst ikisi, sonra görüntü %30 yukarı (W gibi) → alt ikisi; son kenar kalanı alır. Kuru çalıştırmada 4 × ~1,9 sn.
- **22:58 canlı deneme:** savaş başladı (başlatıcı kenardan indi), dokunuştan hemen sonraki karede **bütün yasak alan çok net** (a* −5…−16, büyük köyde haritanın neredeyse tamamı) — ama işareti 22:41 sonrası yanlışlıkla + yapmıştım → "not seen", eski yol: 4 kenar sürüklemesi 7,7 sn ama kalan 60 dokunuş boşa, Champion inmedi (büyük köy). **Düzeltme:** işaret iki yönlü (büyük olan); 22:58 karesinde halka köyün dış çizgisinde, %2,5 dışı dar çimen kuşağında.
- **23:02 canlı deneme: kırmızı alan İLK KEZ canlıda okundu** ("Red area read"), halka köyün dış çizgisinde. Ama köy haritanın köşelerine dayanıyordu: köşeden köşeye 4 kenar sürüklemesi kartı 60 → ~45 indirdi, kalan 60 dokunuş (köşe çevresi) ve kahraman noktaları (köşede) boşa → kuşatma + 4 kahraman inmedi. **Düzeltme:** kenar sürüklemesi kenarın ortasında (±22–30°), kahraman noktası ve kalan barbarlar kenar ortalarında (315/225 önce, 45/135); `_deploy_points` açı da alır.
- **Emre 23:04:** "barbarlardan sonra ganimet 50–70 binin altında kaldıysa direkt çık" → `end.loot_left: [50000, 70000]`: köyde kalan altın ve iksirin ikisi de eşiğin altındaysa yetenek beklemeden hemen teslim.
- **23:07 canlı deneme:** savaş başladı, renk göründü ama duvarlı köyde parçalı → en büyük parça %4 → "not seen", eski yol (kalan 52 dokunuş). **Düzeltme:** bütün parçalar (≥ %0,2) birleşir, dış çizgi 61 px kapamayla köprülenir; **eksik görünme kontrolü:** binaların kırmızı ayrıntılarının dış kenarı (eski `_deploy_ring`) 60 yönde halkanın %85'inden dışarıdaysa >10 yönde → reddet, eski yol. Kayıtlı 6 çiftte: 22:32 / 22:58 / 23:02 halka, 23:07 (yalnız sol yarı görünmüştü) reddedildi, 22:41 / 22:47 (renk yok) reddedildi.
- **23:13 canlı deneme (son hâl 8f2cd66): tuttu.** Kırmızı alan okundu ve kontrolden geçti; 4 kenar sürüklemesi 7,8 sn (alt ikisi için görüntü 233 px yukarı, halka kaymayla taşındı), kalan 22 dokunuş, kart boş; Champion + yetenek, yarasalar sağa; **ganimet 63 k altına inince 35. sn'de teslim** (Emre kuralı). Sonuç 1 yıldız %54, köyün altını 1,93 M → 12 k, iksiri 1,57 M → 22 k. Kuşatma kartı renkli kalıyor ama üstünde can çubuğu ve "boşalt" simgesi var → tomruk inmiş (23:25'te yakından doğrulandı).

## DEVİR 01.11 23:20

- Bot kapalı (deneme betikleriyle çalışıldı). Sırada: Emre `Botu-Baslat.bat` → Başlat ile botun kendi turu, birkaç saldırı izlenecek. Açık: kırmızı alanın okunmadığı köylerde eski yol (köylerin ~yarısı).
- **23:25 botun kendi turu (Emre Başlat, 8f2cd66):** kırmızı alan okundu, 4 kenar 7,9 sn, kalan yalnız 4 dokunuş, Champion + Queen yeteneği hemen, tomruk + kahramanlar indi, yarasa üstte; ganimet 67 k altında ~30. sn'de teslim. **1 yıldız %82**, köyün altını 1,91 M → 30 k, iksiri 1,99 M → 30 k.

## DEVİR 01.11 23:35 — yeni sohbet: "bunun üstüne ne ekleyelim" (Emre)

- Durum: yayma stili botun kendi turunda çalışıyor (8f2cd66 / 8ad5f33). Emre memnun ("harika oldu"). Bot açık, duvar Emre'nin panel ayarıyla.
- Yeni sohbetin işi: Claude araştırır, seçenekleri numaralı/şıklı önerir, Emre seçer; plansız kod yok.
- Araştırma başlıkları (bu belgedeki "ClashFarmer + MyBot'ta olup bizde olmayanlar" listesi + bugün açık kalanlar):
  1. Saldırı: kırmızı alanın okunmadığı köyler (~yarısı) için ikinci yol; teslim penceresinde Okay bazen bulunamıyor; ara sıra "Village did not load".
  2. Klan kalesi doldurma (Emre 1A kararı 15:15, ölçüm yarım: kale boşken istek penceresi, pasta).
  3. Ordu: savaş sonrası ordu dolu mu kontrolü / bekleme (şu an Emre elle dolduruyor; boş orduyla saldırı denenmedi).
  4. Mola / saat ızgarası, günlük saldırı sınırı (insan gibi görünme, hesap güvenliği).
  5. Bildirim: Telegram/telefon (tur özeti, hata, BlueStacks çökmesi).
  6. Hazine / maden arabası / engel toplama, Hammer Jam indirimli geliştirmeler.
  7. Usta üssü saldırısı (şu an kapalı).
  8. BlueStacks NVIDIA çökmeleri (Emre 2A: dokunma — yeniden sorulmaz, yalnız bilgi).

## 02.11 — "bunun üstüne ne ekleyelim" araştırması (kod yazılmadı, Emre seçecek)

**Dün geceki kayıttan (23:13–23:46, 8f2cd66, botun kendi turu):**
- Kırmızı alan 23:13'ten beri **10 köyün 10'unda okundu** (önceki "köylerin yarısı" notu eskidi; 4 "not seen" hepsi 23:07 öncesi). "Okay not found" bütün günde 1, "Village did not load" 2 (biri sunucu tarafı, 20:47).
- 9 saldırıdan 3'ünde (23:27, 23:32, 23:35) kalan 60 dokunuş boşa, kart boşalmadı; 23:27'de kuşatma + 3 kahraman hiç inmedi, 23:35'te kahramanlar ancak yeniden denemede. Yine de ganimet iyi: saldırı başına ~1,2 M altın / ~1,1 M iksir, tur ~2 dk.
- **Sebep (kayıtlı karelerde kuru çizim, scratchpad `kalan_noktalar.py`):** kırmızı çizgi doğru, ama kalan barbar noktaları çizginin %3 / %5 / %7 dışında (58–134 px); büyük köylerde çizgi ile harita kenarı arası ~%1–2 → noktaların neredeyse hepsi ormanda / su kenarında. Kahraman noktası da %3 dışarıda ve inmeyince "daha dışarı" deneniyor (yanlış yön). Sürüklemeler (%1,5–3,5) inmiş.
- **MyBot'ta (`COCBot/functions/Attack/RedArea/GetOffestPixelRedArea2.au3`):** bırakma noktası kırmızı çizgi pikselinin 3 oyun pikseli dışı (≈ 7 px, ekranın ~%0,4'ü), izometrik yönde (x 4/3, y 1); çizgi bulunamazsa sabit dış dörtgen (`_GetVectorOutZone`, haritayı tam uzaklaştırıp ortalayınca).
- Saatte saldırı: 21:00'de 21, 23:00–23:46'da 12; 24 saat aralıksız çalışabiliyor (mola ve günlük sınır yok, `hours_enabled` kapalı).
- Ordu: Mart 2025 "Clash Anytime" güncellemesinden beri eğitim süresi yok, kahraman iyileşmesi yok, ordu saldırıdan hemen sonra hazır (kayıtta 9/9 saldırıda tam ordu) → ordu bekleme / Quick Train işi gereksiz.
- Telegram: `utils.send_notification` var, anahtar `src/configs.py`'de (git'e girmez), ama yalnız geliştirme başlarken çağrılıyor; saldırı / hata / çökme bildirimi yok. MyBot'ta: son saldırı (+ ekran görüntüsü), istatistik, usta / kalkan durumu, başlat / durdur / saldırı aç-kapa, bilgisayarı kapat komutları.
- Kara iksir her ekranda 250 000 (depo dolu); panelde Binalar / Kahramanlar / Lab / Evcil kapalı, yalnız duvar + saldırı açık → gelen kara iksir boşa.
- Klan kalesi büyüleri (yıldırım x1, x2) hiçbir saldırıda kullanılmıyor, kalede duruyor (zarar yok).
- BlueStacks dökümleri: 02.11 00:17 ve 00:39 (bot 23:46'da durmuştu).

**Emre'ye sorulan seçenekler:** sohbette numaralı (1 kalan barbar / kahraman yeri, 2 mola + günlük sınır, 3 Telegram, 4 klan kalesi, 5 kara iksir, 6 usta üssü saldırısı); yapılmaması önerilenler: ordu kontrolü, hazine / toplayıcı / maden arabası, Hammer Jam (15.11'de bitiyor, menü zaten indirimli fiyatı okuyor), Okay / Village did not load (çok seyrek).

## 02.11 — Emre'nin seçimleri (1A 2A 3A 4A 5A 6B) ve yapılanlar

- **1A ✅ kod, canlıda denenmedi (e7ef9cf):** kırmızı alan okununca kalan barbarlar çizginin %0,6 / %1,1 / %1,6 (+0–0,4) dışında (`RED_LEFTOVER`), kahraman / kuşatma noktası %0,8 (+0–0,5) (`RED_SPOT`); kahraman inmezse biraz içeri (−%0,4), biraz dışarı (+%0,6), sonra başka kenarın ortası. Kırmızı alan okunmazsa eski yol aynı. Kayıtlı 10 köyde kuru çizim (`scratchpad/yeni_noktalar.py`): noktalar çizgi ile orman arasındaki çimende; 23:32'de sağ üstte çizgi bir binanın etrafında içeri kıvrılıyor, oradaki 1–2 nokta bina üstünde.
- **3A ✅ kod, canlıda denenmedi (ee9671b):** Telegram (anahtar `src/configs.py` 10. satır, git'e girmez; Emre BotFather'dan alıp kendisi yazar). Mesajlar: her saldırı (sonuç ekranı resmi + kazanılan ganimet + depo, sessiz), günlük özet (yeni günün ilk turunda), tur hatası (15 dk'da bir), BlueStacks yeniden açıldı / açılamadı, bot başladı / durduruldu / duraklatıldı, mola ve günlük sınır, geliştirme başladı. Ayrı iş parçacığında gönderilir. Taklit `requests` ile denendi.
- **2A ✅ kod, canlıda denenmedi (c2a106f):** Genel → "İnsan gibi oyna": 15–25 saldırıda bir 20–40 dk mola (oyun kapanır), günde 30–45 saldırı (sonra ertesi gün 00:05–00:30), 24 saatlik ızgara (varsayılan 02:00–09:00 kapalı); her satırda "?" ile öneri. Sayaçlar `src/cache.json` "play" (bot kapanıp açılınca sıfırlanmaz). Durum çubuğunda "Mola · sonraki tur" / "Günlük sınır doldu". Mantık sahte saatle denendi (23. saldırıda 32 dk mola, 35'te günlük sınır); panel 1280 / 500 ekran görüntüsü alındı (ızgara taşması düzeltildi).
- **4A (klan kalesi isteği + pasta varsa ücretsiz doldur):** kod yok; ölçüm gerekiyor (kale boşken ordu penceresi, istek penceresi; pasta etkinken düğme). Oyuna dokunduğu için Emre'nin onayıyla, Emre oyunu oynamıyorken.
- **5A:** Emre panelden Kahramanlar + Evcil'i açacak (kod yok).
- **6B:** usta üssü saldırısı yok.

## 02.11 gece (devam) — canlı bulgular + panel alt sekmeleri

- **01:42 saldırı bırakıldı:** seçili kart bir boy büyük çiziliyor → barbar kartı bulunamadı; tomruk King'e göre bulunuyordu (King yükselmede). Düzeltme 86dd380: her kart ±1 boy, tomruk barbarın sağındaki ilk kahramana göre, Minion Prince grupta, aramadan çıkış Surrender + Okay. 01:42'deki x56 tek seferlik (sonraki üç başlangıç x60). Yükselmedeki kahraman çubukta hiç yok.
- **Yeni kodla canlı (01:47, 01:49, 01:52):** kırmızı alan okundu, kalan barbarlar 24 / 32 / 5 dokunuşta bitti, kart boş, tomruk ve kahramanlar indi (1A çalışıyor). Telegram çalışıyor (Emre ilk mesajı BotFather'a yazmıştı; @Emre36bot'a yazınca tuttu). Telegram resmi artık sonuç ekranı (Return Home görününce, 6d59401) — canlıda görülmedi.
- **Emre:** duvar kapalı kalsın (2A), ordu 60.
- **Panel (f65ad44, Emre 1A 2A 3A 4A):** Geliştirme alt sekmeleri Kahramanlar · Binalar · Laboratuvar · Evcil · Duvar · Kurallar · Usta üssü; Saldırı alt sekmeleri Arama · Dağıtım · Savaş sonu · İnsan gibi (mola + ızgara Genel'den taşındı); açık işin sekmesinde yeşil nokta; satır açıklamaları "?" içinde; yazı ve satır aralığı küçüldü. MyBot'un Kahramanlar alt sekmesinden: **kahraman sırası** (`home.hero_priority`), **önce kahramanlar** (`home.heroes_first`, indirimden de önce), **kahramanlara ayrılan usta** (`home.hero_builders`: boş usta bu sayıya inince yalnız kahraman); Binalar kapalı + Kahramanlar açıkken yalnız kahraman. Saldırı → Dağıtım / Savaş sonu değerleri `attack_style` ayarında, `yayma.yaml`'ın üstüne yazılır (barbar sayısı, kenar başına, kırmızı alan, Champion önce %, yarasa, "ganimet şunun altına inince çık", ganimet değişmezse sn). Seçim mantığı sahte satırlarla denendi; panel ayrı "deneme" kopyasıyla 1280 / 500 ekran görüntüsü. **Kahraman geliştirmesi canlıda denenmedi** (ustalar 0/6).
- **Emre'nin yeni fikirleri (konuşulacak):** profil 1 / profil 2 (adlı, kendi ayarları ve ordusu); saldırı mantığını md'den üretilen dosyaya taşımak.
