
#include <Arduino.h>

// Pin input sensor MQ-6
const int SENSOR_TABUNG = 34;
const int SENSOR_DAPUR = 35;

// Pin buzzer
const int BUZZER_PIN = 25;

// Ambang ADC awal untuk pengujian
const int BATAS_NORMAL = 1200;
const int BATAS_BAHAYA = 2000;

// Data mentah
int nilaiTabung = 0;
int nilaiDapur = 0;

// baca dua input sensor MQ-6
void bacaSensor() {
    nilaiTabung = analogRead(SENSOR_TABUNG);
    nilaiDapur = analogRead(SENSOR_DAPUR);
}

// Menampilkan status kondisi gas berdasarkan nilai ADC
const char* kondisiGas(int nilai) {
    if (nilai <= BATAS_NORMAL) {
        return "NORMAL";
    } else if (nilai <= BATAS_BAHAYA) {
        return "WASPADA";
    } else {
        return "BAHAYA";
    }
}

// Menampilkan data mentah dan kondisi setiap titik
void dataSensor() {
    Serial.println(" ------------------------------ ");
    Serial.print("Nilai Tabung  : ");
    Serial.print(nilaiTabung);
    Serial.print(", Nilai Dapur : ");
    Serial.print(nilaiDapur);
    Serial.print(", Kondisi Tabung  : ");
    Serial.print(kondisiGas(nilaiTabung));
    Serial.print(", Kondisi Dapur   : ");
    Serial.println(kondisiGas(nilaiDapur));
    Serial.println(" ------------------------------ ");
}

// Alarm lokal jika salah satu titik berbahaya
void statusAlarm() {
    bool bahaya =
        (nilaiTabung > BATAS_BAHAYA) ||
        (nilaiDapur > BATAS_BAHAYA);

    if (bahaya) {
        tone(BUZZER_PIN, 2000);
        Serial.println("!!! BAHAYA - ALARM GASGUARD AKTIF !!!");
    } else {
        noTone(BUZZER_PIN);
        Serial.println("--- Alarm lokal tidak aktif ---");
    }
}

void setup() {
    Serial.begin(115200);

    analogReadResolution(12); // Resolusi ADC 12-bit (0-4095)

    pinMode(SENSOR_TABUNG, INPUT);
    pinMode(SENSOR_DAPUR, INPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    digitalWrite(BUZZER_PIN, LOW);
    noTone(BUZZER_PIN);

    Serial.println("===============================");
    Serial.println(" PROYEK KELOMPOK 8 IoT KELAS D ");
    Serial.println("===============================");
    Serial.println(" ------- GasGuard ESP32 ------ ");
    Serial.println("Pemantauan gas LPG dengan sensor");
    Serial.println("    MQ-6 dan alarm lokal.");
    Serial.println("================================");
    Serial.println("ADC_Tabung, ADC_Dapur, KONDISI_Tabung, KONDISI_Dapur");
}

void loop() {
    bacaSensor();
    dataSensor();   
    
    Serial.println("================================");
    statusAlarm();
    Serial.println("================================");
    Serial.println(" ");

    delay(500);
}
