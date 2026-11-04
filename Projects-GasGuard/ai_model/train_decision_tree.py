from pathlib import Path

from sklearn.model_selection import GridSearchCV, StratifiedKFold
import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.tree import DecisionTreeClassifier, plot_tree

# =========================
# 1. KONFIGURASI
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATASET_CANDIDATES = [
    BASE_DIR / "dataset" / "feature_engineering.csv",
    BASE_DIR / "feature_engineering.csv",
    BASE_DIR / "dataset" / "feature_engineering(1).csv",
    BASE_DIR / "feature_engineering(1).csv",
]

FEATURES = [
    "filter_tabung",
    "filter_dapur",
    "selisih_sensor",
    "tren_tabung",
    "tren_dapur",
]
TARGET = "label_sistem"
SCENARIO_COLUMN = "scenario_id"
TEST_SCENARIO = "S04"
CLASS_ORDER = ["AMAN", "WASPADA", "BAHAYA"]

# =========================
# 2. TEMUKAN DAN BACA DATASET
# =========================
def find_dataset() -> Path:
    for candidate in DATASET_CANDIDATES:
        if candidate.is_file():
            return candidate

    expected = "\n".join(str(path) for path in DATASET_CANDIDATES)
    raise FileNotFoundError(
        "File feature_engineering.csv tidak ditemukan.\n"
        "Letakkan file di salah satu lokasi berikut:\n" + expected
    )


