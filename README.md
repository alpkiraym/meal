# Kur'ân Meali · Giray Akademi

Arapça metin, üç meal (Diyanet İşleri, Diyanet Vakfı, Elmalılı Hamdi Yazır) ve Celâleyn tefsiri; âyet âyet ya da sûre boyunca okuma.

Adres: https://alpkiraym.github.io/meal/

## Kaynaklar

Bütün metinler [Tanzil.net](https://tanzil.net/) projesinden alınmıştır ve değiştirilmeden kullanılmaktadır:

- Arapça metin: Tanzil Quran Text (Simple), https://tanzil.net/download/
- Mealler ve Celâleyn: https://tanzil.net/trans/ (`tr.diyanet`, `tr.vakfi`, `tr.yazir`, `ar.jalalayn`)

Tanzil'in kullanım şartı gereği mealler yalnızca ticari olmayan amaçla kullanılır ve sayfada çeviriler sayfasına bağlantı verilir.

## Derleme

`kaynak/` klasöründeki metinlerden sûre sûre `veri/001.json … veri/114.json` ve `index.html` üretilir:

    python3 kaynak/derle.py

`index.html` elle düzeltilmez; değişiklik `kaynak/sablon.html`, `kaynak/altcubuk.html` ya da `kaynak/derle.py` içinde yapılır.
