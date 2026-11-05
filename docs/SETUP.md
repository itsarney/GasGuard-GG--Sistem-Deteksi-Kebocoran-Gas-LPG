# Setup dan Demo GasGuard

Dokumen ini menjelaskan cara menjalankan firmware Wokwi, layanan AI Python, dan dashboard GasGuard.

## A. Persiapan

Pastikan repository memiliki komponen berikut:

- `Projects-GasGuard/src/main.cpp`
- `Projects-GasGuard/platformio.ini`
- `Projects-GasGuard/diagram.json`
- `Projects-GasGuard/ai_model/decision_tree_model.pkl`
- `Projects-GasGuard/ai_model/integrasi_mqtt.py`
- `Projects-GasGuard/ai_model/requirements.txt`
- `Projects-GasGuard/ai_model/.env.example`
- `dashboard/index.html`

## B. Menjalankan ESP32 di Wokwi

1. Buka folder `Projects-GasGuard` di VS Code.
2. Buka proyek Wokwi yang sesuai dengan konfigurasi `wokwi.toml` dan `diagram.json`.
3. Jalankan simulasi.
4. Buka Serial Monitor dengan baud rate yang digunakan firmware, yaitu `115200`.
5. Pastikan ESP32 membaca input dari dua potensiometer.
6. Pastikan koneksi Wi-Fi Wokwi dan MQTT berhasil.
7. Periksa log publish. Pesan yang diharapkan saat publish berhasil adalah:

   ```text
   [ MQTT: data berhasil dikirim ]
   ```

Konfigurasi firmware:

| Pengaturan | Nilai |
|---|---|
| Wi-Fi simulasi | `Wokwi-GUEST` |
| Broker | `broker.hivemq.com` |
| Port MQTT | `1883` |
| Topic sensor | `gasguard/kelompok8/device01/sensor/data` |
| GPIO sensor tabung | `34` |
| GPIO sensor dapur | `35` |
| GPIO buzzer | `25` |
| Interval pembacaan | `500 ms` |
| Interval publish | `2000 ms` |

Firmware menggunakan Moving Median dengan jendela lima pembacaan. Status sistem ditentukan melalui threshold dan analisis tren. Pada firmware yang telah disesuaikan, buffer PubSubClient diperbesar menjadi 512 byte untuk menampung payload JSON.

## C. Menyiapkan Python di Windows

### 1. Buka terminal

Buka PowerShell pada folder `Projects-GasGuard`, yaitu folder yang berisi `platformio.ini`, `src`, `dataset`, `tools`, dan `ai_model`.

### 2. Buat virtual environment

Contoh lokasi virtual environment yang digunakan saat pengembangan:

```powershell
py -3.13 -m venv C:\venvs\gasguard
```

Aktifkan:

```powershell
C:\venvs\gasguard\Scripts\Activate.ps1
```

Jika PowerShell memblokir aktivasi script, izinkan hanya untuk sesi terminal saat ini:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Lalu jalankan kembali perintah aktivasi. Jika virtual environment sudah dibuat dan aktif, tahap pembuatan tidak perlu diulang.

### 3. Pasang dependency

Pastikan `ai_model/requirements.txt` berisi empat dependency model yang sudah ada dan dua dependency untuk integrasi MQTT:

```text
pandas
scikit-learn
joblib
matplotlib
paho-mqtt==2.2.0
python-dotenv==1.2.4
```

Instal dependency:

```powershell
python -m pip install --upgrade pip
python -m pip install -r .\ai_model\requirements.txt
```

Versi yang telah digunakan pada lingkungan pengembangan integrasi ini:

| Library | Versi terpasang |
|---|---:|
| Python | 3.13.7 |
| scikit-learn | 1.9.1 |
| joblib | 1.6.0 |
| pandas | 3.1.1 |
| matplotlib | 3.11.2 |
| paho-mqtt | 2.2.0 |
| python-dotenv | 1.2.4 |

## D. Menyiapkan Konfigurasi MQTT Python

1. Pastikan file `ai_model/.env.example` tersedia.
2. Salin file contoh menjadi `.env` menggunakan PowerShell:

   ```powershell
   Copy-Item .\ai_model\.env.example .\ai_model\.env
   ```

3. Contoh isi konfigurasi:

   ```env
   MQTT_HOST=broker.hivemq.com
   MQTT_PORT=1883
   MQTT_USERNAME=
   MQTT_PASSWORD=
   MQTT_SENSOR_TOPIC=gasguard/kelompok8/device01/sensor/data
   MQTT_AI_TOPIC=gasguard/kelompok8/device01/ai/prediction
   ```

4. Simpan `.env` secara lokal. Jangan unggah `.env` yang berisi kredensial ke GitHub.

