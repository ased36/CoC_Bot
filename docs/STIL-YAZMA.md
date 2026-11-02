# Saldırı stili yazma kılavuzu

Bu belge, Emre'nin anlattığı bir saldırıyı `attacks/<ad>.yaml` dosyasına çevirmek içindir. Başka bir sohbet bu
belgeye bakıp dosyayı yazar; Emre panelde (Saldırı → Dağıtım → **Saldırı stili**) o stili seçer.

Örnek: `attacks/yayma.yaml` (Emre'nin kendi saldırısı, 01.11 kaydından).

## Dosyanın yapısı

```yaml
steps:            # saldırının sırası (aşağıdaki adımlar)
  - lead: {first: true}
  - troops
  - lead
  - heroes
  - spells
  - retry

card_to_drop: [0.15, 0.35]   # karta bastıktan sonra sahaya dokunmadan önce bekleme (sn)
troops:   {...}              # sürüklenecek asker
siege:    {...}              # kuşatma makinesi
heroes:   {...}              # kahramanlar
spells:   {...}              # kahramanların noktasına atılan büyü
end:      {...}              # savaşın bitişi
```

Süreler saniyedir. `[a, b]` = her seferinde a ile b arasında rastgele. `0.6` gibi tek sayı = olasılık (10 saldırının 6'sı).

## Adımlar

Adım ya yalnız adıdır (`- troops`) ya da tek anahtar + değerleri (`- wait: [1, 2]`).

| Adım | Ne yapar | Değerler |
|---|---|---|
| `troops` | Asker kartını seçer, tek askerle savaşı başlatır, kırmızı alanı okutur, dört kenara basılı sürükler, kalanları tek tek bırakır. **Her stilde olmalı.** | `troops:` bölümünden |
| `lead` | `heroes.lead` kahramanını (Champion) kendi kenarına bırakır, yeteneği `ability_now`'a göre. Önceki bir `lead` bıraktıysa bir şey yapmaz. | `first: true` = panel "Champion barbarlardan önce, %" kadar saldırıda; `chance: 0.3` = bu kadar saldırıda; boş = her zaman |
| `heroes` | Kuşatma + `heroes.group` kahramanlarını aynı noktaya (kahraman noktası) bırakır. `drop` ile önceden inen kart atlanır. | `heroes:` ve `siege:` bölümlerinden |
| `spells` | `spells.card` büyüsünü kahramanların noktasına (bazen başka kenara) `count` kez basar. | `spells:` bölümünden |
| `retry` | İnmemiş kahraman / kuşatma kartlarını bir daha, biraz dışarıdan bırakır. Sona koy. | — |
| `wait` | Bekler. | `wait: [1, 2]` |
| `drop` | Tek kartı bir noktaya bırakır. | `drop: {card: king, at: left}`; `at`: `heroes` (varsayılan), `lead`, `right`, `left`, `top`, `bottom` |
| `cast` | Büyüyü köyün içine basar (öfke, yıldırım, dondurma gibi). | `cast: {card: lightning, count: 3, spread: 0.4, gap: [0.15, 0.3]}`; `spread` = köy yarıçapının payı |
| `ability` | Kahramanın yeteneğini hemen kullanır (rastgele beklemesi iptal). | `ability: king` |

## Bölümler

**troops**
- `card`: asker kartı (ör. `super_barbarian`)
- `count`: ordudaki sayı *(panel üstüne yazar)*
- `per_side: [13, 15]`: dört kenarın her birine; son kenar kalanı alır *(panel)*
- `per_second: 7.3`: basılı tutunca saniyede inen asker
- `hold_share: [0.9, 0.96]`, `hold_still: [0.35, 0.55]`, `sweep_pause: [0.25, 0.6]`
- `red_line: true`: kırmızı alanı okut *(panel)*
- `per_side` yoksa: `halves: 0.7` (iki yarım), `pan: 0.4`, `pan_by: 0.3`

**heroes**
- `lead: champion`: tek başına giden kahraman
- `lead_first: 0.0` *(panel)*
- `group: [king, queen, warden, minion_prince]`: aynı noktaya, sırası rastgele; yükselmedeki kahraman çubukta yoktur, atlanır
- `gap: [0.25, 0.5]`: iki kart arası
- `ability_now: {champion: 1.0, queen: 0.6}`: inince hemen yetenek olasılığı
- `ability_after: {king: [4, 25], ...}`: yoksa inişten bu kadar sonra

**siege**: `card: siege`, `first: 1.0` (kahramanlardan önce olasılığı)

**spells**: `card: bat`, `count: 11` *(panel)*, `on_heroes: 0.85`, `gap: [0.12, 0.17]`

**end**: `after_factor: [0.6, 1.05]` (panel "saldırıyı bitir" süresi × bu), `loot_left: [50000, 70000]` *(panel)*,
`idle_seconds: 20` *(panel)*, `max_seconds: 180`

*(panel)* işaretli değerleri panelin Dağıtım / Savaş sonu sekmeleri her stilin üstüne yazar.

## Kartlar

Bir kart ancak resmi `assets/attacker/cards/` içinde varsa kullanılabilir. Şu an olanlar:
`super_barbarian`, `siege` (`siege_b`), `king`, `queen`, `warden`, `champion`, `minion_prince`, `bat`, `lightning`.

Yeni bir asker ya da büyü (ör. `rage`) için önce kartın resmi gerekir: saldırı ekranında asker çubuğundan kesilmiş
PNG, adı kartın adı. Resim yoksa stil denetimden geçmez. (Resmin ilk saldırıda kendiliğinden alınması henüz yok.)

## Denetim

Bot her turda, **aramadan önce** stili denetler. Bilinmeyen adım, resmi olmayan kart, yanlış `at`, `[a, b]` olmayan
`wait` ya da `troops` adımı eksikse saldırıya girmez. Kayda ve Telegram'a hatanın listesi yazılır, yarım saldırı olmaz.

## Yeni stil adımları (özet)

1. Emre saldırısını anlatır: hangi kart, hangi sırayla, nereye, ne kadar bekleyerek.
2. `yayma.yaml`'ı kopyala, adını değiştir (`attacks/<ad>.yaml`, Türkçe karakter ve boşluk yok).
3. `steps`'i anlatılan sıraya göre yaz, bölümlerdeki sayıları düzelt.
4. Yeni kart varsa resmini iste.
5. Emre panelde profili seçer, Dağıtım'da stili seçer. Bot bir sonraki turda o stille saldırır.
