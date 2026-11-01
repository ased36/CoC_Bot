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
| Kayıtlı ordu (Quick Train) | Ordu 1 — oyunda süper barbar + 11 yıldırım olarak kaydedilir (Emre ayarlar) |
| Ordu boyutu / içerik | __ süper barbar, 11 yıldırım, kahramanlar: __ |
| Klan askerleri | kullanılmaz |

### Arama (panelde de değişir)

| Satır | Değer |
|---|---|
| En az altın | 400 000 |
| En az iksir | 0 (0 = şart yok) |
| En az kara iksir | __ |
| Birleşim | hepsi birden (0 yazılan şart sayılmaz) |
| En fazla arama | 30, bulamazsa vazgeç, sonraki turda yeniden |

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
| Ne zaman | ordudan önce / sonra / ortasında: __ |
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
| Erken bitir | __ (ör. 20 sn ganimet gelmezse, %50 geçince) |

---

## Stil 2 — (ad)

### Ordu
### Arama
### Giriş
### Büyüler
### Kahramanlar
### Savaş sonu
### Başka istekler
