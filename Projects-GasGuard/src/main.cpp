#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// =====================================================
//              KONFIGURASI WIFI DAN MQTT
// =====================================================
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";
const char* MQTT_SERVER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "gasguard/sensor/data";

// identitas skenario dataset untuk membedakan dataset
const char* SCENARIO_ID = "S00"; //test

WiFiClient espClient;
PubSubClient client(espClient);

// =====================================================
// PIN DAN AMBANG SENSOR (konsisten dengan firmware awal)
// =====================================================
const int SENSOR_TABUNG = 34;
const int SENSOR_DAPUR = 35;
const int BUZZER_PIN = 25;

const int BATAS_AMAN = 1200;
const int BATAS_BAHAYA = 2000;

// Tren naik cepat: kenaikan ADC lebih dari 150
// di antara dua pembacaan filter berturut-turut.
// Nilai ini masih parameter awal untuk simulasi.
const float BATAS_TREN_NAIK = 150.0;

// =====================================================
//            DATA SENSOR DAN MOVING MEDIAN
// =====================================================
const int WINDOW_SIZE = 5;

int nilaiMentahTabung = 0;
int nilaiMentahDapur = 0;

float nilaiFilterTabung = 0;
float nilaiFilterDapur = 0;

float bufferTabung[WINDOW_SIZE];
float bufferDapur[WINDOW_SIZE];

int posisiBufferTabung = 0;
int posisiBufferDapur = 0;

float nilaiFilterSebelumnyaTabung = 0;
float nilaiFilterSebelumnyaDapur = 0;

float trenTabung = 0;
float trenDapur = 0;

unsigned long waktuPembacaanSebelumnya = 0;
unsigned long waktuPublishSebelumnya = 0;
unsigned long waktuCobaMQTTSebelumnya = 0;

const unsigned long INTERVAL_PEMBACAAN = 500;
const unsigned long INTERVAL_PUBLISH = 2000;
const unsigned long INTERVAL_COBA_MQTT = 5000;

bool dataFilterPertama = true;

// =====================================================
//               FUNGSI SENSOR DAN FILTER
// =====================================================
void bacaSensor() {
    nilaiMentahTabung = analogRead(SENSOR_TABUNG);
    nilaiMentahDapur = analogRead(SENSOR_DAPUR);
}

float hitungMedian(float data[], int jumlah) {
    float sementara[WINDOW_SIZE];

    for (int i = 0; i < jumlah; i++) {
        sementara[i] = data[i];
    }

    // Pengurutan sederhana (bubble sort)
    for (int i = 0; i < jumlah - 1; i++) {
        for (int j = 0; j < jumlah - i - 1; j++) {
            if (sementara[j] > sementara[j + 1]) {
                float temp = sementara[j];
                sementara[j] = sementara[j + 1];
                sementara[j + 1] = temp;
            }
        }
    }

    return sementara[jumlah / 2];
}

float hitungMovingMedian(
    float nilaiBaru,
    float buffer[],
    int &posisi
) {
    buffer[posisi] = nilaiBaru;
    posisi = (posisi + 1) % WINDOW_SIZE;

    return hitungMedian(buffer, WINDOW_SIZE);
}

void prosesFiltering() {
    nilaiFilterTabung = hitungMovingMedian(
        nilaiMentahTabung,
        bufferTabung,
        posisiBufferTabung
    );

    nilaiFilterDapur = hitungMovingMedian(
        nilaiMentahDapur,
        bufferDapur,
        posisiBufferDapur
    );
}

// =====================================================
//     KLASIFIKASI, PERBANDINGAN, DAN ANALISIS TREN
// =====================================================
const char* kondisiGas(float nilai) {
    if (nilai <= BATAS_AMAN) {
        return "AMAN";
    } else if (nilai <= BATAS_BAHAYA) {
        return "WASPADA";
    } else {
        return "BAHAYA";
    }
}

void analisisTren() {
    if (dataFilterPertama) {
        trenTabung = 0;
        trenDapur = 0;
        dataFilterPertama = false;
    } else {
        trenTabung =
            nilaiFilterTabung - nilaiFilterSebelumnyaTabung;

        trenDapur =
            nilaiFilterDapur - nilaiFilterSebelumnyaDapur;
    }

    nilaiFilterSebelumnyaTabung = nilaiFilterTabung;
    nilaiFilterSebelumnyaDapur = nilaiFilterDapur;
}

