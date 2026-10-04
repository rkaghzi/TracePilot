
import io
import os
import json
import pandas as pd
import streamlit as st
import networkx as nx

st.set_page_config(page_title="TracePilot AI", page_icon="⚡", layout="wide")

st.title("⚡ TracePilot AI")
st.caption("Process intelligence → bottleneck detection → AI automation opportunities")

with st.sidebar:
    st.header("Demo")
    st.write("Upload a process-execution CSV. TracePilot discovers the real workflow from event data.")
    st.markdown("**Expected fields:** case_id, activity, start_time, end_time")
    st.markdown("Optional aliases such as `case`, `caseid`, `task`, `event`, `timestamp`, `time` are also detected.")

ALIASES = {
    "case_id": ["case_id","caseid","case","process_id","trace_id","instance_id"],
    "activity": ["activity","task","event","event_name","activity_name","step"],
    "start_time": ["start_time","start","timestamp","time","datetime","date"],
    "end_time": ["end_time","end","completed_at","finish_time"]
}

def normalize_columns(df):
    original = list(df.columns)
    lower = {str(c).strip().lower().replace(" ","_"): c for c in df.columns}
    found = {}
    for target, names in ALIASES.items():
        for n in names:
            if n in lower:
                found[target] = lower[n]
                break
    return found

def analyze(df, cols):
    x = df.rename(columns={
        cols["case_id"]:"case_id",
        cols["activity"]:"activity",
        cols["start_time"]:"start_time",
    }).copy()
    if "end_time" in cols:
        x = x.rename(columns={cols["end_time"]:"end_time"})
    x["start_time"] = pd.to_datetime(x["start_time"], errors="coerce")
    if "end_time" in x:
        x["end_time"] = pd.to_datetime(x["end_time"], errors="coerce")
        x["duration_min"] = (x["end_time"] - x["start_time"]).dt.total_seconds()/60
    else:
        x["duration_min"] = float("nan")
    x = x.dropna(subset=["case_id","activity","start_time"]).sort_values(["case_id","start_time"])
    return x

def process_edges(x):
    edges = {}
    for _, g in x.groupby("case_id"):
        acts = g["activity"].tolist()
        for a,b in zip(acts, acts[1:]):
            edges[(a,b)] = edges.get((a,b),0)+1
    return pd.DataFrame(
        [{"from":a,"to":b,"frequency":n} for (a,b),n in edges.items()]
    ).sort_values("frequency", ascending=False) if edges else pd.DataFrame()

def local_insights(x, edges):
    insights=[]
    if len(x):
        for activity, g in x.groupby("activity"):
            dur = g["duration_min"].dropna()
            if len(dur):
                insights.append({
                    "activity":activity,
                    "cases":len(g),
                    "avg_minutes":round(dur.mean(),2),
                    "p95_minutes":round(dur.quantile(.95),2),
                    "slow_share":round((dur > dur.quantile(.75)).mean()*100,1)
                })
    return pd.DataFrame(insights).sort_values("avg_minutes", ascending=False) if insights else pd.DataFrame()

def ai_recommendations(insights, edges):
    # Works without an API key: deterministic AI-style recommendations.
    # Optional Ollama integration can be enabled with OLLAMA_MODEL.
    recs=[]
    for _, r in insights.head(8).iterrows():
        if r["p95_minutes"] > max(60, r["avg_minutes"]*2):
            recs.append(f"Automate exception handling around **{r['activity']}**: its long-tail duration suggests manual escalations or missing information.")
        if r["slow_share"] > 25:
            recs.append(f"Add an AI copilot to **{r['activity']}** to pre-fill repetitive work and reduce variance.")
    if len(edges):
        top=edges.iloc[0]
        recs.append(f"Prioritize the transition **{top['from']} → {top['to']}** because it occurs {int(top['frequency'])} times in the observed traces.")
    if not recs:
        recs.append("Start with document extraction and case routing: these are usually high-volume, measurable automation candidates.")
    return recs

uploaded = st.file_uploader("Upload process log CSV", type=["csv"])

if uploaded:
    raw = pd.read_csv(uploaded)
    cols = normalize_columns(raw)

    required = ["case_id","activity","start_time"]
    missing = [k for k in required if k not in cols]
    if missing:
        st.error(f"Could not identify: {', '.join(missing)}. Detected columns: {list(raw.columns)}")
        st.stop()

    x = analyze(raw, cols)
    edges = process_edges(x)
    insights = local_insights(x, edges)

    st.success(f"Loaded {len(x):,} events across {x['case_id'].nunique():,} cases.")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Cases", f"{x['case_id'].nunique():,}")
    c2.metric("Events", f"{len(x):,}")
    c3.metric("Activities", f"{x['activity'].nunique():,}")
    if x["duration_min"].notna().any():
        c4.metric("Median activity time", f"{x['duration_min'].median():.1f} min")
    else:
        c4.metric("Median activity time", "N/A")

    tab1,tab2,tab3 = st.tabs(["🔎 Process", "🚨 Bottlenecks", "🤖 AI Opportunities"])

    with tab1:
        st.subheader("Observed process transitions")
        if len(edges):
            st.dataframe(edges, use_container_width=True, hide_index=True)
        st.subheader("Activity performance")
        st.dataframe(insights, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Where should a business intervene first?")
        if len(insights):
            top = insights.head(5)
            st.bar_chart(top.set_index("activity")["avg_minutes"])
            st.write("Long average duration and high variance are prioritized because they often indicate manual work or exception handling.")
        else:
            st.info("End timestamps are needed for duration-based bottleneck analysis.")

    with tab3:
        st.subheader("Recommended automation opportunities")
        for i, rec in enumerate(ai_recommendations(insights, edges),1):
            st.markdown(f"**{i}.** {rec}")

        st.divider()
        st.subheader("Next action")
        st.write("In production, these opportunities become governed AI workflows: the agent executes low-risk steps automatically and escalates policy-sensitive exceptions to a human.")

else:
    st.info("Upload a CSV to start. A sample dataset is included with the MVP.")
    sample = pd.DataFrame([
        ["C1","Order","2026-09-01 09:00:00","2026-09-01 09:01:00"],
        ["C1","Prepare","2026-09-01 09:01:00","2026-09-01 09:04:00"],
        ["C1","Serve","2026-09-01 09:04:00","2026-09-01 09:05:00"],
        ["C2","Order","2026-09-01 09:02:00","2026-09-01 09:03:00"],
        ["C2","Prepare","2026-09-01 09:03:00","2026-09-01 09:10:00"],
        ["C2","Serve","2026-09-01 09:10:00","2026-09-01 09:11:00"],
    ], columns=["case_id","activity","start_time","end_time"])
    st.dataframe(sample, use_container_width=True, hide_index=True)
    st.download_button("Download sample CSV", sample.to_csv(index=False), "sample_process_log.csv", "text/csv")
