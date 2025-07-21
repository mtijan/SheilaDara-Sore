# SheilaDara-Sore

*“Seluruh metrik sentimen saat ini masih berbasis rule lexicon awal dan belum melalui validasi manual; interpretasi bersifat indikatif, bukan final.”*

> **Status:** *Preliminary Insights (v0)* – Sentimen masih berbasis aturan (rule-based) dan **belum** divalidasi manual atau model ML lanjut (IndoBERT).
> > **Waktu Pengambilan Data:** Data diambil pada rentang waktu satu bulan *19 Juli 2025 - 19 Juni 2025*

---

## 1. Tujuan Proyek

1. Memetakan perilaku komentar penonton (volume, partisipasi, pola ekspresi).
2. Mengukur fokus dan intensitas keterlibatan terhadap figur **Sheila Dara**.
3. Membangun *baseline* sentimen + rancangan awal **Sheila Impact Index** (versi v0).
4. Menyusun landasan untuk pengembangan model sentimen berbasis Machine Learning (IndoBERT) di tahap berikutnya.

---

## 2. Sumber & Struktur Data

- Sumber: Komentar publik (YouTube / platform lain) yang sudah diekstraksi dan digabung.
- Format akhir (after cleaning): satu baris = satu komentar.
- Kolom utama:
  | Kolom | Deskripsi Singkat |
  |-------|-------------------|
  | `username` | Username ter-normalisasi |
  | `comment_raw` | Teks asli (termasuk emoji) |
  | `comment_clean` | Versi dibersihkan ringan (URL dihapus, lowercase) |
  | `comment_plain` | Versi alfanumerik (untuk tokenisasi sederhana) |
  | `token_len` | Jumlah token (kata) |
  | `emoji_count` | Jumlah emoji di komentar |
  | `has_sheila` | Boolean: apakah menyebut “sheila” / “sheila dara” |
  | `suspect_user` | Heuristik akun mencurigakan (numeric-heavy) |
  | `sentiment_score` | Skor numerik rule-based |
  | `sentiment_label` | Kategori: `pos` / `neg` / `neu` |

---

## 3. Proses Cleaning (Ringkas)

1. Standardisasi nama kolom, drop baris kosong untuk `username` & `comment`.
2. Normalisasi username (hapus `@`, lowercase, hilangkan spasi & karakter kontrol).
3. Simpan dua versi teks (`comment_clean` & `comment_plain`) agar:
   - `clean` mempertahankan emoji untuk fitur emosi.
   - `plain` memudahkan tokenisasi & pencocokan leksikon.
4. Hilangkan duplikat berdasarkan pasangan `(username, comment_raw)`.
5. Buat fitur: panjang karakter/token, flag pertanyaan (`?`), emoji, flag sebut “Sheila”.
6. Tandai akun mencurigakan (rasio digit > 50% & panjang > 10, atau blok digit panjang).

---

## 4. Metodologi Sentimen (Rule-Based v0)

| Komponen | Penjelasan |
|----------|-----------|
| Lexicon kata positif & negatif | Daftar kata/ungkapan umum (slang + standar) |
| Bigram frasa penting | Misal: `akting natural`, `ending nanggung` |
| Emoji positif/negatif | ❤️ 😍 😂 👍 vs 😒 😔 😡 👎 |
| Negasi | Membalik polaritas kata berikutnya: `tidak`, `gak`, `kurang`, `bukan` |
| Intensifier | Menambah bobot (misal: `banget`, `sangat`, `bgt`) |
| Skor akhir | Penjumlahan bobot → >0 = `pos`, <0 = `neg`, 0 = `neu` |

> *Keterbatasan:* Belum mengenali sarkasme, ironi halus, konteks multi-kalimat, atau kalimat campuran +/– yang kompleks.

---


## 5. Metrik Kunci  

| Metrik | Nilai | Keterangan |
|--------|-------|------------|
| Total komentar | `[TOTAL_COMMENTS]` | Setelah cleaning |
| Pengguna unik | `[UNIQUE_USERS]` | Partisipasi |
| Share top 10 user | `[TOP10_SHARE]%` | Dominasi partisipasi |
| Komentar sebut “Sheila” | `[SHEILA_SHARE]%` | Fokus figur |
| Rata‑rata token (Sheila / Non) | `[AVG_TOKEN_SHEILA] / [AVG_TOKEN_NON]` | Depth |
| Rata‑rata emoji (Sheila / Non) | `[EMOJI_SHEILA] / [EMOJI_NON]` | Ekspresivitas |
| Sentimen global (pos/neg/neu) | `[POS_GLOB]% / [NEG_GLOB]% / [NEU_GLOB]%` | Rule‑based |
| Sentimen Sheila subset | `[POS_SHE]% / [NEG_SHE]% / [NEU_SHE]%` | Rule‑based |
| Positive lift Sheila | `[POS_LIFT]` pp | POS_SHE – POS_GLOB |
| Emoji lift | `[EMOJI_LIFT]` | Rata‑rata emoji selisih |
| Sheila Impact v0 | `[IMPACT_V0]` | Formula awal |
| Komentar bertanya | `[QUESTION_PCT]%` | Potensi FAQ |
| Suspect user | `[SUSPECT_PCT]%` | Potensi bias |
| Top 5 kata global | `[K1, K2, K3, K4, K5]` | Unigram |
| Top 5 kata Sheila | `[S1, S2, S3, S4, S5]` | Unigram subset |
| Top emoji | `[E1, E2, E3…]` | Tone visual |

