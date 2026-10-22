# Production Monitoring and Quality Prediction System

A machine-learning based dashboard that predicts the expected number of
defective rolls in a nonwoven fabric production run, analyzes downtime risk,
and generates a downloadable Word production report.

This matches the project described in the "Summer Training Report" (Future X /
Supreme Nonwoven Industries Pvt. Ltd. internship report).

## Tech Stack
- **Python** — core programming language
- **Pandas** — dataset handling
- **Scikit-learn (Random Forest Regressor)** — prediction model
- **Streamlit** — interactive dashboard
- **Microsoft Excel** — dataset storage
- **python-docx** — automatic Word report generation

## Project Structure
```
project/
├── data/
│   └── production_data.xlsx      # generated dataset
├── model/
│   ├── model.pkl                 # trained Random Forest model
│   └── encoders.pkl              # label encoders for categorical inputs
├── generate_dataset.py           # creates the synthetic production dataset
├── train_model.py                # trains and saves the ML model
├── report_generator.py           # builds the downloadable Word report
├── app.py                        # Streamlit dashboard (main app)
├── requirements.txt
└── README.md
```

## Setup & Run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate the dataset**
   ```bash
   python generate_dataset.py
   ```

3. **Train the model**
   ```bash
   python train_model.py
   ```

4. **Launch the dashboard**
   ```bash
   streamlit run app.py
   ```

The dashboard opens in your browser (usually `http://localhost:8501`).

## How It Works

1. Enter production details in the sidebar — **Shift**, **Machine Type**,
   **Bonding Type**, **Rolls Produced**, and **Downtime Minutes**.
2. Click **Predict**.
3. The system:
   - Predicts the expected **Defective Rolls** using the trained Random
     Forest Regressor.
   - Classifies **Downtime Risk** as Low / Medium / High.
   - Calculates **Production Efficiency**, **Defect Percentage**, and
     **Good Rolls Produced**.
   - Displays a **Production Overview** table.
   - Generates dynamic **Recommendations** based on the inputs and results.
   - Lets you **download a structured Word report** of the full analysis.

## Notes
- The dataset in `generate_dataset.py` is synthetic but built with realistic
  relationships (machine type, bonding type, shift, and downtime all
  influence defect rate) so the model learns meaningful patterns.
- If you have real production data, replace `data/production_data.xlsx`
  with your own file (same column names) and re-run `train_model.py`.
- This project is intended for educational / internship demonstration
  purposes, matching the scope described in the report.
