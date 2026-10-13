# Pemeriksaan sampel awal

Sampel ini ditinjau oleh **asisten AI** pada ekspor `youtube_comments_3.csv` dengan SHA-256 `9daeff64fce6065f5291464993622586bd3ec5eed2095be31c3110cbefc20ada`. Ini adalah telaah eksploratif, **bukan label manusia independen** dan bukan data uji untuk mengklaim akurasi sentimen. CSV review hanya memuat `row_id` dan label telaah; teks komentar tetap berada di CSV sumber.

## Komentar bertanda tanya

`question_spotcheck.csv` berisi 35 komentar yang dipilih acak (`random_state=42`) dari 417 komentar dengan `?` setelah pembersihan. Kategorinya:

- `factual_information`: meminta informasi yang berpotensi dijawab secara faktual.
- `interpretation_discussion`: meminta pendapat atau penjelasan cerita/perilaku.
- `social_or_rhetorical`: candaan, pujian, atau sapaan berbentuk pertanyaan.
- `quoted_question`: tanda tanya berada dalam kutipan percakapan.
- `promotion_noise`: promosi yang tampak tidak relevan dengan diskusi.
- `unclear`: maksudnya belum dapat dipastikan.

Dalam sampel ini, **8/35** ditandai sebagai pertanyaan faktual dan **6/35** sebagai promosi yang tampak tidak relevan. Sampel kecil ini tidak digunakan untuk memperkirakan proporsi seluruh 417 komentar. Pemeriksaan oleh penilai manusia tetap diperlukan sebelum membuat FAQ.

## Sentimen

`sentiment_spotcheck.csv` berisi 36 komentar: enam dari tiap kombinasi `has_sheila` (ya/tidak) dan label aturan (`pos`, `neg`, `neu`), dipilih dengan `random_state=42`. `mixed_or_unclear` dipakai bila nada tidak tunggal atau tidak cukup jelas. Desain sampel sengaja seimbang menurut label aturan, sehingga tidak mewakili distribusi sentimen dataset.

Pada telaah awal, **5/36** diberi `mixed_or_unclear`. Di antara **31** kasus lainnya, label telaah berbeda dari aturan pada **11** kasus. Contoh penyebabnya adalah negasi, ejaan informal, dan komentar panjang dengan nada campuran. Angka ini adalah **indikator masalah**, bukan tingkat kesalahan populasi atau ukuran performa model.

Langkah validasi berikutnya adalah penilaian independen dengan panduan label, sebaiknya oleh dua orang. Simpan label tersebut sebagai `manual_labels.csv` lokal, lalu jalankan `Try_model.ipynb`. Jangan memasukkan label dari kedua file spot-check ini sebagai ground truth.