---

<!-- ## 6. Insight Sementara (Narasi v0)

> **Volume & Partisipasi:** Dataset memuat **[TOTAL_COMMENTS]** komentar dari **[UNIQUE_USERS]** akun. Pola distribusi menunjukkan long tail dengan kontribusi top 10 user sebesar **[TOP10_SHARE]%**—belum indikasi dominasi ekstrem, tetapi tetap dipantau.

> **Fokus Figur:** Sekitar **[SHEILA_SHARE]%** komentar menyebut “Sheila”. Ini menandakan figur tersebut menjadi salah satu pusat perhatian audiens.

> **Kedalaman & Ekspresivitas:** Komentar yang menyebut Sheila lebih panjang (**[AVG_TOKEN_SHEILA] vs [AVG_TOKEN_NON] token**) dan menggunakan emoji lebih sering (**[EMOJI_SHEILA] vs [EMOJI_NON]**). Ini mengindikasikan *engagement emosional lebih intens* saat figur dibahas.

> **Tema Bahasa:** Global didominasi kata: **[K1, K2, K3, K4, K5]**. Subset Sheila menonjol pada: **[S1, S2, S3, S4, S5]** → fokus pada aspek akting, chemistry, dan daya tarik personal.

> **Sentimen (Preliminary – Rule-Based):** Global: **[POS_GLOB]% pos**, **[NEG_GLOB]% neg**, **[NEU_GLOB]% neu**. Subset Sheila: **[POS_SHE]% pos** (lift +**[POS_LIFT]**), **[NEG_SHE]% neg**, sisanya netral. *Angka dapat berubah setelah validasi manual & model.*

> **Ekspresi Visual:** Emoji dominan seperti **[E1, E2, E3]** mendukung tone apresiatif (indikatif, bukan konklusif).

> **Sheila Impact v0:** Skor awal **[IMPACT_V0]** (gabungan share Sheila, positive lift, emoji expressiveness). Ini masih *indikator internal*, bukan indeks final.

> **Informasi vs Opini:** Sekitar **[QUESTION_PCT]%** komentar berupa pertanyaan; peluang membuat FAQ / konten edukatif (misal platform nonton, jadwal rilis).

> **Kualitas Data:** Proporsi akun mencurigakan **[SUSPECT_PCT]%** → saat ini **[rendah/sedang/tinggi]**, belum perlu filtering agresif.

> **Kesimpulan Sementara:** Figur Sheila memicu keterlibatan lebih dalam & ekspresif; tone awal condong ke arah positif. Diperlukan validasi lebih lanjut secara manual (jika dibutuhkan) agar klaim sentimen lebih kredibel. -->

---
## 6. 🧩 Topic Clusters (K‑Means v0)

| Cluster | Quick Meaning | Top Keywords | Comments | % of All | % Mention Sheila |
|---------|---------------|--------------|----------|----------|------------------|
| **Short Praise / Hype** | Spontan “keren banget” | *keren, keren banget, mantap* | `[C1]` | `[P1]%` | `[S1]%` |
| **Sheila Appearance & Look** | Komentar soal penampilan | *sheila dara, cantik* | `[C2]` | `[P2]%` | `[S2]%` |
| **Cross‑Reference Films** | Bandingkan dgn film lain | *partikelir, one cut of the dead* | `[C3]` | `[P3]%` | `[S3]%` |
| **General / Neutral** | Info nonton, pernyataan biasa | *nonton, film ini, sore* | `[C4]` | `[P4]%` | `[S4]%` |
| **Character Dynamics (Kukuh)** | Bahas Kukuh vs Sheila | *kukuh, lawan sepadan* | `[C5]` | `[P5]%` | `[S5]%` |
| **Guest Requests** | “Bang undang …” | *undang, densu, radit* | `[C6]` | `[P6]%` | `[S6]%` |
| **Podcast / Episode Context** | Podhub & lineup tamu | *podhub, vidi, datang* | `[C7]` | `[P7]%` | `[S7]%` |
| **Personality / Introvert Chemistry** | Duo introvert ngobrol | *introvert, nyambung, seru* | `[C8]` | `[P8]%` | `[S8]%` |

> **Cara isi angka ➜** jalankan `cluster_stats` lalu hitung:  
> `comments`, `pct_all`, `sheila_share_pct` → copas ke tabel.

**Kenapa penting?**  
- Kita tahu topik pujian cepat mana yang paling ramai.  
- Cluster “Guest Requests” = backlog ide kolaborasi.  
- Kritik terfokus di cluster “Character Dynamics” – bahan evaluasi cerita.

---


## 7. Sheila Impact v0 – Formula

```text
Impact_v0 = 0.4 * SheilaMentionShare(%) 
          + 0.4 * max(0, PositiveLift_pp) 
          + 0.2 * max(0, EmojiLift * 10)
“Cluster ‘Short Praise’ menyumbang [P1]% komentar dengan 90% sentimen positif.”)*