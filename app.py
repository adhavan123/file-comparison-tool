import re
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

from comparison import FileComparator
from reports import export_csv, export_excel, export_pdf
from history import load_history, save_history

st.set_page_config(
    page_title="File Comparison Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --paper: #F7F5F0;
    --surface: #FFFFFF;
    --ink: #1C1F26;
    --slate: #5B6270;
    --line: #DAD5C8;
    --green: #2F7A4D;
    --red: #B23B3B;
    --amber: #C08A2E;
}

.stApp {
    background-color: var(--paper);
}

html, body, [class*="css"], p, span, label, li {
    font-family: 'Source Serif 4', Georgia, serif;
    color: var(--ink);
}

section[data-testid="stSidebar"] {
    background-color: var(--surface);
    border-right: 1px solid var(--line);
}

h1, h2, h3 {
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--ink);
}

h1 {
    border-bottom: 1px solid var(--line);
    padding-bottom: 0.6rem;
}

[data-testid="stCaptionContainer"] {
    color: var(--slate);
    font-style: italic;
}

/* Numeric / data content in monospace */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
.stDataFrame, .stDataFrame *,
div[data-testid="stFileUploaderFileName"] {
    font-family: 'JetBrains Mono', 'SFMono-Regular', monospace !important;
}

[data-testid="stMetricLabel"] {
    color: var(--slate);
    font-size: 0.78rem;
}

/* Semantic metric coloring, scoped to the 6-column metrics row only */
div[data-testid="column"]:nth-of-type(1) [data-testid="stMetricValue"] { color: var(--ink); }
div[data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] { color: var(--slate); }
div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] { color: var(--amber); }
div[data-testid="column"]:nth-of-type(4) [data-testid="stMetricValue"] { color: var(--green); }
div[data-testid="column"]:nth-of-type(5) [data-testid="stMetricValue"] { color: var(--red); }
div[data-testid="column"]:nth-of-type(6) [data-testid="stMetricValue"] {
    color: var(--green);
    font-size: 2rem;
    font-weight: 600;
}

/* Buttons */
.stDownloadButton button {
    font-family: 'JetBrains Mono', monospace;
    background-color: #FFFFFF;
    color: var(--ink);
    border: 1px solid var(--ink);
    border-radius: 2px;
    padding: 0.5rem 1.2rem;
    transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
.stDownloadButton button:hover {
    background-color: var(--ink);
    border-color: var(--ink);
    color: #FFFFFF;
}

.stButton button {
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--ink);
    color: var(--paper);
    border: 1px solid var(--ink);
    border-radius: 2px;
    padding: 0.5rem 1.2rem;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}
.stButton button:hover {
    background-color: var(--green);
    border-color: var(--green);
    color: #fff;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background-color: var(--ink);
    border: 1px dashed rgba(247, 245, 240, 0.35);
    border-radius: 2px;
}

[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzoneInstructions"] * {
    color: #FFFFFF !important;
}

[data-testid="stFileUploaderDropzone"] svg {
    fill: #FFFFFF;
}

[data-testid="stFileUploaderDropzone"] button {
    background-color: transparent;
    color: #FFFFFF;
    border: 1px solid rgba(247, 245, 240, 0.6);
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background-color: #FFFFFF;
    color: var(--ink);
    border-color: #FFFFFF;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--green);
    border-bottom: 2px solid var(--green);
}

