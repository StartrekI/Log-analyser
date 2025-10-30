# # app.py
# """
# Streamlit app — Log Error Explorer with full category->sub-error mapping (expanded).
# - Shows category buttons only when total count > 0
# - Clicking a category expands a sub-error selector (only sub-errors present appear)
# - Selecting sub-errors filters the logs
# - Uses matplotlib for charts; st-aggrid optional (allow_unsafe_jscode=True)
# """

# import re
# import math
# import textwrap
# from datetime import datetime
# from collections import Counter, defaultdict

# import pandas as pd
# import streamlit as st
# from dateutil import parser as dateparser

# # Matplotlib for charts
# import matplotlib.pyplot as plt

# # Optional st-aggrid
# USE_AGGRID = False
# try:
#     from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
#     USE_AGGRID = True
# except Exception:
#     USE_AGGRID = False

# # ---------------------------
# # Expanded full mapping: categories with comprehensive sub-error lists
# # (includes builtins + common library/framework exceptions)
# # ---------------------------
# CATEGORY_MAPPING = {
#     "Type_1_Syntax": {
#         "category": "Syntax and Parsing Errors",
#         "description": "Errors that occur during parsing of Python code before execution.",
#         "errors": [
#             "SyntaxError", "IndentationError", "TabError", "SyntaxWarning"
#         ]
#     },

#     "Type_2_Runtime": {
#         "category": "Runtime and Logical Errors",
#         "description": "Errors that occur during runtime of valid Python code.",
#         "errors": [
#             # common builtins
#             "Exception", "BaseException", "ArithmeticError", "AssertionError", "AttributeError", "BufferError",
#             "EOFError", "FloatingPointError", "GeneratorExit", "ImportError", "ModuleNotFoundError", "IndexError",
#             "KeyError", "KeyboardInterrupt", "MemoryError", "NameError", "NotImplementedError", "OSError",
#             "OverflowError", "RecursionError", "ReferenceError", "RuntimeError", "StopIteration", "StopAsyncIteration",
#             "SyntaxError", "SystemError", "SystemExit", "TypeError", "ValueError", "ZeroDivisionError",
#             # more specific / related
#             "LookupError", "UnboundLocalError", "BufferError", "TimeoutError", "BlockingIOError", "BrokenPipeError",
#             "ChildProcessError", "ConnectionError", "PermissionError", "ProcessLookupError", "FileNotFoundError",
#             "FileExistsError", "IsADirectoryError", "NotADirectoryError", "InterruptedError",
#             # library-ish / framework-ish names (runtime)
#             "AttributeError", "AssertionError", "RuntimeWarning", "ReferenceError", "StopIteration", "StopAsyncIteration"
#         ]
#     },

#     "Type_3_Import": {
#         "category": "Import and Module Errors",
#         "description": "Errors related to imports and package availability.",
#         "errors": [
#             "ImportError", "ModuleNotFoundError", "PackageNotFoundError", "ZipImportError"
#         ]
#     },

#     "Type_4_IO_OS": {
#         "category": "I/O and Operating System Errors",
#         "description": "File/OS and I/O errors.",
#         "errors": [
#             "OSError", "IOError", "FileNotFoundError", "PermissionError", "FileExistsError", "IsADirectoryError",
#             "NotADirectoryError", "BlockingIOError", "ChildProcessError", "BrokenPipeError", "InterruptedError",
#             "ProcessLookupError", "TimeoutError", "UnsupportedOperation", "EOFError"
#         ]
#     },

#     "Type_5_Network": {
#         "category": "Network and AsyncIO Errors",
#         "description": "Networking, sockets, and asyncio errors.",
#         "errors": [
#             # socket/ssl/asyncio common exceptions
#             "ConnectionError", "ConnectionAbortedError", "ConnectionRefusedError", "ConnectionResetError",
#             "socket.gaierror", "socket.herror", "socket.timeout", "ssl.SSLError",
#             "asyncio.TimeoutError", "asyncio.CancelledError", "asyncio.InvalidStateError",
#             "asyncio.IncompleteReadError", "asyncio.LimitOverrunError",
#             # requests/http client names
#             "requests.exceptions.RequestException", "requests.exceptions.Timeout", "requests.exceptions.ConnectionError",
#             "requests.exceptions.SSLError", "requests.exceptions.TooManyRedirects", "http.client.HTTPException"
#         ]
#     },

