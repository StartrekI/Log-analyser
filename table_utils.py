# table_utils.py
"""
Helpers to show either AgGrid (with allow_unsafe_jscode=True) if available,
or a plain Streamlit dataframe with a detail panel.
"""

import streamlit as st
import pandas as pd

try:
    from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
    AGGRID_AVAILABLE = True
except Exception:
    AGGRID_AVAILABLE = False


def show_table(display_df: pd.DataFrame, enable_aggrid: bool = True, show_traceback_default: bool = False):
    """
    display_df: DataFrame with columns: timestamp_text, timestamp, module, level, exception, exception_message, traceback
    enable_aggrid: if True and st-aggrid installed, use AgGrid with JsCode renderer (allow_unsafe_jscode=True).
    Returns: None (renders to streamlit).
    """
    if AGGRID_AVAILABLE and enable_aggrid:
        grid_df = display_df.fillna("")

        gb = GridOptionsBuilder.from_dataframe(grid_df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
        gb.configure_default_column(resizable=True, sortable=True, filter=True, wrapText=True)

        js_renderer = JsCode(
            """
            function(params) {
              if (!params.value) { return ''; }
              var safe = (params.value + '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
              return `<pre style="white-space: pre-wrap; font-family: monospace; font-size:12px;">${safe}</pre>`;
            }
            """
        )

        if "traceback" in grid_df.columns:
            try:
                gb.configure_column("traceback", cellRenderer=js_renderer)
            except Exception:
                pass

        grid_options = gb.build()
        grid_response = AgGrid(grid_df, gridOptions=grid_options, enable_enterprise_modules=False, fit_columns_on_grid_load=True, allow_unsafe_jscode=True)
        selected = grid_response.get("selected_rows", [])
        if selected:
            sel = selected[0]
            st.markdown("### Selected occurrence details")
            st.write(f"Timestamp: {sel.get('timestamp_text')}")
            st.write(f"Module: {sel.get('module')}")
            st.write(f"Level: {sel.get('level')}")
            st.write(f"Exception: {sel.get('exception')}")
            st.write(f"Message: {sel.get('exception_message')}")
            tb = sel.get("traceback") or ""
            if tb:
                st.code(tb)
    else:
        st.dataframe(display_df.drop(columns=["traceback"]), height=420)
        if len(display_df) > 0:
            idx = st.number_input("Show detail for row index (0..N-1)", min_value=0, max_value=max(0, len(display_df) - 1), value=0, step=1)
            sel_row = display_df.reset_index(drop=True).iloc[idx]
            st.markdown("### Selected occurrence details")
            st.write(f"Timestamp: {sel_row['timestamp_text']}")
            st.write(f"Module: {sel_row['module']}")
            st.write(f"Level: {sel_row['level']}")
            st.write(f"Exception: {sel_row['exception']}")
            st.write(f"Message: {sel_row['exception_message']}")
            if show_traceback_default and sel_row.get("traceback"):
                st.code(sel_row["traceback"])
