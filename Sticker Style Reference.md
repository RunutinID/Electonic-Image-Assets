# Sticker Style Reference — Koleksi Stiker Komponen Runutin

Referensi styling untuk koleksi stiker komponen elektronika di platform Runutin. Semua style wajib tetap selaras design system: Playful Brutalism (bg `#fdf8ee`, primary teal `#2f9f8a`, accent yellow `#ffd166`, ink `#1a1a1a`, Fredoka/Nunito) dan identitas komponen akurat (warna fisik asli, silkscreen benar).

**Spesifikasi produksi umum (berlaku semua style):**
- Die-cut: outline putih tebal 10–16 px mengelilingi objek (standar industri stiker).
- Output: PNG transparan → WebP (standar Runutin), resolusi ≥1024×1024 px.
- Safe zone: elemen penting ≥5% dari tepi kanvas.
- Zero meta-text: tidak ada kata "lesson/module/sticker" di dalam gambar.
- 1 stiker = 1 komponen tunggal, pose konsisten (corner isometric 30–45° kecuali style menyatakan lain).

---

## 1. 🧱 Playful Brutalism Die-Cut (Style Utama — Brand Default)

Ciri khas Runutin paling murni.
- Objek: render isometrik base style (cream bg versi stiker dibuang → die-cut transparan).
- Outline putih tebal + **hard drop shadow offset** (`4px 4px 0 #1a1a1a`) — khas brutalism.
- Aksen: 1–2 elemen kecil kuning `#ffd166` (bintang, petir, titik) di sekitar komponen.
- Cocok untuk: stiker default semua komponen, reward/koleksi siswa.
- Prompt kunci: `die-cut sticker, thick white sticker border, flat hard offset black shadow, playful brutalism, warm cream accents, yellow spark accents`.

## 2. 📸 Photoreal Die-Cut (Base Style Continuation)

Render fotorealistis base style langsung jadi stiker.
- Objek: render octane photorealistic isometrik persis folder `base/`.
- Die-cut outline putih tipis-sedang (8–10 px), bayangan lembut natural (bukan hard shadow).
- Kesan: premium, "foto asli dipotong jadi stiker".
- Cocok untuk: stiker edisi flagship (ESP32, Arduino UNO, Raspberry Pi), merchandise.
- Prompt kunci: `photorealistic die-cut sticker of electronic component, subtle white border, soft natural contact shadow, octane render`.

## 3. 😺 Kawaii Component (Maskot Karakter)

Komponen jadi karakter cute.
- Komponen chibi dengan mata kecil + senyum simpel (2 dot mata + garis mulut), kadang blush pink, kadang tangan kecil.
- Tetap akurat bentuk fisik; wajah hanya overlay minimal — jangan mengubah anatomi komponen.
- Outline putih tebal, warna tetap asli komponen.
- Cocok untuk: sticker pack pemula/anak, maskot Runutin (Kamo platypus + komponen), engagement media sosial.
- Prompt kunci: `cute kawaii chibi electronic component character, tiny dot eyes, small smile, blush cheeks, thick white die-cut border, soft pastel accents`.
- ⚠️ Batasan: jangan untuk materi lesson teknis — hanya untuk sosial/merchandise.

## 4. ⚡ Retro Pixel 8-bit

Nostalgia game retro, cocok tema Game Dev Runutin.
- Komponen dirender sebagai pixel art 32–64 px feel, palet warna terbatas (komponen asli + krem + teal).
- Outline pixelated tebal, kadang efek "glow" 1px.
- Cocok untuk: crossover Game Development, stiker event/challenge coding.
- Prompt kunci: `retro 8-bit pixel art sticker of electronic component, limited color palette, crisp pixel edges, thick white border, subtle dithering`.

## 5. 🔵 Flat Line Art (Technical Icon)