const char* bandingkanTitik() {
    if (nilaiFilterTabung > nilaiFilterDapur) {
        return "TABUNG_LEBIH_TINGGI";
    } else if (nilaiFilterDapur > nilaiFilterTabung) {
        return "DAPUR_LEBIH_TINGGI";
    } else {
        return "KEDUA_TITIK_SAMA";
    }
}

const char* tentukanStatusSistem() {
    bool bahaya =
        nilaiFilterTabung > BATAS_BAHAYA ||
        nilaiFilterDapur > BATAS_BAHAYA;

    bool waspada =
        nilaiFilterTabung > BATAS_AMAN ||
        nilaiFilterDapur > BATAS_AMAN ||
        trenTabung > BATAS_TREN_NAIK ||
        trenDapur > BATAS_TREN_NAIK;

    if (bahaya) {
        return "BAHAYA";
    } else if (waspada) {
        return "WASPADA";
    } else {
        return "AMAN";
    }
}

// =====================================================
//                    ALARM LOKAL
// Menggunakan tone/noTone seperti firmware awal.
// untuk buzzer pasif Wokwi.
void perbaruiAlarm(const char* statusSistem) {
    if (strcmp(statusSistem, "BAHAYA") == 0) {
        tone(BUZZER_PIN, 2000);
    } else {
        noTone(BUZZER_PIN);
        digitalWrite(BUZZER_PIN, LOW);
    }
}

// =====================================================
//                    WIFI DAN MQTT 
// =====================================================
void mulaiWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.println("\n[ Memulai koneksi Wi-Fi... ]");
}

void cobaHubungkanMQTT() {
    if (WiFi.status() != WL_CONNECTED || client.connected()) {
        return;
    }

    unsigned long sekarang = millis();

    if (sekarang - waktuCobaMQTTSebelumnya < INTERVAL_COBA_MQTT) {
        return;
    }

    waktuCobaMQTTSebelumnya = sekarang;

    String clientId = "GasGuard-";
    clientId += String((uint32_t)ESP.getEfuseMac(), HEX);

    Serial.print("\n[ Mencoba koneksi MQTT... ]");

    if (client.connect(clientId.c_str())) {
        Serial.println("[ TERHUBUNG ]\n");
    } else {
        Serial.print("\n[ GAGAL, state = ");
        Serial.println(client.state());
        Serial.print(" ]\n [ Mencoba lagi dalam ");
        Serial.print(INTERVAL_COBA_MQTT / 1000);
        Serial.println(" detik ]\n");
    }
}

void kirimDataMQTT(const char* statusSistem) {
    if (!client.connected()) {
        return;
    }

    String payload = "{";
    payload += "\"device_id\":\"gasguard_01\",";
    payload += "\"sensor_tabung\":{";
    payload += "\"adc_mentah\":" + String(nilaiMentahTabung) + ",";
    payload += "\"adc_filter\":" + String(nilaiFilterTabung, 1) + ",";
    payload += "\"status\":\"" + String(kondisiGas(nilaiFilterTabung)) + "\",";
    payload += "\"tren\":" + String(trenTabung, 1);
    payload += "},";
    payload += "\"sensor_dapur\":{";
    payload += "\"adc_mentah\":" + String(nilaiMentahDapur) + ",";
    payload += "\"adc_filter\":" + String(nilaiFilterDapur, 1) + ",";
    payload += "\"status\":\"" + String(kondisiGas(nilaiFilterDapur)) + "\",";
    payload += "\"tren\":" + String(trenDapur, 1);
    payload += "},";
    payload += "\"selisih_sensor\":" +
    String(abs(nilaiFilterTabung - nilaiFilterDapur), 1) + ",";

    payload += "\"perbandingan\":\"" + String(bandingkanTitik()) + "\",";
    payload += "\"status_sistem\":\"" + String(statusSistem) + "\",";
    payload += "\"alarm\":" + String(
        strcmp(statusSistem, "BAHAYA") == 0 ? "true" : "false"
    );
    payload += "}";

    bool berhasil = client.publish(MQTT_TOPIC, payload.c_str());

    Serial.println(
        berhasil ? "\n[ MQTT: data berhasil dikirim ]\n"
                 : "\n[ MQTT: data gagal dikirim ]\n"
    );
}

