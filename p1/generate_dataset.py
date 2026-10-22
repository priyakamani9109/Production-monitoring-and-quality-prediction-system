"""
generate_dataset.py

Creates the production dataset (production_data.xlsx) used to train the
Random Forest Regressor model for the Production Monitoring and Quality
Prediction System.

Columns:
    Shift             -> Morning / Evening / Night
    Machine_Type      -> PP Spunbond Line / Spunmelt Machine / Roll-to-Sheet Cutter
    Bonding_Type      -> Thermal / Mechanical
    Rolls_Produced    -> total rolls produced in that production run
    Downtime_Minutes  -> total machine downtime (minutes)
    Defect_Type       -> Tear / Uneven Bonding / Thickness Variation / None
    Defective_Rolls   -> target variable, number of defective rolls
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N_RECORDS = 500

SHIFTS = ["Morning", "Evening", "Night"]
MACHINES = ["PP Spunbond Line", "Spunmelt Machine", "Roll-to-Sheet Cutter"]
BONDING_TYPES = ["Thermal", "Mechanical"]
DEFECT_TYPES = ["Tear", "Uneven Bonding", "Thickness Variation", "None"]

# Base defect risk multiplier per machine / bonding type, to make the
# dataset internally consistent (so the trained model finds real patterns
# instead of pure noise).
MACHINE_RISK = {
    "PP Spunbond Line": 1.0,
    "Spunmelt Machine": 1.3,
    "Roll-to-Sheet Cutter": 0.8,
}
BONDING_RISK = {
    "Thermal": 0.9,
    "Mechanical": 1.15,
}
SHIFT_RISK = {
    "Morning": 0.9,
    "Evening": 1.0,
    "Night": 1.25,
}

rows = []
for _ in range(N_RECORDS):
    shift = np.random.choice(SHIFTS)
    machine = np.random.choice(MACHINES)
    bonding = np.random.choice(BONDING_TYPES)

    rolls_produced = int(np.random.randint(150, 600))
    downtime_minutes = int(np.random.randint(0, 180))

    risk = MACHINE_RISK[machine] * BONDING_RISK[bonding] * SHIFT_RISK[shift]

    # base defect rate ~ 1.5% - 6% of rolls, scaled by risk and downtime
    base_rate = 0.015 + 0.03 * (downtime_minutes / 180)
    defect_rate = base_rate * risk
    defective_rolls = int(round(rolls_produced * defect_rate + np.random.normal(0, 2)))
    defective_rolls = max(0, min(defective_rolls, rolls_produced))

    if defective_rolls == 0:
        defect_type = "None"
    else:
        defect_type = np.random.choice(
            ["Tear", "Uneven Bonding", "Thickness Variation"]
        )

    rows.append(
        {
            "Shift": shift,
            "Machine_Type": machine,
            "Bonding_Type": bonding,
            "Rolls_Produced": rolls_produced,
            "Downtime_Minutes": downtime_minutes,
            "Defect_Type": defect_type,
            "Defective_Rolls": defective_rolls,
        }
    )

df = pd.DataFrame(rows)
df.to_excel("data/production_data.xlsx", index=False)
print(f"Generated {len(df)} records -> data/production_data.xlsx")
print(df.head())
