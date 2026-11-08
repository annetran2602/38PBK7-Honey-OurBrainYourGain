
import streamlit as st
import tempfile
import os

from combine import (
    analyze_resume,
    search_and_match_jobs
)

# PAGE CONFIGURATION


st.set_page_config(
    page_title="Our Brain Your Gain",
    page_icon="🧠",
    layout="wide"
)


# SESSION STATE


defaults = {
    "resume_text": None,
    "resume_name": None,
    "jobs": [],
    "analyzed": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==================================
# SIDEBAR
# ==================================
st.sidebar.title("Welcome to...💡")
st.sidebar.title("🧠Our Brain Your Gain🧠")
st.sidebar.caption("AI-Powered Job Matching")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Resume",
        "Job Search",
        "Job Matches"
    ]
)

st.sidebar.divider()
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        min-width: 350px;
        max-width: 350px;
    }
</style>
""", unsafe_allow_html=True)
st.sidebar.caption("Powered by Python + Ollama + Adzuna")

# ==================================
# DASHBOARD
# ==================================

if page == "Dashboard":

    st.title("Dashboard")

    st.write("Welcome to your AI Resume Analysis & Job Matching.")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Jobs Found",
        len(st.session_state.jobs)
    )

    col2.metric(
        "Jobs Analyzed",
        len(st.session_state.jobs)
    )

    scores = [
        job["score"]
        for job in st.session_state.jobs
    ]

    average = sum(scores) / len(scores) if scores else 0

    col3.metric(
        "Average Match",
        f"{average:.1f}%"
    )

    st.divider()

    st.subheader("Getting Started")

    st.markdown("""
    1. Upload your resume in PDF format.
    2. Analyze your resume.
    3. Search for jobs using Adzuna.
    4. Let Ollama compare your resume against job descriptions.
    5. View your highest-ranking job matches.
    """)

    if st.session_state.analyzed:
        st.success(
            f"Resume analyzed: {st.session_state.resume_name}"
        )
    else:
        st.info("Upload your resume to get started.")

# ==================================
# UPLOAD RESUME
# ==================================

elif page == "Upload Resume":

    st.title("Upload Your Resume")

    st.write(
        "Upload your PDF resume to analyze your qualifications."
    )

    uploaded_file = st.file_uploader(
        "Choose your resume",
        type=["pdf"]
    )

    if uploaded_file:

        st.success("Resume uploaded successfully!")

        st.write("Filename:", uploaded_file.name)

        st.write(
            "File size:",
            f"{uploaded_file.size / 1024:.2f} KB"
        )

        if st.button("Analyze Resume", type="primary"):

            try:

                with st.spinner("Extracting resume information..."):

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:

                        temp_file.write(
                            uploaded_file.getvalue()
                        )

                        temp_path = temp_file.name

                    try:
                        resume_text = analyze_resume(temp_path)

                    finally:
                        os.remove(temp_path)

                st.session_state.resume_text = resume_text
                st.session_state.resume_name = uploaded_file.name
                st.session_state.analyzed = True
                st.session_state.jobs = []

                st.success("Resume analyzed successfully!")

                st.subheader("Extracted Resume Text")

                with st.expander("View extracted text"):
                    st.text(resume_text)

            except Exception as e:

                st.error(f"Resume analysis failed: {e}")

# JOB SEARCH

elif page == "Job Search":

    st.title("Search for Jobs")

    st.write(
        "Find opportunities and compare them against your resume."
    )

    if not st.session_state.analyzed:

        st.warning(
            "Please upload and analyze your resume first."
        )

    else:

        with st.form("job_search_form"):

            job_title = st.text_input(
                "Job Title",
                placeholder="e.g. Python Developer"
            )

            location = st.text_input(
                "Location",
                value="Calgary"
            )

            submitted = st.form_submit_button(
                "Search and Analyze Jobs",
                type="primary"
            )

        if submitted:

            if not job_title.strip():

                st.warning("Please enter a job title.")

            else:

                try:

                    with st.spinner(
                        "Searching jobs and analyzing matches with Ollama..."
                    ):

                        matched_jobs = search_and_match_jobs(
                            st.session_state.resume_text,
                            job_title,
                            location
                        )

                    st.session_state.jobs = matched_jobs

                    if matched_jobs:

                        st.success(
                            f"Successfully analyzed {len(matched_jobs)} jobs!"
                        )

                        st.info(
                            "Visit Job Matches to see your rankings."
                        )

                    else:

                        st.warning(
                            "No jobs were found or successfully analyzed."
                        )

                except Exception as e:

                    st.error(f"Job search failed: {e}")

# JOB MATCHES

elif page == "Job Matches":
    st.title("Your Best Job Matches")
    st.write(
        "Jobs ranked according to your resume matching score."
    )
    if not st.session_state.jobs:

        st.info(
            "No job matches available yet. Search for jobs first."
        )
    else:
        ranked_jobs = sorted(
            st.session_state.jobs,
            key=lambda job: job["score"],
            reverse=True
        )
        for index, job in enumerate(
            ranked_jobs,
            start=1
        ):
            with st.container(border=True):
                st.subheader(
                    f"#{index} {job['title']}"
                )
                st.write(f"**Company:** {job['company']}")
                st.metric(
                    "Matching Score",
                    f"{job['score']:.1f}%"
                )
                st.write("**AI Assessment:**")
                st.write(job["summary"])
                st.write("**Missing Qualifications:**")
                if job["missing_skills"]:
                    for skill in job["missing_skills"]:
                        st.write(f"- {skill}")
                else:
                    st.write("No missing qualifications identified.")

                with st.expander("View Detailed AI Analysis"):

                    st.write("### Matching Qualifications")

                    for item in job["matching_qualifications"]:
                        st.write(
                            f"**{item.get('requirement', '')}**"
                        )
                        st.write(
                            f"Evidence: {item.get('resume_evidence', '')}"
                        )
                        st.write(
                            f"Match: {item.get('match', '')}"
                        )

                    st.write("### Experience Analysis")
                    st.write(job["experience_analysis"])

                    st.write("### Education Analysis")
                    st.write(job["education_analysis"])

                    st.write("### Recommendations")

                    for recommendation in job["recommendations"]:
                        st.write(f"- {recommendation}")

                if job["link"] != "N/A":
                    st.markdown(
                        f"[View Job / Apply Here]({job['link']})"
                    )
