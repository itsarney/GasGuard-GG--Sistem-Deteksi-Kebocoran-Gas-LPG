import csv
import json
import math
import os
import time

from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
import paho.mqtt.client as mqtt

from dotenv import load_dotenv

# KONFIGURASI DIREKTORI

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "decision_tree_model.pkl"
LOG_PATH = BASE_DIR / "ai_prediction_log.csv"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

# KONFIGURASI MQTT

MQTT_HOST = os.getenv("MQTT_HOST", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

MQTT_SENSOR_TOPIC = os.getenv(
    "MQTT_SENSOR_TOPIC",
    "gasguard/kelompok8/device01/sensor/data"
)

MQTT_AI_TOPIC = os.getenv(
    "MQTT_AI_TOPIC",
    "gasguard/kelompok8/device01/ai/prediction"
)

MQTT_CLIENT_ID = "gasguard-ai-kelompok8"

# FITUR MODEL DECISION TREE

FEATURES = [
    "filter_tabung",
    "filter_dapur",
    "selisih_sensor",
    "tren_tabung",
    "tren_dapur"
]

VALID_CLASSES = {
    "AMAN",
    "WASPADA",
    "BAHAYA"
}

# MEMUAT MODEL

print("[AI] Memuat model Decision Tree...")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model tidak ditemukan: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

model_features = list(model.feature_names_in_)

if model_features != FEATURES:
    raise ValueError(
        "Urutan atau nama fitur model tidak sesuai.\n"
        f"Model: {model_features}\n"
        f"Program: {FEATURES}"
    )

model_classes = {
    str(label).upper()
    for label in model.classes_
}

if model_classes != VALID_CLASSES:
    raise ValueError(
        f"Kelas model tidak sesuai: {model_classes}"
    )

print("[AI] Model berhasil dimuat.")
print("[AI] Fitur:", model_features)
print("[AI] Kelas:", model_classes)


# PENCATATAN HASIL PREDIKSI

LOG_FIELDS = [
    "timestamp",
    "device_id",
    "firmware_status",
    *FEATURES,
    "prediction",
    "mqtt_publish"
]


def save_prediction(row):
    """Menyimpan hasil prediksi ke CSV."""

    file_exists = LOG_PATH.exists()

    with open(
        LOG_PATH,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=LOG_FIELDS
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

# VALIDASI NILAI NUMERIK

def get_number(value, field_name):
    """Memastikan nilai merupakan angka yang valid."""

    if value is None or isinstance(value, bool):
        raise ValueError(
            f"Field {field_name} kosong atau tidak valid."
        )

    try:
        number = float(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"Field {field_name} bukan angka."
        )

    if not math.isfinite(number):
        raise ValueError(
            f"Field {field_name} bukan angka finite."
        )

    return number

# FEATURE ENGINEERING

def prepare_features(data):
    """Mengubah payload MQTT menjadi lima fitur model."""

    if not isinstance(data, dict):
        raise ValueError("Payload harus berupa JSON object.")

    sensor_tabung = data.get("sensor_tabung")
    sensor_dapur = data.get("sensor_dapur")

    if not isinstance(sensor_tabung, dict):
        raise ValueError("Data sensor tabung tidak tersedia.")

    if not isinstance(sensor_dapur, dict):
        raise ValueError("Data sensor dapur tidak tersedia.")

    filter_tabung = get_number(
        sensor_tabung.get("adc_filter"),
        "sensor_tabung.adc_filter"
    )

    filter_dapur = get_number(
        sensor_dapur.get("adc_filter"),
        "sensor_dapur.adc_filter"
    )

    tren_tabung = get_number(
        sensor_tabung.get("tren"),
        "sensor_tabung.tren"
    )

    tren_dapur = get_number(
        sensor_dapur.get("tren"),
        "sensor_dapur.tren"
    )
    selisih_sensor = filter_tabung - filter_dapur

    features = pd.DataFrame(
        [[
            filter_tabung,
            filter_dapur,
            selisih_sensor,
            tren_tabung,
            tren_dapur
        ]],
        columns=FEATURES
    )

    return features


# MQTT CALLBACK: KONEKSI

def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    if reason_code == 0:

        print("[MQTT] Berhasil terhubung ke HiveMQ.")

        result, message_id = client.subscribe(
            MQTT_SENSOR_TOPIC,
            qos=0
        )

        if result == mqtt.MQTT_ERR_SUCCESS:
            print(
                "[MQTT] Subscribe berhasil:",
                MQTT_SENSOR_TOPIC
            )
        else:
            print("[MQTT] Subscribe gagal:", result)

    else:
        print(
            "[MQTT] Koneksi ditolak:",
            reason_code
        )

# MQTT CALLBACK: DISCONNECT

def on_disconnect(
    client,
    userdata,
    disconnect_flags,
    reason_code,
    properties
):
    print(
        "[MQTT] Terputus. Alasan:",
        reason_code
    )

    print("[MQTT] Mencoba menghubungkan kembali...")


# MQTT CALLBACK: MENERIMA DATA SENSOR

def on_message(client, userdata, msg):

    print("\n" + "=" * 45)
    print("[MQTT] Pesan sensor diterima.")

    try:
        # Mengubah payload byte menjadi JSON.
        raw_message = msg.payload.decode("utf-8")
        data = json.loads(raw_message)

        if not isinstance(data, dict):
            raise ValueError(
                "Payload JSON harus berbentuk object."
            )

        # Mengambil fitur sesuai model.
        input_data = prepare_features(data)

        print("\n[AI] Input Decision Tree:")
        print(input_data.to_string(index=False))

        # Menjalankan prediksi.
        prediction = str(
            model.predict(input_data)[0]
        ).strip().upper()

        if prediction not in VALID_CLASSES:
            raise ValueError(
                f"Hasil prediksi tidak dikenal: {prediction}"
            )

        firmware_status = str(
            data.get("status_sistem", "TIDAK DIKETAHUI")
        ).strip().upper()

        device_id = str(
            data.get("device_id", "unknown")
        )

        timestamp = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        print("\n[AI] HASIL PREDIKSI:", prediction)
        print("[AI] Status firmware:", firmware_status)

        # Membuat payload hasil AI.
        result_payload = {
            "device_id": device_id,
            "model": "DecisionTree",
            "prediction": prediction,
            "firmware_status": firmware_status,
            "timestamp": timestamp,
            "features": {
                feature: float(input_data.iloc[0][feature])
                for feature in FEATURES
            }
        }

        # Mengirim hasil AI ke topic baru.
        info = client.publish(
            MQTT_AI_TOPIC,
            json.dumps(result_payload),
            qos=0
        )

        publish_success = (
            info.rc == mqtt.MQTT_ERR_SUCCESS
        )

        publish_status = (
            "BERHASIL"
            if publish_success
            else "GAGAL"
        )

        print(
            "[MQTT] Publish hasil AI:",
            publish_status
        )

        # Mencatat hasil prediksi.
        log_row = {
            "timestamp": timestamp,
            "device_id": device_id,
            "firmware_status": firmware_status,
            **{
                feature: float(input_data.iloc[0][feature])
                for feature in FEATURES
            },
            "prediction": prediction,
            "mqtt_publish": publish_status
        }

        save_prediction(log_row)

        print("[AI] Hasil prediksi dicatat ke CSV.")

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        ValueError,
        KeyError,
        TypeError,
        OverflowError
    ) as error:

        print("[ERROR] Data sensor tidak valid:", error)

    except Exception as error:

        print("[ERROR] Gagal memproses pesan:", error)


# PROGRAM UTAMA

def main():

    print("\n")
    print(" GASGUARD - AI DECISION TREE")
    print("\n")

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=MQTT_CLIENT_ID
    )

    if MQTT_USERNAME:
        client.username_pw_set(
            MQTT_USERNAME,
            MQTT_PASSWORD
        )

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Mengatur jeda reconnect otomatis.
    client.reconnect_delay_set(
        min_delay=1,
        max_delay=30
    )

    print("[MQTT] Broker:", MQTT_HOST)
    print("[MQTT] Sensor topic:", MQTT_SENSOR_TOPIC)
    print("[MQTT] AI topic:", MQTT_AI_TOPIC)

    try:
        print("\n[MQTT] Menghubungkan ke HiveMQ...")

        client.connect(
            MQTT_HOST,
            MQTT_PORT,
            keepalive=60
        )

        # Menangani pesan dan reconnect.
        client.loop_forever(
            retry_first_connection=True
        )

    except KeyboardInterrupt:
        print("\n[PROGRAM] Dihentikan oleh pengguna.")

    except Exception as error:
        print("\n[ERROR] MQTT:", error)

    finally:
        client.disconnect()
        print("[PROGRAM] Koneksi MQTT ditutup.")


if __name__ == "__main__":
    main()
