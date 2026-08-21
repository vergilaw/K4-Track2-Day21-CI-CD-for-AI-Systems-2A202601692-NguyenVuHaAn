import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
import json
import joblib
import os
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

# Nguong chat luong cua lab nay la f1_score, KHONG phai accuracy.
# Ly do: bo du lieu Adult co ty le lop 75/25. Mot mo hinh doan bua
# "thu nhap thap" cho moi mau da dat accuracy 0.75 ma khong hoc duoc gi.
F1_THRESHOLD = 0.65


def train(
    params: dict,
    data_path: str = "data/train_batch1.csv",
    eval_path: str = "data/holdout.csv",
) -> float:
    """
    Huan luyen mo hinh va ghi nhan ket qua vao MLflow.

    Tham so:
        params     : dict chua cac sieu tham so cho GradientBoostingClassifier.
        data_path  : duong dan den file du lieu huan luyen.
        eval_path  : duong dan den file du lieu danh gia (holdout).

    Tra ve:
        f1 (float): diem F1 cua lop duong (thu nhap > 50K) tren tap holdout.
    """

    # TODO 1: Doc du lieu huan luyen va danh gia
    df_train = pd.read_csv(data_path)
    df_eval  = pd.read_csv(eval_path)

    # TODO 2: Tach dac trung (X) va nhan (y)
    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval  = df_eval.drop(columns=["target"])
    y_eval  = df_eval["target"]

    # BONUS 5: Canh bao Data Drift co ban (Kiem tra lech phan phoi tuoi)
    age_mean_train = X_train["age"].mean()
    age_mean_eval = X_eval["age"].mean()
    age_drift = abs(age_mean_train - age_mean_eval)
    if age_drift > 2.0:
        print(f"WARNING: Data Drift phat hien tren dac trung 'age'! (Lech {age_drift:.2f} tuoi)")

    with mlflow.start_run():

        # TODO 3: Ghi nhan cac sieu tham so
        mlflow.log_params(params)

        # TODO 4: Khoi tao va huan luyen GradientBoostingClassifier
        model = GradientBoostingClassifier(**params, random_state=42)
        model.fit(X_train, y_train)

        # TODO 5: Du doan tren tap holdout va tinh chi so
        preds = model.predict(X_eval)
        f1    = f1_score(y_eval, preds)
        acc   = accuracy_score(y_eval, preds)

        # TODO 6: Ghi nhan chi so vao MLflow
        mlflow.log_metric("f1_score", float(f1))
        mlflow.log_metric("accuracy", float(acc))
        mlflow.log_metric("age_drift", float(age_drift))
        mlflow.sklearn.log_model(model, "model")

        # TODO 7: In ket qua ra man hinh
        print(f"F1: {f1:.4f} | Accuracy: {acc:.4f}")

        # TODO 8: Luu metrics ra file outputs/report.json
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/report.json", "w") as f:
            json.dump({"f1_score": float(f1), "accuracy": float(acc)}, f)

        # BONUS 3: Luu Precision/Recall, Confusion Matrix ra detail.txt
        with open("outputs/detail.txt", "w") as f:
            f.write("=== CLASSIFICATION REPORT ===\n")
            f.write(classification_report(y_eval, preds))
            f.write("\n\n=== CONFUSION MATRIX ===\n")
            f.write(str(confusion_matrix(y_eval, preds)))

        # TODO 9: Luu mo hinh ra file models/model.joblib
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.joblib")

    # TODO 10: Tra ve f1
    return float(f1)


if __name__ == "__main__":
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    train(params)
