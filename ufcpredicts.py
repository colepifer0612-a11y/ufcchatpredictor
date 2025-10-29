import streamlit as st
import pandas as pd

st.set_page_config(page_title="UFC Fight Predictor", layout="centered")
st.title("🥊 UFC Fight Predictor (Simple Version)")

# Load dataset
df = pd.read_csv("ufc_fights_historical.csv")

# Compute average stats for each fighter
fighters = {}
for _, row in df.iterrows():
    for prefix, name in [("A", row.fighter_A), ("B", row.fighter_B)]:
        if name not in fighters:
            fighters[name] = []
        fighters[name].append({
            "age": row[f"{prefix}_age"],
            "height": row[f"{prefix}_height"],
            "reach": row[f"{prefix}_reach"],
            "SLpM": row[f"{prefix}_SLpM"],
            "SApM": row[f"{prefix}_SApM"],
            "TdAvg": row[f"{prefix}_TdAvg"],
            "SubAvg": row[f"{prefix}_SubAvg"],
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

    # Compute simple score based on differences
    score = 0
    score += (A["age"] < B["age"]) * 1   # younger fighter +1
    score += (A["height"] > B["height"]) * 1
    score += (A["reach"] > B["reach"]) * 1
    score += (A["SLpM"] > B["SLpM"]) * 1
    score += (A["SApM"] < B["SApM"]) * 1
    score += (A["TdAvg"] > B["TdAvg"]) * 1
    score += (A["SubAvg"] > B["SubAvg"]) * 1

    prob = (score / 7) * 100

    st.subheader(f"🏆 Predicted chance {fighter_A} wins: {prob:.1f}%")

    # Show stats comparison
    st.markdown("### 📊 Fighter Stats Comparison")
    comp_df = pd.DataFrame({
        "Stat": ["Age","Height","Reach","SLpM","SApM","TdAvg","SubAvg"],
        fighter_A: [A["age"],A["height"],A["reach"],A["SLpM"],A["SApM"],A["TdAvg"],A["SubAvg"]],
        fighter_B: [B["age"],B["height"],B["reach"],B["SLpM"],B["SApM"],B["TdAvg"],B["SubAvg"]],
    })
    st.dataframe(comp_df.set_index("Stat"), use_container_width=True)
else:
    st.warning("Please select two different fighters.")
