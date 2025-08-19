import streamlit as st
import re
import csv
import spacy
from typing import List, Set, Dict
from fuzzywuzzy import fuzz
from resume_parser import extract_text, extract_email, extract_phone, extract_education

# --- Load a pre-trained SpaCy model for dynamic skill extraction ---
# 'en_core_web_lg' is recommended for better entity recognition, but 'en_core_web_sm'
# is a lighter alternative. You need to install it first: python -m spacy download en_core_web_lg
try:
    nlp = spacy.load('en_core_web_lg')
except OSError:
    st.warning("Downloading 'en_core_web_lg' model. This may take a moment.")
    spacy.cli.download('en_core_web_lg')
    nlp = spacy.load('en_core_web_lg')

def extract_name(text):
    ignore_keywords = ['email', 'phone', 'mobile', 'contact', 'objective', 'address', 'resume', 'curriculum vitae', 'examination', 'institute', 'year']
    lines = text.split('\n')

    for line in lines[:10]:
        line_clean = line.strip()
        if not line_clean or any(k in line_clean.lower() for k in ignore_keywords):
            continue
        words = [w for w in line_clean.split() if w.isalpha()]
        if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words):
            return ' '.join(words)
    
    for line in lines:
        line_clean = line.strip()
        if line_clean and not any(k in line_clean.lower() for k in ignore_keywords):
            return line_clean

    return "Not Found"

# --- Dynamic Skill Extraction Function using NER ---
def extract_skills_with_ner(text: str) -> list[str]:
    """
    Extracts potential skills using SpaCy's Named Entity Recognition and POS tagging.
    This function is a fallback/supplement to find unseen skills.
    """
    skills = set()
    doc = nlp(text)

    # We are looking for entities that are organizations, products, etc.
    skill_labels = ['PRODUCT', 'ORG', 'NORP', 'WORK_OF_ART', 'LANGUAGE', 'GPE']
    
    # Heuristics to filter out common false positives
    ignore_words = {'company', 'group', 'services', 'inc', 'corp', 'ltd', 'university', 'college', 'email', 'phone', 'address', 'institute', 'year', 'project', 'summary', 'experience', 'objective', 'profile', 'education'}

    for ent in doc.ents:
        if ent.label_ in skill_labels:
            entity_text = ent.text.strip()
            # Basic filtering for length and common words
            if len(entity_text) > 1 and not any(w in entity_text.lower() for w in ignore_words) and not any(char.isdigit() for char in entity_text):
                skills.add(entity_text)

    # Use part-of-speech tagging to find capitalized words that are not entities
    for token in doc:
        if token.is_title and not token.is_stop and token.text.strip().lower() not in ignore_words and token.text.strip() not in skills:
            # Simple check to see if it's a potential technical term and not a common word
            if len(token.text.strip()) > 2 and re.match(r'^[A-Z][a-zA-Z0-9+#.-]*$', token.text):
                 skills.add(token.text.strip())

    return sorted(list(skills))

# --- Main App Logic (Modified) ---

# Streamlit UI
st.title("Smart Resume Analyzer")

st.subheader("Job Description Input")
jd_option = st.radio("Choose JD input method:", ("Paste JD Text", "Upload JD PDF/TXT"))
jd_text = ""
if jd_option == "Paste JD Text":
    jd_text = st.text_area("Paste Job Description here", height=200)
elif jd_option == "Upload JD PDF/TXT":
    jd_file = st.file_uploader("Upload JD File", type=['pdf','txt'])
    if jd_file:
        jd_text = extract_text(jd_file)

st.subheader("Upload Multiple Resumes (PDF/DOCX)")
resume_files = st.file_uploader("Upload Resumes", type=['pdf','docx'], accept_multiple_files=True)

if jd_text and resume_files:
    st.success("Job Description Loaded Successfully!")
    
    # Extract skills from JD using the dynamic NER approach
    jd_skills = extract_skills_with_ner(jd_text)

    st.header("Resume Analysis Result")
    for resume in resume_files:
        resume_text = extract_text(resume)
        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        education = extract_education(resume_text)

        # Extract skills from resume using the dynamic NER approach
        resume_skills = extract_skills_with_ner(resume_text)

        matched_skills = sorted(list(set(resume_skills) & set(jd_skills)))
        extra_skills = sorted(list(set(resume_skills) - set(jd_skills)))
        missing_skills = sorted(list(set(jd_skills) - set(resume_skills)))

        match_score = round(len(matched_skills) / len(jd_skills) * 100, 2) if jd_skills else 0.0

        st.markdown(f"""
---
**Resume Name:** {name}
**Email:** {email}
**Phone:** {phone}
**Education:** {', '.join(education) if education else 'Not Found'}

**Resume Skills (Extracted Dynamically):**
- {"\n- ".join(resume_skills) if resume_skills else 'Not Found'}

**JD Skills (Extracted Dynamically):**
- {"\n- ".join(jd_skills) if jd_skills else 'Not Found'}

**Matched Skills:**
- {"\n- ".join(matched_skills) if matched_skills else 'None'}

**Extra Skills:**
- {"\n- ".join(extra_skills) if extra_skills else 'None'}

**Missing Skills:**
- {"\n- ".join(missing_skills) if missing_skills else 'None'}

**Overall Match Score:** {match_score}%
---
""")
