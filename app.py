import streamlit as st
import re
import csv
from typing import List, Set, Dict
from resume_parser import extract_text, extract_email, extract_phone
from fuzzywuzzy import fuzz

# Load skills from CSV
def load_skills_from_csv(file_path='data/newSkills.csv'):
    skills = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                skills.add(row[0].strip().title())
    return skills

ALL_SKILLS = load_skills_from_csv()
# Load majors from CSV
# ----------------------------
def load_majors(file_path='data/majors.csv'):
    majors = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                majors.add(row[0].strip())
    return majors

MAJORS = load_majors()

# Utility functions
# def extract_education(text):
#     edu_patterns = r"(B\.?Tech|M\.?Tech|Bachelor|Master|University|College|Institute|Certification|Certified)"
#     matches = re.findall(edu_patterns, text, re.IGNORECASE)
#     return sorted(list(set([m.title() for m in matches]))) if matches else ["Not Found"]

    # Find the start of the next section to define the end of the education block
def extract_education(text: str) -> List[str]:
    """
    Extracts the full education section from a resume using a two-pass approach.

    1. It first looks for a section heading to capture the full education block.
    2. If no heading is found, it performs a second pass to look for
       specific educational keywords and captures the entire line of text
       for each match.

    Args:
        text (str): The full text of the resume.

    Returns:
        List[str]: A list containing a single string of the full education
                   section.
    """
    education_info = []
    text_lower = text.lower()
    
    # Define common education headings to find the correct section
    education_headings = [
        'education', 'academic experience', 'qualifications', 
        'professional certifications', 'academic background', 'academics'
    ]
    
    # Define common section headers to mark the end of the education section
    end_of_section_headers = [
        'skills', 'experience', 'projects', 'work history', 
        'professional summary', 'awards'
    ]
    
    # --- Pass 1: Find a section based on headings ---
    education_start_index = -1
    for heading in education_headings:
        heading_pattern = re.compile(r'\b' + re.escape(heading) + r'\b', re.IGNORECASE)
        match = heading_pattern.search(text_lower)
        if match:
            education_start_index = match.end()
            break
            
    if education_start_index != -1:
        # Get the text after the education header
        education_text = text[education_start_index:]
        
        # Find the start of the next section to define the end of the education block
        education_end_index = len(education_text)
        for end_heading in end_of_section_headers:
            end_heading_pattern = re.compile(r'\b' + re.escape(end_heading) + r'\b', re.IGNORECASE)
            match = end_heading_pattern.search(education_text)
            if match and match.start() < education_end_index:
                education_end_index = match.start()
                
        # Extract the full education block and clean up any extra whitespace
        full_education_block = education_text[:education_end_index].strip()
        
        return [full_education_block] if full_education_block else ["Not Found"]

    # --- Pass 2: Fallback for unstructured resumes ---
    # If no section heading was found, search the whole text for education keywords
    education_keywords = [
        'b.tech', 'bachelor', 'master', 'secondary', 'diploma', 'phd'
    ]
    
    found_lines = set()
    
    # Split the entire text into lines to process each line individually
    lines = text.split('\n')
    for line in lines:
        for keyword in education_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', line, re.IGNORECASE):
                # We found a match, add the entire line to our set of found entries
                found_lines.add(line.strip())
                # Break the inner loop since we found a keyword in this line
                break

    if found_lines:
        # Sort the lines for consistent output and return them as a list of strings
        return sorted(list(found_lines))
    
    return ["Not Found"]
    
            
            
# def extract_education_with_majors(text, majors=MAJORS):
#     ignore_keywords = ['email', 'phone', 'mobile', 'resume', 'project', 'github', 'linkedin', 'portfolio']
#     education_lines = []
#     lines = text.split('\n')

#     for line in lines:
#         clean_line = line.strip()
#         if not clean_line:
#             continue

#         # skip lines with ignored keywords
#         if any(kw.lower() in clean_line.lower() for kw in ignore_keywords):
#             continue

#         # Remove emails and phone numbers
#         clean_line = re.sub(r'\S+@\S+', '', clean_line)
#         clean_line = re.sub(r'\+?\d[\d\s.-]{7,}', '', clean_line)

#         normalized_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line).lower()

#         # Include line if any major exists in it
#         if any(major.lower() in normalized_line for major in majors):
#             education_lines.append(clean_line)

#     return education_lines if education_lines else ["Not Found"]

def extract_name(text):
    ignore_keywords = ['email', 'phone', 'mobile', 'contact', 'objective', 'address', 'resume', 'curriculum vitae', 'examination', 'institute', 'year']
    lines = text.split('\n')

    # Try first 10 lines first
    for line in lines[:10]:
        line_clean = line.strip()
        if not line_clean or any(k in line_clean.lower() for k in ignore_keywords):
            continue
        words = [w for w in line_clean.split() if w.isalpha()]
        if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words):
            return ' '.join(words)

    # Fallback: first non-empty line
    for line in lines:
        line_clean = line.strip()
        if line_clean and not any(k in line_clean.lower() for k in ignore_keywords):
            return line_clean

    return "Not Found"
