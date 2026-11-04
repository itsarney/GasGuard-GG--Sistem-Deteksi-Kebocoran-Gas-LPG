import serial
import csv
import os

# Konfigurasi serial Wokwi
PORT = "rfc2217://localhost:4000"
BAUDRATE = 115200

# Lokasi file dataset {sesuaikan nama file}
FILE_CSV = "dataset/test_dataset.csv"

# Nama kolom dataset
HEADER = [
    "timestamp_ms",
    "adc_tabung",
    "adc_dapur",
    "filter_tabung",
    "filter_dapur",
    "label_tabung",
    "label_dapur",
    "label_sistem",
    "scenario_id"
]

# Pastikan folder dataset tersedia
os.makedirs("dataset", exist_ok=True)

# Periksa apakah file sudah memiliki header
file_baru = (
    not os.path.exists(FILE_CSV)
    or os.path.getsize(FILE_CSV) == 0
)

print("----- GasGuard CSV Logger -----")
print("Menghubungkan ke Wokwi...")

try:
    with serial.serial_for_url(
        PORT,
        baudrate=BAUDRATE,
        timeout=1
    ) as ser:

        with open(
            FILE_CSV,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            if file_baru:
                writer.writerow(HEADER)
                file.flush()

            print("Terhubung! Merekam dataset...")
            print(f"File: {FILE_CSV}")
            print("Tekan Ctrl+C untuk berhenti.\n")

            jumlah_data = 0

            while True:
                baris = ser.readline()

                if not baris:
                    continue

                teks = baris.decode(
                    "utf-8",
                    errors="replace"
                ).strip()

                # Hanya ambil keluaran yang diawali CSV,
                if not teks.startswith("CSV,"):
                    continue

                data = teks.split(",")[1:]

                # Pastikan jumlah kolom sesuai
                if len(data) != len(HEADER):
                    print("Baris dilewati:", teks)
                    continue

                writer.writerow(data)
                file.flush()

                jumlah_data += 1

                print(
                    f"Data ke-{jumlah_data}: "
                    f"{data[1]}, {data[2]} "
                    f"| {data[7]}"
                )

except KeyboardInterrupt:
    print("\nPerekaman dihentikan.")

except serial.SerialException as error:
    print(f"\nKesalahan serial: {error}")

print(f"Dataset tersimpan di: {FILE_CSV}")