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
| Arama şartı | en az altın · en az iksir · en az kara iksir · birleşim VE / VEYA / TOPLAM | 300k / 300k / 0, VE | 🟨 (rakip ganimeti okunacak + "Next" düğmesi) |
| En fazla Belediye seviyesi | sayı | sınırsız | 🟨 |
| Şartları düşür | her X aramada %Y | 20 / 10 | ✅ (arama varsa) |
| En fazla arama | sayı, sonra: ilk köye saldır · vazgeç | 50, vazgeç | ✅ |
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

## Ek: ClashFarmer + MyBot'ta olup bizde olmayanlar (01.11 araştırması)

Kaynak: clashfarmer.com ekran görüntüleri (status/army/search/attack/clan/village/remote/other.png, resimler tek tek incelendi) + MyBot `develop` dalı GUI `.au3` dosyaları ve `functions/Village/UpgradeWall.au3`. Görüntüdeki değerler varsayılan olmayabilir.

**ClashFarmer sekmeleri:** Durum (bot kaydı + saldırı kaydı tablosu) · Ordu (oyunun Quick Train tarifi 1/2/3, süper birlik etkinleştirme) · Arama (en az altın/iksir/kara iksir, yalnız dolu toplayıcılı ölü köy, VE/VEYA, eşleşmede ses, "hiç arama yapma, yalnız köyü bakımla", altın şunun altındaysa arama) · Saldırı (dalga/asker hızı 1–9, klan askerleri, kahraman yeteneği N sn sonra, N sn ganimet gelmezse bitir, saldırı yönleri KB/KD/GB/GD, 1–3 dalga, kırmızı çizgiye yakın, sürükle-bırak asker sırası) · Klan (bağış, anahtar kelimeye göre bağış, asker iste) · Köy (altın/iksir/kara iksir topla, mezar taşı, maden arabası; başka cihaz bağlanınca N sn bekle; otomatik duvar: duvar seviyesi seçimi, "önce iksir sonra altın", kalacak en az) · Uzaktan (Telegram) · Diğer (açılışta otomatik başla — kapalı, 24 saatlik mola ızgarası, günlük rastgele 25–35 saldırı sınırı).
Alt şeritte her sekmede: **Start Bot · Search Only · Close Bot**. Bot Start'a basılmadan çalışmaz.

**MyBot duvar mantığı (kodda doğrulandı):** her boş turda en sona; en az 1 boş usta; önce açık bina/kahraman/lab geliştirmelerinin maliyetini ayırır, kalandan duvar; "kaynak − duvar maliyeti ≥ en az" oldukça döngü; seçilen seviye bitince bir üst seviye; Belediye seviyesi yetmiyorsa atlar; "duvara 1 usta ayır".

**İkisinde olup planımızda olmayanlar:** asker eğitimi (hızlı eğitim/özel ordu) · süper birlik · kahraman/büyü/klan askerini bekle · güçlendirmeler (kışla, kahraman; saat ızgarası) · asker isteme/bağış · hazine toplama, engel/mücevher kutusu, sihirli eşya, başarı/görev ödülleri · klan oyunları · klan başkenti · usta üssü yıldız bonusu · arama: savunma seviyesi süzgeci, kupa aralığı, ölü köy algılama, zorba modu · SmartZap (kara iksir sondajına şimşek) · kupa düşürme · tekrar paylaşımı · Telegram olay bildirimleri + uzaktan komut · çok hesap · Android'i N saatte yeniden başlat · istatistik CSV.
