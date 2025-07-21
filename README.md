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

Impact_v0 = 0.4 * SheilaMentionShare(%) 
          + 0.4 * max(0, PositiveLift_pp) 
          + 0.2 * max(0, EmojiLift * 10)
“Cluster ‘Short Praise’ menyumbang [P1]% komentar dengan 90% sentimen positif.”)*

---

## 🚀 Snapshot Insights (v0)
| Take‑away | Data point | So what? |
|-------------|-----------------|---------------|
| **Cerita & ending paling ramai dibahas** | Klaster *Plot/Ending* menampung **50,5 %** dari 6.147 komentar (3.107 post); hanya **9,4 %** di klaster ini yang menyebut Sheila. | Pace & akhir cerita jadi sorotan utama penonton, melebihi topik mengenai aktor. |
| **Visual jadi kekuatan jelas** | *Visual/Production* = **18,4 %** komentar; mayoritas bernada positif. | Sinematografi layak di‑highlight di materi promo. |
| **Duet Sheila × Vidi disukai** | Klaster “Sheila & Vidi” = **7,7 %** komentar dengan **45,8 %** eksplisit menyebut Sheila. | Kolaborasi ini memicu engagement—potensi konten lanjutan. |
| **Pertanyaan “nonton di mana?” cukup populer** | *Access/WhereToWatch* memang kecil (**4,9 %**), tapi **95,7 %** komentarnya menyebutkan nama Sheila. | Buat FAQ / pinned comment untuk menekan pertanyaan berulang. |
| **Kritik tempo terkonsentrasi** | *Pace/Critique* cuma **3,6 %** volume, namun **35,6 %** menyebut Sheila sambil memberikan kritik. | Perbaikan ritme cerita perlu diprioritaskan agar reputasi tetap positif. |
| **One‑liner “keren!” mewarnai sentimen** | *Short Praise* = **3,1 %**, >90 % positif singkat. | Memberikan sinyal bagus dan bernilai optimis, tapi kurang mendalam sehingga terlalu susah hanya menilai berdasarkan klaster ini saja. |

### TL;DR
*Setengah percakapan penonton fokus ke alur & ending; visual dipuji.  
Duet Sheila–Vidi menambah antusiasme, tetapi masih banyak yang menanyakan platform nonton dan mengeluhkan tempo cerita.  
Semua temuan berbasis rule‑based & klaster—label manual dan model ML akan memperkuat angka di fase berikut.* 

### Sampel Comment Each Cluster

=== Access/WhereToWatch ===
- part vidi bilang " punya istri sheila dara siapa sih yang gaa insecure" terdengar alami dan nyentuh banget walupun ngungkapinnya se-santai i
- Senang banget akhirnya Sheila Dara hadir di podhub, seru, lucu liat chemistry Vidi dan Sheila. Saya bukan pecinta film drama romantis, tpi a
- sheila dara cantik banget sumpah, visualnya ngangenin, gak ngebosenin, gimana yang ngungkapinnya, udah ah pokoknya the best shiela, luv poko
- Episode paling favorit gua ada sheila dara, seneng banget sumpaaah... Ngakak terus... Sehat-sehat yah kalian semua... Happy terussss...
- Finally Akhirnya Podhub Berhasil Juga Ngundang Kak Sheila Dara .. gemeshhh

=== Acting/Chemistry ===
- emang idaman sih pasangan vidi ma sheila ini , ga selebai kya yg di umbar2 di publik , tapi aslinya saling sayang , saling suport , saling b
- Kocak banget mereka berdua ,kompak keren gw suka liat sheila wajahnya gak ngebosenin
- Sumpah Dara Cintanya beneran, ternyata sebelum Nikah Vidi udah sakit, dan Dara menerima , keren keren
- Om Ded tolong bikinin Adi program dong Keren ngehostnya, asik
- Aslinya gayanya Vidi kalah sama gayanya istri, kalah saing pantesan dilarang, emang gayanya keren banget

=== Humor/Slang ===
- OMM UNDANG DUTA S07 DONG!!!!
- Waaah....bang @denzu berjasa ini... Akhirnya...
- ini ke 6x nya gua tonton loh bang viiiiidiiiiiii
- Lihat sheila udah nih. Undang lagi om biar nyanyi bareng
- Sukses truuuuussss bang vidiiiiiii

