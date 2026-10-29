# GasGuard - Sistem Deteksi Kebocoran Gas LPG Berbasis IoT 
Mencegah terjadinya kebocoran gas dengan pemantauan dua titik secara berkala dan analisis tren
---
<p> Risiko kebocoran gas LPG senantiasa mengintai di lingkungan rumah tangga. GasGuard terinspirasi dari penelitian terdahulu yang telah mengembangkan deteksi das menggunakan sensor MQ-6, ESP32, alarm, dan notifikasi jarak jauh. Proyek ini berfokus pada pengembangan sistem yang dapat mengolah dan membandingkan pembacaan sensor dari dua titik berbeda demi meningkatkan akurasi. </p>

## Rancangan Sistem
Adapun sistem GasGuard dirancang terdiri dari:
<ol>
  <li><i> Edge Device:</i>
    <ol>
    <li> <p>ESP32 sebagai "otak" perangkat yang membaca input sensor, memproses data, mengambil keputusan, dan mengirim data ke <i>cloud.</i></p> </li>
    <li> <p>HP Android sebagai perangkat yang meanmpilkan  informasi sensor dan meneruskan data sensor ke pengguna.</p></li>
    </ol>
  </li>
  <li> 2 Buah Sensor MQ-6 di dua titik pemantauan yang berbeda, yaitu di area tabung gas dan ruangan dapur
  </li>
  <li>Alarm <i>(buzzer)</i> sebagai aktuator yang  memberikan peringatan suara berdasarkan keputusan ESP32.</li>
  <li> Komunikasi melalui WiFi dan MQTT.</li>
  <li> <i>CLoud</i> sebagai penerima dan penerus data sensor.</li>
</ol>
<p>Simulasi Sistem GasGuard menggunakan Wokwi dan PlatformIO. Pada simulasi, potensiometer digunakan sebagai pengganti nilai keluaran sensor gas.</p>
