# GasGuard - Sistem Deteksi Kebocoran Gas LPG Berbasis IoT 
Mencegah terjadinya kebocoran gas dengan pemantauan dua titik secara berkala dan analisis tren
---
<p> Risiko kebocoran gas LPG senantiasa mengintai di lingkungan rumah tangga. GasGuard terinspirasi dari penelitian terdahulu yang telah mengembangkan deteksi das menggunakan sensor MQ-6, ESP32, alarm, dan notifikasi jarak jauh. Proyek ini berfokus pada pengembangan sistem yang dapat mengolah dan membandingkan pembacaan sensor dari dua titik berbeda demi meningkatkan akurasi. </p>

## Rancangan Sistem
Adapun sistem GasGuard dirancang terdiri dari:
<ol>
  <li><p><i> Edge Device:</i></p>
    <ol>
    <li> <p>ESP32 sebagai "otak" perangkat yang membaca input sensor, memproses data, mengambil keputusan, dan mengirim data ke <i>cloud.</i></p> </li>
    <li> <p>HP Android sebagai perangkat yang meanmpilkan  informasi sensor dan meneruskan data sensor ke pengguna.</p></li>
    </ol>
  </li>
  <li> <p>2 Buah Sensor MQ-6 di dua titik pemantauan yang berbeda, yaitu di area tabung gas dan ruangan dapur.</p>
  </li>
  <li> <p>Alarm <i>(buzzer)</i> sebagai aktuator yang  memberikan peringatan suara berdasarkan keputusan ESP32.</li></p>
  <li> <p>Komunikasi melalui WiFi dan MQTT.</p></li>
  <li> <p><i>Cloud</i> sebagai penerima dan penerus data sensor.</p></li>
</ol>
<p>Simulasi Sistem GasGuard menggunakan Wokwi dan PlatformIO. Pada simulasi, potensiometer digunakan sebagai pengganti nilai keluaran sensor gas.</p>
    
--

## Cara Kerja
    

### 1. ESP32 — Sistem Sensor

Pastikan ESP32 telah terhubung dengan dua sensor gas, buzzer, dan jaringan Wi-Fi. Program dapat dijalankan melalui Arduino IDE atau PlatformIO.

**Konfigurasi pin perangkat keras:**

| Komponen | Pin ESP32 | Fungsi |
|---|---|---|
| Sensor Gas 1 | GPIO 34 | Membaca data sensor di area tabung gas |
| Sensor Gas 2 | GPIO 35 | Membaca data sensor di area dapur |
| Buzzer | GPIO 25 | Memberikan alarm lokal |

Pada saat dijalankan, ESP32 menginisialisasi Serial Monitor dengan baud rate `115200`, mengatur buzzer dalam kondisi mati, lalu mencoba terhubung ke Wi-Fi `Wokwi-GUEST`.

Setelah itu, ESP32 mengatur koneksi MQTT menuju broker publik `broker.hivemq.com` melalui port `1883`. Apabila koneksi MQTT terputus, program akan mencoba menghubungkan kembali perangkat ke broker.

### 2. Pemrosesan Data Sensor

Setelah sistem berjalan, ESP32 membaca data analog dari kedua sensor secara berulang. Data tersebut diproses melalui beberapa tahapan.

### A. Pembacaan Sensor

ESP32 membaca nilai mentah menggunakan fungsi `analogRead()` pada GPIO 34 dan GPIO 35. Kedua nilai ini mewakili pembacaan sensor di area tabung gas dan area dapur.

### B. Moving Median Filter

Data mentah dari setiap sensor diproses menggunakan Moving Median Filter dengan ukuran jendela lima data (`WINDOW_SIZE = 5`).

Prosesnya adalah:
1. Memasukkan data terbaru ke dalam buffer sensor.
2. Mengurutkan lima data yang tersimpan.
3. Mengambil nilai tengah sebagai hasil filter.
4. Mengulangi proses ketika data sensor berikutnya diterima.

