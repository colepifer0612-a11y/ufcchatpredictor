import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="UFC Fight Predictor", layout="centered")
st.title("🥊 UFC Fight Predictor (Full Polished Version)")

# Load dataset
df = pd.read_csv("ufc-master.csv")

# Detect fighter columns automatically
fighter_columns = [col for col in df.columns if "fighter" in col.lower()]
if len(fighter_columns) < 2:
    st.error("Could not find fighter columns in CSV.")
    st.stop()

fighter_col1, fighter_col2 = fighter_columns[:2]

# Drop rows missing fighter names
df = df.dropna(subset=[fighter_col1, fighter_col2])

# Identify numeric stats automatically
stat_cols = df.select_dtypes(include="number").columns.tolist()

# Build stats per fighter
fighters = {}
for _, row in df.iterrows():
    for prefix, name in zip([fighter_col1, fighter_col2], [row[fighter_col1], row[fighter_col2]]):
        if name not in fighters:
            fighters[name] = []
        stats = {col: row.get(col, 0) for col in stat_cols if pd.notnull(row.get(col, None))}
        fighters[name].append(stats)

fighter_stats = {}
for name, stats_list in fighters.items():
    df_stats = pd.DataFrame(stats_list)
    fighter_stats[name] = df_stats.fillna(0).mean().to_dict()  # fill missing values with 0

# Slider to adjust minimum number of fights
MIN_FIGHTS = st.slider("Minimum number of fights to show a fighter:", min_value=1, max_value=10, value=3)

# Filter fighters based on MIN_FIGHTS
fighters_list = sorted([name for name, stats_list in fighters.items() if len(stats_list) >= MIN_FIGHTS])

if not fighters_list:
    st.error(f"No fighters found with at least {MIN_FIGHTS} recorded fights.")
    st.stop()

# Fighter selection dropdowns
col1, col2 = st.columns(2)
fighter_A = col1.selectbox("Select Fighter A", fighters_list)
fighter_B = col2.selectbox("Select Fighter B", fighters_list, index=1)

if fighter_A != fighter_B:
    A = fighter_stats[fighter_A]
    B = fighter_stats[fighter_B]

    # Compute simple win score safely
    score = 0
    for stat in stat_cols:
        a_val = A.get(stat, 0)
        b_val = B.get(stat, 0)
        if a_val > b_val:
            score += 1
        elif a_val < b_val:
            score -= 1
    prob = ((score + len(stat_cols)) / (2 * len(stat_cols))) * 100

    st.subheader(f"🏆 Predicted chance {fighter_A} wins: {prob:.1f}%")

    # Stats comparison table
    comp_df = pd.DataFrame({
        "Stat": stat_cols,
        fighter_A: [A.get(s,0) for s in stat_cols],
        fighter_B: [B.get(s,0) for s in stat_cols]
    })
    st.markdown("### 📊 Fighter Stats Comparison")
    st.dataframe(comp_df.set_index("Stat"), use_container_width=True)

    # Highlight favored fighter in chart
    favored = fighter_A if prob >= 50 else fighter_B
    comp_chart = pd.melt(comp_df, id_vars="Stat", var_name="Fighter", value_name="Value")
    comp_chart["Color"] = comp_chart["Fighter"].apply(lambda x: "green" if x == favored else "red")

    chart = alt.Chart(comp_chart).mark_bar().encode(
        x=alt.X("Stat:N", sort=stat_cols),
        y="Value:Q",
        color=alt.Color("Color:N", scale=None),
        tooltip=["Fighter", "Stat", "Value"]
    ).properties(width=700, height=400)
    st.altair_chart(chart)

else:
    st.warning("Please select two different fighters.")
