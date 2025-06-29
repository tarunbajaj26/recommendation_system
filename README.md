Internship Recommendation System
This is a Streamlit-based web application that helps students find internships based on their preferences for domain, job role, and difficulty level. The app filters internships from a provided dataset (internships.csv) and displays matching opportunities with details and hyperlinks. Student responses are saved to a student_responses.csv file.

Setup Instructions
Ensure you have a Hugging Face account: Sign up here.

Create a new Space in Hugging Face Spaces, selecting Streamlit as the SDK.

Upload the following files to the Space repository:

app.py: The main Streamlit application.

requirements.txt: Lists dependencies (streamlit and pandas).

internships.csv: The internship dataset.

README.md: This file.

The Space will automatically build and deploy the app once files are uploaded.

Usage
Enter your name and contact information.

Select one or more domains, job roles, and difficulty levels.

Click "Find Internships" to view matching internships.

Expand each internship to see details and a hyperlink (uses a placeholder URL).

Responses are saved to student_responses.csv.

Notes
Replace the placeholder URL in generate_internship_link in app.py with your company's actual URL pattern.

Ensure internships.csv is in the root directory of the Space.