Hasilnya adalah `filtered1` untuk sensor tabung gas dan `filtered2` untuk sensor dapur. Penyaringan ini bertujuan mengurangi pengaruh gangguan atau perubahan pembacaan yang menyimpang.

### C. Evaluasi Tren dan Status

Sistem menghitung tren perubahan dengan membandingkan nilai hasil filter saat ini terhadap nilai hasil filter pada iterasi sebelumnya.

Rumus yang digunakan:

```text
trend1 = filtered1 - lastFiltered1
trend2 = filtered2 - lastFiltered2
```

Setelah tren dihitung, nilai sebelumnya diperbarui menggunakan pembacaan terbaru. Sistem kemudian menentukan status dengan urutan pemeriksaan berikut:

| Status | Kondisi pada kode | Respons Buzzer |
|---|---|---|
| `BAHAYA` | Salah satu nilai sensor lebih dari 2000 | Menyala |
| `WASPADA` | Tidak memenuhi kondisi BAHAYA, tetapi salah satu nilai sensor lebih dari 1200 atau tren salah satu sensor lebih dari 150 | Mati |
| `AMAN` | Tidak memenuhi kondisi BAHAYA maupun WASPADA | Mati |

**Urutan keputusan:** status `BAHAYA` diperiksa terlebih dahulu, kemudian `WASPADA`, dan terakhir `AMAN`. Dengan demikian, jika nilai sensor melewati 2000, status tetap `BAHAYA` meskipun kondisi WASPADA juga terpenuhi.

Ambang batas di atas merupakan parameter program dan perlu disesuaikan melalui kalibrasi serta pengujian sensor. Nilai ADC tidak langsung menunjukkan konsentrasi gas dalam ppm tanpa kalibrasi yang sesuai.

### 3. Perbandingan Nilai Sensor

Setelah data sensor difilter, sistem membandingkan nilai kedua titik pemantauan menggunakan fungsi `compareGasPoints()`.

Hasil perbandingan terdiri dari tiga kondisi:

- `TABUNG LEBIH TINGGI`: nilai `filtered1` lebih besar daripada `filtered2`.
- `DAPUR LEBIH TINGGI`: nilai `filtered2` lebih besar daripada `filtered1`.
- `KEDUA TITIK SAMA`: kedua nilai hasil filter sama.

Informasi perbandingan dicetak ke Serial Monitor untuk membantu pengamatan data sensor. Pada kode saat ini, informasi tersebut belum disertakan dalam payload MQTT sehingga belum dikirimkan sebagai field tersendiri ke dashboard HP.

### 4. Pengiriman Data ke MQTT

Setelah status keamanan ditentukan, ESP32 menyusun data hasil pemrosesan dalam format JSON. Data kemudian dikirimkan ke broker MQTT menggunakan fungsi `client.publish()`.

**Konfigurasi MQTT:**

- Broker: `broker.hivemq.com`
- Port: `1883`
- Topic: `gasguard/sensor/data`
- Interval pengiriman: sekitar 2 detik, mengikuti jeda pada program utama.

Contoh payload JSON:

```json
{
  "titik1": 1234,
  "titik2": 856,
  "status": "AMAN"
}
```

Keterangan:
- `titik1`: nilai sensor area tabung setelah difilter.
- `titik2`: nilai sensor area dapur setelah difilter.
- `status`: status keamanan hasil evaluasi sistem.

Angka pada contoh hanya ilustrasi struktur pesan, bukan hasil pengukuran aktual.

Jika pesan berhasil dipublikasikan, Serial Monitor menampilkan pesan `MQTT: Pesan berhasil dikirim ke broker`. Jika gagal, program menampilkan pesan kegagalan pengiriman.

### 5. Buzzer — Alarm Lokal

Buzzer yang terhubung ke GPIO 25 dikendalikan langsung oleh fungsi `evaluateGasStatus()`.

Perilaku buzzer pada kode terbaru adalah:

