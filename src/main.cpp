#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// --- KONFIGURASI WIFI & MQTT ---
const char* ssid = "Wokwi-GUEST";
const char* password = ""; 
const char* mqtt_server = "broker.hivemq.com"; 

WiFiClient espClient;
PubSubClient client(espClient);

// --- PIN PERANGKAT KERAS (Sesuai Konfigurasi Anggota 1) ---
const int SENSOR_TABUNG = 34;  // Pin ADC Sensor 1 (Area Tabung Gas)
const int SENSOR_DAPUR = 35;   // Pin ADC Sensor 2 (Area Dapur)
const int BUZZER_PIN = 25;     // Pin Buzzer Alarm Lokal

// --- KONFIGURASI FILTER & TREN ---
const int WINDOW_SIZE = 5;
float buffer1[WINDOW_SIZE];
float buffer2[WINDOW_SIZE];
int head1 = 0;
int head2 = 0;

float lastFiltered1 = 0;
float lastFiltered2 = 0;

// Fungsi Median
float getMedian(float arr[], int n) {
    float temp[n];
    for(int i = 0; i < n; i++) temp[i] = arr[i];
    for(int i = 0; i < n - 1; i++) {
        for(int j = 0; j < n - i - 1; j++) {
            if(temp[j] > temp[j + 1]) {
                float t = temp[j]; temp[j] = temp[j + 1]; temp[j + 1] = t;
            }
        }
    }
    return temp[n / 2];
}

float calculateMovingMedian(float newValue, float buffer[], int *head, int n) {
    buffer[*head] = newValue;
    *head = (*head + 1) % n;
    return getMedian(buffer, n);
}

String compareGasPoints(float titik1, float titik2) {
    if (titik1 > titik2) {
        return "TABUNG LEBIH TINGGI";
    } else if (titik2 > titik1) {
        return "DAPUR LEBIH TINGGI";
    } else {
        return "KEDUA TITIK SAMA";
    }
}

// --- ALGORITMA EVALUASI STATUS & KEPUTUSAN ---
String evaluateGasStatus(float currentFiltered1, float currentFiltered2) {
    float trend1 = currentFiltered1 - lastFiltered1;
    float trend2 = currentFiltered2 - lastFiltered2;
    lastFiltered1 = currentFiltered1;
    lastFiltered2 = currentFiltered2;

    // Logika Pengambilan Keputusan & Kontrol Buzzer
    if (currentFiltered1 > 2500 || currentFiltered2 > 2500) {
        digitalWrite(BUZZER_PIN, HIGH); // Nyalakan Buzzer jika Bahaya
        return "BAHAYA";
    } else if (trend1 > 150 || trend2 > 150) {
        digitalWrite(BUZZER_PIN, HIGH); // Nyalakan Buzzer jika Tren Cepat Naik
        return "WASPADA";
    } else if (currentFiltered1 > 1200 || currentFiltered2 > 1200) {
        digitalWrite(BUZZER_PIN, LOW);
        return "SIAGA";
    } else {
        digitalWrite(BUZZER_PIN, LOW);
        return "AMAN";
    }
}

// Fungsi Koneksi WiFi
void setup_wifi() {
    Serial.println();
    Serial.println("Menghubungkan ke WiFi Wokwi...");

    WiFi.mode(WIFI_STA);
    WiFi.begin("Wokwi-GUEST", "", 6);

    int percobaan = 0;

    while (WiFi.status() != WL_CONNECTED && percobaan < 30) {
        delay(500);
        Serial.print(".");
        percobaan++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi terhubung!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi gagal terhubung.");
    }
}

// Fungsi Rekoneksi MQTT
void reconnect() {
    while (!client.connected()) {
        Serial.print("Menghubungkan ke MQTT Broker...");
        String clientId = "GasGuardHana-";
        clientId += String(random(0xffff), HEX);
        
        if (client.connect(clientId.c_str())) {
            Serial.println("TERHUBUNG!");
        } else {
            Serial.print("Gagal, rc=");
            Serial.print(client.state());
            Serial.println(" Coba lagi dalam 5 detik...");
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);

    setup_wifi();
    client.setServer(mqtt_server, 1883);

    float nilaiAwal1 = analogRead(34);
    float nilaiAwal2 = analogRead(35);

    for (int i = 0; i < WINDOW_SIZE; i++) {
        buffer1[i] = nilaiAwal1;
        buffer2[i] = nilaiAwal2;
}

    lastFiltered1 = nilaiAwal1;
    lastFiltered2 = nilaiAwal2;
    
    Serial.println("=== GasGuard: Branch 2 (Moving Median & MQTT) Loaded ===");
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();

    // Membaca data mentah dari pin sensor
    float raw1 = analogRead(SENSOR_TABUNG);
    float raw2 = analogRead(SENSOR_DAPUR);

    // Data Processing 1: Moving Median Filtering
    float filtered1 = calculateMovingMedian(raw1, buffer1, &head1, WINDOW_SIZE);
    float filtered2 = calculateMovingMedian(raw2, buffer2, &head2, WINDOW_SIZE);

    // Data Processing 2: Evaluasi Tren & Status Sistem
    String status = evaluateGasStatus(filtered1, filtered2);

    // Membandingkan nilai gas di Titik 1 dan Titik 2
    String perbandingan = compareGasPoints(filtered1, filtered2);

    // Format payload JSON untuk dikirim via MQTT
    String payload = "{";
    payload += "\"titik1\":" + String(filtered1) + ",";
    payload += "\"titik2\":" + String(filtered2) + ",";
    payload += "\"status\":\"" + status + "\"";
    payload += "}";

    // Publikasikan data ke topik MQTT
    bool berhasil = client.publish("gasguard/sensor/data", payload.c_str());

    if (berhasil) {
        Serial.println("MQTT: Pesan berhasil dikirim ke broker");
    } else {
        Serial.println("MQTT: Pesan gagal dikirim");
    }

    // Cetak ke Serial Monitor untuk memantau hasil
    Serial.print("T1 [Filtered]: ");
    Serial.print(filtered1);
    Serial.print(" | T2 [Filtered]: ");
    Serial.print(filtered2);
    Serial.print(" | Status: ");
    Serial.print(status);
    Serial.print(" | Perbandingan: ");
    Serial.println(perbandingan);


    delay(2000);
}
