# Setup dan Demo GasGuard

## A. Menjalankan Simulasi ESP32 di Wokwi

1. Buka proyek Wokwi yang menggunakan firmware final yang telah disepakati kelompok.
2. Jalankan simulasi ESP32.
3. Buka Serial Monitor.
4. Pastikan ESP32 berhasil terhubung ke Wi-Fi virtual `Wokwi-GUEST`.
5. Pastikan ESP32 berhasil terhubung ke broker MQTT `broker.hivemq.com`.
6. Periksa Serial Monitor untuk memastikan data berhasil dikirim ke broker MQTT.

Informasi koneksi yang digunakan:

- **Wi-Fi:** `Wokwi-GUEST`
- **Broker MQTT:** `broker.hivemq.com`
- **Port MQTT:** `1883`
- **Topic:** `gasguard/sensor/data`

## B. Menjalankan Dashboard di Laptop

1. Buka folder utama repositori GasGuard di VS Code.
2. Buka file `dashboard/index.html`.
3. Jalankan dashboard menggunakan ekstensi Live Server.
4. Pastikan halaman dashboard berhasil dibuka dan indikator koneksi MQTT ditampilkan.
5. Tunggu hingga ESP32 mengirim data.
6. Cocokkan nilai T1, T2, dan status pada dashboard dengan keluaran Serial Monitor.

Pastikan konfigurasi dashboard menggunakan broker dan topic yang sama dengan firmware.

Untuk koneksi MQTT melalui browser, dashboard menggunakan WebSocket. Jika dashboard dijalankan melalui Live Server dengan protokol HTTP, alamat MQTT WebSocket yang digunakan adalah:

`ws://broker.hivemq.com:8000/mqtt`

**Perhatian:** Port `8000` pada alamat di atas merupakan port WebSocket MQTT, bukan otomatis port untuk membuka halaman dashboard.

Jika dashboard tidak menerima data:

1. Periksa koneksi internet laptop.
2. Periksa nilai `MQTT_URL` dan topic pada file dashboard.
3. Pastikan firmware berhasil mengirim data ke broker.
4. Periksa pesan kesalahan melalui Console pada Developer Tools browser.

## C. Membuka Dashboard di HP Android

Agar dashboard dapat dibuka melalui HP, laptop harus menjalankan server web yang dapat diakses melalui jaringan lokal.

### 1. Hubungkan perangkat

1. Sambungkan laptop dan HP ke Wi-Fi atau hotspot yang sama.
2. Pastikan kedua perangkat dapat saling mengakses melalui jaringan tersebut.

### 2. Jalankan server dashboard

Jika dashboard melalui Live Server tidak dapat diakses dari HP, gunakan server lokal alternatif berikut:

1. Buka terminal VS Code pada folder utama repositori GasGuard.
2. Jalankan perintah berikut:

   `py -m http.server 8000 --bind 0.0.0.0`

   Jika perintah `py` tidak tersedia, coba:

   `python -m http.server 8000 --bind 0.0.0.0`

3. Biarkan terminal tetap berjalan selama dashboard digunakan.

### 3. Cari alamat IP laptop

1. Buka Command Prompt di Windows.
2. Jalankan perintah `ipconfig`.
3. Cari bagian adapter jaringan yang sedang digunakan, misalnya **Wireless LAN adapter Wi-Fi**.
4. Catat nilai `IPv4 Address`.

### 4. Buka dashboard melalui HP

Buka browser di HP dan masukkan alamat berikut:

`http://192.168.1.10:8000/dashboard/`

Ganti `192.168.1.10` dengan alamat IPv4 laptop yang sebenarnya.

Jika halaman tidak dapat dibuka:

- Pastikan server web masih berjalan.
- Periksa kembali alamat IPv4 dan port yang digunakan.
- Izinkan akses pada Windows Firewall jika diperlukan.
- Pastikan laptop dan HP benar-benar berada pada jaringan yang sama.

**Catatan:** ESP32 yang disimulasikan di Wokwi terhubung ke internet melalui lingkungan virtual Wokwi. HP tidak harus terhubung ke jaringan virtual tersebut. ESP32 dan dashboard cukup dapat mengakses broker MQTT yang sama melalui internet.

## D. Urutan Video Demo

1. Tampilkan diagram Wokwi yang berisi ESP32, dua potensiometer sebagai simulasi input analog, dan buzzer.
2. Jalankan simulasi dan tunjukkan koneksi Wi-Fi, koneksi MQTT, serta pesan pengiriman data pada Serial Monitor.
3. Naikkan nilai potensiometer pada titik tabung gas, lalu amati perubahan nilai dan status.
4. Lakukan pengujian serupa pada titik dapur.
5. Tunjukkan perubahan status AMAN, WASPADA, dan BAHAYA sesuai hasil pengujian.
6. Tampilkan dashboard di HP dan cocokkan nilai serta statusnya dengan Serial Monitor.
7. Jika waktu memungkinkan, uji kondisi koneksi MQTT terputus. Amati apakah program masih membaca input dan apakah buzzer tetap merespons. Catat hasil aktual tanpa mengasumsikan pengujian berhasil.
8. Tampilkan repositori GitHub beserta struktur folder proyek.

**Catatan pengujian:** Potensiometer hanya menyimulasikan perubahan nilai analog. Pengujian ini belum membuktikan bahwa sistem dapat mendeteksi kebocoran gas menggunakan sensor MQ-6 secara nyata.

## E. Bukti Demo dan Dokumentasi

1. Simpan screenshot diagram Wokwi, Serial Monitor, dan dashboard ke folder `docs/assets/`. Buat folder tersebut jika belum tersedia.
2. Catat hasil pengujian yang benar-benar diamati pada `docs/hasil-pengujian.md`.
3. Pastikan dokumentasi membedakan hasil yang berhasil, hasil yang masih perlu diverifikasi, dan pengujian yang belum dilakukan.
4. Setelah video demo diunggah, tambahkan tautannya ke `README.md`.
5. Pastikan repositori GitHub berisi firmware, dashboard, dokumentasi setup, hasil pengujian, dan bukti demo yang relevan.
