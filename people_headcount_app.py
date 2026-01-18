import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

CSV_PATH = Path("/Users/sharzhou/m2-project/data_room/people/employee_roster.csv")

st.set_page_config(page_title="People Headcount Scenarios", layout="wide")

# --- Styling: minimal modern CSS
st.markdown(
    """
    <style>
      .app-title { font-family: "Segoe UI", Roboto, sans-serif; font-size:28px; font-weight:700; margin-bottom:6px; }
      .app-sub { color: #6b7280; margin-top:0; margin-bottom:12px; }
      .kpi-card { padding: 14px; border-radius:10px; color: white; }
      .kpi-label { font-size:13px; color: rgba(255,255,255,0.85); margin-bottom:6px; }
      .kpi-value { font-size:20px; font-weight:700; }
      .small-note { color: #6b7280; font-size:12px; }
      .data-table { border-radius:8px; overflow:hidden; box-shadow: 0 2px 6px rgba(15,23,42,0.06); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-title">Headcount scenario simulator — prioritize by compensation</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">Choose a target headcount and prioritize hires by compensation to see cost impact.</div>', unsafe_allow_html=True)


@st.cache_data
def load_roster(csv_path: Path) -> pd.DataFrame:
    # Read CSV; file contains a "Summary Statistics" section at the bottom, so coerce comp_usd and drop non-employee rows.
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    # Normalize columns
    if "comp_usd" not in df.columns:
        raise RuntimeError("Expected column 'comp_usd' in roster CSV")
    df["comp_usd"] = pd.to_numeric(df["comp_usd"], errors="coerce")
    # Keep rows that have an employee_id and a numeric compensation
    df = df[df["employee_id"].str.startswith("E", na=False)]
    df = df.dropna(subset=["comp_usd"])
    # Convert comp to integer
    df["comp_usd"] = df["comp_usd"].astype(int)
    return df


try:
    roster_df = load_roster(CSV_PATH)
except Exception as exc:
    st.error(f"Could not load roster: {exc}")
    st.stop()

total_employees = int(roster_df.shape[0])

st.sidebar.header("Scenario inputs")
target_headcount = st.sidebar.slider(
    "Target headcount",
    min_value=0,
    max_value=total_employees,
    value=min(10, total_employees),
    step=1,
)

priority_option = st.sidebar.radio(
    "Prioritize by compensation",
    options=["Lowest compensation first (cost-minimizing)", "Highest compensation first"],
)

accent_choice = st.sidebar.selectbox("Accent color", options=["Teal", "Indigo", "Purple"], index=0)
accent_map = {"Teal": "#0d9488", "Indigo": "#3730a3", "Purple": "#7c3aed"}
accent_color = accent_map.get(accent_choice, "#0d9488")

ascending = priority_option.startswith("Lowest")

# Select top N based on compensation ordering
selected = roster_df.sort_values("comp_usd", ascending=ascending).head(target_headcount)

total_cost = int(selected["comp_usd"].sum()) if not selected.empty else 0
average_cost = int(selected["comp_usd"].mean()) if not selected.empty else 0
median_cost = int(selected["comp_usd"].median()) if not selected.empty else 0

def _fmt(x: int) -> str:
    return f"${x:,.0f}"

# KPI cards
k1, k2, k3, k4 = st.columns([1,1,1,1])
card_template = '<div class="kpi-card" style="background:{bg}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'
k1.markdown(card_template.format(bg=accent_color, label="Selected headcount", value=f"{selected.shape[0]}/{total_employees}"), unsafe_allow_html=True)
k2.markdown(card_template.format(bg="#111827", label="Total compensation", value=_fmt(total_cost)), unsafe_allow_html=True)
k3.markdown(card_template.format(bg="#111827", label="Average compensation", value=_fmt(average_cost) if selected.shape[0] else "$0"), unsafe_allow_html=True)
k4.markdown(card_template.format(bg="#111827", label="Median compensation", value=_fmt(median_cost) if selected.shape[0] else "$0"), unsafe_allow_html=True)

st.markdown("### Selected employees")
if selected.empty:
    st.info("No employees selected for the current headcount.")
else:
    display_cols = ["employee_id", "name", "role", "department", "location", "comp_usd"]
    display_df = selected[display_cols].copy().reset_index(drop=True)
    display_df["comp_usd"] = display_df["comp_usd"].map(lambda x: _fmt(int(x)))
    # nicer table
    st.markdown('<div class="data-table">', unsafe_allow_html=True)
    st.table(display_df)
    st.markdown("</div>", unsafe_allow_html=True)
    st.download_button(
        "Download selected as CSV",
        selected[display_cols].to_csv(index=False).encode("utf-8"),
        file_name="selected_employees.csv",
        mime="text/csv",
    )

st.markdown("### Compensation breakdown")
if not selected.empty:
    chart_df = selected.reset_index().loc[:, ["name", "comp_usd"]]
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("comp_usd:Q", title="Compensation (USD)"),
            y=alt.Y("name:N", sort=alt.EncodingSortField(field="comp_usd", op="sum", order="descending"), title=None),
            color=alt.value(accent_color),
            tooltip=["name", alt.Tooltip("comp_usd:Q", format="$,.0f")],
        )
        .properties(height=450)
    )
    st.altair_chart(chart, use_container_width=True)

st.markdown("---")
st.caption(f"Roster source: `{CSV_PATH}` — total employees in roster: {total_employees}")

