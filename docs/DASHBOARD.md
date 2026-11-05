# Dashboard GasGuard

## 1. Gambaran Umum

Dashboard GasGuard berada pada `dashboard/index.html`. Dashboard menggunakan HTML, CSS, JavaScript, dan MQTT.js untuk menerima pesan dari HiveMQ melalui MQTT over WebSocket.

Dashboard menampilkan:

- Nilai hasil filter sensor tabung.
- Nilai hasil filter sensor dapur.
- Status sistem dari firmware ESP32.
- Indikator perintah alarm berdasarkan status firmware.
- Hasil klasifikasi AI dari model Decision Tree.
- Status koneksi broker dan waktu pesan terakhir.

Status firmware dan prediksi AI ditampilkan secara terpisah. Prediksi AI tidak menggantikan status firmware dan tidak mengendalikan buzzer.

## 2. Konfigurasi MQTT

Pengaturan koneksi pada JavaScript `dashboard/index.html`:

| Pengaturan | Nilai |
|---|---|
| Broker | `broker.hivemq.com` |
| URL WebSocket | `ws://broker.hivemq.com:8000/mqtt` |
| Topic sensor | `gasguard/kelompok8/device01/sensor/data` |
| Topic AI | `gasguard/kelompok8/device01/ai/prediction` |

Dashboard melakukan subscribe ke kedua topic setelah koneksi broker berhasil.

**Catatan:** URL WebSocket di atas digunakan pada dashboard yang dibuka melalui HTTP lokal. Jika halaman dipasang pada hosting HTTPS, endpoint WebSocket harus menggunakan koneksi terenkripsi (`wss://`) yang sesuai dengan endpoint broker.

## 3. Topic dan Fungsi

| Topic | Publisher | Subscriber | Isi |
|---|---|---|---|
| `gasguard/kelompok8/device01/sensor/data` | ESP32 | Dashboard dan Python | Pembacaan mentah/filter, tren, perbandingan, status firmware, dan perintah alarm |
| `gasguard/kelompok8/device01/ai/prediction` | Python `integrasi_mqtt.py` | Dashboard | Prediksi Decision Tree, informasi model, status firmware pembanding, timestamp, dan lima fitur |

Topic AI merupakan topic tambahan. Topic sensor existing tetap digunakan oleh ESP32.

## 4. Struktur Payload Sensor

Firmware mengirim JSON bertingkat. Field utama yang digunakan dashboard adalah:

- `sensor_tabung.adc_filter`
- `sensor_dapur.adc_filter`
- `status_sistem`

Field lain yang tersedia pada payload firmware mencakup `device_id`, pembacaan ADC mentah, status tiap sensor, tren, `selisih_sensor`, `perbandingan`, dan `alarm`.

## 5. Struktur Payload AI

Python menerbitkan hasil klasifikasi dengan field utama:

- `device_id`
- `model`
- `prediction`
- `firmware_status`
- `timestamp`
- `features`

## 6. Cara Menjalankan Dashboard di Laptop

### Opsi A — Live Server

1. Buka repository GasGuard di VS Code.
2. Klik kanan `dashboard/index.html`.
3. Pilih **Open with Live Server**.
4. Pastikan browser menampilkan dashboard.
5. Buka Developer Tools (`F12`) dan periksa Console untuk memastikan subscription topic sensor dan topic AI berhasil.

### Opsi B — Python HTTP Server

Jalankan PowerShell pada direktori utama repository (direktori yang memiliki folder `dashboard`), lalu jalankan:

```powershell
py -m http.server 5500 --bind 127.0.0.1
```

Buka alamat berikut pada browser laptop:

`http://127.0.0.1:5500/dashboard/`

Terminal server harus tetap berjalan selama dashboard digunakan.

## 7. Cara Membuka Dashboard di HP Android dengan Termux

Pada cara ini, file dashboard disajikan langsung dari HP yang sama. Laptop tetap menjalankan Wokwi dan program Python AI. Dashboard pada HP menerima pesan dari HiveMQ melalui internet; tidak perlu menggunakan IP laptop untuk membuka halaman yang disajikan oleh Termux di HP itu sendiri.

1. Salin `dashboard/index.html` versi terbaru ke folder Download HP.
2. Buka Termux dan berikan izin penyimpanan:

   ```bash
   termux-setup-storage
   ```

3. Masuk ke folder Download. Coba:

   ```bash
   cd ~/storage/downloads
   ```

   Jika path tersebut tidak tersedia, coba path Android langsung:

   ```bash
   cd /storage/emulated/0/Download
   ```

4. Periksa file:

   ```bash
   ls
   ```

   Pastikan `index.html` terlihat.

5. Jalankan server lokal pada HP:

   ```bash
   python -m http.server 5500 --bind 127.0.0.1
   ```

6. Buka Chrome pada HP yang sama dan akses:

   `http://127.0.0.1:5500/index.html`

Biarkan Termux berjalan selama dashboard digunakan. Jika folder atau file tidak ditemukan, periksa izin penyimpanan, lokasi Download, dan nama file. Cara ini tidak menggunakan IP laptop.

## 8. Pemeriksaan Jika Dashboard Tidak Menerima Pesan

1. Pastikan koneksi internet perangkat tersedia.
2. Pastikan URL WebSocket MQTT dapat diakses dari browser.
3. Pastikan dashboard subscribe ke topic sensor dan topic AI yang benar.
4. Pastikan ESP32 menerbitkan data ke topic sensor yang sama.
5. Pastikan Python menerima data sensor dan menerbitkan hasil AI ke topic AI.
6. Periksa Console browser untuk error JSON, MQTT, atau library MQTT.js.
7. Periksa terminal Python dan Serial Monitor ESP32 untuk log pengiriman/penerimaan.

Jika hanya data sensor yang tampil, periksa proses Python dan subscription topic AI. Jika data AI tidak berubah, dashboard mungkin masih menampilkan prediksi terakhir; pastikan layanan Python masih berjalan dan menghasilkan pesan baru.

## 9. Keamanan dan Batasan

- Broker yang digunakan adalah broker publik. Jangan mengirim kredensial atau data sensitif.
- Indikator alarm pada dashboard mencerminkan perintah alarm berdasarkan status firmware.
- Nilai ADC pada dashboard bukan konsentrasi gas LPG dalam ppm.