def extract_skills_from_resume(resume_text, skill_set):
    # Replace unwanted chars but keep +, # for skills like C++, C#
    text_clean = re.sub(r'[^a-zA-Z0-9+.#\s]', ' ', resume_text)
    # Split words carefully
    words = [w.strip(' ,;:.') for w in text_clean.split()]
    words_lower = {w.lower() for w in words}
    text_lower = text_clean.lower()

    found_skills = set()

    for skill in skill_set:
        skill_clean = skill.strip()
        skill_lower = skill_clean.lower()

        if len(skill_clean) <= 2 or '+' in skill_clean or '#' in skill_clean:
            # Exact match for short/symbol skills
            if skill_lower in words_lower:
                found_skills.add(skill_clean)
        else:
            # Multi-word skill: exact match anywhere OR fuzzy match
            if skill_lower in text_lower:
                found_skills.add(skill_clean)
            else:
                for word in words_lower:
                    if fuzz.ratio(skill_lower, word) >= 90:
                        found_skills.add(skill_clean)
                        break
    return sorted(found_skills)

def extract_jd_skills(jd_text, skill_set):
    
   # Extracts skills from JD text using the curated skill list (ALL_SKILLS)
    
    jd_text_clean = re.sub(r'[^a-zA-Z0-9+.#\s]', ' ', jd_text)
    jd_text_lower = jd_text_clean.lower()
    
    jd_skills_found = set()
    for skill in skill_set:
        if skill.lower() in jd_text_lower:
            jd_skills_found.add(skill)
    return sorted(jd_skills_found)

    

def extract_dynamic_skills(text, skill_set=None, threshold=85):
    ignore_words = set([
        "job", "description", "summary", "title", "responsibilities", "skills",
        "required", "preferred", "location", "key", "knowledge", "experience",
        "education", "stay", "we", "perform", "the", "our", "and", "or", "for",
        "with", "of", "a", "in", "to", "on", "by", "at", "any", "anywhere",
        "strong", "good", "solid", "document", "background", "field"
    ])
    
    skills_found = set()
    text_clean = re.sub(r'[^a-zA-Z0-9+&.\s]', ' ', text)
    words = set(re.findall(r'\b\w[\w+#]*\b', text_clean))  # full words only
    words_lower = {w.lower() for w in words}

    if skill_set:
        for skill in skill_set:
            skill_lower = skill.lower()
            skill_words = skill.strip().split()
            
            # Single-word skills -> exact match only
            if len(skill_words) == 1:
                if skill_lower in words_lower:
                    skills_found.add(skill)
            else:
                # Multi-word skills -> exact or fuzzy match
                if skill_lower in text_clean.lower():
                    skills_found.add(skill)
                else:
                    for w in words_lower:
                        if w not in ignore_words and fuzz.ratio(skill_lower, w) >= threshold:
                            skills_found.add(skill)
                            break

    # Add capitalized dynamic skills from text (optional)
    for ds in re.findall(r'\b[A-Z][a-zA-Z0-9+\-\.]*\b', text):
        ds_clean = ds.strip()
        if ds_clean not in skills_found and (len(ds_clean) > 1 or ds_clean in ['C', 'R', 'AI']):
            skills_found.add(ds_clean)

    return sorted(list({s.strip().title() for s in skills_found}))

def normalize_skills(skills_list):
    return sorted(list({skill.strip().title() for skill in skills_list if skill.strip()}))

# Streamlit UI
st.title("** Smart Resume Analyzer** ")

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
    # jd_skills = normalize_skills(extract_dynamic_skills(jd_text, ALL_SKILLS))
    jd_skills = extract_jd_skills(jd_text, ALL_SKILLS)


    st.header(" **Resume Analysis Result**")
    for resume in resume_files:
        resume_text = extract_text(resume)
        name = extract_name(resume_text)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        education = extract_education(resume_text)
        resume_skills = normalize_skills(extract_skills_from_resume(resume_text, ALL_SKILLS))

        matched_skills = normalize_skills(list(set(resume_skills) & set(jd_skills)))
        extra_skills = normalize_skills(list(set(resume_skills) - set(jd_skills)))
        missing_skills = normalize_skills(list(set(jd_skills) - set(resume_skills)))
        match_score = round(len(matched_skills)/len(jd_skills)*100, 2) if jd_skills else 0.0

        st.markdown(f"""
**Resume Name:** {name}  
**Email:** {email}  
**Phone:** {phone}  
**Education:** {', '.join(education) if education else 'Not Found'}  

**Resume Skills:**  
- {"\n- ".join(resume_skills) if resume_skills else 'Not Found'}  

**JD Skills:**  
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
