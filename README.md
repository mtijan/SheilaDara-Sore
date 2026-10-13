# Apa yang bisa dibaca dari komentar YouTube tentang Sheila Dara dan *Sore*?

**Portofolio analisis data dan teks berbahasa Indonesia.** Saya menganalisis **6.418 observasi komentar dari 48 video YouTube** untuk melihat seberapa sering Sheila Dara disebut, bagaimana panjang komentarnya, dan apa yang dapat disimpulkan secara hati-hati dari pola tersebut.

**Peran saya:** pembersihan data, analisis eksploratif, visualisasi, pipeline Python, dan dokumentasi.

**Alat:** Python, Pandas, scikit-learn, notebook, SVG.
**Mulai dari:** [notebook analisis dengan hasil yang sudah tampil](Sheila_Dara_Sore_YT_Sentiment.ipynb).

## Temuan utama

**1. Sekitar satu dari enam komentar menyebut Sheila.** Ada **1.046 dari 6.418 observasi (16,30%)** yang memuat kata “Sheila”. Angka ini menyatakan frekuensi penyebutan dalam ekspor, bukan proporsi seluruh penonton atau penggemar.

![Diagram batang jumlah komentar: 1.046 menyebut Sheila dan 5.372 komentar lainnya.](assets/mention.svg)

**2. Komentar yang menyebut Sheila cenderung lebih panjang.** Rata-ratanya **21,01 token**, dibanding **14,12 token** pada komentar lain. Median masing-masing **13** dan **8** token. Pada 11 video yang memiliki sedikitnya 10 komentar di setiap kelompok, arah perbedaannya sama.

![Diagram batang rata-rata token per komentar: 21,01 untuk komentar yang menyebut Sheila dan 14,12 untuk komentar lain.](assets/tokens.svg)

**3. Sebagian besar observasi terkumpul di sedikit video.** Lima video dengan komentar terbanyak menyumbang **71,72%** observasi. Karena itu, angka gabungan saja kurang cukup untuk menggambarkan seluruh 48 video. [Laporan per video tersedia sebagai CSV](reports/video_summary.csv).

![Diagram batang persentase observasi: lima video teratas 71,72 persen dan 43 video lainnya 28,28 persen.](assets/concentration.svg)

**4. Aturan sentimen memberi sinyal awal, belum kesimpulan opini publik.** Aturan kata menandai **26,96%** komentar yang menyebut Sheila sebagai positif, dibanding **14,50%** komentar lain. Perbedaan ini konsisten arahnya pada 11 video yang memenuhi batas sampel di atas. Namun, aturan belum dinilai terhadap label manusia, sehingga angka ini **tidak boleh dibaca sebagai akurasi model atau bukti sebab akibat**.

![Diagram batang persentase label positif menurut aturan kata: 26,96 persen dan 14,50 persen; label belum divalidasi manusia.](assets/sentiment.svg)

## Insight dan langkah berikutnya

- **Penyebutan Sheila tidak mendominasi jumlah komentar, tetapi percakapannya lebih panjang.** Selisih rata-rata **6,89 token** dan median **5 token** menunjukkan ada bahan untuk dibaca lebih jauh. Tinjau sampel komentar secara manual untuk menemukan tema yang berulang; panjang komentar sendiri belum menjelaskan alasan orang menulisnya.
- **Sinyal positif masih berupa hipotesis.** Selisih **12,46 poin persentase** berasal dari aturan kata yang belum divalidasi. Beri label pada sampel bersama penilai manusia sebelum menyebut respons audiens sebagai “positif”. [Telaah awal berbantuan asisten](reviews/README.md) hanya membantu menemukan calon kesalahan aturan.
- **Pola gabungan sangat dipengaruhi lima video.** Karena **71,72%** observasi berasal dari lima video, baca [hasil per video](reports/video_summary.csv) dan kumpulkan sampel yang lebih seimbang sebelum memperluas kesimpulan ke percakapan YouTube secara umum.

## Kesimpulan

Dalam ekspor ini, Sheila disebut pada **16,30%** observasi. Komentar yang menyebutnya cenderung lebih panjang daripada komentar lain; pola itu juga terlihat pada **11 video** yang memiliki cukup observasi di kedua kelompok. Label positif berbasis aturan lebih sering muncul pada kelompok tersebut, tetapi **belum membuktikan sentimen publik yang sebenarnya**. Langkah paling berguna selanjutnya adalah membaca tema komentar per video dan memvalidasi sentimen dengan penilai manusia.

Perhitungan, perbandingan dalam video, dan tabel pendukung dapat dilihat langsung di [notebook analisis](Sheila_Dara_Sore_YT_Sentiment.ipynb).
