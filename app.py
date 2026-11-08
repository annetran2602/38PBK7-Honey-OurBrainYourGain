import streamlit as st
import tempfile
import os

from combine import (
    analyze_resume,
    search_and_match_jobs
)

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Our Brain Your Gain", #browser tab title
    page_icon="🧠", #browser tab icon
    layout="wide" #use full width of browser
)


# SESSION STATE
defaults = {
    "resume_text": None, #stores text from resume
    "resume_name": None, #stores file name of resume
    "jobs": [], #stores analyzed job matches
    "analyzed": False #tracks if resume has been analyzed
}

#initialize the session default data if no variables exist yet
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# SIDEBAR
# display app name and welcome message in the side bar
st.sidebar.title("Welcome to...💡")
st.sidebar.title("🧠Our Brain Your Gain🧠")
st.sidebar.caption("AI-Powered Job Matching")

#navigation menu for users to switch between pages
page = st.sidebar.radio(
    "---MENU---",
    [
        "Dashboard",
        "Upload Resume",
        "Job Search",
        "Job Matches"
    ]
)

#sidebar to separate navigation menu from application info
st.sidebar.divider()
#Expand sidebar to fit text
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        min-width: 350px;
        max-width: 350px;
    }
</style>
""", unsafe_allow_html=True)
st.sidebar.caption("Powered by Python + Ollama + Adzuna")

# DASHBOARD
#display dashboard if user selects "Dashboard"
if page == "Dashboard":
    st.title("Dashboard")
    st.write("Welcome to your AI Resume Analysis & Job Matching.")
    #columns to display app statistics
    col1, col2, col3 = st.columns(3)
    #display number of jobs found
    col1.metric(
        "Jobs Found",
        len(st.session_state.jobs)
    )
    #display number of jobs analyzed
    col2.metric(
        "Jobs Analyzed",
        len(st.session_state.jobs)
    )
    #extract job scores from all analyzed jobs
    scores = [
        job["score"]
        for job in st.session_state.jobs
    ]
    #calculate average matching score, 0 if no jobs
    average = sum(scores) / len(scores) if scores else 0
    col3.metric(
        "Average Match",
        f"{average:.1f}%"
    )
    st.divider()
    #display instructions on how to use app
    st.subheader("Getting Started")
    st.markdown("""
    1. Upload your resume PDF.
    2. Get your resume analyzed.
    3. Search for jobs you're qualified for.
    4. Compare your resume against job descriptions.
    5. View your highest-ranking job matches.
    """)

    if st.session_state.analyzed: #if a resume has been analyzed
        st.success(f"Resume analyzed: {st.session_state.resume_name}") #display success message
    else:
        st.info("Upload your resume to get started.") #prompt user to input a resume

# UPLOAD RESUME
#display resume upload page
elif page == "Upload Resume":
    st.title("Upload Your Resume")
    st.write("Upload your PDF resume to analyze your qualifications.")
    #file uploader that only accepts pdfs
    uploaded_file = st.file_uploader("Choose your resume",type=["pdf"])
    
    #if user uploaded a file
    if uploaded_file:
        st.success("Resume uploaded successfully!") #display success message
        st.write("Filename:", uploaded_file.name) #display uploaded file name
        st.write("File size:",f"{uploaded_file.size / 1024:.2f} KB") #convert file size to kilobytes
        if st.button("Analyze Resume", type="primary"): #create button that starts resume analysis
            try:
                with (st.spinner("Extracting resume information...")): #display loading message
                    with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as temp_file: #create temp pdf file on computer
                        temp_file.write(uploaded_file.getvalue()) #write pdf contents into temp file
                        temp_path = temp_file.name #save temp file name
                    try:
                        resume_text = analyze_resume(temp_path) #analyze temporary pdf file
                    finally:
                        os.remove(temp_path) #delete pdf after processing
                st.session_state.resume_text = resume_text #save extracted resume text in session state
                st.session_state.resume_name = uploaded_file.name #save file name of resume
                st.session_state.analyzed = True
                st.session_state.jobs = [] #clear previous job matches
                st.success("Resume analyzed successfully!") #success message
                st.subheader("Extracted Resume Text") #extracted resume info
                with st.expander("View extracted text"): #place extracted text inside an expandable section
                    st.text(resume_text)
            except Exception as e:
                st.error(f"Resume analysis failed: {e}") #display error message if analysis fails

# JOB SEARCH
#display job search page when selected
elif page == "Job Search":
    st.title("Search for Jobs")
    st.write("Find opportunities and compare them against your resume.")
    if not st.session_state.analyzed: #check if resume has been uploaded
        st.warning("Please upload and analyze your resume first.") #prevent job searching prior to uploading resume
    else:
        with st.form("job_search_form"): #create form to collect job search info
            job_title = st.text_input( #ask user for type of job to search for
                "Job Title",
                placeholder="e.g. Python Developer"
            )
            location = st.text_input( #ask user for location of the job
                "Location",
                value="Calgary"
            )
            submitted = st.form_submit_button( #create submit button to start job search
                "Search and Analyze Jobs",
                type="primary"
            )
        if submitted:
            if not job_title.strip(): #make sure job title is not empty
                st.warning("Please enter a job title.")
            else:
                try:
                    with st.spinner("Searching jobs and analyzing matches with Ollama..."): #display loading message while job are being matched
                        #match jobs to user
                        matched_jobs = search_and_match_jobs(
                            st.session_state.resume_text,
                            job_title,
                            location
                        )
                    st.session_state.jobs = matched_jobs
                    if matched_jobs:
                        st.success(
                            f"Successfully analyzed {len(matched_jobs)} jobs!" #display success
                        )
                        st.info( #display list of compatible jobs
                            "Visit Job Matches to see your rankings."
                        )
                    else:
                        st.warning( #display no jobs found
                            "No jobs were found or successfully analyzed."
                        )
                except Exception as e: #job search failed
                    st.error(f"Job search failed: {e}")

# JOB MATCHES
#display job matching results when selected
elif page == "Job Matches":
    st.title("Your Best Job Matches")
    st.write(
        "Jobs ranked according to your resume matching score."
    )
    if not st.session_state.jobs: #check if job matching results are available 
        st.info("No job matches available yet. Search for jobs first.") #prompt user to search for jobs first
    else:
        #sort job results according to the highest matching score
        ranked_jobs = sorted(
            st.session_state.jobs,
            key=lambda job: job["score"],
            reverse=True
        )
        #loop through each job in the sorted list
        for index, job in enumerate(
            ranked_jobs,
            start=1
        ):
            with st.container(border=True): #container for each job listing
                st.subheader( #display job ranking and title
                    f"#{index} {job['title']}"
                )
                #display company offering postion
                st.write(f"**Company:** {job['company']}")
                #display AI matching score as percentage
                st.metric(
                    "Matching Score",
                    f"{job['score']:.1f}%"
                )
                #display AI assessment of job match
                st.write("**AI Assessment:**")
                st.write(job["summary"])
                #display qualifications or skills missing from resume
                st.write("**Missing Qualifications:**")
                #Check for missing skills 
                if job["missing_skills"]:
                    # display each missing skill separately
                    for skill in job["missing_skills"]:
                        st.write(f"- {skill}")
                else:
                    #display if no missing skills identified
                    st.write("No missing qualifications identified.")
                with st.expander("View Detailed AI Analysis"):
                    st.write("### Matching Qualifications")
                    #loop through matching qualifications
                    for item in job["matching_qualifications"]:
                        #display job requirements
                        st.write(
                            f"**{item.get('requirement', '')}**"
                        )
                        #Display evidence found in uploaded resume
                        st.write(
                            f"Evidence: {item.get('resume_evidence', '')}"
                        )
                        #display how well resume satisfies requirement
                        st.write(
                            f"Match: {item.get('match', '')}"
                        )
                    st.write("### Experience Analysis") #AI analysis of users work experience
                    st.write(job["experience_analysis"])
                    
                    st.write("### Education Analysis") #AI evaluation of user's education
                    st.write(job["education_analysis"])
                    
                    st.write("### Recommendations") #reccomendations for improving user's job application
                    #loop and display all recommendations
                    for recommendation in job["recommendations"]:
                        st.write(f"- {recommendation}")
                #check if valid job application link exists
                if job["link"] != "N/A":
                    st.markdown( #display clickable link that takes user to original job posting
                        f"[View Job / Apply Here]({job['link']})"
                    )