- **BAHAYA:** buzzer menyala (`HIGH`).
- **WASPADA:** buzzer mati (`LOW`).
- **AMAN:** buzzer mati (`LOW`).

Perlu diperhatikan bahwa status `WASPADA` pada versi kode ini hanya dikirim sebagai data MQTT dan ditampilkan di Serial Monitor; status tersebut tidak mengaktifkan buzzer.

Buzzer merupakan alarm pendukung pada prototipe dan tidak menggantikan detektor kebocoran gas bersertifikasi.

### 6. Dashboard HP — Pemantauan Data

Dashboard HP direncanakan sebagai antarmuka untuk menerima dan menampilkan data yang dikirimkan ESP32 melalui MQTT.

Dashboard dapat dikembangkan untuk menampilkan:
- Nilai sensor di area tabung gas.
- Nilai sensor di area dapur.
- Status keamanan `AMAN`, `WASPADA`, atau `BAHAYA`.
- Grafik perubahan nilai kedua sensor.
- Informasi perbandingan nilai sensor.

Untuk menerima data, dashboard harus terhubung ke broker MQTT yang sama dan melakukan subscribe pada topic `gasguard/sensor/data`. Dashboard kemudian perlu membaca field JSON `titik1`, `titik2`, dan `status`.

**Status implementasi:** program ESP32 telah mencakup pembacaan sensor, Moving Median Filter, evaluasi tren dan status, kontrol buzzer, serta pengiriman MQTT. Dashboard HP belum tersedia dalam kode yang diberikan dan perlu dikembangkan secara terpisah.

### 7. Cara Menguji Sistem

1. Jalankan simulasi pada Wokwi atau unggah program ke perangkat ESP32 fisik.
2. Buka Serial Monitor dengan baud rate `115200`.
3. Pastikan perangkat berhasil terhubung ke Wi-Fi dan broker MQTT.
4. Amati nilai `T1 [Filtered]`, `T2 [Filtered]`, `Status`, dan `Perbandingan`.
5. Uji perubahan pembacaan sensor melalui simulasi atau prosedur pengujian yang aman.
6. Periksa apakah status berubah sesuai ambang batas yang ditentukan.
7. Periksa apakah buzzer menyala ketika status `BAHAYA` dan mati ketika status `WASPADA` atau `AMAN`.
8. Setelah dashboard dibuat, hubungkan dashboard ke broker MQTT dan pastikan data pada topic `gasguard/sensor/data` diterima dengan benar.

Proses pembacaan dan pemrosesan data diulang setiap dua detik melalui fungsi `loop()`. Namun, jika koneksi MQTT terputus, fungsi rekoneksi dapat menghentikan sementara pemrosesan sampai koneksi berhasil dibangun kembali.

### 8. Fungsi Utama dalam Kode

- `setup_wifi()` — Menghubungkan ESP32 ke jaringan Wi-Fi.
- `reconnect()` — Membangun kembali koneksi MQTT jika terputus.
- `getMedian()` — Mengurutkan data dan menentukan nilai median.
- `calculateMovingMedian()` — Memperbarui buffer sensor dan menghitung hasil filter.
- `evaluateGasStatus()` — Menghitung tren, menentukan status keamanan, dan mengontrol buzzer.
- `compareGasPoints()` — Membandingkan nilai kedua sensor.
- `setup()` — Menginisialisasi Serial Monitor, buzzer, Wi-Fi, MQTT, dan nilai awal buffer.
- `loop()` — Membaca sensor, memfilter data, mengevaluasi status, membandingkan nilai, mengirimkan MQTT, dan mencetak hasil pemantauan.

### 9. Ringkasan Alur Kerja

**Pembacaan Sensor → Moving Median Filter → Evaluasi Tren dan Status → Perbandingan Nilai Sensor → Pengiriman Data MQTT → Dashboard HP**

Buzzer bekerja sebagai keluaran alarm lokal berdasarkan status yang dihasilkan. Seluruh proses berjalan berulang selama program aktif dan koneksi yang dibutuhkan tersedia.




