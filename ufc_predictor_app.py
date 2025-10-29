import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb

# ==========================
# Load and prepare data
# ==========================
@st.cache_data
def load_and_train_model():
    df = pd.read_csv("ufc_fights_historical.csv", parse_dates=["date"])
    df["label"] = (df["winner"] == "A").astype(int)

    df["age_diff"] = df["A_age"] - df["B_age"]
    df["height_diff"] = df["A_height"] - df["B_height"]
    df["reach_diff"] = df["A_reach"] - df["B_reach"]
    df["SLpM_diff"] = df["A_SLpM"] - df["B_SLpM"]
    df["SApM_diff"] = df["A_SApM"] - df["B_SApM"]
    df["TdAvg_diff"] = df["A_TdAvg"] - df["B_TdAvg"]
    df["SubAvg_diff"] = df["A_SubAvg"] - df["B_SubAvg"]

    features = [
        "age_diff","height_diff","reach_diff",
        "SLpM_diff","SApM_diff","TdAvg_diff","SubAvg_diff"
    ]

    X = df[features]
    y = df["label"]

    dtrain = xgb.DMatrix(X, label=y)
    params = {
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "eta": 0.1,
        "max_depth": 3,
        "seed": 42
    }
    model = xgb.train(params, dtrain, num_boost_round=200)

    # Build average fighter profiles
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
    fighter_stats = {
        name: pd.DataFrame(stats).mean().to_dict()
        for name, stats in fighters.items()
    }

    return model, fighter_stats, features

model, fighter_stats, features = load_and_train_model()

# ==========================
# Streamlit UI
# ==========================
st.set_page_config(page_title="UFC Fight Predictor", layout="centered")

st.title("🥊 UFC Fight Predictor")
st.markdown("Predict the outcome of UFC fights using simple machine learning!")

fighters_list = sorted(fighter_stats.keys())
col1, col2 = st.columns(2)
fighter_A = col1.selectbox("Select Fighter A", fighters_list)
fighter_B = col2.selectbox("Select Fighter B", fighters_list, index=1)

if fighter_A == fighter_B:
    st.warning("Please select two different fighters.")
else:
    A = fighter_stats[fighter_A]
    B = fighter_stats[fighter_B]

    row = {
        "age_diff": A["age"] - B["age"],
        "height_diff": A["height"] - B["height"],
        "reach_diff": A["reach"] - B["reach"],
        "SLpM_diff": A["SLpM"] - B["SLpM"],
        "SApM_diff": A["SApM"] - B["SApM"],
        "TdAvg_diff": A["TdAvg"] - B["TdAvg"],
        "SubAvg_diff": A["SubAvg"] - B["SubAvg"],
    }

    dnew = xgb.DMatrix(pd.DataFrame([row])[features])
    prob = float(model.predict(dnew)[0])

    st.subheader(f"🏆 Predicted chance {fighter_A} wins:")
    st.metric(label="", value=f"{prob*100:.1f}%")

    # Stat comparison table
    st.markdown("### 📊 Fighter Comparison")
    comp_df = pd.DataFrame({
        "Stat": ["Age", "Height", "Reach", "SLpM", "SApM", "TdAvg", "SubAvg"],
        fighter_A: [A["age"], A["height"], A["reach"], A["SLpM"], A["SApM"], A["TdAvg"], A["SubAvg"]],
        fighter_B: [B["age"], B["height"], B["reach"], B["SLpM"], B["SApM"], B["TdAvg"], B["SubAvg"]],
    })
    st.dataframe(comp_df.set_index("Stat"), use_container_width=True)

    st.caption("Model uses averaged historical fight data for each fighter.")
