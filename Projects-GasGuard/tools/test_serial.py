import serial

PORT = "rfc2217://localhost:4000"
BAUDRATE = 115200

print("Menghubungkan ke serial Wokwi...")

try:
    with serial.serial_for_url(
        PORT,
        baudrate=BAUDRATE,
        timeout=1
    ) as ser:

        print("Terhubung! Menunggu data...\n")

        while True:
            data = ser.readline()

            if data:
                print(data.decode("utf-8", errors="replace").strip())

except KeyboardInterrupt:
    print("\nPengambilan data dihentikan.")

except serial.SerialException as error:
    print(f"Gagal mengakses serial: {error}")