=== Pace/Critique ===
- Gila sabtu ini gue bahagia banget,sheila dtg ke podhub,dan selucu itu dia.....bahagia bgt pasti kak vidi
- sesuai ekspektasi banget, liat sheila berkeliaran di podcast pasti ada di podhub dan ya finally worth to wait! seruuuu!!
- Parah wehh abis nonton ini gue bahagia banget,sheila dtg ke podhub,dan selucu itu dia.....bahagia bgt pasti kak vidi
- Yeahhhh.....   Akhirnya Ibu Negara di Podhub juga.  Pasti trending nih..  Semoga Next datang lagi ya jangan cuma pas mo promo film aja
- MASYA ALLAH... TERIMA KASIH SHEILA UDAH MAU DATENG KE PODHUB. DAN INI EPISODE TER TER TER TERFAVORITE YANG PASTI BAKAL GW TONTON RATUSAN KAL

=== Personality & Introvert Chemistry ===
- Guys,sheila itu introvert bukan ansos. Introvert itu kalo sm orang yg udh kenal dan akrab dia bakal seru juga. Beda kalo ansos yg emg bner2 
- sheilaa yang katanya introvert gak kalah energinya sama vidi di video ini
- orang introvert klo masuk podhub jdi awkward gak sih  aneh tapi lucu
- Extrovert fix ingetnya general introvert ingetnya emang yang detail
- introvert seasik ini woyyyy

=== Plot/Ending ===
- Baru Mulai aja udah pecahh  Makin betah sama konten nya
- WAIT?AKHIRNYAAAAA
- Pas nonton tu aq ketawa" pokoknya happy bgtttt.... Tapi pas baca komen aq tu kaya nyes bgt dihati komen " sahabat podhub tu positif n mbikin
- Podcast penuh tawa tp sedihh secara bersamaan dr awal smpe akhirr... Semangat yaa vid, aku  juga lagi survive sm penyakit ginjalku. Dan sllu
- adhi tuh cocok setiap di undang di podhub, seru banget pas ngomong dan joke nya ngena di semua jadi kayak nyambung. pinter pembawaannya, kel

=== Sheila & Vidi Duo / Greetings	 ===
- Om ded kaya seneng bangga bgttt lihat mereka bahagia adem ayem apalagi lihat vidi yang bener* full senyum ceria dan dengan bangganya cerita 
- Salut sama keterbukaan dan kejujuran Vidi & Sheila. Perjalanan cinta kalian itu bukti nyata kalau jodoh nggak akan kemana. Terima kasih suda
- Ya Allah, beri vidi kesehatan & panjang umur, Krn energy nya membahagiakan banyak org.
- Dari awal cuma mau nonton iseng, eh malah dapet pelajaran soal sabar, cinta, dan kehidupan. Sehat terus ya Vidi, Sheila, dan Om Deddy
- Terharu banget waktu denger sheila ngomong kurangnya vidi cuma bersinnya doang. Liat deh mata vidi itu terharu mau nangis dan aku jg berasa.

=== Sheila-Focused ===
- Seumur umur baru kali ini gua nonton podcast si kukuh sampe abis. Kemaren2 ga kuat gua sama ni orang ngeselin banget
- Kukuh biasanya chaos… tapi kali ini chaos-nya terstruktur karena Sheila juga sama gilanya
- Lah kok malah nyambung, kukuh menemukan lawan sepadan
- kali ini ngeliat kukuh jadi kelihatan lucu
- Dua orang pinter yg ngeselin  Seruuuu bangettt… Kuat banget Kukuh ditatap sama sheila

=== Short Praise ===
- No 8
- Trending no 1
- Best couple of the year sih
- Yandy Laurens is on his run to becoming one of the greatest Indonesian directors
- 4:59 Gua tebak film nomor 1 Bang Pandji adalah Jokowi adalah Kita (2014)

=== Visual/Production ===
- Senin pagi ini ak nonton pudhub.. Sore nya ak lagsung bawa team ak nonton film Sore Ka Sheila Dara...  Film nya bagus banget  Kaka keren ban
- kak Sheilaaa kak Vidiii, sukak bgt film "Sore" nya, dari trailer pun aku kehook dari premise ceritanya.. berasa balik lagi ke kualitas film-
- Bahagia sihhh, setelah minggu lalu nge-skip, berharap Sabtu ini baik dan ternyata lebih dari baik, karena yg dinanti selama ini, dan makin b
- "gue bersyukur Tuhan kasih karakter sore in real life dikehidupan gue"  setelah kak vidi ngomong gitu kepalaku langsung flashback ke film SO
- Finally, the wait is over. Ibu Negara akhirnya nongol di Podhub. Aku juga udah nonton film SORE tgl 10 kemarin. Filmnya keren parah, mind-bl

---