// =====================================================
//                    OUTPUT SERIAL
// =====================================================
void cetakData() {
    Serial.print("Tabung mentah: ");
    Serial.print(nilaiMentahTabung);
    Serial.print(" | Tabung filter: ");
    Serial.print(nilaiFilterTabung, 1);
    Serial.print(" | Status: ");
    Serial.print(kondisiGas(nilaiFilterTabung));

    Serial.print(" || Dapur mentah: ");
    Serial.print(nilaiMentahDapur);
    Serial.print(" | Dapur filter: ");
    Serial.print(nilaiFilterDapur, 1);
    Serial.print(" | Status: ");
    Serial.print(kondisiGas(nilaiFilterDapur));

    Serial.print(" || Tren tabung: ");
    Serial.print(trenTabung, 1);
    Serial.print(" | Tren dapur: ");
    Serial.println(trenDapur, 1);
}

void cetakBarisCSV(const char* statusSistem) {
    Serial.print("\nCSV,");
    Serial.print(millis());
    Serial.print(",");
    Serial.print(nilaiMentahTabung);
    Serial.print(",");
    Serial.print(nilaiMentahDapur);
    Serial.print(",");
    Serial.print(nilaiFilterTabung, 1);
    Serial.print(",");
    Serial.print(nilaiFilterDapur, 1);
    Serial.print(",");
    Serial.print(kondisiGas(nilaiFilterTabung));
    Serial.print(",");
    Serial.print(kondisiGas(nilaiFilterDapur));
    Serial.print(",");
    Serial.print(statusSistem);
    Serial.print(",");
    Serial.println(SCENARIO_ID);
}

// =====================================================
//                    SETUP DAN LOOP
// =====================================================
void setup() {
    Serial.begin(115200);

    analogReadResolution(12);

    pinMode(SENSOR_TABUNG, INPUT);
    pinMode(SENSOR_DAPUR, INPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    digitalWrite(BUZZER_PIN, LOW);
    noTone(BUZZER_PIN);

    // Isi awal buffer dengan pembacaan pertama agar median
    // tidak tercampur nilai nol saat lima sampel pertama.
    bacaSensor();

    for (int i = 0; i < WINDOW_SIZE; i++) {
        bufferTabung[i] = nilaiMentahTabung;
        bufferDapur[i] = nilaiMentahDapur;
    }

    nilaiFilterTabung = nilaiMentahTabung;
    nilaiFilterDapur = nilaiMentahDapur;

    nilaiFilterSebelumnyaTabung = nilaiFilterTabung;
    nilaiFilterSebelumnyaDapur = nilaiFilterDapur;

    client.setServer(MQTT_SERVER, MQTT_PORT);

    mulaiWiFi();

    Serial.println("=== GasGuard: Firmware + Wi-Fi + MQTT ===");
    Serial.println("Status kondisi: AMAN / WASPADA / BAHAYA");
}

void loop() {
    unsigned long sekarang = millis();

    // Wi-Fi/MQTT dikelola tanpa menghentikan loop alarm.
    cobaHubungkanMQTT();

    if (client.connected()) {
        client.loop();
    }

    // Pembacaan dan alarm lokal tetap berjalan setiap 500 ms.
    if (sekarang - waktuPembacaanSebelumnya >= INTERVAL_PEMBACAAN) {
        waktuPembacaanSebelumnya = sekarang;

        bacaSensor();
        prosesFiltering();
        analisisTren();

        const char* statusSistem = tentukanStatusSistem();

        // Alarm diproses langsung, tidak menunggu MQTT.
        perbaruiAlarm(statusSistem);

        cetakData();
        cetakBarisCSV(statusSistem);
        // Publish lebih jarang daripada pembacaan sensor.
        if (sekarang - waktuPublishSebelumnya >= INTERVAL_PUBLISH) {
            waktuPublishSebelumnya = sekarang;
            kirimDataMQTT(statusSistem);
        }
    }
}