Minimalis, paling versatile.
- Komponen digambar line art tebal hitam `#1a1a1a` + fill flat warna asli (atau monochrome teal).
- Tanpa gradasi, tanpa shadow — bersih seperti ikon UX.
- Cocok untuk: badge skill, ikon modul, navigasi katalog, stiker hemat tinta.
- Prompt kunci: `flat line art sticker, bold black outlines, flat color fill, minimal electronic component icon, clean vector style, white border`.

## 6. 🏅 Vintage Stamp / Badge

Kesan resmi edisi terbatas.
- Komponen di tengah "perangko": border bergigi (perforasi), teks melingkar mis. `RUNUTIN ELECTRONICS • ESP32 •`.
- Warna faded vintage: cream kertas, teal pudar, merah bata aksen; tekstur kertas halus.
- Cocok untuk: stiker edisi terbatas, sertifikat/koleksi rare, reward achievement.
- Prompt kunci: `vintage postage stamp sticker, perforated edges, circular text banner, faded retro colors, paper texture, electronic component centerpiece`.

## 7. 💠 Holographic Foil

Premium collectible look.
- Komponen base style + efek foil rainbow iridesen di area metalik/pin, shimmer diagonal.
- Background tetap die-cut transparan; foil hanya di permukaan komponen.
- Cocok untuk: stiker rare/legendary (edisi terbatas), bundle kit fisik.
- Prompt kunci: `holographic foil sticker effect, iridescent rainbow shimmer on metallic pins, prismatic reflections, die-cut white border`.
- ⚠️ Untuk implementasi web: siapkan versi static + CSS gradient overlay animasi ringan.

## 8. 🌈 Gradient Pop 3D (Y2K Glass)

Modern playful untuk audiens muda.
- Komponen die-cut + border gradient teal→kuning `#2f9f8a → #ffd166`, highlight glossy, gelembung/ sparkle aksen.
- Bisa semi-glossy 3D bubble feel.
- Cocok untuk: sticker pack promosi, TikTok/IG Reels assets, event bootcamp.
- Prompt kunci: `y2k glossy sticker, teal to yellow gradient border, bubble highlights, sparkles, die-cut, vibrant playful`.

## 9. 🖤 Neon Tech Glow (Dark Circuit)

Satu-satunya style dark mode.
- Background die-cut transparan, komponen garis neon teal/cyan bercahaya di siluet gelap, jejak circuit board glow di belakang.
- Cocok untuk: stiker komunitas advanced (MQTT, Edge AI), laptop dev, tema dark dashboard.
- Prompt kunci: `neon glow sticker, dark silhouette electronic component with glowing teal circuit traces, cyberpunk neon outline, die-cut`.

## 10. 📰 Comic Pop Halftone

Energi komik Amerika.
- Komponen dengan outline tebal ink, shading halftone dot, efek onomatopoeia kecil ("ZAP!", "BEEP!") sebagai aksen terpisah.
- Warna komponen asli + pop yellow `#ffd166` background burst.
- Cocok untuk: komik edukasi Runutin, stiker event, poster kampanye.
- Prompt kunci: `comic book style sticker, bold ink outlines, halftone dot shading, pop art burst background, electronic component hero shot, die-cut`.

---

## Matriks Pemilihan Cepat

| Kebutuhan | Style |
|---|---|
| Default brand / katalog lengkap | #1 Playful Brutalism |
| Premium flagship | #2 Photoreal / #7 Holographic |
| Anak/pemula/maskot | #3 Kawaii |
| Game dev / event coding | #4 Pixel |
| Ikon UI / badge skill | #5 Flat Line Art |
| Edisi terbatas / achievement | #6 Vintage Stamp / #7 Holographic |
| Promosi sosmed / event | #8 Gradient Pop / #10 Comic |
| Komunitas advanced / dark theme | #9 Neon Glow |

## Rekomendasi Rollout

1. **Batch 1 (MVP)**: Style #1 untuk 20 komponen paling umum (dari `component.md`) — jadi identitas koleksi.
2. **Batch 2**: #3 Kawaii untuk media sosial + #5 untuk badge skill platform.
3. **Batch 3**: #7 Holographic edisi terbatas per komponen flagship sebagai reward.
