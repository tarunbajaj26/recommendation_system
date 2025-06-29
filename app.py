import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

from langchain_community.llms import HuggingFaceHub
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent

# Load environment variables
load_dotenv()

# Load OpenRouter-compatible LLM
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE"),
    model="mistralai/mistral-7b-instruct"
)

# Load internship data
@st.cache_data
def load_internship_data():
    df = pd.read_csv("internships with websites.csv")
    return df

# Save student responses to CSV
def save_student_response(name, contact, domain, job_role, level, industry, timestamp):
    response = {
        "Timestamp": timestamp,
        "Name": name,
        "Contact": contact,
        "Domain": ", ".join(domain),
        "Job Role": ", ".join(job_role),
        "Level": ", ".join(level),
        "Industry": ", ".join(industry),
    }
    response_df = pd.DataFrame([response])
    response_file = "student_responses.csv"
    if os.path.exists(response_file):
        response_df.to_csv(response_file, mode='a', header=False, index=False)
    else:
        response_df.to_csv(response_file, mode='w', header=True, index=False)

# Streamlit UI
def main():
    st.set_page_config(page_title="Internship Recommendation", page_icon="🎓", layout="wide")
    st.title("🎓 Internship Recommendation System")
    st.markdown("Get personalized internship suggestions based on your interests and goals.")

    df = load_internship_data()

    industries = sorted(df["Industry"].dropna().unique().tolist())
    domains = sorted(df["Domain"].dropna().unique().tolist())
    job_roles = sorted(df["Job Role"].dropna().unique().tolist())
    levels = sorted(df["Level"].dropna().unique().tolist())

    with st.form("filter_form"):
        name = st.text_input("Your Full Name")
        contact = st.text_input("Email or Phone")
        selected_domain = st.multiselect("Preferred Domain(s)", domains)
        selected_job = st.multiselect("Preferred Job Role(s)", job_roles)
        selected_level = st.multiselect("Experience Level(s)", levels)
        selected_industry = st.multiselect("Preferred Industry", industries)
        submit = st.form_submit_button("🔍 Get Matching Internships")

    if submit:
        if not name or not contact:
            st.warning("Please fill in your name and contact info.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_student_response(name, contact, selected_domain, selected_job, selected_level, selected_industry, timestamp)
            filtered_df = df[
                df["Domain"].isin(selected_domain) &
                df["Job Role"].isin(selected_job) &
                df["Level"].isin(selected_level) &
                df["Industry"].isin(selected_industry)
            ]
            if not filtered_df.empty:
                st.success(f"Found {len(filtered_df)} matching internships.")
                for _, row in filtered_df.iterrows():
                    with st.expander(f"{row['Menternship Name']} at {row['Company']}"):
                        st.markdown(f"**Job Role:** {row['Job Role']}")
                        st.markdown(f"**Domain:** {row['Domain']}")
                        st.markdown(f"**Industry:** {row['Industry']}")
                        st.markdown(f"**Level:** {row['Level']}")
                        st.markdown(f"**Summary:** {row['One-line Summary']}")
                        st.markdown(f"**Skills:** {row['Skills - Apply']}")
                        st.markdown(f"[Visit Website]({row['Website']})")
            else:
                st.warning("No exact matches found. Try broader criteria.")

    st.divider()

    # 🔮 AI Recommendation Section
    st.subheader("🔍 Search Internships by Skills/Goals (AI-Powered)")
    user_prompt = st.text_input("Enter your career goal, skills you want to learn, or preferred industry")
    if st.button("🔮 Search using AI"):
        if user_prompt:
            with st.spinner("Searching using AI..."):
                try:
                    agent = create_pandas_dataframe_agent(
                        llm,
                        df,
                        verbose=False,
                        agent_type="openai-tools",
                        handle_parsing_errors=True,
                        allow_dangerous_code=True
                    )

                    response = agent.run(
                        f"""A student says: \"{user_prompt}\".
Check the dataset for internships that closely match based on domain, skills, and industry.
If no exact match is found, suggest similar internships and clearly mention:
\"We’ll work on your feedback and add a more suitable internship soon. Meanwhile, you can consider these related opportunities.\"
Include internship name and company if possible."""
                    )

                    st.success("AI Response:")
                    st.markdown(response)

                    # Try to enrich with related internships
                    match_found = False
                    for _, row in df.iterrows():
                        title = str(row["Menternship Name"]).strip().lower()
                        company = str(row["Company"]).strip().lower()

                        if title in response.lower() and company in response.lower():
                            st.markdown(
                                f"🔗 **[View: {row['Menternship Name']} at {row['Company']}]({row['Website']})**"
                            )
                            match_found = True

                    if not match_found:
                        st.warning("We couldn’t find an exact match, but here are some related internships:")
                        keywords = user_prompt.lower().split()

                        related_df = df[
                            df["Domain"].str.lower().apply(lambda x: any(word in x for word in keywords))
                            | df["Skills - Apply"].fillna("").str.lower().apply(lambda x: any(word in x for word in keywords))
                        ].head(5)

                        if related_df.empty:
                            st.info("No related internships found in our current dataset.")
                        else:
                            for _, row in related_df.iterrows():
                                st.markdown(
                                    f"🔗 **[Related: {row['Menternship Name']} at {row['Company']}]({row['Website']})**  \n"
                                    f"🧠 **Skills**: {row['Skills - Apply']}  \n"
                                    f"📚 **Domain**: {row['Domain']}  \n"
                                    f"🏢 **Industry**: {row['Industry']}"
                                )
                            st.markdown("---")
                            st.markdown("📝 _We’ll work on your feedback and try to include internships aligned with your preferences soon._")

                except Exception as e:
                    st.error(f"Error using AI: {e}")
        else:
            st.warning("Please enter your query before clicking the button.")

if __name__ == "__main__":
    main()
