
# from src.workflow.approvals import (
#     submit_proposal,
#     decide_proposal
# )

# import sqlite3
# from pathlib import Path

# import pandas as pd
# import plotly.express as px
# import streamlit as st


import sys
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Add project root to Python import path
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import workflow functions
from src.workflow.approvals import (
    submit_proposal,
    decide_proposal
)




# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

# ROOT = Path(__file__).resolve().parents[1]

DB_PATH = ROOT / "database" / "compensation.db"
OUTPUT_PATH = ROOT / "outputs"

COMPENSATION_FILE = OUTPUT_PATH / "compensation_analysis_2026-12-31.csv"
DISPARITY_FILE = OUTPUT_PATH / "disparity_flags.csv"
EVIDENCE_FILE = OUTPUT_PATH / "evidence_based_review.csv"


# --------------------------------------------------
# 2. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="YottaFlex | Compensation Intelligence",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# 3. LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_csv_files():

    compensation = pd.read_csv(COMPENSATION_FILE)
    disparity = pd.read_csv(DISPARITY_FILE)
    evidence = pd.read_csv(EVIDENCE_FILE)

    return compensation, disparity, evidence


@st.cache_data
def load_master_data():

    conn = sqlite3.connect(DB_PATH)

    roles = pd.read_sql_query(
        "SELECT role_id, role_name FROM Role",
        conn
    )

    levels = pd.read_sql_query(
        "SELECT level_id, level_name FROM Level",
        conn
    )

    locations = pd.read_sql_query(
        "SELECT location_id, location_name FROM Location",
        conn
    )

    employee_count = pd.read_sql_query(
        "SELECT COUNT(*) AS total FROM Employee",
        conn
    )["total"][0]

    proposals = pd.read_sql_query(
        """
        SELECT proposal_id, employee_id, proposed_annual_salary,
               currency_code, reason, status, created_at
        FROM AdjustmentProposal
        ORDER BY created_at DESC
        """,
        conn
    )

    conn.close()

    return roles, levels, locations, employee_count, proposals


try:
    compensation, disparity, evidence = load_csv_files()

    roles, levels, locations, employee_count, proposals = (
        load_master_data()
    )

except Exception as error:
    st.error(f"Unable to load project data: {error}")
    st.stop()


# --------------------------------------------------
# 4. ADD READABLE NAMES
# --------------------------------------------------

role_map = dict(zip(roles["role_id"], roles["role_name"]))
level_map = dict(zip(levels["level_id"], levels["level_name"]))
location_map = dict(zip(locations["location_id"], locations["location_name"]))

compensation["Role"] = compensation["role_id"].map(role_map)
compensation["Level"] = compensation["level_id"].map(level_map)
compensation["Location"] = compensation["location_id"].map(location_map)

disparity["Location"] = disparity["location_id"].map(location_map)
evidence["Location"] = evidence["location_id"].map(location_map)


# --------------------------------------------------
# 5. HEADER
# --------------------------------------------------

st.title("Compensation Intelligence Dashboard")

st.caption(
    "YottaFlex | Compensation Analysis and Decision Support"
)

st.divider()


# --------------------------------------------------
# 6. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Analysis Filters")

selected_locations = st.sidebar.multiselect(
    "Location",
    sorted(compensation["Location"].dropna().unique()),
    default=sorted(compensation["Location"].dropna().unique())
)

selected_roles = st.sidebar.multiselect(
    "Role",
    sorted(compensation["Role"].dropna().unique()),
    default=sorted(compensation["Role"].dropna().unique())
)

selected_levels = st.sidebar.multiselect(
    "Level",
    sorted(compensation["Level"].dropna().unique()),
    default=sorted(compensation["Level"].dropna().unique())
)

selected_status = st.sidebar.multiselect(
    "Band Status",
    sorted(compensation["band_status"].dropna().unique()),
    default=sorted(compensation["band_status"].dropna().unique())
)


# --------------------------------------------------
# 7. APPLY FILTERS
# --------------------------------------------------

