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

## Stil 2 — (ad)

### Ordu
### Arama
### Giriş
### Büyüler
### Kahramanlar
### Savaş sonu
### Başka istekler