#     "Type_6_Concurrency": {
#         "category": "Threading and Multiprocessing Errors",
#         "description": "Errors from threading, multiprocessing and concurrency libs.",
#         "errors": [
#             "threading.ThreadError", "concurrent.futures.TimeoutError", "BrokenProcessPool",
#             "multiprocessing.ProcessError", "multiprocessing.AuthenticationError", "multiprocessing.BufferTooShort",
#             "RuntimeError", "DeadlockError"
#         ]
#     },

#     "Type_7_System": {
#         "category": "System Exit and Signal Errors",
#         "description": "Process exit and signals.",
#         "errors": [
#             "SystemExit", "KeyboardInterrupt", "GeneratorExit"
#         ]
#     },

#     "Type_8_Arithmetic": {
#         "category": "Arithmetic and Numeric Errors",
#         "description": "Numeric / math related errors.",
#         "errors": [
#             "ArithmeticError", "FloatingPointError", "OverflowError", "ZeroDivisionError",
#             "numpy.linalg.LinAlgError", "numpy.AxisError", "decimal.InvalidOperation"
#         ]
#     },

#     "Type_9_Database": {
#         "category": "Database and ORM Errors",
#         "description": "Database drivers and ORM errors.",
#         "errors": [
#             # generic DB
#             "DatabaseError", "InterfaceError", "OperationalError", "IntegrityError", "DataError",
#             "ProgrammingError", "InternalError", "NotSupportedError",
#             # common DB libs
#             "psycopg2.Error", "psycopg2.OperationalError", "psycopg2.IntegrityError",
#             "sqlite3.Error", "sqlite3.OperationalError", "pymongo.errors.PyMongoError",
#             # ORMs / frameworks
#             "django.db.IntegrityError", "django.core.exceptions.ObjectDoesNotExist",
#             "sqlalchemy.exc.IntegrityError", "sqlalchemy.exc.OperationalError"
#         ]
#     },

#     "Type_10_Serialization": {
#         "category": "Serialization and Data Parsing Errors",
#         "description": "JSON/YAML/XML parsing and serialization errors.",
#         "errors": [
#             "json.JSONDecodeError", "pickle.PickleError", "pickle.UnpicklingError", "pickle.PicklingError",
#             "yaml.YAMLError", "xml.etree.ElementTree.ParseError", "csv.Error", "configparser.Error",
#             "msgpack.ExtraData"
#         ]
#     },

#     "Type_11_Warnings": {
#         "category": "Warnings (Non-fatal Issues)",
#         "description": "Warning classes (non-fatal).",
#         "errors": [
#             "Warning", "UserWarning", "DeprecationWarning", "PendingDeprecationWarning", "SyntaxWarning",
#             "RuntimeWarning", "FutureWarning", "ImportWarning", "UnicodeWarning", "BytesWarning", "ResourceWarning"
#         ]
#     },

#     "Type_12_Unicode": {
#         "category": "Unicode and Encoding Errors",
#         "description": "Encoding/decoding and unicode problems.",
#         "errors": [
#             "UnicodeError", "UnicodeEncodeError", "UnicodeDecodeError", "UnicodeTranslateError"
#         ]
#     },

#     "Type_13_Security": {
#         "category": "Security and Cryptography Errors",
#         "description": "SSL/TLS, cryptography, JWT, and auth errors.",
#         "errors": [
#             "ssl.SSLError", "cryptography.exceptions.InvalidSignature", "cryptography.exceptions.InvalidKey",
#             "jwt.exceptions.ExpiredSignatureError", "jwt.exceptions.InvalidTokenError", "PermissionError",
#             "paramiko.ssh_exception.SSHException"
#         ]
#     },

#     "Type_14_HTTP_API": {
#         "category": "HTTP and API Client Errors",
#         "description": "HTTP client & framework errors (requests, starlette, fastapi, werkzeug).",
#         "errors": [
#             "requests.exceptions.Timeout", "requests.exceptions.ConnectionError", "requests.exceptions.SSLError",
#             "requests.exceptions.TooManyRedirects", "http.client.HTTPException",
#             "starlette.exceptions.HTTPException", "fastapi.exceptions.RequestValidationError",
#             "werkzeug.exceptions.BadRequest", "werkzeug.exceptions.NotFound", "werkzeug.exceptions.InternalServerError",
#             "aiohttp.ClientError", "aiohttp.ClientConnectorError"
#         ]
#     },