filtered = compensation[
    compensation["Location"].isin(selected_locations)
    & compensation["Role"].isin(selected_roles)
    & compensation["Level"].isin(selected_levels)
    & compensation["band_status"].isin(selected_status)
].copy()

selected_ids = set(filtered["employee_id"])

filtered_disparity = disparity[
    disparity["employee_id"].isin(selected_ids)
].copy()

filtered_evidence = evidence[
    evidence["employee_id"].isin(selected_ids)
].copy()


# --------------------------------------------------
# 8. KEY METRICS
# --------------------------------------------------

st.subheader("Compensation Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Employees Analyzed",
        f"{len(filtered):,}"
    )

with col2:
    within_band = (
        filtered["band_status"] == "WITHIN_BAND"
    ).sum()

    st.metric(
        "Within Compensation Band",
        f"{within_band:,}"
    )

with col3:
    review_count = (
        filtered_disparity["review_required"] == "YES"
    ).sum()

    st.metric(
        "Disparity Reviews",
        f"{review_count:,}"
    )

with col4:
    st.metric(
        "Adjustment Proposals",
        f"{len(proposals):,}"
    )


st.divider()


# --------------------------------------------------
# 9. COMPENSATION ANALYSIS
# --------------------------------------------------

st.subheader("Compensation Distribution")

col1, col2 = st.columns(2)

