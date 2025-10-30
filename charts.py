# charts.py
"""
Matplotlib chart helpers used by the Streamlit UI.
Provides functions to plot pivoted time-series: module / level / exception.
"""

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd


def plot_pivot_time_series(agg_df: pd.DataFrame, group_name: str, title: str, max_series: int = 8):
    """
    agg_df: DataFrame with columns ['bucket', group_name, 'count']
    group_name: e.g. 'module', 'level', 'exception'
    """
    if agg_df.empty:
        st.info(f"No data for {title}.")
        return

    pivot = agg_df.pivot(index="bucket", columns=group_name, values="count").fillna(0)
    if pivot.empty:
        st.info(f"No data for {title}.")
        return

    # limit series
    if pivot.shape[1] > max_series:
        total_counts = pivot.sum().sort_values(ascending=False)
        top_cols = total_counts.index[:max_series].tolist()
        pivot_plot = pivot[top_cols]
    else:
        pivot_plot = pivot

    fig, ax = plt.subplots(figsize=(10, 3.0 + 0.4 * min(8, pivot_plot.shape[1])))
    for colname in pivot_plot.columns:
        ax.plot(pivot_plot.index, pivot_plot[colname], marker="o", label=str(colname))
    ax.set_xlabel("Time")
    ax.set_ylabel("Count")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize="small", ncol=1)
    ax.grid(True)
    fig.autofmt_xdate()
    st.pyplot(fig)
