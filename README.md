# GasGuard - Sistem Deteksi Kebocoran Gas LPG Berbasis IoT 
Mencegah terjadinya kebocoran gas dengan pemantauan dua titik secara berkala dan analisis tren
---
<p> Risiko kebocoran gas LPG senantiasa mengintai di lingkungan rumah tangga. GasGuard terinspirasi dari penelitian terdahulu yang telah mengembangkan deteksi das menggunakan sensor MQ-6, ESP32, alarm, dan notifikasi jarak jauh. Proyek ini berfokus pada pengembangan sistem yang dapat mengolah dan membandingkan pembacaan sensor dari dua titik berbeda demi meningkatkan akurasi. </p>

## Rancangan Sistem
Adapun sistem GasGuard dirancang terdiri dari:
<ol>
  <li><<p>i> Edge Device:</i></p>
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
    
## 1. ESP32 — Jalankan Sistem Sensor

Pastikan ESP32 sudah terhubung dengan dua sensor gas, buzzer, dan jaringan Wi-Fi. Program dapat dijalankan menggunakan Arduino IDE atau lingkungan PlatformIO yang telah dikonfigurasi.

**Konfigurasi pin perangkat keras:**

| Komponen | Pin ESP32 | Fungsi |
|---|---|---|
| Sensor Gas 1 | GPIO 34 | Membaca kondisi gas di area tabung |
| Sensor Gas 2 | GPIO 35 | Membaca kondisi gas di area dapur |
| Buzzer | GPIO 25 | Memberikan alarm lokal |

Setelah program diunggah ke ESP32, sistem akan menghubungkan perangkat ke Wi-Fi `Wokwi-GUEST` sesuai konfigurasi pada kode. Selanjutnya, ESP32 menghubungkan diri ke broker MQTT publik `broker.hivemq.com` menggunakan port `1883`.

## 2. Pemrosesan Data Sensor

Setelah terhubung, ESP32 membaca data analog dari kedua sensor secara berkala. Data tersebut diproses melalui beberapa tahapan berikut.

### A. Pembacaan Sensor

ESP32 membaca nilai mentah dari sensor gas pada area tabung dan area dapur. Pembacaan dilakukan secara berulang untuk memperoleh data terbaru dari kedua titik pemantauan.

### B. Moving Median Filter

Data mentah diproses menggunakan Moving Median Filter dengan ukuran jendela lima data (`WINDOW_SIZE = 5`). Filter ini mengambil nilai tengah dari lima data yang tersimpan untuk membantu mengurangi gangguan pembacaan sensor.

Hasil pemrosesan menghasilkan dua nilai, yaitu `filtered1` untuk sensor tabung dan `filtered2` untuk sensor dapur.

### C. Evaluasi Tren dan Status

Sistem membandingkan nilai hasil filter saat ini dengan nilai hasil filter sebelumnya untuk menghitung perubahan nilai atau tren sensor. Status ditentukan berdasarkan aturan berikut:

| Status | Kondisi pada program | Respons Buzzer |
|---|---|---|
| `BAHAYA` | Salah satu nilai sensor lebih dari 2500 | Menyala |
| `WASPADA` | Tren salah satu sensor naik lebih dari 150, jika kondisi BAHAYA tidak terpenuhi | Menyala |
| `SIAGA` | Salah satu nilai sensor lebih dari 1200, jika kondisi sebelumnya tidak terpenuhi | Mati |
| `AMAN` | Tidak memenuhi kondisi di atas | Mati |

Urutan pemeriksaan status mengikuti logika pada program. Ambang batas tersebut masih perlu diuji dan dikalibrasi sesuai karakteristik sensor yang digunakan.

### D. Perbandingan Nilai Sensor

Sistem membandingkan nilai sensor tabung dan dapur untuk mengetahui titik dengan nilai pembacaan lebih tinggi. Hasil perbandingan dapat berupa:

- `TABUNG LEBIH TINGGI`
- `DAPUR LEBIH TINGGI`
- `KEDUA TITIK SAMA`

Informasi ini dicetak pada Serial Monitor sebagai informasi tambahan. Pada kode saat ini, hasil perbandingan belum dimasukkan ke payload MQTT sehingga belum otomatis diterima dashboard.

## 3. Pengiriman Data — MQTT

Setelah data diproses, ESP32 mengemas nilai kedua sensor dan status keamanan dalam format JSON, lalu mengirimkannya ke broker MQTT.

**Konfigurasi MQTT:**

- Broker: `broker.hivemq.com`
- Port: `1883`
- Topic: `gasguard/sensor/data`

Contoh payload yang dikirimkan:

```json
{
  "titik1": 1234,
  "titik2": 856,
  "status": "AMAN"
}
```

Nilai pada contoh hanya ilustrasi format data, bukan hasil pengukuran aktual.