/* Dividers */
hr {
    border: none;
    border-top: 1px solid var(--line);
    margin: 2rem 0;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 2px;
    border-left: 3px solid var(--green);
}
</style>
""", unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Navigation",
    ["Compare Files", "History"]
)

# =========================
# HISTORY PAGE
# =========================
if page == "History":
    st.title("📜 Comparison History")
    st.caption("A record of every comparison run")

    history = load_history()

    if history:
        st.dataframe(
            pd.DataFrame(history),
            use_container_width=True
        )
    else:
        st.info("No History Found")

# =========================
# COMPARE PAGE
# =========================
if page == "Compare Files":
    st.title("📂 File Comparison Dashboard")
    st.caption("Row-by-row reconciliation across two datasets")

    col1, col2 = st.columns(2)

    with col1:
        file_a = st.file_uploader(
            "Upload File A",
            type=["csv", "xlsx", "json", "txt"]
        )

    with col2:
        file_b = st.file_uploader(
            "Upload File B",
            type=["csv", "xlsx", "json", "txt"]
        )

    if file_a and file_b:
        try:
            df1 = FileComparator.load_file(file_a)
            df2 = FileComparator.load_file(file_b)
        except ValueError as e:
            st.error(f"Unsupported file format: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Could not read one of the files: {e}")
            st.stop()

        st.subheader("File Statistics")

        stats = pd.DataFrame({
            "Metric": ["Rows", "Columns"],
            "File A": [len(df1), len(df1.columns)],
            "File B": [len(df2), len(df2.columns)]
        })

        st.dataframe(stats, use_container_width=True)

        st.subheader("Preview")

        t1, t2 = st.tabs(["File A", "File B"])

        with t1:
            st.dataframe(df1)

        with t2:
            st.dataframe(df2)

        try:
            result = FileComparator.compare(df1, df2)
        except Exception as e:
            st.error(f"Comparison failed: {e}")
            st.stop()

        save_history({
            "timestamp": str(datetime.now()),
            "fileA": file_a.name,
            "fileB": file_b.name,
            "rowsCompared": result["totalRows"],
            "differences": result["modifiedRows"],
            "matchPercentage": result["matchPercentage"]
        })

        st.subheader("Comparison Dashboard")

        m1, m2, m3, m4, m5, m6 = st.columns(6)

        m1.metric("Total", result["totalRows"])
        m2.metric("Matched", result["matchedRows"])
        m3.metric("Modified", result["modifiedRows"])
        m4.metric("Added", result["addedRows"])
        m5.metric("Removed", result["removedRows"])
        m6.metric("Match %", f"{result['matchPercentage']}%")

        st.subheader("Analytics")

        chart_df = pd.DataFrame({
            "Category": ["Matched", "Modified", "Added", "Removed"],
            "Count": [
                result["matchedRows"],
                result["modifiedRows"],
                result["addedRows"],
                result["removedRows"]
            ]
        })

        left, right = st.columns(2)

        with left:
            pie = px.pie(
                chart_df,
                names="Category",
                values="Count",
                hole=0.4
            )
            st.plotly_chart(pie, use_container_width=True)

        with right:
            bar = px.bar(
                chart_df,
                x="Category",
                y="Count",
                color="Category"
            )
            st.plotly_chart(bar, use_container_width=True)

        # =========================
        # COLUMN CHANGES
        # =========================
        st.subheader("Column Changes")

        c1, c2 = st.columns(2)

        with c1:
            st.write("### Added Columns")
            if result.get("addedColumns"):
                st.write(result["addedColumns"])
            else:
                st.success("No Added Columns")

        with c2:
            st.write("### Removed Columns")
            if result.get("removedColumns"):
                st.write(result["removedColumns"])
            else:
                st.success("No Removed Columns")

        st.subheader("Difference Table")

        search = st.text_input("Search Difference")

        diff_df = pd.DataFrame(result["differences"])

        if not diff_df.empty:
            if search:
                pattern = re.escape(search)
                diff_df = diff_df[
                    diff_df.astype(str)
                    .apply(
                        lambda col: col.str.contains(
                            pattern,
                            case=False,
                            na=False,
                            regex=True
                        )
                    )
                    .any(axis=1)
                ]

            def style_status(value):
                colors = {
                    "Modified": "color: #C08A2E; font-weight: 600;",
                    "Added": "color: #2F7A4D; font-weight: 600;",
                    "Removed": "color: #B23B3B; font-weight: 600;",
                }
                return colors.get(value, "")

            if "Status" in diff_df.columns:
                try:
                    styled_diff = diff_df.style.map(style_status, subset=["Status"])
                except AttributeError:
                    styled_diff = diff_df.style.applymap(style_status, subset=["Status"])
            else:
                styled_diff = diff_df

            st.dataframe(
                styled_diff,
                use_container_width=True,
                height=500
            )

            export_col1, export_col2, export_col3 = st.columns(3)

            with export_col1:
                try:
                    csv_data = export_csv(diff_df)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="comparison_report.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.warning(f"CSV export unavailable: {e}")

            with export_col2:
                try:
                    excel_data = export_excel(diff_df)
                    st.download_button(
                        label="Download Excel",
                        data=excel_data,
                        file_name="comparison_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.warning(f"Excel export unavailable: {e}")

            with export_col3:
                try:
                    pdf_data = export_pdf(result)
                    st.download_button(
                        "Download PDF",
                        pdf_data,
                        "comparison_report.pdf",
                        "application/pdf"
                    )
                except Exception as e:
                    st.warning(f"PDF export unavailable: {e}")
        else:
            st.success("No Differences Found ✅")