#     "Type_15_Custom": {
#         "category": "Custom and Framework-Specific Errors",
#         "description": "Application-specific or third-party custom error classes.",
#         "errors": [
#             "MyAppError", "CustomError", "ValidationError", "AuthenticationError", "AuthorizationError",
#             "RateLimitError", "ServiceUnavailableError", "ThirdPartyAPIError",
#             # common framework-specific
#             "django.core.exceptions.ValidationError", "flask_restful.errors.BadRequest"
#         ]
#     },

#     # Extra bucket to catch many builtins & library names not covered above:
#     "Type_99_Others": {
#         "category": "Other/Additional Exceptions",
#         "description": "Misc builtins and library exceptions included for completeness.",
#         "errors": [
#             # builtins & misc
#             "BaseException", "Exception", "EnvironmentError", "WindowsError",
#             "ImportWarning", "ResourceWarning", "StopIteration", "StopAsyncIteration",
#             "MemoryError", "BufferError", "LookupError", "IndexError", "KeyError", "OSError",
#             # numeric / modules
#             "ModuleNotFoundError", "ImportError", "AttributeError", "NameError", "ReferenceError",
#             "RecursionError", "NotImplementedError", "SystemError", "SystemExit",
#             # common library placeholders
#             "pandas.errors.EmptyDataError", "pandas.errors.ParserError", "numpy.AxisError",
#             "sklearn.exceptions.NotFittedError", "tensorflow.errors.OpError",
#             "concurrent.futures.TimeoutError", "asyncio.CancelledError"
#         ]
#     }
# }

# # Flatten mapping: map sub-error -> top category key (if a sub-error appears in multiple categories, first wins)
# SUB_TO_CAT = {}
# for cat_key, cat_obj in CATEGORY_MAPPING.items():
#     for sub in cat_obj['errors']:
#         if sub not in SUB_TO_CAT:
#             SUB_TO_CAT[sub] = cat_key

# # ---------------------------
# # Log parsing regexes & helpers (same robust heuristics)
# # ---------------------------
# LOG_LINE_RE = re.compile(
#     r'^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s*-\s*(?P<module>[^-]+?)\s*-\s*(?P<level>[A-Z]+)\s*-\s*(?P<message>.*)$'
# )
# EXC_LINE_RE = re.compile(
#     # allow names with dots, colons, angle brackets (for templated exceptions), etc.
#     r'^\s*(?P<exc>[A-Za-z_][\w\.\:\-<>]*?(?:Error|Exception|Warning|Exit|Interrupt)?)\s*[:]\s*(?P<msg>.*)$'
# )
# SINGLELINE_EXC_RE = re.compile(
#     r'(?P<exc>[A-Za-z_][\w\.\:\-<>]*?(?:Error|Exception|Warning|Exit|Interrupt)?)\s*[:\-]\s*(?P<msg>.+)$'
# )

# def parse_timestamp(ts_str):
#     try:
#         return dateparser.parse(ts_str.replace(',', '.'))
#     except Exception:
#         return None

# def extract_errors_from_log_text(log_text: str):
#     lines = log_text.splitlines()
#     entries = []
#     i = 0
#     n = len(lines)
#     while i < n:
#         line = lines[i].rstrip('\n')
#         m = LOG_LINE_RE.match(line)
#         if m:
#             ts_str = m.group('ts')
#             ts = parse_timestamp(ts_str)
#             module = m.group('module').strip()
#             level = m.group('level').strip()
#             message = m.group('message').strip()

#             exc_name = None
#             exc_msg = None
#             single_m = SINGLELINE_EXC_RE.search(message)
#             if single_m:
#                 exc_name = single_m.group('exc')
#                 exc_msg = single_m.group('msg').strip()

#             raw_tb = ""
#             if (i + 1) < n and lines[i+1].lstrip().startswith('Traceback (most recent call last):'):
#                 tb_lines = []
#                 j = i + 1
#                 while j < n:
#                     tb_lines.append(lines[j])
#                     ex_m = EXC_LINE_RE.match(lines[j].strip())
#                     if ex_m:
#                         exc_name = ex_m.group('exc')
#                         exc_msg = ex_m.group('msg').strip()
#                         j += 1
#                         break
#                     j += 1
#                 raw_tb = "\n".join(tb_lines)
#                 i = j - 1

