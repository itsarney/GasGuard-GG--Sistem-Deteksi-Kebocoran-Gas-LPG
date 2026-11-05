# Hasil Pengujian GasGuard

## 1. Informasi Pengujian

- Tanggal pengujian tambahan: 5 November 2026.
- Rentang waktu log tambahan: 10:08:31–14:48:59 WIB.
- Lingkungan pengujian: Wokwi dan ESP32 simulasi.
- Input: Dua potensiometer sebagai simulasi input sensor MQ-6, untuk titik tabung LPG dan area dapur.
- Device ID pada log tambahan: `gasguard_01`.
- Broker MQTT: `broker.hivemq.com`.
- Topic: `gasguard/kelompok8/device01/sensor/data`.
- Pemrosesan data: Moving Median serta Decision & Trend Analysis.
- Klasifikasi tambahan: kolom `prediction` sebagai keluaran klasifikasi AI pada log.
- Data yang dicatat: timestamp, device ID, status firmware, nilai hasil filtering kedua sensor, selisih sensor, tren kedua sensor, hasil prediction, dan status pengiriman MQTT.

**Ringkasan:** Pengujian menunjukkan koneksi Wi-Fi dan MQTT berhasil berdasarkan hasil pengujian sebelumnya. Pada log tambahan, pengiriman MQTT tercatat berhasil pada seluruh entri yang diberikan. Ketiga status firmware dan ketiga keluaran klasifikasi AI juga teramati. Selain itu, demonstrasi proyek telah memperlihatkan dashboard menerima data serta memperbarui nilai dan status, dan buzzer berbunyi pada kondisi `BAHAYA`.

## 2. Hasil Pengujian

| ID | Skenario | Hasil Aktual | Status |
|---|---|---|---|
| T01 | Koneksi Wi-Fi | Serial Monitor menampilkan `WiFi terhubung!` dan alamat IP `10.13.37.2` pada pengujian sebelumnya. | Berhasil |
| T02 | Koneksi MQTT | Serial Monitor menampilkan `TERHUBUNG!` pada pengujian sebelumnya. | Berhasil |
| T03 | Pengiriman data MQTT | Pada log tambahan tanggal 5 November 2026, seluruh entri yang diberikan mencatat `mqtt_publish = BERHASIL`. | Berhasil |
| T04 | Kondisi AMAN | Status firmware `AMAN` teramati, misalnya pada nilai filtering tabung dan dapur sebesar 200 dan 200, serta 440 dan 272. | Berhasil teramati |
| T05 | Perubahan input sensor tabung | Nilai filtering tabung meningkat hingga 1409 dan 1457 dengan status firmware `WASPADA`, serta mencapai 2262 dengan status `BAHAYA`. | Berhasil teramati |
| T06 | Perubahan input sensor dapur | Nilai filtering dapur mencapai 1169 dengan status `WASPADA`, serta 2094, 2214, dan 2366 dengan status firmware `BAHAYA` pada beberapa pengamatan. | Berhasil teramati |
| T07 | Moving Median | Log tambahan mencatat nilai `filter_tabung` dan `filter_dapur` yang berubah mengikuti perubahan input. | Berhasil teramati |
| T08 | Decision & Trend Analysis | Kolom `tren_tabung` dan `tren_dapur` mencatat kenaikan maupun penurunan pada beberapa siklus. Contohnya, tren dapur sebesar 969 pada pukul 14:05:53 dan 1201 pada pukul 14:08:22. | Berhasil teramati |
| T09 | Perubahan status firmware | Ketiga status `AMAN`, `WASPADA`, dan `BAHAYA` muncul pada kolom `firmware_status` dalam log tambahan. | Berhasil teramati |
| T10 | Klasifikasi AI | Kolom `prediction` menghasilkan tiga kelas, yaitu `AMAN`, `WASPADA`, dan `BAHAYA`. Contoh `BAHAYA` muncul pada pukul 14:06:18 dan 14:20:38; contoh `WASPADA` muncul pada pukul 14:05:53 dan 14:43:51. | Berhasil teramati |
| T11 | Dashboard menerima data MQTT | Dalam demonstrasi proyek, dashboard menerima data MQTT dan menampilkan pembaruan nilai serta status pada browser. Log tambahan juga mencatat seluruh pengiriman MQTT berstatus `BERHASIL`. | Berhasil didemonstrasikan |
| T12 | Respons buzzer pada kondisi BAHAYA | Dalam demonstrasi proyek, buzzer diperlihatkan berbunyi ketika sistem berada pada kondisi `BAHAYA`. | Berhasil didemonstrasikan |

## 3. Ringkasan Hasil Pengamatan

### a. Koneksi dan komunikasi

Pada pengujian sebelumnya, ESP32 berhasil terhubung ke jaringan Wi-Fi Wokwi dan broker MQTT HiveMQ. Serial Monitor menampilkan pesan koneksi berhasil. Pada log tambahan tanggal 5 November 2026, seluruh entri yang diberikan menunjukkan `mqtt_publish = BERHASIL`. Hasil ini membuktikan bahwa proses pengiriman pesan dari perangkat tercatat berhasil. Penerimaan pesan dan pembaruan tampilan dashboard juga telah diperlihatkan dalam demonstrasi proyek. Dengan demikian, bukti pengiriman dari log dan bukti penerimaan/tampilan dari demo saling melengkapi.

