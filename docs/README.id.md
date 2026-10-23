# Copilot Agent Hub dan Pelatihan T1: Panduan Pengguna

[English](../README.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [ไทย](README.th.md) · **Bahasa Indonesia** · [Tiếng Việt](README.vi.md)

Aplikasi web lokal ini mengajarkan karyawan untuk membangun **satu agen Microsoft 365 Copilot dengan satu tujuan**, mengujinya, dan menggunakannya dengan aman. Setelah pelatihan, aplikasi ini menjadi satu pintu utama untuk agen Copilot di organisasi: registri agen dengan tinjauan tata kelola, papan ide, permintaan lisensi, jaringan coach, pustaka prompt, wawasan adopsi, dan tolok ukur terhadap perusahaan terdepan.

Aplikasi berjalan di PC mana pun yang memiliki Python. Tidak perlu memasang apa pun dan tidak perlu koneksi internet; semua data disimpan dalam satu file SQLite. Seluruh aplikasi tersedia dalam **bahasa Inggris, Jepang, Tionghoa Sederhana, Thai, Indonesia, dan Vietnam**.

## Memulai

1. Pasang **Python 3.8 atau lebih baru** dari <https://www.python.org/downloads/>. Di Windows, centang *Add Python to PATH* saat penyiapan.
2. Unduh atau kloning folder ini.
3. Jalankan aplikasi:
   - **Windows:** klik dua kali `start_windows.bat`
   - **macOS / Linux:** jalankan `./start_mac_linux.sh`
   - **Atau dari terminal mana pun:** `python app.py`
4. Browser akan membuka <http://127.0.0.1:8000>. Saat pertama kali dijalankan, buat akun administrator.
5. Peserta memilih **Buat akun Anda** di halaman masuk dan mendaftar dengan ID karyawan.

Untuk menghentikan aplikasi, tekan `Ctrl+C` di jendela terminal (atau tutup jendelanya).

## Mengganti bahasa

Setiap halaman (termasuk halaman masuk) memiliki menu **Bahasa** di bagian atas. Pilihan Anda akan diingat.

Layar, pelajaran, soal kuis dan penjelasannya, langkah lab, templat, glosarium, tabel tolok ukur, notifikasi, dan sertifikat semuanya diterjemahkan. Dua hal sengaja dibiarkan dalam bahasa Inggris:

- **Label antarmuka Microsoft** seperti *New agent*, *Configure*, *Try it*, *Can chat*, dan *Settings > Personalization*. Peserta melihat label ini di Microsoft 365 Copilot, jadi kursus menggunakannya persis sama.
- **Judul halaman sumber Microsoft Learn**, agar fasilitator dapat menemukan halaman aslinya.

Di halaman Templat, setiap templat yang diterjemahkan juga menampilkan **Versi asli bahasa Inggris**, karena sebagian organisasi mewajibkan instruksi agen ditulis dalam bahasa Inggris. Teks yang diketik administrator (pertanyaan khusus organisasi, pedoman penggunaan) ditampilkan sesuai yang ditulis.

## Panduan untuk peserta

1. Di **beranda**, lihat kemajuan dan langkah berikutnya.
2. Di **Kursus saya**, ikuti kursus inti (10 modul, 29 pelajaran, sekitar 150 menit). Setelah membaca setiap pelajaran, tekan *Tandai pelajaran selesai*. Jika waktu terbatas, gunakan rute inti 60 menit yang dijelaskan di pelajaran 1.3.
3. Setiap modul diakhiri **kuis** singkat. Jawaban yang benar dan penjelasannya langsung tampil setelah dikirim, dan Anda boleh mencoba berulang kali.
4. Di **Piagam agen saya**, rencanakan tujuan, apa yang dilakukan dan tidak dilakukan, serta sumber pengetahuan agen. Aplikasi menyusun draf instruksi agen dari piagam Anda, dan agen bisa langsung didaftarkan di pusat agen.
5. Buka halaman **Lab** sambil mengerjakan 12 langkah di Microsoft 365 Copilot, lalu centang setiap langkah ketika "Selesai jika" terpenuhi. Langkah 1 sampai 10 wajib.
6. **Asesmen akhir** mengambil 15 soal dari bank soal berisi 58 soal, selalu termasuk 3 soal cek pengetahuan utama. Nilai lulus default 80%.
7. Setelah semua pelajaran, langkah lab 1 sampai 10, dan asesmen akhir selesai, **Sertifikat** Anda terbuka. Sertifikat dapat dicetak atau disimpan sebagai PDF.

Kerjakan **Cek keterampilan** (sekitar 2 menit) untuk mendapatkan rekomendasi modul. Di **Jalur belajar**, lihat level builder 1 sampai 3 dan cakupan berbagi yang terbuka di setiap level. **Jalur pemimpin** untuk manajer dan **Jalur coach** untuk coach bersifat opsional.

**Perangkat** berisi templat dengan tombol salin, kartu referensi cepat yang bisa dicetak, glosarium, referensi Microsoft, panduan fasilitator, serta halaman kebijakan dan bantuan.

## Cara menggunakan Pusat agen

| Fitur | Cara menggunakan |
|---|---|
| **Registri agen** | Setiap agen yang dibagikan kepada orang lain didaftarkan dengan tujuan, pemilik, tingkat, sumber pengetahuan, sensitivitas data, cakupan berbagi, satu KPI dengan nilai dasar, hasil uji, dan tanggal tinjauan. Sebelum membangun, cari di katalog yang disetujui apakah sudah ada agen yang dapat digunakan ulang. |
| **Tinjauan tata kelola** | Agen yang akan dibagikan ke tim atau seluruh organisasi, atau yang menggunakan data rahasia, masuk ke antrean tinjauan coach dan diperiksa dengan daftar 8 poin. Tingkat 3 dan 4 (bertindak atas data atau secara otonom) ditinjau oleh CoE. Pengaju harus memiliki sertifikat T1. |
| **Tinjauan nilai 90 hari** | Agen yang disetujui mendapat tanggal tinjauan. Pemilik mencatat hasil KPI, dan agen tanpa nilai yang terukur dipensiunkan. |
| **Papan ide** | Posting tugas yang bisa dibantu Copilot, beri suara, dan berkomentar. Agen yang dibangun dari sebuah ide ditautkan kembali ke ide tersebut. |
| **Permintaan lisensi** | Tim meminta kursi Microsoft 365 Copilot dengan kasus penggunaan dan perkiraan jam yang dihemat. CoE menyetujuinya secara bergelombang, mulai dari nilai harapan tertinggi. |
| **Komunitas** | Direktori coach dengan jam konsultasi, acara (promptathon, pamer karya, pelatihan langsung), dan pustaka prompt yang dinilai. |
| **Tanya CoE** | Kirim pertanyaan tentang kebijakan, data, lisensi, dan insiden. Pedoman penggunaan dan aturan data ada di halaman yang sama. |
| **Mencatat jam yang dihemat** | Catat jam yang dihemat setiap minggu di beranda Pusat agen. |
| **Notifikasi** | Terima hasil tinjauan, keputusan lisensi, komentar pada ide, dan jawaban dari CoE. |

## Panduan untuk coach

- Targetkan sekitar 1 coach per 60 karyawan (sekitar 170 untuk 10.000 karyawan).
- Tulis jam konsultasi di profil Anda agar tampil di direktori komunitas.
- Di **Antrean tinjauan**, periksa agen yang akan dibagikan ke tim atau organisasi. Baca tujuan, tingkat, sumber pengetahuan, sensitivitas data, dan hasil uji, minta tautan obrolan dari pemilik, lalu jalankan tiga pengujian sendiri.
- Anda hanya dapat menyetujui jika setiap item daftar periksa terpenuhi. Jika tidak, pilih *Minta perubahan* dan jelaskan apa yang harus diubah. Anda tidak dapat meninjau agen Anda sendiri.

## Panduan untuk administrator (CoE)

- **Ikhtisar**: jumlah karyawan yang dimuat, yang tersertifikasi, sedang belajar, dan belum mulai; rata-rata nilai akhir dan masukan; tingkat sertifikasi per departemen; dan corong modul.
- **Peserta**: cari dan saring, edit detail, atur ulang kata sandi, atau *Jadikan orang ini coach*.
- **Impor karyawan**: unggah CSV (`associate_id, name, email, department, location`). Impor ulang memperbarui detail dan mempertahankan kemajuan.
- **Ekspor CSV**: laporan kemajuan lengkap, serta bank soal beserta jawabannya dalam satu atau semua bahasa.
- **Bank soal**: diurutkan dari tingkat jawaban benar terendah. Nonaktifkan soal atau tambahkan soal khusus organisasi.
- **Pengaturan**: nama organisasi, nilai lulus, dan pedoman penggunaan organisasi Anda (jika kosong, pedoman awal yang sudah diterjemahkan ditampilkan).
- **Wawasan** dan **Tolok ukur**: lihat pelatihan, agen, ide, lisensi, dan jam yang dihemat dalam satu dasbor, dan bandingkan dengan target yang disesuaikan dengan jumlah karyawan.

## Peluncuran untuk 10.000 karyawan

- **Muat karyawan lebih dulu**: masukkan daftar dari bagian SDM ke templat CSV lalu impor, atau jalankan `python app.py import-users associates.csv`.
- **Satu database untuk semua**: jalankan `python app.py --host 0.0.0.0 --port 8000` di mesin yang dapat diakses dari intranet. Aplikasi menggunakan HTTP, jadi buka hanya di jaringan internal tepercaya, atau letakkan di belakang reverse proxy HTTPS organisasi. Konsultasikan dengan TI terlebih dahulu.
- **Cadangan**: semua data ada di `data/training.db`. Salin file ini saat aplikasi dihentikan.

## Daftar perintah

```text
python app.py                          Jalankan aplikasi (membuka browser)
python app.py --port 8080 --no-browser Gunakan port lain, dan jangan buka browser
python app.py --host 0.0.0.0           Dengarkan di jaringan (lihat catatan peluncuran di atas)
python app.py create-admin             Tambahkan administrator, atau naikkan akun yang sudah ada
python app.py import-users FILE.csv    Impor atau perbarui karyawan dari CSV
python app.py export FILE.csv          Tulis laporan kemajuan ke CSV
python app.py reseed                   Muat ulang konten kursus setelah mengedit training/content.py
python app.py demo-data 500            Tambahkan 500 peserta DEMO fiktif untuk mencoba
python app.py i18n-extract --check     Tampilkan jumlah terjemahan yang kurang di setiap bahasa
python app.py i18n-extract --missing id  Daftar teks bahasa Inggris yang belum diterjemahkan ke bahasa Indonesia
```

Gunakan `demo-data` hanya pada database uji.

## Memperbarui konten dan terjemahan

1. Edit teks bahasa Inggris di `training/content.py` dan `training/blocks.py`.
2. Jalankan `python app.py reseed`. Kemajuan dan riwayat kuis peserta tetap tersimpan.
3. Jalankan `python app.py i18n-extract --check` untuk melihat teks yang diubah dan belum diterjemahkan di setiap bahasa, lalu tambahkan terjemahannya di `training/locales/`. Sampai terjemahan ditambahkan, teks bahasa Inggris yang ditampilkan.
4. Mulai ulang aplikasi.

**Sebelum menyampaikan kursus**, fasilitator sebaiknya:
- Membuka setiap halaman Microsoft Learn di halaman Referensi dan memastikan langkah dan label masih sesuai dengan tenant Anda. Microsoft sering mengubah tampilan Copilot.
- Menambahkan tangkapan layar terverifikasi milik organisasi Anda untuk modul 4. Aplikasi tidak menyertakan tangkapan layar Microsoft.
- Memeriksa ulang sumber studi kasus dan tolok ukur sebelum menyajikannya.
- Mengganti pedoman penggunaan awal dengan pedoman yang telah disetujui di Admin → Pengaturan.

## Cakupan dan batasan

- Aplikasi ini tidak terhubung ke Microsoft 365, sehingga tidak dapat melihat agen di tenant Anda atau memastikan peserta benar-benar membangun agen. Lab dan registri bersifat laporan mandiri, dan coach memverifikasi melalui tautan obrolan saat meninjau.
- Angka tolok ukur berasal dari sumber publik perusahaan, vendor, dan media yang diberi tanggal di aplikasi, dan tidak diaudit secara independen.
- Tidak ada sistem masuk tunggal (Microsoft Entra ID). Akun dikelola di dalam aplikasi.
- Terjemahan disiapkan untuk proyek ini. Seperti materi pelatihan lainnya, minta fasilitator penutur asli di setiap negara meninjaunya sebelum peluncuran.
