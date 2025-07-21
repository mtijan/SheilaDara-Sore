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
## 6. ## 🧩 Topic Clusters (K‑Means v0)

| Cluster | Quick Meaning | Top Keywords (sample) | Comments | % of All | % Mention Sheila |
|---------|---------------|-----------------------|----------|----------|------------------|
| **Plot / Ending** | Storyline & ending talk | *alur, ending, nanggung* | **3 107** | **50.5 %** | **9.40 %** |
| **Visual / Production** | Cinematography & production value | *visual, look, sinematografi* | **1 129** | **18.4 %** | **8.86 %** |
| **Sheila & Vidi Duo / Greetings** | Fans greeting both hosts | *sheila, vidi, kak* | **472** | **7.7 %** | **45.76 %** |
| **Humor / Slang** | Jokes & casual banter | *bang, lu, slang* | **321** | **5.2 %** | **5.30 %** |
| **Access / Where to Watch** | “Link please” & platform Q&A | *nonton di mana, link* | **301** | **4.9 %** | **95.68 %** |
| **Pace / Critique** | Complaints about tempo | *lambat, pace, boring* | **222** | **3.6 %** | **35.59 %** |
| **Short Praise** | One‑liner hype (“keren!”) | *keren, mantap, bgt* | **193** | **3.1 %** | **0.52 %** |
| **Sheila‑Focused** | Direct comments about Sheila | *sheila, cantik, dara* | **170** | **2.8 %** | **9.41 %** |
| **Acting / Chemistry** | Acting quality & on‑screen chemistry | *akting, chemistry, natural* | **119** | **1.9 %** | **16.81 %** |
| **Personality & Introvert Chemistry** | “Duo introvert” vibe | *introvert, ngobrol, nyambung* | **113** | **1.8 %** | **13.27 %** |

> *Hasil Berasal dari `cluster_stats` (run date : 2025‑07‑21).*  
<!-- > These clusters are still coarse; we’ll re‑run after adding extra stop‑words and manual checks. -->

<!-- > **Cara isi angka ➜** jalankan `cluster_stats` lalu hitung:  
> `comments`, `pct_all`, `sheila_share_pct` → copas ke tabel. -->

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


## 🚀 Snapshot Insights (v0)

| Take‑away | Data point | So what? |
|-----------|------------|----------|
| **Story & ending dominate the chat** | *Plot/Ending* cluster holds **50.5 %** of all 6 147 comments (3 107 posts) while only **9.4 %** name‑checks Sheila. | Narrative pacing is what viewers talk about most, not cast. |
| **Visual quality is a clear strength** | *Visual/Production* = **18.4 %** of comments; sentiment largely positive. | Cinematography can be spotlighted in promos & trailers. |
| **Duo Sheila × Vidi sparks big love** | “Sheila & Vidi” greetings cluster = **7.7 %** of comments with **45.8 %** explicit Sheila mentions. | Pairing drives engagement—good content lever. |
| **Where‑to‑watch questions are loud** | *Access/WhereToWatch* is small (**4.9 %**) but **95.7 %** of those posts call out Sheila. | Drop a pinned FAQ or link to cut repetitive neutral noise. |
| **Pacing criticism is concentrated** | *Pace/Critique* only **3.6 %** of volume yet **35.6 %** mention Sheila while complaining. | Address tempo issues to avoid eroding goodwill. |
| **“Keren!” one‑liners skew the mood** | *Short Praise* = **3.1 %**, 90 %+ positive bursts. | Good for topline positivity, but depth is shallow—don’t over‑weight. |

### TL;DR
*Half the conversation is about plot & ending; visual flair is widely praised.  
Fans love the Sheila–Vidi combo, but still nag about where to watch and pacing hiccups.  
These findings are rule‑based & cluster‑derived — manual labels and ML fine‑tuning come next.*