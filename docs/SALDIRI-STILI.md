# Saldırı stili

Her saldırı stili bu belgedeki gibi bir bölümdür. Emre stili Türkçe anlatır, Claude bunu
`attacks/<ad>.yaml` saldırı betiğine çevirir. Bot her saldırıda betiği okur ve **her seferinde
biraz farklı oynar** (yön, zamanlama, sapma rastgele seçilir; aşağıdaki "değişkenlik" satırları).

Yeni stil eklemek için: son bölümü kopyala, boşlukları doldur, Claude'a gönder.
Bilmediğin satırı boş bırak; Claude önerisini yazar, sen onaylarsın.

---

## Stil 1 — Süper barbar + yıldırım (01.11, betik: `attacks/super-barbar.yaml`)

`(öneri)` yazan satırlar Claude'un önerisi; değiştirmek istediğini üstüne yaz.

### Ordu

| Satır | Değer |
|---|---|
| Kayıtlı ordu (Quick Train) | Ordu 1 — oyunda süper barbar + 11 yıldırım olarak kaydedilir (Emre ayarlar). Oyunda Quick Train'in yeni adı "Saved Recipes" |
| Ordu boyutu / içerik | 60 süper barbar (sv. 11), 11 yıldırım (sv. 10), kahramanlar: King 90, Queen 90, Warden 65, Champion 70 (01.11 ordu ekranından okundu, 6A). 3 kuşatma makinesi ordudaydı, stilde yok → kullanılmaz |
| Klan askerleri | kullanılmaz |

### Arama (panelde de değişir)

| Satır | Değer |
|---|---|
| En az altın | 400 000 |
| En az iksir | 0 (0 = şart yok) |
| En az kara iksir | 0 = şart yok (3A) |
| Birleşim | hepsi birden (0 yazılan şart sayılmaz) |
| En fazla arama | 30, bulamazsa vazgeç, sonraki turda yeniden |
| Şartları düşür | her 15 aramada %10 (panelden; Emre bazen %30 yapar) — 2B |

### Giriş

| Satır | Değer |
|---|---|
| Yön | **dört köşe birden** (sağ / sol / üst / alt), sırası her saldırıda rastgele (Emre 2A, 01.11) |
| Şekil | köşe başına **15 süper barbar**, köşenin iki kenarına yayarak; alt köşe asker çubuğunun altında → görünen alt kenara |
| Süre | bütün ordu **10–15 sn** (Emre); dokunuş arası 0,06–0,18 sn, köşeler arası 0,3–0,9 sn. Basılı tutarak bırakma sonra (hız ölçülünce) |
| Kuşatma makinesi | her maç **1 tane, rastgele bir köşeden** (Emre) |
| Dokunuş sapması | her dokunuşta birkaç piksel `(öneri)` |
| Bazen bir taraf geç | saldırıların ~%30'unda ordunun bir kısmı karşı kenardan 5–15 sn sonra `(öneri)` |

### Büyüler

| Satır | Değer |
|---|---|
| Yıldırım hedefi | **köyün içinde rastgele yerler** (Emre 1B: sonda şart değil, saldırı insan gibi görünsün) |
| Dağılım | 11 yıldırım, her biri ayrı rastgele nokta, aralarında 0,15–0,45 sn |
| Klan büyüleri | kullanılmaz (klan kartları sağda, dokunulmaz) |
| Ne zaman | ordudan önce (4A) |
| Bazen saptır | yıldırımın düştüğü yer sondanın merkezinden biraz kayar `(öneri)` |

### Kahramanlar

| Satır | Değer |
|---|---|
| Giriş | rastgele bir köşeden, barbarların arkasından (Claude, Emre değiştirebilir) |
| Yetenek | girişten 8–12 sn sonra, rastgele |

### Savaş sonu

| Satır | Değer |
|---|---|
| Bitir | savaş bitene kadar bekle, sonra Return Home |
| Erken bitir | 20 sn ganimet değişmezse bitir (5B) |

---

## Stil 2 — Yayma (01.11, betik: `attacks/yayma.yaml`, botun şu anki stili)

Emre'nin elle 10 saldırısından çıkarıldı (kayıt `X:\CoC\kayit\20261101_185832`, 19:12–19:27; notlarda 9 yazıyor,
19:19'daki notta yok). Rakamlar kayıttan ölçüldü.

### Ordu

60 süper barbar, kuşatma, King · Queen · Warden · Royal Champion (Minion Prince çıktı, Queen girdi), **11 yarasa büyüsü**
(yıldırım çıktı), klan büyüsü (x2) — dokunulmaz.

### Arama

Altın ≥ 700 000 **ve** iksir ≥ 600 000 (Emre 3A). Saldırılan 10 köyün en zayıfı 755 k / 624 k; geçilen 5 köyün en iyisi
681 k / 104 k (diğerleri 444 k / 259 k, 344 k / 337 k, 73 k / 140 k, 47 k / 66 k). Ölü köy aranmıyor, ganimete bakılıyor.

### Giriş

| Satır | Kayıtta | Bot |
|---|---|---|
| Royal Champion | tek başına bir kenara, yeteneği hemen; 10'un 6'sında barbarlardan önce; kahraman grubundan farklı kenar (9/10) | aynı |
| Barbarlar | **parmak basılı sürükleyerek** köyün çevresine; 7 saldırıda iki yarım (üst + alt, 3,4–5,3 sn), 3'ünde tek tur (6,3–8,5 sn); sürükleme ekranın kenarından başlıyor, yer yer köyün içinden geçiyor | aynı; süre = 60 ÷ 7,3 × %90–96 |
| Basılı tutma hızı | 1,5 sn'de ~11 barbar (~7,3/sn), sabit | — |
| Kalan barbar | 4 saldırıda sürükleme sonrası kenarda tek tek dokunuş | kalan adımı |
| Kuşatma + King, Queen, Warden | hepsi **aynı noktaya**, 0,5–0,8 sn arayla; kuşatma çoğunlukla ilk | aynı |
| Görüntü | bazen asker atmadan önce görüntüyü hafifçe kaydırıyor | yok |

### Büyüler

11 yarasa **kahramanların noktasına** (10'un 9'u), 0,13–0,16 sn arayla hızlı dokunuş, nokta kenar boyunca biraz kayıyor.

### Kahramanlar

| Yetenek | Kayıtta (inişten sonra) | Bot |
|---|---|---|
| Royal Champion | hemen | hemen |
| Queen | 10'un 6'sında hemen, diğerlerinde 6–48 sn | %60 hemen, yoksa 6–30 sn |
| King | 4–33 sn | 4–25 sn |
| Warden | 10–36 sn | 10–30 sn |

### Savaş sonu

Emre ilk askerden 29–65 sn sonra teslim oluyor (Surrender → Okay → Return Home). Bot: paneldeki "Saldırıyı bitir" (60)
× 0,6–1,05 = 36–63 sn.

### Kart çubuğu

Bu orduda çubuk boş yuvalar gösteriyor, kartlar eski resimlerin ~0,8'i kadar → kartlar çok ölçekli aranıyor; can çubuğu
ve gri kart kontrolü ölçeğe göre. Yarasa ve Queen kart resimleri kayıttaki 10 arama ekranının ortalamasından.

---

## Stil 3 — (ad)

### Ordu
### Arama
### Giriş
### Büyüler
### Kahramanlar
### Savaş sonu
### Başka istekler
