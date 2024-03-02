import streamlit as st
from tika import parser
import re
import spacy
from spacy.matcher import Matcher
import json

# Function to extract email addresses
def get_email_addresses(string):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(string)

# Function to extract phone numbers
def get_phone_numbers(string):
    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phone_numbers = r.findall(string)
    return [re.sub(r'\D', ' ', num) for num in phone_numbers]

# Function to extract name
def extract_name(text):
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)
    nlp_text = nlp(text)
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    matcher.add('NAME', [pattern], on_match=None)
    matches = matcher(nlp_text)
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

# Function to parse resume
def parse_resume(file_path, json_file_path):
    file_data = parser.from_file(file_path)
    text = file_data['content']
    parsed_content = {}

    email = get_email_addresses(text)
    parsed_content['E-mail'] = email

    phone_number = get_phone_numbers(text)
    if len(phone_number) <= 10:
        parsed_content['Phone number'] = phone_number

    name = extract_name(text)
    parsed_content['Name'] =  name

    keywords = ["education", "summary", "accomplishments", "executive profile", "professional profile",
                "personal profile", "work background", "academic profile", "other activities", "qualifications",
                "experience", "interests", "skills", "achievements", "publications", "publication", "certifications",
                "workshops", "projects", "internships", "trainings", "hobbies", "overview", "objective",
                "position of responsibility", "jobs"]

    text = text.replace("\n", " ")
    text = text.replace("[^a-zA-Z0-9]", " ")
    text = re.sub('\W+', ' ', text)
    text = text.lower()

    content = {}
    indices = []
    keys = []
    for key in keywords:
        try:
            content[key] = text[text.index(key) + len(key):]
            indices.append(text.index(key))
            keys.append(key)
        except:
            pass

    zipped_lists = zip(indices, keys)
    sorted_pairs = sorted(zipped_lists)

    tuples = zip(*sorted_pairs)
    indices, keys = [list(tuple) for tuple in tuples]

    content = []
    for idx in range(len(indices)):
        if idx != len(indices) - 1:
            content.append(text[indices[idx]: indices[idx + 1]])
        else:
            content.append(text[indices[idx]:])

    for i in range(len(indices)):
        parsed_content[keys[i]] = content[i]

    with open(json_file_path, "w") as outfile:
        json.dump(parsed_content, outfile)

    return parsed_content

# Function to display content of JSON file
def display_json_content(json_file_path):
    with open(json_file_path, "r") as file:
        data = json.load(file)
    
    st.subheader("Parsed Content:")
    for key, value in data.items():
        st.write(f"*{key.capitalize()}:*")
        if isinstance(value, list):
            for item in value:
                st.write(f"- {item} ")
        else:
            st.write(" ",value,".")

# Streamlit UI
def main():
    st.title("Resume Parser")

    uploaded_file = st.file_uploader("Upload a resume file", type=["docx","pdf"])

    if uploaded_file is not None:
        file_path = "uploaded_resume.docx"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File uploaded successfully!")

        # Parse the resume and save parsed content to JSON file
        parsed_json_path = "Parsed_Resume.json"
        parse_resume(file_path, parsed_json_path)

        # Display the parsed content
        display_json_content(parsed_json_path)

if _name_ == "_main_":
    main()