#             if not exc_name:
#                 ex_m2 = EXC_LINE_RE.search(message)
#                 if ex_m2:
#                     exc_name = ex_m2.group('exc')
#                     exc_msg = ex_m2.group('msg').strip()

#             # Normalize some common fully-qualified names to short names where appropriate
#             # e.g., "requests.exceptions.Timeout" -> "requests.exceptions.Timeout" (keep), but also map "TimeoutError" -> TimeoutError
#             cat_key = SUB_TO_CAT.get(exc_name)
#             entries.append({
#                 "timestamp": ts,
#                 "timestamp_raw": ts_str if ts else None,
#                 "module": module,
#                 "level": level,
#                 "message": message,
#                 "exception": exc_name,
#                 "exc_message": exc_msg or "",
#                 "category_key": cat_key,
#                 "raw_traceback": raw_tb
#             })
#         else:
#             # handle traceback-only sequence
#             if line.lstrip().startswith("Traceback (most recent call last):"):
#                 tb_lines = [line]
#                 j = i + 1
#                 exc_name = None
#                 exc_msg = None
#                 while j < n:
#                     tb_lines.append(lines[j])
#                     ex_m = EXC_LINE_RE.match(lines[j].strip())
#                     if ex_m:
#                         exc_name = ex_m.group('exc')
#                         exc_msg = ex_m.group('msg').strip()
#                         break
#                     j += 1
#                 cat_key = SUB_TO_CAT.get(exc_name)
#                 entries.append({
#                     "timestamp": None,
#                     "timestamp_raw": None,
#                     "module": None,
#                     "level": "ERROR",
#                     "message": "(traceback-only entry)",
#                     "exception": exc_name,
#                     "exc_message": exc_msg or "",
#                     "category_key": cat_key,
#                     "raw_traceback": "\n".join(tb_lines)
#                 })
#                 i = j
#         i += 1

#     df = pd.DataFrame(entries)
#     if df.empty:
#         return df
#     df["category"] = df["category_key"].map(lambda k: CATEGORY_MAPPING[k]['category'] if k in CATEGORY_MAPPING else ("Unknown" if pd.notnull(k) else None))
#     df["date"] = df["timestamp"].dt.date
#     df["time"] = df["timestamp"].dt.time
#     return df

# # ---------------------------
# # UI
# # ---------------------------
# st.set_page_config(page_title="Log Error Explorer (full exceptions mapping)", layout="wide")
# st.title("Log Error Explorer — full category/subcategory mapping")

# # Sidebar: file upload & options
# with st.sidebar:
#     st.header("Upload & Options")
#     uploaded = st.file_uploader("Upload log file (.log/.txt)", type=['log', 'txt', 'text'])
#     st.markdown("---")
#     st.write("Display options")
#     show_traceback_default = st.checkbox("Show tracebacks in details by default", value=False)
#     enable_aggrid = st.checkbox("Enable AgGrid table (optional)", value=USE_AGGRID)
#     st.markdown("---")
#     st.caption("Only categories and sub-errors with count>0 are shown. Click a category to expand sub-errors.")

# if not uploaded:
#     st.info("Upload a log file from the sidebar to start.")
#     st.stop()

# raw_text = uploaded.getvalue().decode('utf-8', errors='replace')
# with st.spinner("Parsing log file..."):
#     df = extract_errors_from_log_text(raw_text)

# if df.empty:
#     st.warning("No exception-like entries detected in the uploaded file.")
#     st.code(raw_text[:800] + ("\n..." if len(raw_text) > 800 else ""))
#     st.stop()

# # compute counts for all sub-errors in mapping (present or zero)
# all_suberrors = sorted({sub for cat in CATEGORY_MAPPING.values() for sub in cat['errors']})
# sub_counts_raw = df['exception'].value_counts().to_dict()  # only present ones
# sub_counts_full = {sub: int(sub_counts_raw.get(sub, 0)) for sub in all_suberrors}

# # totals per category
# cat_totals = {cat_key: sum(sub_counts_full.get(sub, 0) for sub in cat_obj['errors']) for cat_key, cat_obj in CATEGORY_MAPPING.items()}