def main() -> None:
    dataset_path = find_dataset()
    print(f"Dataset ditemukan: {dataset_path}")

    data = pd.read_csv(dataset_path)
    print(f"Jumlah baris awal: {len(data)}")

    # Pastikan seluruh kolom yang dibutuhkan tersedia.
    required_columns = FEATURES + [TARGET, SCENARIO_COLUMN]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Kolom berikut tidak ditemukan: {missing_columns}")

    # Ubah fitur menjadi angka dan rapikan tulisan label/skenario.
    for column in FEATURES:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data[TARGET] = data[TARGET].astype("string").str.strip().str.upper()
    data[SCENARIO_COLUMN] = (
        data[SCENARIO_COLUMN].astype("string").str.strip().str.upper()
    )

    # Hanya gunakan tiga kelas target yang disepakati.
    data = data[data[TARGET].isin(CLASS_ORDER)].copy()

    # Baris dengan fitur tren kosong tidak dipakai pada training/testing.
    before_drop = len(data)
    data = data.dropna(subset=FEATURES + [TARGET, SCENARIO_COLUMN]).copy()
    dropped_rows = before_drop - len(data)

    print("\nDistribusi label berdasarkan skenario:")
    print(pd.crosstab(data[SCENARIO_COLUMN], data[TARGET]))

    if data.empty:
        raise ValueError("Tidak ada baris data yang tersisa setelah pembersihan.")

    print(f"Baris yang dihapus karena fitur/label kosong: {dropped_rows}")
    print(f"Jumlah baris siap pakai: {len(data)}")
    print("Distribusi label keseluruhan:")
    print(data[TARGET].value_counts().reindex(CLASS_ORDER, fill_value=0))

    # =========================
    # 3. PISAHKAN TRAINING DAN TESTING BERDASARKAN SKENARIO
    # =========================
    test_data = data[data[SCENARIO_COLUMN] == TEST_SCENARIO].copy()
    train_data = data[data[SCENARIO_COLUMN] != TEST_SCENARIO].copy()

    if train_data.empty or test_data.empty:
        available = sorted(data[SCENARIO_COLUMN].dropna().unique().tolist())
        raise ValueError(
            f"Data training/testing kosong. Skenario tersedia: {available}. "
            f"Periksa TEST_SCENARIO = {TEST_SCENARIO}."
        )

    missing_train_classes = sorted(set(CLASS_ORDER) - set(train_data[TARGET]))
    if missing_train_classes:
        raise ValueError(
            "Data training tidak memiliki semua kelas target: "
            f"{missing_train_classes}. Jangan lanjutkan training sebelum dataset diperbaiki."
        )

    print(f"\nSkenario untuk training: {sorted(train_data[SCENARIO_COLUMN].unique())}")
    print(f"Skenario untuk testing : {TEST_SCENARIO}")
    print(f"Jumlah data training   : {len(train_data)}")
    print(f"Jumlah data testing    : {len(test_data)}")

    X_train = train_data[FEATURES]
    y_train = train_data[TARGET]
    X_test = test_data[FEATURES]
    y_test = test_data[TARGET]

    # =========================
    # 4. HYPERPARAMETER TUNING
    # =========================

    parameter_grid = {
        "criterion": ["gini", "entropy"],
        "max_depth": [3, 4, 5, 6, 8, None],
        "min_samples_split": [2, 5, 10, 20],
        "min_samples_leaf": [2, 3, 5, 8, 10],
        "class_weight": [None, "balanced"]
    }

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    base_model = DecisionTreeClassifier(
        random_state=42
    )

    grid_search = GridSearchCV(
        estimator=base_model,
        param_grid=parameter_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=1
    )

    print("\nMemulai Hyperparameter Tuning...")

    grid_search.fit(X_train, y_train)

    model = grid_search.best_estimator_

    print("\n========== MODEL TERBAIK ==========")
    print("Parameter terbaik:")
    print(grid_search.best_params_)

    print(
        "Macro F1-score validasi:",
        round(grid_search.best_score_, 4)
    )

    # Prediksi menggunakan data testing S04
    predictions = model.predict(X_test)

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    # =========================
    # 5. EVALUASI MODEL
    # =========================
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(
        y_test,
        predictions,
        labels=CLASS_ORDER,
        target_names=CLASS_ORDER,
        digits=3,
        zero_division=0,
    )

    matrix = confusion_matrix(y_test, predictions, labels=CLASS_ORDER)
    matrix_df = pd.DataFrame(
        matrix,
        index=[f"Aktual_{label}" for label in CLASS_ORDER],
        columns=[f"Prediksi_{label}" for label in CLASS_ORDER],
    )

    print("\n========== HASIL EVALUASI ==========")
    print(f"Akurasi testing: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print("\nClassification report:")
    print(report)
    print("Confusion matrix (baris = aktual, kolom = prediksi):")
    print(matrix_df)

    # =========================
    # 6. SIMPAN MODEL DAN LAPORAN
    # =========================
    model_path = BASE_DIR / "decision_tree_model.pkl"
    report_path = BASE_DIR / "classification_report.txt"
    matrix_path = BASE_DIR / "confusion_matrix.csv"
    importance_path = BASE_DIR / "feature_importance.csv"
    tree_image_path = BASE_DIR / "decision_tree.png"

    joblib.dump(model, model_path)
    matrix_df.to_csv(matrix_path)

    importance_df = pd.DataFrame(
        {
            "fitur": FEATURES,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    importance_df.to_csv(importance_path, index=False)

    with report_path.open("w", encoding="utf-8") as report_file:
        report_file.write(f"Dataset: {dataset_path.name}\n")
        report_file.write(f"Training rows: {len(train_data)}\n")
        report_file.write(f"Testing rows: {len(test_data)}\n")
        report_file.write(f"Test scenario: {TEST_SCENARIO}\n")
        report_file.write(f"Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)\n\n")
        report_file.write(report)
        report_file.write("\nConfusion matrix (baris = aktual, kolom = prediksi):\n")
        report_file.write(matrix_df.to_string())
        report_file.write("\n\nFeature importance:\n")
        report_file.write(importance_df.to_string(index=False))

    # Gambar pohon keputusan agar proses klasifikasi mudah dijelaskan.
    plt.figure(figsize=(24, 12))
    plot_tree(
        model,
        feature_names=FEATURES,
        class_names=model.classes_.tolist(),
        filled=True,
        rounded=True,
        fontsize=8,
    )
    plt.title("Decision Tree - GasGuard")
    plt.tight_layout()
    plt.savefig(tree_image_path, dpi=180, bbox_inches="tight")
    plt.close()

    print("\n========== FILE BERHASIL DISIMPAN ==========")
    print(f"Model             : {model_path}")
    print(f"Laporan evaluasi  : {report_path}")
    print(f"Confusion matrix  : {matrix_path}")
    print(f"Feature importance: {importance_path}")
    print(f"Gambar pohon      : {tree_image_path}")
    print("\nSelesai. Model prototipe")


if __name__ == "__main__":
    main()

