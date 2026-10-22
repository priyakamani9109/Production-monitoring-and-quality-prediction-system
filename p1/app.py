"""
app.py

Production Monitoring and Quality Prediction System
-----------------------------------------------------
A Streamlit dashboard that predicts the expected number of defective rolls
from production parameters using a trained Random Forest Regressor, and
provides downtime risk analysis, production insights, recommendations, and
a downloadable Word report.

Run with:
    streamlit run app.py
"""

import os
import pickle
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from report_generator import generate_report

MODEL_PATH = "model/model.pkl"
ENCODERS_PATH = "model/encoders.pkl"

SHIFTS = ["Morning", "Evening", "Night"]
MACHINES = ["PP Spunbond Line", "Spunmelt Machine", "Roll-to-Sheet Cutter"]
BONDING_TYPES = ["Thermal", "Mechanical"]

st.set_page_config(
    page_title="Production Monitoring & Quality Prediction System",
    page_icon="🏭",
    layout="wide",
)


@st.cache_resource
def load_model():
    if not (os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH)):
        return None, None
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(ENCODERS_PATH, "rb") as f:
        encoders = pickle.load(f)
    return model, encoders


def downtime_risk_level(downtime_minutes: int) -> str:
    if downtime_minutes < 45:
        return "Low"
    elif downtime_minutes < 100:
        return "Medium"
    else:
        return "High"


def build_recommendations(shift, machine, bonding, efficiency, defect_pct, downtime_risk):
    recs = []

    if downtime_risk == "High":
        recs.append("Schedule immediate maintenance check to reduce machine downtime.")
    elif downtime_risk == "Medium":
        recs.append("Monitor machine performance closely to prevent further downtime increase.")
    else:
        recs.append("Downtime is under control; continue routine preventive maintenance.")

    if defect_pct > 5:
        recs.append("Defect percentage is high — inspect bonding parameters and raw material quality.")
    elif defect_pct > 2:
        recs.append("Defect percentage is moderate — review machine calibration periodically.")
    else:
        recs.append("Defect percentage is within acceptable limits.")

    if bonding == "Mechanical":
        recs.append("Mechanical bonding shows higher variability — verify pressure settings regularly.")

    if shift == "Night":
        recs.append("Night shift shows higher risk — ensure adequate supervision and lighting on the floor.")

    if machine == "Spunmelt Machine":
        recs.append("Spunmelt Machine requires closer monitoring due to combined spunbond/meltblown process.")

    if efficiency < 90:
        recs.append("Production efficiency is below target — review workflow for bottlenecks.")

    return recs


def main():
    st.title("🏭 Production Monitoring and Quality Prediction System")
    st.caption(
        "Predicts expected defective rolls, analyzes downtime risk, and generates "
        "production recommendations based on production parameters."
    )

    model, encoders = load_model()

    if model is None:
        st.error(
            "Model files not found. Please run `python generate_dataset.py` "
            "followed by `python train_model.py` before launching the dashboard."
        )
        st.stop()

    # ---------------- Sidebar: Production Input Panel ----------------
    st.sidebar.header("📋 Production Input Panel")

    shift = st.sidebar.selectbox("Shift", SHIFTS)
    machine = st.sidebar.selectbox("Machine Type", MACHINES)
    bonding = st.sidebar.selectbox("Bonding Type", BONDING_TYPES)
    rolls_produced = st.sidebar.number_input(
        "Rolls Produced", min_value=1, max_value=5000, value=300, step=10
    )
    downtime_minutes = st.sidebar.number_input(
        "Downtime Minutes", min_value=0, max_value=1000, value=30, step=5
    )

    predict_clicked = st.sidebar.button("🔍 Predict", use_container_width=True)

    if "predicted" not in st.session_state:
        st.session_state.predicted = False

    if predict_clicked:
        st.session_state.predicted = True

    if not st.session_state.predicted:
        st.info("Enter production details in the sidebar and click **Predict** to see results.")
        return

    # ---------------- Encode inputs & predict ----------------
    input_row = pd.DataFrame(
        [
            {
                "Shift": encoders["Shift"].transform([shift])[0],
                "Machine_Type": encoders["Machine_Type"].transform([machine])[0],
                "Bonding_Type": encoders["Bonding_Type"].transform([bonding])[0],
                "Rolls_Produced": rolls_produced,
                "Downtime_Minutes": downtime_minutes,
            }
        ]
    )

    predicted_defects = model.predict(input_row)[0]
    predicted_defects = max(0, round(predicted_defects))
    predicted_defects = min(predicted_defects, rolls_produced)

    good_rolls = rolls_produced - predicted_defects
    defect_pct = (predicted_defects / rolls_produced) * 100
    efficiency = 100 - defect_pct
    risk = downtime_risk_level(downtime_minutes)

    # ---------------- Prediction Results ----------------
    st.subheader("📊 Prediction Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predicted Defective Rolls", f"{predicted_defects}")
    c2.metric("Downtime Risk", risk)
    c3.metric("Production Efficiency", f"{efficiency:.1f}%")
    c4.metric("Defect Percentage", f"{defect_pct:.1f}%")

    # ---------------- Production Insights ----------------
    st.subheader("📈 Production Insights")
    i1, i2, i3 = st.columns(3)
    i1.metric("Good Rolls Produced", f"{good_rolls}")
    i2.metric("Rolls Produced", f"{rolls_produced}")
    i3.metric("Downtime Minutes", f"{downtime_minutes}")

    # ---------------- Production Overview ----------------
    st.subheader("🗂️ Production Overview")
    overview_df = pd.DataFrame(
        {
            "Parameter": [
                "Shift", "Machine Type", "Bonding Type", "Rolls Produced",
                "Downtime Minutes", "Predicted Defective Rolls", "Good Rolls",
                "Downtime Risk", "Production Efficiency (%)", "Defect Percentage (%)",
            ],
            "Value": [
                shift, machine, bonding, rolls_produced,
                downtime_minutes, predicted_defects, good_rolls,
                risk, f"{efficiency:.1f}", f"{defect_pct:.1f}",
            ],
        }
    )
    st.table(overview_df)

    # ---------------- Recommendations ----------------
    st.subheader("💡 Production Recommendations")
    recommendations = build_recommendations(shift, machine, bonding, efficiency, defect_pct, risk)
    for rec in recommendations:
        st.write(f"- {rec}")

    # ---------------- Report Generation ----------------
    st.subheader("📄 Report Generation")

    inputs_for_report = {
        "Shift": shift,
        "Machine Type": machine,
        "Bonding Type": bonding,
        "Rolls Produced": rolls_produced,
        "Downtime Minutes": downtime_minutes,
    }
    results_for_report = {
        "Predicted Defective Rolls": predicted_defects,
        "Good Rolls Produced": good_rolls,
        "Downtime Risk": risk,
        "Production Efficiency": f"{efficiency:.1f}%",
        "Defect Percentage": f"{defect_pct:.1f}%",
    }
    insights_for_report = {
        "Production Efficiency": f"{efficiency:.1f}%",
        "Defect Percentage": f"{defect_pct:.1f}%",
        "Good Rolls Produced": good_rolls,
    }

    report_bytes = generate_report(
        inputs_for_report, results_for_report, insights_for_report, recommendations
    )

    st.download_button(
        label="⬇️ Download Production Report (Word)",
        data=report_bytes,
        file_name=f"Production_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
