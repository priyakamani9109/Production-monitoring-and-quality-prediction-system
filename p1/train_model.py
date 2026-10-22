"""
train_model.py

Trains a Random Forest Regressor to predict the expected number of
defective rolls from production parameters, and saves the trained model
plus the label encoders to model/ for use by the Streamlit dashboard.
"""

import pickle

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATA_PATH = "data/production_data.xlsx"
MODEL_PATH = "model/model.pkl"
ENCODERS_PATH = "model/encoders.pkl"

CATEGORICAL_COLS = ["Shift", "Machine_Type", "Bonding_Type"]
FEATURE_COLS = ["Shift", "Machine_Type", "Bonding_Type", "Rolls_Produced", "Downtime_Minutes"]
TARGET_COL = "Defective_Rolls"


def main():
    df = pd.read_excel(DATA_PATH)

    encoders = {}
    for col in CATEGORICAL_COLS:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"Model trained.")
    print(f"MAE : {mae:.3f}")
    print(f"R^2 : {r2:.3f}")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(ENCODERS_PATH, "wb") as f:
        pickle.dump(encoders, f)

    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved encoders -> {ENCODERS_PATH}")


if __name__ == "__main__":
    main()
