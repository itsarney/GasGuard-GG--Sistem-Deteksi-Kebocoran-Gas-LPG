
import pandas as pd

# 1. Membaca dataset awal {disesuaikan alamat file}
FILE_INPUT = "Projects-GasGuard/dataset/dataset_simulasi.csv"
FILE_OUTPUT = "Projects-GasGuard/dataset/feature_engineering.csv"

df = pd.read_csv(FILE_INPUT)

# 2. Memastikan kolom yang diperlukan tersedia
kolom_wajib = [
    "timestamp_ms",
    "filter_tabung",
    "filter_dapur",
    "scenario_id"
]

for kolom in kolom_wajib:
    if kolom not in df.columns:
        raise ValueError(f"Kolom {kolom} tidak ditemukan!")

# 3. Mengurutkan data berdasarkan skenario dan waktu
df = df.sort_values(
    by=["scenario_id", "timestamp_ms"]
).reset_index(drop=True)

# 4. Feature Engineering: Selisih sensor
df["selisih_sensor"] = (
    df["filter_tabung"] - df["filter_dapur"]
)

# 5. Feature Engineering: Tren Tabung
df["tren_tabung"] = (
    df.groupby("scenario_id")["filter_tabung"].diff()
)

# 6. Feature Engineering: Tren Dapur
df["tren_dapur"] = (
    df.groupby("scenario_id")["filter_dapur"].diff()
)

# 7. Menyimpan dataset baru
df.to_csv(FILE_OUTPUT, index=False)

print("Feature Engineering selesai!")
print(f"Jumlah data: {len(df)}")
print(f"Dataset tersimpan di: {FILE_OUTPUT}")

# 8. Menampilkan contoh hasil
print("\nContoh hasil Feature Engineering:")
print(
    df[
        [
            "scenario_id",
            "filter_tabung",
            "filter_dapur",
            "selisih_sensor",
            "tren_tabung",
            "tren_dapur"
        ]
    ].head(10)
)