# # UI: show only categories with total > 0
# visible_cat_keys = [k for k,v in cat_totals.items() if v > 0]
# cols = st.columns(min(6, max(1, len(visible_cat_keys))))

# # session-state selections
# if 'sel_cat_key' not in st.session_state:
#     st.session_state['sel_cat_key'] = None
# if 'sel_subs' not in st.session_state:
#     st.session_state['sel_subs'] = []

# st.subheader("Categories")
# for idx, cat_key in enumerate(visible_cat_keys):
#     col = cols[idx % len(cols)]
#     label = f"{CATEGORY_MAPPING[cat_key]['category']}\n\n{cat_totals[cat_key]}"
#     if col.button(label, key=f"catbtn_{cat_key}"):
#         if st.session_state['sel_cat_key'] == cat_key:
#             st.session_state['sel_cat_key'] = None
#             st.session_state['sel_subs'] = []
#         else:
#             st.session_state['sel_cat_key'] = cat_key
#             st.session_state['sel_subs'] = []

# # Active category: show description + only sub-errors with count > 0
# if st.session_state['sel_cat_key']:
#     active_key = st.session_state['sel_cat_key']
#     st.markdown(f"**Active category:** {CATEGORY_MAPPING[active_key]['category']} — {cat_totals[active_key]} occurrences")
#     st.caption(CATEGORY_MAPPING[active_key]['description'])
#     available_subs = [s for s in CATEGORY_MAPPING[active_key]['errors'] if sub_counts_full.get(s,0) > 0]
#     if available_subs:
#         labeled = [f"{s} ({sub_counts_full[s]})" for s in available_subs]
#         prev = [f"{s} ({sub_counts_full[s]})" for s in st.session_state['sel_subs'] if s in available_subs]
#         chosen_labeled = st.multiselect("Select sub-error(s) to filter (only shown if count>0)", labeled, default=prev)
#         chosen_subs = [item.split(" (")[0] for item in chosen_labeled]
#         st.session_state['sel_subs'] = chosen_subs
#         st.markdown(f"Selected sub-errors: {len(chosen_subs)}")
#     else:
#         st.info("No sub-errors with count > 0 in this category.")
# else:
#     st.markdown("**No category selected** — click a category button to inspect sub-errors.")

# st.markdown("---")
# search_col, _ = st.columns([6,1])
# with search_col:
#     search_input = st.text_input("Search exceptions, messages or modules (case-insensitive)")

# # Build filtered DataFrame
# filtered = df.copy()
# if st.session_state['sel_cat_key']:
#     if st.session_state['sel_subs']:
#         filtered = filtered[filtered['exception'].isin(st.session_state['sel_subs'])]
#     else:
#         subs_in_cat = CATEGORY_MAPPING[st.session_state['sel_cat_key']]['errors']
#         filtered = filtered[filtered['exception'].isin(subs_in_cat)]

# if search_input:
#     q = search_input.strip().lower()
#     filtered = filtered[
#         filtered['exception'].fillna('').str.lower().str.contains(q) |
#         filtered['exc_message'].fillna('').str.lower().str.contains(q) |
#         filtered['message'].fillna('').str.lower().str.contains(q) |
#         filtered['module'].fillna('').str.lower().str.contains(q)
#     ]

# # Summary metrics
# c1, c2, c3 = st.columns([2,2,2])
# c1.metric("Total lines", len(raw_text.splitlines()))
# c2.metric("Detected occurrences", len(df))
# c3.metric("Filtered occurrences", len(filtered))

# # three timelines (module, level, exception)
# st.subheader("Timelines (module / level / exception)")
# timeline_df = filtered.dropna(subset=['timestamp']).copy()

