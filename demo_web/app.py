from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "data" / "spageo_demo_heads.npz"

st.set_page_config(
    page_title="SPAGeo | Groundwater Demo",
    page_icon="🌊",
    layout="wide",
)

st.title("SPAGeo")
st.subheader("Smart Predictive Aquifer & Groundwater Engineering Optimizer")
st.caption("Browser demonstration · Saved MODFLOW output")

st.warning(
    "Demonstration data only. This page displays a previously saved model run; "
    "it does not run a new simulation. The model configuration and results have "
    "not been independently validated. Do not use these values for operational "
    "groundwater decisions."
)

if not DATA_FILE.is_file():
    st.error(f"Demo data file not found: {DATA_FILE}")
    st.stop()

try:
    with np.load(DATA_FILE, allow_pickle=False) as saved:
        times = np.asarray(saved["times_days"], dtype=float)
        heads = np.asarray(saved["heads"], dtype=float)
except Exception as exc:
    st.error(f"Could not read the saved demonstration data: {exc}")
    st.stop()

if heads.ndim != 3 or heads.shape[0] != len(times) or len(times) == 0:
    st.error("The saved data has an unexpected shape.")
    st.stop()

if not np.isfinite(heads).all():
    st.error("The saved data contains non-finite values.")
    st.stop()

st.sidebar.header("Explore saved results")
selected_index = st.sidebar.selectbox(
    "Saved simulation time",
    options=list(range(len(times))),
    index=len(times) - 1,
    format_func=lambda i: f"Day {times[i]:.2f}",
)
st.sidebar.caption(
    "Selecting a time changes the displayed saved snapshot only. "
    "No simulation is run."
)

snapshot = heads[selected_index]
first_snapshot = heads[0]
change = float(np.max(np.abs(snapshot - first_snapshot)))

st.markdown(f"### Saved snapshot at day {times[selected_index]:.2f}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Grid rows", f"{snapshot.shape[0]}")
m2.metric("Grid columns", f"{snapshot.shape[1]}")
m3.metric("Minimum head", f"{snapshot.min():.4f}")
m4.metric("Maximum head", f"{snapshot.max():.4f}")

left, right = st.columns([2, 1])

with left:
    st.markdown("#### Groundwater head field")
    fig, ax = plt.subplots(figsize=(11, 4.5))
    image = ax.imshow(snapshot, origin="lower", aspect="auto", cmap="viridis")
    ax.set_xlabel("Grid column index")
    ax.set_ylabel("Grid row index")
    ax.set_title(f"Saved head field — day {times[selected_index]:.2f}")
    fig.colorbar(image, ax=ax, label="Head value (model units not confirmed)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.markdown("#### Snapshot details")
    st.write(f"**Saved time:** day {times[selected_index]:.2f}")
    st.write(f"**Array dimensions:** {snapshot.shape[0]} × {snapshot.shape[1]}")
    st.write(f"**Mean head:** {snapshot.mean():.6f}")
    st.write(f"**Change from first snapshot:** {change:.10f}")
    st.caption(
        "The grid is shown by row and column index. Geographic coordinates, "
        "map projection, and head units have not been confirmed for this display."
    )

st.markdown("### Saved-run summary")
summary = pd.DataFrame({
    "Day": times,
    "Minimum": heads.min(axis=(1, 2)),
    "Mean": heads.mean(axis=(1, 2)),
    "Maximum": heads.max(axis=(1, 2)),
})
st.line_chart(summary.set_index("Day")[["Minimum", "Mean", "Maximum"]])

st.info(
    "Interpretation note: the saved snapshots differ, but the largest "
    "cell-by-cell change from the first snapshot is approximately 0.0000085. "
    "This demo therefore does not establish a meaningful groundwater response "
    "over time or scientific validity."
)

st.markdown("---")
st.caption(
    "SPAGeo community demonstration · Uses a previously saved output file · "
    "No live GIS processing, AI workflow generation, or cloud simulation is performed here."
)
