# Saldırı stili

Her saldırı stili bu belgedeki gibi bir bölümdür. Emre stili Türkçe anlatır, Claude bunu
`attacks/<ad>.yaml` saldırı betiğine çevirir. Bot her saldırıda betiği okur ve **her seferinde
biraz farklı oynar** (yön, zamanlama, sapma rastgele seçilir; aşağıdaki "değişkenlik" satırları).

Yeni stil eklemek için: son bölümü kopyala, boşlukları doldur, Claude'a gönder.
Bilmediğin satırı boş bırak; Claude önerisini yazar, sen onaylarsın.

---

## Stil 1 — Süper barbar + yıldırım (taslak, 01.11)

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
| Yön | sağ / sol / alt / üst; rastgele, art arda aynı yön gelmez |
| Şekil | seçilen köşenin iki kenarına yayarak `(öneri)` |
| Dalga sayısı | 4–5 `(öneri)` |
| Dalgalar arası bekleme | 1–3 sn rastgele `(öneri)` |
| Dokunuş sapması | her dokunuşta birkaç piksel `(öneri)` |
| Bazen bir taraf geç | saldırıların ~%30'unda ordunun bir kısmı karşı kenardan 5–15 sn sonra `(öneri)` |

### Büyüler

| Satır | Değer |
|---|---|
| Yıldırım hedefi | kara iksir sondaları |
| Dağılım | 4 sonda: 3 + 3 + 3 + 2 = 11 |
| Az sonda bulunursa | bulunanlara bölünür; hiç bulunamazsa yıldırım atılmaz |
| Ne zaman | ordudan önce (4A) |
| Bazen saptır | yıldırımın düştüğü yer sondanın merkezinden biraz kayar `(öneri)` |

### Kahramanlar

| Satır | Değer |
|---|---|
| Giriş | ordunun arkasından, aynı yönden |
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