# def plot_pivot(ax_title, agg_df, group_col, max_series=8):
#     if agg_df.empty:
#         st.info(f"No timestamped data for {ax_title}")
#         return
#     pivot = agg_df.pivot(index='bucket', columns=group_col, values='count').fillna(0)
#     if pivot.empty:
#         st.info(f"No timestamped data for {ax_title}")
#         return
#     if pivot.shape[1] > max_series:
#         total_counts = pivot.sum().sort_values(ascending=False)
#         top_cols = total_counts.index[:max_series].tolist()
#         pivot_plot = pivot[top_cols]
#     else:
#         pivot_plot = pivot
#     fig, ax = plt.subplots(figsize=(10, 3.0 + 0.4 * min(8, pivot_plot.shape[1])))
#     for colname in pivot_plot.columns:
#         ax.plot(pivot_plot.index, pivot_plot[colname], marker='o', label=str(colname))
#     ax.set_xlabel("Time")
#     ax.set_ylabel("Count")
#     ax.set_title(ax_title)
#     ax.legend(loc='upper right', fontsize='small', ncol=1)
#     ax.grid(True)
#     fig.autofmt_xdate()
#     st.pyplot(fig)

# if timeline_df.empty:
#     st.info("No timestamped entries available to build timelines for current filter.")
# else:
#     min_ts = timeline_df['timestamp'].min()
#     max_ts = timeline_df['timestamp'].max()
#     span_seconds = (max_ts - min_ts).total_seconds() if max_ts and min_ts else 0
#     if span_seconds <= 3600*6:
#         timeline_df['bucket'] = timeline_df['timestamp'].dt.floor('T')  # minute
#     elif span_seconds <= 3600*24*10:
#         timeline_df['bucket'] = timeline_df['timestamp'].dt.floor('H')  # hour
#     else:
#         timeline_df['bucket'] = timeline_df['timestamp'].dt.floor('D')  # day

#     agg_module = timeline_df.groupby(['bucket', 'module']).size().reset_index(name='count')
#     agg_level = timeline_df.groupby(['bucket', 'level']).size().reset_index(name='count')
#     agg_exception = timeline_df.groupby(['bucket', 'exception']).size().reset_index(name='count')

#     plot_pivot("By module", agg_module, "module", max_series=6)
#     plot_pivot("By level", agg_level, "level", max_series=6)
#     plot_pivot("By exception type", agg_exception, "exception", max_series=12)

# st.markdown("---")

# # Table of occurrences
# display_df = filtered[['timestamp_raw', 'timestamp', 'module', 'level', 'exception', 'exc_message', 'raw_traceback']].copy()
# display_df = display_df.rename(columns={'timestamp_raw':'timestamp_text','exc_message':'exception_message','raw_traceback':'traceback'})

# st.subheader("Occurrences")
# if USE_AGGRID and enable_aggrid:
#     grid_df = display_df.fillna("")
#     gb = GridOptionsBuilder.from_dataframe(grid_df)
#     gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
#     gb.configure_default_column(resizable=True, sortable=True, filter=True, wrapText=True)

#     js_renderer = JsCode(
#         """
#         function(params) {
#           if (!params.value) { return ''; }
#           var safe = (params.value + '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
#           return `<pre style="white-space: pre-wrap; font-family: monospace; font-size:12px;">${safe}</pre>`;
#         }
#         """
#     )
#     if 'traceback' in grid_df.columns:
#         try:
#             gb.configure_column("traceback", cellRenderer=js_renderer)
#         except Exception:
#             pass

#     grid_options = gb.build()
#     grid_response = AgGrid(grid_df, gridOptions=grid_options, enable_enterprise_modules=False, fit_columns_on_grid_load=True, allow_unsafe_jscode=True)
#     selected = grid_response.get('selected_rows', [])
#     if selected:
#         sel = selected[0]
#         st.markdown("### Selected occurrence details")
#         st.write(f"Timestamp: {sel.get('timestamp_text')}")
#         st.write(f"Module: {sel.get('module')}")
#         st.write(f"Level: {sel.get('level')}")
#         st.write(f"Exception: {sel.get('exception')}")
#         st.write(f"Message: {sel.get('exception_message')}")
#         tb = sel.get('traceback') or ""
#         if tb:
#             st.code(tb)
# else:
#     st.dataframe(display_df.drop(columns=['traceback']), height=420)
#     if len(display_df) > 0:
#         idx = st.number_input("Show detail for row index (0..N-1)", min_value=0, max_value=max(0, len(display_df)-1), value=0, step=1)
#         sel_row = display_df.reset_index(drop=True).iloc[idx]
#         st.markdown("### Selected occurrence details")
#         st.write(f"Timestamp: {sel_row['timestamp_text']}")
#         st.write(f"Module: {sel_row['module']}")
#         st.write(f"Level: {sel_row['level']}")
#         st.write(f"Exception: {sel_row['exception']}")
#         st.write(f"Message: {sel_row['exception_message']}")
#         if show_traceback_default and sel_row['traceback']:
#             st.code(sel_row['traceback'])

