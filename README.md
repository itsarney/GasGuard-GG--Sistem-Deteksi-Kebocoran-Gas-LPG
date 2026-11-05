# GasGuard - Sistem Deteksi Kebocoran Gas LPG Berbasis IoT 
Mencegah terjadinya kebocoran gas dengan pemantauan dua titik secara berkala dan analisis tren
---
<p> Risiko kebocoran gas LPG senantiasa mengintai di lingkungan rumah tangga. GasGuard terinspirasi dari penelitian terdahulu yang telah mengembangkan deteksi das menggunakan sensor MQ-6, ESP32, alarm, dan notifikasi jarak jauh. Proyek ini berfokus pada pengembangan sistem yang dapat mengolah dan membandingkan pembacaan sensor dari dua titik berbeda demi meningkatkan akurasi. </p>

## Rancangan Sistem
Adapun sistem GasGuard dirancang terdiri dari:
<ol>
  <li><p><i> Edge Device:</i></p>
    <ol>
    <li> <p>ESP32 sebagai "otak" perangkat yang membaca input sensor, memproses data, mengambil keputusan, dan mengirim data ke <i>cloud.</i></p> </li>
    <li> <p>HP Android sebagai perangkat yang  meneruskan data sensor dan menampilkan informasi sensor ke pengguna melalui <i>dashboard.</i> </p></li>
    </ol>
  </li>
  <li> <p>2 Buah Sensor MQ-6 di dua titik pemantauan yang berbeda, yaitu di area tabung gas dan ruangan dapur.</p>
  </li>
  <li> <p>Alarm <i>(buzzer)</i> sebagai aktuator yang  memberikan peringatan suara berdasarkan keputusan ESP32.</li></p>
  <li> <p>Komunikasi melalui WiFi dan MQTT.</p></li>
  <li> <p><i>Cloud</i> sebagai penerima dan penerus data sensor.</p></li>
</ol>
<p>Simulasi Sistem GasGuard menggunakan Wokwi dan PlatformIO. Pada simulasi, potensiometer digunakan sebagai pengganti nilai keluaran sensor gas. Sistem juga menggunakan <i>Moving Median</i> dan <i>Decision Tree Algorithm </i> dalam menentukan status dari pembacaaan sensor. Terdapat pula model yang dikembangkan untuk melakukan hal yang sama berdasarkan input pembacaan sensor yang dilatih menggunakan sekumpulan dataset berlabel skenario tertentu. Semua hasil tersebut akan ditampilkan pada <i>dashboard android</i>. </p
--
><p>Untuk dokumentasi selengkapnya, dipersilakan untuk mengecek file-file yang terdapat pada folder <i>docs</i>.</p>

