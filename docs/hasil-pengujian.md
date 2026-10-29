# Hasil Pengujian GasGuard

**Dokumen ini adalah template.** Isi berdasarkan pengujian aktual. Jangan mengganti status menjadi Berhasil jika belum ada hasil yang diamati dan/atau bukti pendukung.

## Informasi pengujian

- Tanggal: Belum diisi
- Penguji: Belum diisi
- Firmware/commit yang diuji: Belum diisi
- Lingkungan: Wokwi, browser laptop/HP, broker MQTT publik
- Ringkasan hasil: Belum dapat disimpulkan

## Hasil per skenario

| ID | Hasil aktual | Bukti (screenshot/log/video) | Status | Catatan |
|---|---|---|---|---|
| T01 | Belum diuji | — | Belum diuji | — |
| T02 | Belum diuji | — | Belum diuji | — |
| T03 | Belum diuji | — | Belum diuji | — |
| T04 | Belum diuji | — | Belum diuji | — |
| T05 | Belum diuji | — | Belum diuji | — |
| T06 | Belum diuji | — | Belum diuji | — |
| T07 | Belum diuji | — | Belum diuji | — |
| T08 | Belum diuji | — | Belum diuji | — |

## Catatan keterbatasan

Pengujian Wokwi menggunakan potentiometer sebagai simulasi input analog. Hasilnya tidak memvalidasi sensor MQ-6 fisik atau membuktikan sistem memenuhi standar perangkat keselamatan LPG. Hasil respons buzzer ketika MQTT terputus perlu ditulis sesuai pengamatan. Implementasi reconnect yang menunggu koneksi pada loop dapat menahan pembacaan dan pemrosesan sampai koneksi kembali.