# # Downloads
# download_df = filtered.copy()
# download_df['timestamp'] = download_df['timestamp'].apply(lambda x: x.isoformat() if pd.notnull(x) else "")
# export_df = download_df[['timestamp','module','level','exception','exc_message','category','raw_traceback']].rename(columns={'exc_message':'exception_message','raw_traceback':'traceback'})
# st.download_button("Download filtered results (CSV)", data=export_df.to_csv(index=False).encode('utf-8'), file_name="parsed_errors_filtered.csv", mime="text/csv")
# st.download_button("Download filtered results (JSON)", data=export_df.to_json(orient='records', date_format='iso').encode('utf-8'), file_name="parsed_errors_filtered.json", mime="application/json")

# st.markdown("---")
# st.caption("Expanded mapping included. Categories & sub-errors shown only when count>0. Ask to refine categories or rename any item.")

# app.py
"""
Main Streamlit app that wires everything together.
"""

import streamlit as st
import pandas as pd
from errors_mapping import CATEGORY_MAPPING, get_all_suberrors
from parser import extract_errors_from_log_text
from charts import plot_pivot_time_series
from table_utils import show_table

st.set_page_config(page_title="Log Error Explorer (modular)", layout="wide")
st.title("Log Error Explorer — modular project")

# Sidebar
with st.sidebar:
    st.header("Upload & Options")
    uploaded = st.file_uploader("Upload log file (.log/.txt)", type=["log", "txt", "text"])
    st.markdown("---")
    show_traceback_default = st.checkbox("Show tracebacks in details by default", value=False)
    enable_aggrid = st.checkbox("Enable AgGrid table (optional)", value=False)
    st.markdown("---")
    st.caption("Categories with count>0 are shown. Click to expand sub-errors (only sub-errors with count>0 appear).")

if not uploaded:
    st.info("Upload a log file from the sidebar to start.")
    st.stop()

raw_text = uploaded.getvalue().decode("utf-8", errors="replace")
with st.spinner("Parsing..."):
    df = extract_errors_from_log_text(raw_text)

if df.empty:
    st.warning("No exception-like entries detected in the uploaded file.")
    st.code(raw_text[:800] + ("\n..." if len(raw_text) > 800 else ""))
    st.stop()

# prepare counts
all_subs = get_all_suberrors()
sub_counts_raw = df["exception"].value_counts().to_dict()
sub_counts_full = {s: int(sub_counts_raw.get(s, 0)) for s in all_subs}
cat_totals = {k: sum(sub_counts_full.get(sub, 0) for sub in v["errors"]) for k, v in CATEGORY_MAPPING.items()}

# UI: category buttons (only those with >0)
visible_cat_keys = [k for k, v in cat_totals.items() if v > 0]
cols = st.columns(min(6, max(1, len(visible_cat_keys))))

if "sel_cat_key" not in st.session_state:
    st.session_state["sel_cat_key"] = None
if "sel_subs" not in st.session_state:
    st.session_state["sel_subs"] = []

st.subheader("Categories (count > 0)")
for idx, cat_key in enumerate(visible_cat_keys):
    col = cols[idx % len(cols)]
    label = f"{CATEGORY_MAPPING[cat_key]['category']}\n\n{cat_totals[cat_key]}"
    if col.button(label, key=f"catbtn_{cat_key}"):
        if st.session_state["sel_cat_key"] == cat_key:
            st.session_state["sel_cat_key"] = None
            st.session_state["sel_subs"] = []
        else:
            st.session_state["sel_cat_key"] = cat_key
            st.session_state["sel_subs"] = []

