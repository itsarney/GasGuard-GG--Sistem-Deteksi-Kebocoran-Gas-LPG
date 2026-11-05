# Integrasi AI Decision Tree GasGuard

## 1. Model dan Kontrak Input-Output

Model yang digunakan adalah Decision Tree dari Scikit-learn dan disimpan dalam format Joblib pada `ai_model/decision_tree_model.pkl`.

Model menerima lima fitur dengan nama dan urutan persis sebagai berikut:

| Urutan | Nama fitur | Sumber/perhitungan saat inferensi |
|---:|---|---|
| 1 | `filter_tabung` | `sensor_tabung.adc_filter` dari payload ESP32 |
| 2 | `filter_dapur` | `sensor_dapur.adc_filter` dari payload ESP32 |
| 3 | `selisih_sensor` | Dihitung Python: `filter_tabung - filter_dapur` |
| 4 | `tren_tabung` | `sensor_tabung.tren` dari payload ESP32 |
| 5 | `tren_dapur` | `sensor_dapur.tren` dari payload ESP32 |

Target/kelas model adalah `AMAN`, `WASPADA`, dan `BAHAYA`.

**Penting:** nama, urutan, arti, satuan/skala, dan metode pembentukan fitur harus konsisten dengan dataset yang digunakan untuk training. Program integrasi memeriksa `model.feature_names_in_` sebelum menerima pesan MQTT.

## 2. Sumber Data dan Topic Sensor

ESP32 menerbitkan data ke broker `broker.hivemq.com` melalui MQTT TCP port `1883` dengan topic:

`gasguard/kelompok8/device01/sensor/data`

## 3. Perhitungan Fitur

### 3.1 Nilai filter

Python mengambil nilai hasil Moving Median dari:

- `sensor_tabung.adc_filter` menjadi `filter_tabung`.
- `sensor_dapur.adc_filter` menjadi `filter_dapur`.

### 3.2 Selisih sensor

Feature engineering dataset menghitung selisih bertanda:

`selisih_sensor = filter_tabung - filter_dapur`

Firmware juga mengirim field `selisih_sensor`, tetapi field itu dibentuk dengan `abs()`. Karena perbedaan tersebut, program Python mengabaikan field selisih dari payload dan menghitung ulang berdasarkan kedua nilai filter.

### 3.3 Tren sensor

Python mengambil `sensor_tabung.tren` dan `sensor_dapur.tren` dari payload firmware. Firmware menghitung tren dari selisih hasil filter sekarang dengan hasil filter sebelumnya.

**Catatan kesesuaian waktu:** firmware membaca dan memperbarui tren sekitar setiap 500 ms, tetapi mengirim payload MQTT sekitar setiap 2.000 ms. Dataset feature engineering dibuat dari rekaman pembacaan berurutan. Karena itu, perbedaan frekuensi antara data dataset dan pesan inferensi perlu dievaluasi; kesamaan rumus saja belum membuktikan kesamaan distribusi fitur.

## 4. Program Integrasi

File utama integrasi adalah:

`Projects-GasGuard/ai_model/integrasi_mqtt.py`

Tugas program:

1. Membaca konfigurasi broker dan topic dari `.env`.
2. Memuat `decision_tree_model.pkl` menggunakan Joblib.
3. Memvalidasi nama dan urutan lima fitur serta kelas model.
4. Terhubung ke HiveMQ menggunakan Paho-MQTT.
5. Subscribe ke topic sensor.
6. Mengubah payload JSON menjadi lima fitur numerik.
7. Menjalankan `model.predict()`.
8. Menyimpan hasil prediksi ke `ai_prediction_log.csv`.
9. Publish hasil prediksi ke topic AI.
10. Mencoba kembali koneksi ketika koneksi MQTT terputus.

Program juga melewati pesan yang payload JSON-nya tidak valid, field sensor tidak tersedia, atau nilai fitur bukan angka finite. Pesan kesalahan dicetak di terminal.

## 5. Topic dan Payload Hasil AI

Python menerbitkan hasil prediksi ke topic:

`gasguard/kelompok8/device01/ai/prediction`

Dashboard melakukan subscribe terhadap dua topic:

- Topic sensor untuk nilai pembacaan dan status firmware.
- Topic AI untuk hasil klasifikasi Decision Tree.

Status firmware dan prediksi AI ditampilkan terpisah. Hasil AI tidak mengubah status firmware atau mengendalikan buzzer.

## 6. Pencatatan Prediksi

Program membuat file berikut secara otomatis ketika pesan berhasil diproses:

`ai_model/ai_prediction_log.csv`

Kolom log mencakup timestamp, device ID, status firmware, lima fitur input, prediksi AI, dan status publish MQTT. File ini merupakan hasil runtime. File log dapat disimpan sebagai bukti pengujian bila diperlukan, tetapi tidak wajib menjadi bagian dari source code aplikasi.

## 8. Konfigurasi dan Keamanan

Konfigurasi yang digunakan:

```env
MQTT_HOST=broker.hivemq.com
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_SENSOR_TOPIC=gasguard/kelompok8/device01/sensor/data
MQTT_AI_TOPIC=gasguard/kelompok8/device01/ai/prediction
```
