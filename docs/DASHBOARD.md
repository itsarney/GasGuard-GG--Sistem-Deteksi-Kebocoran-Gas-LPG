
## Konfigurasi MQTT

Pastikan konfigurasi dashboard sesuai dengan firmware ESP32.

- **Broker:** `broker.hivemq.com`
- **Topic:** `gasguard/sensor/data`
- **Field payload:** `titik1`, `titik2`, `status`
- **Protokol ESP32:** MQTT TCP, port `1883`
- **Protokol dashboard:** MQTT over WebSocket

### URL WebSocket

Pada bagian JavaScript di `dashboard/index.html`, periksa konstanta `MQTT_URL`.

Untuk dashboard yang dijalankan melalui HTTP atau Live Server, gunakan:

`ws://broker.hivemq.com:8000/mqtt`

Jika dashboard dibuka melalui HTTPS, misalnya GitHub Pages, gunakan koneksi WebSocket terenkripsi:

`wss://broker.hivemq.com:8884/mqtt`

Pastikan endpoint yang digunakan tersedia pada broker. Jangan menggunakan `ws://` dari halaman HTTPS karena browser dapat memblokir koneksi tersebut.

### Format Pesan MQTT

Dashboard mengharapkan pesan JSON dengan format berikut:

```json
{
  "titik1": 1350,
  "titik2": 980,
  "status": "SIAGA"
}
```
