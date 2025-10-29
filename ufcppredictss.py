import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Fight Predictor", layout="centered")
st.title("🥊 UFC Fight Predictor (Updated Dataset)")

# Load the new dataset
df = pd.read_csv("ufc-master.csv")

# Make sure only fights with both fighters' stats are used
df = df.dropna(subset=["fighter_1", "fighter_2"])

# Compute average stats per fighter
fighters = {}
for _, row in df.iterrows():
    for prefix, name in [("1", row.fighter_1), ("2", row.fighter_2)]:
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

# Select fighters
fighters_list = sorted(fighter_stats.keys())
col1, col2 = st.columns(2)
fighter_A = col1.selectbox("Select Fighter A", fighters_list)
fighter_B = col2.selectbox("Select Fighter B", fighters_list, index=1)

if fighter_A != fighter_B:
    A = fighter_stats[fighter_A]
    B = fighter_stats[fighter_B]

    # Simple scoring system based on differences
    score = 0
    score += (A["age"] < B["age"]) * 1   # younger fighter
    score += (A["height"] > B["height"]) * 1
    score += (A["reach"] > B["reach"]) * 1
    score += (A["SLpM"] > B["SLpM"]) * 1
    score += (A["SApM"] < B["SApM"]) * 1
    score += (A["TdAvg"] > B["TdAvg"]) * 1
    score += (A["SubAvg"] > B["SubAvg"]) * 1

    prob = (score / 7) * 100

    st.subheader(f"🏆 Predicted chance {fighter_A} wins: {prob:.1f}%")

    # Stats comparison table
    st.markdown("### 📊 Fighter Stats Comparison")
    comp_df = pd.DataFrame({
        "Stat": ["Age","Height","Reach","SLpM","SApM","TdAvg","SubAvg"],
        fighter_A: [A["age"],A["height"],A["reach"],A["SLpM"],A["SApM"],A["TdAvg"],A["SubAvg"]],
        fighter_B: [B["age"],B["height"],B["reach"],B["SLpM"],B["SApM"],B["TdAvg"],B["SubAvg"]],
    })
    st.dataframe(comp_df.set_index("Stat"), use_container_width=True)
else:
    st.warning("Please select two different fighters.")