## E. Menjalankan Integrasi AI

Pastikan terminal masih berada di `Projects-GasGuard` dan virtual environment `(gasguard)` aktif.

Jalankan:

```powershell
python .\ai_model\integrasi_mqtt.py
```

Program akan:

1. Memuat `ai_model/decision_tree_model.pkl`.
2. Memeriksa lima fitur dan kelas model.
3. Terhubung ke HiveMQ.
4. Subscribe topic sensor.
5. Menerima payload ESP32 dan membentuk lima fitur.
6. Menjalankan prediksi Decision Tree.
7. Mencatat hasil ke `ai_model/ai_prediction_log.csv`.
8. Publish hasil ke topic AI.

Biarkan program tetap berjalan selama pengujian. Hentikan dengan `Ctrl + C` setelah pengujian selesai.

## F. Menjalankan Dashboard di Laptop

### Opsi A — Live Server

1. Buka repository utama di VS Code.
2. Klik kanan `dashboard/index.html`.
3. Pilih **Open with Live Server**.
4. Pastikan browser menampilkan dashboard.

### Opsi B — Python HTTP Server

Jalankan dari direktori utama repository, yaitu direktori yang memuat folder `dashboard`:

```powershell
py -m http.server 5500 --bind 127.0.0.1
```

Buka browser laptop:

`http://127.0.0.1:5500/dashboard/`

Terminal server harus tetap terbuka.

## G. Membuka Dashboard di HP Android Menggunakan Termux

Pada cara ini, dashboard disajikan langsung dari HP. Laptop tetap menjalankan Wokwi dan `integrasi_mqtt.py`.

1. Salin file `dashboard/index.html` versi terbaru ke folder Download HP.
2. Instal Termux dan jalankan:

   ```bash
   pkg update && pkg upgrade
   pkg install python
   termux-setup-storage
   ```

3. Berikan izin penyimpanan Android ketika diminta.
4. Masuk ke folder Download:

   ```bash
   cd ~/storage/downloads
   ```

   Jika tidak ditemukan, coba:

   ```bash
   cd /storage/emulated/0/Download
   ```

5. Pastikan file ada:

   ```bash
   ls
   ```

6. Jalankan server:

   ```bash
   python -m http.server 5500 --bind 127.0.0.1
   ```

7. Buka Chrome pada HP yang sama:

   `http://127.0.0.1:5500/index.html`

Biarkan Termux berjalan. Cara ini tidak membutuhkan IP laptop karena server dan browser berada pada HP yang sama. HP tetap memerlukan internet untuk menerima pesan MQTT dari HiveMQ.

## H. Urutan Menjalankan Sistem untuk Demo

1. Jalankan simulasi ESP32 di Wokwi.
2. Pastikan Serial Monitor menunjukkan koneksi MQTT dan publish data sensor berhasil.
3. Aktifkan virtual environment Python di laptop.
4. Jalankan `integrasi_mqtt.py` dan pastikan Python berhasil subscribe topic sensor.
5. Buka dashboard di laptop atau HP.
6. Pastikan dashboard terhubung ke broker dan subscribe topic sensor serta topic AI.
7. Ubah kedua potensiometer untuk mencoba skenario pembacaan berbeda.
8. Amati status firmware di dashboard, hasil prediksi AI, dan log Python.
9. Simpan bukti pengujian yang benar-benar diperoleh.

## I. Pemecahan Masalah Singkat

| Gejala | Pemeriksaan |
|---|---|
| `decision_tree_model.pkl` tidak ditemukan | Jalankan program dari folder `Projects-GasGuard` dan periksa lokasi file model di `ai_model/` |
| `Import dotenv could not be resolved` | Pilih interpreter `C:\venvs\gasguard\Scripts\python.exe` di VS Code dan periksa instalasi `python-dotenv` |
| Python terhubung tetapi tidak menerima data | Pastikan Wokwi berjalan, ESP32 publish berhasil, dan topic sensor sama |
| Dashboard tidak menampilkan data sensor | Periksa URL WebSocket, subscription topic sensor, dan format payload JSON |
| Dashboard tidak menampilkan prediksi AI | Pastikan Python memproses pesan, publish topic AI, dan dashboard subscribe topic AI |
| `No such file or directory` di Termux | Periksa izin penyimpanan, gunakan `ls`, dan pastikan lokasi serta nama `index.html` benar |
| Dashboard HP timeout saat memakai IP laptop | Pastikan server laptop aktif, bind ke alamat jaringan, firewall mengizinkan port, dan jaringan tidak mengisolasi client. Alternatif: sajikan file langsung dari Termux di HP yang sama |
