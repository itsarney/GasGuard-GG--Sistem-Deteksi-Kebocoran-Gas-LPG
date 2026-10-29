
# Hasil Pengujian GasGuard

## 1. Informasi Pengujian

- Lingkungan pengujian: Wokwi dan ESP32 simulasi
- Input: Dua potensiometer sebagai simulasi input sensor MQ-6
- Broker MQTT: `broker.hivemq.com`
- Topic: `gasguard/sensor/data`
- Algoritma: Moving Median dan Decision & Trend Analysis
- Hasil keseluruhan: Pengujian awal berhasil untuk koneksi, pengiriman MQTT, dan perubahan status. Pengujian integrasi dashboard dan respons buzzer masih perlu diverifikasi.

## 2. Hasil Pengujian

| ID | Skenario | Hasil Aktual | Status |
|---|---|---|---|
| T01 | Koneksi Wi-Fi | Serial Monitor menampilkan `WiFi terhubung!` dan alamat IP `10.13.37.2`. | Berhasil |
| T02 | Koneksi MQTT | Serial Monitor menampilkan `TERHUBUNG!`. | Berhasil |
| T03 | Pengiriman data MQTT | Pesan `MQTT: Pesan berhasil dikirim ke broker` muncul berulang kali. | Berhasil |
| T04 | Kondisi AMAN | Ketika kedua nilai hasil filtering rendah, misalnya T1 = 0 dan T2 = 0, sistem menampilkan status `AMAN`. | Berhasil |
| T05 | Perubahan input sensor tabung | Nilai T1 meningkat hingga 2033 dan 2170. Sistem menampilkan status `BAHAYA`. | Berhasil |
| T06 | Perubahan input sensor dapur | Nilai T2 tercatat 1349 dengan status `WASPADA`, kemudian 2033, 2550, dan 3987 dengan status `BAHAYA`. | Berhasil |
| T07 | Moving Median | Nilai hasil filtering berubah mengikuti perubahan input, misalnya T2 dari 3987 menjadi 1349 lalu 0. Namun, efektivitas filter dalam mengurangi noise belum dibandingkan dengan data mentah. | Teramati, perlu verifikasi |
| T08 | Analisis tren | Status `WASPADA` muncul ketika terjadi kenaikan nilai, termasuk saat T1 = 925 dan T2 = 713. Ketika nilai stabil pada T1 = 1137 dan T2 = 713, status berubah menjadi `AMAN`. | Berhasil diamati |
| T09 | Dashboard menerima data MQTT | Log menunjukkan pesan berhasil dikirim oleh ESP32, tetapi penerimaan dan pembaruan nilai pada dashboard belum dibuktikan melalui hasil pengujian ini. | Belum diuji |
| T10 | Respons buzzer pada kondisi BAHAYA | Firmware memberikan perintah untuk mengaktifkan buzzer ketika status `BAHAYA`. Bunyi buzzer belum terkonfirmasi dari log yang tersedia. | Belum diverifikasi |
| T11 | MQTT terputus dan tersambung kembali | Belum terdapat hasil pengujian ketika koneksi broker sengaja diputus dan dipulihkan. | Belum diuji |
| T12 | Alarm saat MQTT terputus | Belum terdapat hasil pengamatan yang memastikan alarm lokal tetap bekerja saat MQTT terputus. | Belum diuji |

## 3. Ringkasan Hasil Pengamatan

### a. Koneksi dan komunikasi

ESP32 berhasil terhubung ke jaringan Wi-Fi Wokwi dan broker MQTT HiveMQ. Serial Monitor juga berulang kali menunjukkan bahwa pesan berhasil dikirim ke broker.

### b. Perubahan status sistem

Tiga status berikut telah teramati dalam log:

- **AMAN:** Contoh pembacaan T1 = 0 dan T2 = 0.
- **WASPADA:** Contoh pembacaan T1 = 0 dan T2 = 713 ketika terjadi kenaikan tren, serta T2 = 1349.
- **BAHAYA:** Contoh pembacaan T1 = 2033 dan T2 = 2033, serta T1 = 2170 dan T2 = 2550.

Hasil tersebut memperlihatkan bahwa status berubah mengikuti nilai hasil filtering dan logika pengambilan keputusan pada firmware.

Status `WASPADA` tidak hanya ditentukan oleh nilai ADC di atas 1200, tetapi juga dapat muncul ketika kenaikan hasil filtering melebihi 150 dalam satu siklus pemeriksaan.

### c. Pemrosesan data

Program menampilkan nilai hasil filtering untuk kedua titik setiap siklus pengiriman. Nilai yang diamati berubah mengikuti perubahan input potensiometer.

Namun, log yang tersedia hanya menampilkan nilai hasil filtering. Oleh karena itu, pengurangan noise oleh Moving Median belum dapat dinilai secara kuantitatif tanpa membandingkannya dengan pembacaan mentah.

### d. Dashboard dan alarm lokal

Pengiriman MQTT dari ESP32 telah terkonfirmasi berhasil. Penerimaan data oleh dashboard, pembaruan status pada browser, dan bunyi buzzer masih harus diperiksa secara langsung.

## 4. Bukti Pengujian

Bukti awal tersedia dalam bentuk log Serial Monitor yang menunjukkan:

- Wi-Fi berhasil terhubung.
- Broker MQTT berhasil terhubung.
- Pengiriman pesan MQTT berhasil.
- Perubahan nilai kedua titik.
- Munculnya status AMAN, WASPADA, dan BAHAYA.

Screenshot Serial Monitor dan dashboard dapat ditambahkan ke folder `docs/assets/` setelah dokumentasi bukti dikumpulkan.

## 5. Keterbatasan Pengujian

- Pengujian menggunakan potensiometer sebagai simulasi input analog di Wokwi, bukan sensor MQ-6 fisik.
- Nilai ADC bukan pengukuran konsentrasi gas LPG dalam PPM.
- Efektivitas Moving Median dalam mengurangi noise belum dibandingkan secara kuantitatif dengan data mentah.
- Bunyi buzzer, penerimaan data dashboard, serta perilaku sistem ketika koneksi MQTT terputus belum terkonfirmasi melalui bukti pengujian.
- Hasil simulasi tidak membuktikan akurasi deteksi kebocoran LPG pada kondisi nyata.