# show sub-errors for selected category
if st.session_state["sel_cat_key"]:
    active = st.session_state["sel_cat_key"]
    st.markdown(f"**Active category:** {CATEGORY_MAPPING[active]['category']} — {cat_totals[active]} occurrences")
    st.caption(CATEGORY_MAPPING[active]["description"])
    available_subs = [s for s in CATEGORY_MAPPING[active]["errors"] if sub_counts_full.get(s, 0) > 0]
    if available_subs:
        labeled = [f"{s} ({sub_counts_full[s]})" for s in available_subs]
        prev = [f"{s} ({sub_counts_full[s]})" for s in st.session_state["sel_subs"] if s in available_subs]
        chosen_labeled = st.multiselect("Select sub-error(s) to filter", labeled, default=prev)
        chosen_subs = [item.split(" (")[0] for item in chosen_labeled]
        st.session_state["sel_subs"] = chosen_subs
        st.markdown(f"Selected sub-errors: {len(chosen_subs)}")
    else:
        st.info("No sub-errors with count > 0 in this category.")

st.markdown("---")
search_input = st.text_input("Search exceptions, messages or modules (case-insensitive)")

# Filtering
filtered = df.copy()
if st.session_state["sel_cat_key"]:
    if st.session_state["sel_subs"]:
        filtered = filtered[filtered["exception"].isin(st.session_state["sel_subs"])]
    else:
        subs_in_cat = CATEGORY_MAPPING[st.session_state["sel_cat_key"]]["errors"]
        filtered = filtered[filtered["exception"].isin(subs_in_cat)]

if search_input:
    q = search_input.strip().lower()
    filtered = filtered[
        filtered["exception"].fillna("").str.lower().str.contains(q) |
        filtered["exc_message"].fillna("").str.lower().str.contains(q) |
        filtered["message"].fillna("").str.lower().str.contains(q) |
        filtered["module"].fillna("").str.lower().str.contains(q)
    ]

# Stats
c1, c2, c3 = st.columns([2,2,2])
c1.metric("Total lines", len(raw_text.splitlines()))
c2.metric("Detected occurrences", len(df))
c3.metric("Filtered occurrences", len(filtered))

# timelines
st.subheader("Timelines (module / level / exception)")
timeline_df = filtered.dropna(subset=["timestamp"]).copy()
if not timeline_df.empty:
    min_ts = timeline_df["timestamp"].min()
    max_ts = timeline_df["timestamp"].max()
    span_seconds = (max_ts - min_ts).total_seconds() if max_ts and min_ts else 0
    if span_seconds <= 3600 * 6:
        timeline_df["bucket"] = timeline_df["timestamp"].dt.floor("T")
    elif span_seconds <= 3600 * 24 * 10:
        timeline_df["bucket"] = timeline_df["timestamp"].dt.floor("H")
    else:
        timeline_df["bucket"] = timeline_df["timestamp"].dt.floor("D")

    agg_module = timeline_df.groupby(["bucket", "module"]).size().reset_index(name="count")
    agg_level = timeline_df.groupby(["bucket", "level"]).size().reset_index(name="count")
    agg_exception = timeline_df.groupby(["bucket", "exception"]).size().reset_index(name="count")

    plot_pivot_time_series(agg_module, "module", "Exceptions by Module (timeline)", max_series=6)
    plot_pivot_time_series(agg_level, "level", "Exceptions by Level (timeline)", max_series=6)
    plot_pivot_time_series(agg_exception, "exception", "Exceptions by Exception Type (timeline)", max_series=12)
else:
    st.info("No timestamped entries available to build timelines for current filter.")

st.markdown("---")

# Table
display_df = filtered[["timestamp_raw", "timestamp", "module", "level", "exception", "exc_message", "raw_traceback"]].copy()
display_df = display_df.rename(columns={"timestamp_raw": "timestamp_text", "exc_message": "exception_message", "raw_traceback": "traceback"})
st.subheader("Occurrences")
show_table(display_df, enable_aggrid=enable_aggrid, show_traceback_default=show_traceback_default)

# downloads
download_df = filtered.copy()
download_df["timestamp"] = download_df["timestamp"].apply(lambda x: x.isoformat() if pd.notnull(x) else "")
export_df = download_df[["timestamp", "module", "level", "exception", "exc_message", "category", "raw_traceback"]].rename(columns={"exc_message": "exception_message", "raw_traceback": "traceback"})
st.download_button("Download filtered results (CSV)", data=export_df.to_csv(index=False).encode("utf-8"), file_name="parsed_errors_filtered.csv", mime="text/csv")
st.download_button("Download filtered results (JSON)", data=export_df.to_json(orient="records", date_format="iso").encode("utf-8"), file_name="parsed_errors_filtered.json", mime="application/json")
