import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Fight Predictor", layout="centered")
st.title("🥊 UFC Fight Predictor (Updated Dataset)")

# Load the dataset
df = pd.read_csv("ufc-master.csv")

# Check actual column names
st.write("Columns detected in CSV:", df.columns.tolist())

# Use correct fighter columns from this dataset
fighter_cols = ["RedFighter", "BlueFighter"]  # Replace with the actual columns in your CSV if different

# Drop rows missing fighter names
df = df.dropna(subset=fighter_cols)

# Compute average stats per fighter
fighters = {}
for _, row in df.iterrows():
    for prefix, name in zip(["R", "B"], [row[fighter_cols[0]], row[fighter_cols[1]]]):
        if name not in fighters:
            fighters[name] = []
        fighters[name].append({
            "age": row.get(f"{prefix}_age", 0),
            "height": row.get(f"{prefix}_height", 0),
            "reach": row.get(f"{prefix}_reach", 0),
            "SLpM": row.get(f"{prefix}_sig_strike_landed_per_min", 0),
            "SApM": row.get(f"{prefix}_sig_strike_absorbed_per_min", 0),
            "TdAvg": row.get(f"{prefix}_td_avg", 0),
            "SubAvg": row.get(f"{prefix}_sub_avg", 0),
        })

fighter_stats = {name: pd.DataFrame(stats).mean().to_dict() for name, stats in fighters.items()}

# Fighter selection dropdowns
fighters_list = sorted(fighter_stats.keys())
col1, col2 = st.columns(2)
fighter_A = col1.selectbox("Select Fighter A", fighters_list)
fighter_B = col2.selectbox("Select Fighter B", fighters_list, index=1)

if fighter_A != fighter_B:
    A = fighter_stats[fighter_A]
    B = fighter_stats[fighter_B]

    # Simple scoring
    score = 0
    score += (A["age"] < B["age"]) * 1
    score += (A["height"] > B["height"]) * 1
    score += (A["reach"] > B["reach"]) * 1
    score += (A["SLpM"] > B["SLpM"]) * 1
    score += (A["SApM"] < B["SApM"]) * 1
    score += (A["TdAvg"] > B["TdAvg"]) * 1
    score += (A["SubAvg"] > B["SubAvg"]) * 1

    prob = (score / 7) * 100
    st.subheader(f"🏆 Predicted chance {fighter_A} wins: {prob:.1f}%")

    # Stats comparison table
    comp_df = pd.DataFrame({
        "Stat": ["Age","Height","Reach","SLpM","SApM","TdAvg","SubAvg"],
        fighter_A: [A["age"],A["height"],A["reach"],A["SLpM"],A["SApM"],A["TdAvg"],A["SubAvg"]],
        fighter_B: [B["age"],B["height"],B["reach"],B["SLpM"],B["SApM"],B["TdAvg"],B["SubAvg"]],
    })
    st.dataframe(comp_df.set_index("Stat"), use_container_width=True)
else:
    st.warning("Please select two different fighters.")
