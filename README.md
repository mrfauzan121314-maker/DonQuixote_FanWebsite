# Don Quixote — Fan Site

Situs statis (HTML/CSS/JS tanpa framework) untuk Don Quixote dari *Limbus Company*.
Seluruh halaman dihasilkan oleh paket Python kecil di `builder/`.

## Struktur

```
builder/            Generator halaman
  config.py         Nama situs, URL dasar, warna sin, daftar navigasi
  layout.py         <head> (termasuk OG/Twitter/canonical), nav, footer — satu sumber
  data.py           Pembacaan data/ dan resolusi path aset
  components.py     Potongan markup yang dipakai lebih dari satu halaman
  template.py       Renderer `{{placeholder}}` tanpa dependensi
  pages/            home.py · identity.py · ego.py
templates/          Markup per halaman (home, galeri E.G.O, detail Identity, detail E.G.O)
data/               identities.json · ego.json (sumber kebenaran konten)
assets/             WebP artwork, font self-hosted, OG image, favicon
tools/check_site.py Pemeriksaan metadata, referensi, dan struktur HTML
```

Halaman hasil build (`index.html`, `ego.html`, `identity/`, `ego/`) **tidak diedit manual** —
ubah data atau template lalu build ulang.

## Perintah

```bash
make build                 # bangun semua halaman (OG relatif, untuk preview lokal)
make check                 # metadata + referensi + struktur HTML
SITE_URL=https://domain.com make build   # OG/canonical absolut untuk produksi
make og                    # render ulang kartu Open Graph E.G.O
make assets                # varian WebP 640w + font + OG
make preview               # server lokal di :3000
```

## Catatan

- OG image hanya terbaca crawler bila absolut, jadi isi `SITE_URL` saat build produksi.
- Data E.G.O bersumber dari Limbus Company Wiki (CC BY-SA 4.0); fan site tidak resmi.