### b. Perubahan status firmware

Ketiga status pada kolom `firmware_status` teramati dalam log tambahan:

- **AMAN:** Contoh nilai `filter_tabung = 200.0` dan `filter_dapur = 200.0` pada pukul 10:08:31, serta `filter_tabung = 440.0` dan `filter_dapur = 272.0` pada pukul 14:22:51.
- **WASPADA:** Contoh nilai `filter_tabung = 1409.0` dan `filter_dapur = 1109.0` pada pukul 14:43:51.
- **BAHAYA:** Contoh nilai `filter_tabung = 1061.0` dan `filter_dapur = 2366.0` pada pukul 14:06:18, serta `filter_tabung = 2262.0` dan `filter_dapur = 2426.0` pada pukul 14:20:38.

Dengan demikian, log tambahan memperlihatkan bahwa ketiga kategori status firmware telah muncul selama simulasi. Contoh tersebut merupakan pembacaan hasil filtering dari potensiometer, bukan pengukuran konsentrasi LPG dalam PPM.

### c. Pemrosesan data dan analisis tren

Log mencatat nilai hasil filtering untuk titik tabung dan dapur, selisih kedua nilai, serta tren masing-masing titik. Sebagai contoh, pada pukul 14:05:53 nilai `filter_dapur` sebesar 1169.0 dengan `tren_dapur` sebesar 969.0. Pada pukul 14:08:22, nilai `filter_dapur` sebesar 1473.0 dengan `tren_dapur` sebesar 1201.0. Nilai tren juga tercatat pada titik tabung, misalnya `tren_tabung = 849.0` pada pukul 10:53:32 dan `tren_tabung = 1958.0` pada pukul 14:47:38.

### d. Hasil klasifikasi AI (`prediction`)

Kolom `prediction` pada log menghasilkan tiga kategori klasifikasi, yaitu `AMAN`, `WASPADA`, dan `BAHAYA`. Beberapa contoh hasilnya adalah:

- **AMAN:** Pada pukul 14:21:01, nilai filtering tabung 320.0 dan dapur 272.0 menghasilkan `prediction = AMAN`.
- **WASPADA:** Pada pukul 14:05:53, nilai filtering tabung 200.0 dan dapur 1169.0 menghasilkan `prediction = WASPADA`.
- **BAHAYA:** Pada pukul 14:20:38, nilai filtering tabung 2262.0 dan dapur 2426.0 menghasilkan `prediction = BAHAYA`.

### e. Dashboard dan alarm lokal

Pengiriman MQTT dari ESP32 tercatat berhasil pada seluruh entri log tambahan. Selain itu, dalam demonstrasi proyek, dashboard diperlihatkan menerima data dan memperbarui nilai serta status pada browser. Demonstrasi tersebut juga memperlihatkan buzzer berbunyi ketika sistem berada pada kondisi `BAHAYA`. Dengan demikian, fungsi penerimaan dan tampilan dashboard serta respons buzzer telah didemonstrasikan, meskipun log tambahan tidak merekam kedua keluaran tersebut secara langsung.

## 4. Bukti Pengujian

Bukti pengujian yang tersedia meliputi log Serial Monitor dan log data bertimestamp tanggal 5 November 2026. Log tambahan memuat:

- Identitas perangkat melalui `device_id`.
- Status firmware melalui `firmware_status`.
- Nilai hasil filtering sensor tabung dan dapur melalui `filter_tabung` dan `filter_dapur`.
- Selisih kedua nilai melalui `selisih_sensor`.
- Nilai tren melalui `tren_tabung` dan `tren_dapur`.
- Hasil klasifikasi AI melalui `prediction`.
- Status pengiriman MQTT melalui `mqtt_publish`.

Selain log, demonstrasi proyek menjadi bukti bahwa dashboard menerima data MQTT, memperbarui nilai dan status pada browser, serta buzzer berbunyi ketika kondisi `BAHAYA`. Rekaman atau screenshot dari bagian demo tersebut dapat disimpan di folder `docs/assets/` agar bukti pengujian terdokumentasi bersama log.

## 5. Keterbatasan Pengujian

- Pengujian menggunakan potensiometer sebagai simulasi input analog di Wokwi, bukan sensor MQ-6 fisik.
- Nilai hasil filtering merupakan nilai simulasi/ADC dan bukan pengukuran konsentrasi gas LPG dalam PPM.
- Efektivitas Moving Median dalam mengurangi noise belum dibandingkan secara kuantitatif dengan data mentah.
- Log `mqtt_publish = BERHASIL` hanya menunjukkan status pengiriman dari sisi perangkat. Penerimaan dan pembaruan tampilan dashboard serta bunyi buzzer telah diperlihatkan dalam demonstrasi.