with col1:

    band_counts = (
        filtered["band_status"]
        .value_counts()
        .rename_axis("Band Status")
        .reset_index(name="Employees")
    )

    fig = px.pie(
        band_counts,
        names="Band Status",
        values="Employees",
        title="Employees by Compensation Band",
        hole=0.45
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    fig = px.box(
        filtered,
        x="Level",
        y="normalized_salary_inr",
        color="Role",
        title="Salary Distribution by Level",
        labels={
            "normalized_salary_inr": "Normalized Salary (INR)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 10. COMPA-RATIO ANALYSIS
# --------------------------------------------------

st.subheader("Compa-Ratio Analysis")

fig = px.histogram(
    filtered,
    x="compa_ratio",
    color="band_status",
    nbins=30,
    title="Distribution of Compa-Ratios",
    labels={
        "compa_ratio": "Compa-Ratio"
    }
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 11. DISPARITY REVIEW
# --------------------------------------------------

st.divider()

st.subheader("Potential Compensation Disparities")

st.caption(
    "These are screening flags, not proof of discrimination "
    "or an incorrect compensation decision."
)

if filtered_disparity.empty:

    st.info("No disparity records for the selected filters.")

else:

    st.metric(
        "Employees Flagged",
        len(filtered_disparity)
    )

    st.dataframe(
        filtered_disparity,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 12. EVIDENCE-BASED REVIEW
# --------------------------------------------------

st.divider()

st.subheader("Evidence-Based Review")

if filtered_evidence.empty:

    st.info("No evidence review records for the selected filters.")

else:

    assessment_counts = (
        filtered_evidence["evidence_assessment"]
        .value_counts()
        .rename_axis("Assessment")
        .reset_index(name="Employees")
    )

    fig = px.bar(
        assessment_counts,
        x="Assessment",
        y="Employees",
        title="Evidence Assessment Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        filtered_evidence,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 13. ADJUSTMENT PROPOSALS
# --------------------------------------------------

st.divider()

st.subheader("Adjustment Proposal Workflow")

status_counts = (
    proposals["status"]
    .value_counts()
    .rename_axis("Status")
    .reset_index(name="Proposals")
)

fig = px.bar(
    status_counts,
    x="Status",
    y="Proposals",
    title="Proposal Status Distribution"
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    proposals,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 13.1 INTERACTIVE PROPOSAL REVIEW
# --------------------------------------------------

st.subheader("Review and Process a Proposal")

actionable_proposals = proposals[
    proposals["status"].isin(["DRAFT", "SUBMITTED"])
].copy()

if actionable_proposals.empty:

    st.info("No proposals are currently awaiting action.")

else:

    selected_proposal_id = st.selectbox(
        "Select a proposal",
        actionable_proposals["proposal_id"].tolist()
    )

    selected_proposal = actionable_proposals[
        actionable_proposals["proposal_id"]
        == selected_proposal_id
    ].iloc[0]

    employee_id = selected_proposal["employee_id"]

    st.write("**Proposal ID:**", selected_proposal_id)
    st.write("**Employee ID:**", employee_id)
    st.write("**Current Status:**", selected_proposal["status"])
    st.write(
        "**Proposed Salary:**",
        f'{selected_proposal["proposed_annual_salary"]:,.2f} '
        f'{selected_proposal["currency_code"]}'
    )
    st.write("**Reason:**", selected_proposal["reason"])

    # Show compensation information
    employee_compensation = compensation[
        compensation["employee_id"] == employee_id
    ]

    if not employee_compensation.empty:

        st.write("**Compensation Analysis**")

        st.dataframe(
            employee_compensation[
                [
                    "normalized_salary_inr",
                    "band_min_inr",
                    "band_midpoint_inr",
                    "band_max_inr",
                    "compa_ratio",
                    "band_status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    # Show evidence information
    employee_evidence = evidence[
        evidence["employee_id"] == employee_id
    ]

    if not employee_evidence.empty:

        st.write("**Evidence Review**")

        st.dataframe(
            employee_evidence,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.warning("No evidence review record found for this employee.")

    st.divider()

    # DRAFT -> SUBMITTED
    if selected_proposal["status"] == "DRAFT":

        with st.form("submit_proposal_form"):

            submitter = st.text_input(
                "Submitter ID or name"
            )

            submitted = st.form_submit_button(
                "Submit for Approval"
            )

            if submitted:

                if not submitter.strip():
                    st.error("Enter the submitter ID or name.")

                else:
                    try:
                        submit_proposal(
                            selected_proposal_id,
                            submitter.strip()
                        )

                        load_master_data.clear()
                        st.success("Proposal submitted.")
                        st.rerun()

                    except (ValueError, sqlite3.Error) as error:
                        st.error(str(error))

    # SUBMITTED -> APPROVED / REJECTED
    elif selected_proposal["status"] == "SUBMITTED":

        with st.form("decision_form"):

            approver = st.text_input(
                "Approver ID or name"
            )

            decision = st.radio(
                "Decision",
                ["APPROVED", "REJECTED"]
            )

            comments = st.text_area(
                "Decision comments"
            )

            decided = st.form_submit_button(
                "Record Decision"
            )

            if decided:

                if not approver.strip() or not comments.strip():
                    st.error(
                        "Approver and decision comments are required."
                    )

                else:
                    try:
                        decide_proposal(
                            selected_proposal_id,
                            decision,
                            approver.strip(),
                            comments.strip()
                        )

                        load_master_data.clear()
                        st.success("Decision recorded.")
                        st.rerun()

                    except (ValueError, sqlite3.Error) as error:
                        st.error(str(error))


# --------------------------------------------------
# 14. EMPLOYEE COMPENSATION TABLE
# --------------------------------------------------

st.divider()

st.subheader("Employee Compensation Details")

display_columns = [
    "employee_id",
    "Role",
    "Level",
    "Location",
    "fte",
    "normalized_salary_inr",
    "band_min_inr",
    "band_midpoint_inr",
    "band_max_inr",
    "compa_ratio",
    "band_position_percent",
    "band_status"
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 15. DOWNLOAD REPORT
# --------------------------------------------------

st.divider()

csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Compensation Analysis CSV",
    data=csv_data,
    file_name="compensation_analysis_report.csv",
    mime="text/csv"
)


# --------------------------------------------------
# 16. FOOTER
# --------------------------------------------------

st.caption(
    "YottaFlex Compensation Intelligence | "
    "Synthetic demonstration dataset | Analysis date: 31 Dec 2026"
)