Keterangan:
- `titik1` merupakan nilai sensor area tabung setelah difilter.
- `titik2` merupakan nilai sensor area dapur setelah difilter.
- `status` merupakan status keamanan yang ditentukan oleh ESP32.

ESP32 mengirimkan data setiap dua detik. Perangkat penerima harus terhubung ke broker yang sama dan melakukan subscribe pada topic `gasguard/sensor/data`.

## 4. Dashboard HP — Pemantauan Data

Dashboard HP berfungsi sebagai antarmuka untuk menampilkan data yang dikirimkan ESP32 melalui MQTT.

Dashboard dapat dirancang untuk menampilkan:
- Nilai sensor gas pada area tabung.
- Nilai sensor gas pada area dapur.
- Status keamanan sistem: AMAN, SIAGA, WASPADA, atau BAHAYA.
- Grafik perubahan nilai sensor secara berkala.
- Informasi titik sensor dengan nilai pembacaan lebih tinggi.

**Catatan implementasi:** Kode ESP32 yang tersedia baru menangani pembacaan sensor, pemrosesan data, buzzer, dan pengiriman MQTT. Dashboard HP belum dibuat dalam kode tersebut. Untuk menampilkan data, diperlukan aplikasi atau web dashboard yang terhubung ke broker MQTT dan berlangganan pada topic yang sesuai.

## 5. Coba Sistem GasGuard

1. Jalankan simulasi Wokwi atau unggah program ke ESP32 fisik yang telah terhubung dengan sensor dan buzzer.
2. Buka Serial Monitor dengan baud rate `115200`.
3. Pastikan ESP32 berhasil terhubung ke Wi-Fi dan broker MQTT.
4. Amati nilai `T1 [Filtered]`, `T2 [Filtered]`, dan `Status` pada Serial Monitor.
5. Uji perubahan pembacaan sensor menggunakan simulator atau prosedur pengujian yang aman dan sesuai spesifikasi sensor.
6. Periksa apakah status berubah mengikuti aturan yang telah diprogram.
7. Periksa respons buzzer saat status menjadi `BAHAYA` atau `WASPADA`.
8. Setelah dashboard tersedia, hubungkan dashboard ke broker MQTT dan subscribe ke topic `gasguard/sensor/data` untuk melihat data yang diterima.

Untuk pengujian awal, simulasi dapat digunakan untuk memeriksa logika program. Namun, simulasi tidak menggantikan kalibrasi dan pengujian menggunakan perangkat keras nyata.

## 6. Pelajari Kode Program

Bagian-bagian utama kode GasGuard memiliki fungsi sebagai berikut:

- `setup_wifi()` → Menghubungkan ESP32 ke jaringan Wi-Fi.
- `reconnect()` → Menghubungkan kembali ESP32 ke broker MQTT ketika koneksi terputus.
- `getMedian()` → Mengurutkan data dan mengambil nilai median.
- `calculateMovingMedian()` → Memperbarui buffer dan menghitung hasil Moving Median Filter.
- `evaluateGasStatus()` → Menghitung tren, menentukan status keamanan, dan mengontrol buzzer.
- `compareGasPoints()` → Membandingkan nilai hasil filter dari kedua sensor.
- `loop()` → Menjalankan pembacaan sensor, pemrosesan data, pengiriman MQTT, dan pencetakan hasil ke Serial Monitor secara berulang.

## 7. Catatan Pengembangan

- Dashboard HP perlu dibuat dan dihubungkan ke broker MQTT sebelum pemantauan melalui HP dapat dilakukan.
- Broker MQTT publik tidak menyediakan privasi untuk topik yang digunakan. Hindari mengirimkan informasi sensitif dan gunakan broker dengan autentikasi serta koneksi terenkripsi untuk penerapan yang lebih serius.
- Nilai sensor tidak otomatis menunjukkan konsentrasi gas dalam ppm tanpa kalibrasi yang sesuai.
- Buzzer pada prototipe merupakan alarm pendukung, bukan pengganti detektor gas bersertifikasi.
- Koneksi Wi-Fi dan MQTT perlu dipantau agar kegagalan komunikasi tidak disalahartikan sebagai kondisi AMAN.

## 8. Ringkasan Alur Kerja

**Sensor Gas → ESP32 → Moving Median Filter → Evaluasi Tren dan Status → Kontrol Buzzer → Pengiriman MQTT → Dashboard HP**

GasGuard dirancang untuk memantau pembacaan gas dari dua titik, mengevaluasi kondisi berdasarkan aturan yang ditentukan, memberikan alarm lokal, dan mengirimkan data ke dashboard melalui MQTT. Pengembangan dashboard, kalibrasi sensor, dan pengujian keselamatan merupakan tahapan penting sebelum sistem digunakan pada lingkungan nyata.

> **Penting:** GasGuard merupakan prototipe pembelajaran IoT. Jangan mengandalkannya sebagai satu-satunya sistem keselamatan untuk mendeteksi kebocoran LPG.
