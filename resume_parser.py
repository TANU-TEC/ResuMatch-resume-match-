import pdfplumber
import docx
import re
import spacy

nlp = spacy.load('en_core_web_sm')

# Expanded skill dictionary for filtering
skill_keywords = [
    'Python','Java','C++','C','JavaScript','PHP','SQL','Flask','Django',
    'Machine Learning','Deep Learning','NLP','Data Science','Docker','Kubernetes',
    'Computer Vision','AI','Cybersecurity','HTML','CSS','React','Node.js',
    'Figma','Photoshop','Android','MySQL','Cloud','AWS','GCP','Azure','TensorFlow','PyTorch'
]

def extract_text(file):
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = ''.join([page.extract_text() + '\n' for page in pdf.pages])
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        text = '\n'.join([p.text for p in doc.paragraphs])
    elif file.name.endswith('.txt'):
        text = file.read()
        if isinstance(text, bytes):
            text = text.decode("utf-8")
    else:
        raise ValueError("Unsupported file type")
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    match = re.search(r'\+?\d[\d -]{8,12}\d', text)
    return match.group(0) if match else "Not Found"

def extract_education(text):
    doc = nlp(text)
    education = []
    for ent in doc.ents:
        if ent.label_ == 'ORG' or any(word in ent.text for word in ['University', 'College']):
            education.append(ent.text)
    return education

def extract_skills_filtered(text):
    text_lower = text.lower()
    # 1. Predefined skills found
    found_skills = [skill for skill in skill_keywords if skill.lower() in text_lower]
    # 2. NLP-based dynamic detection
    doc = nlp(text)
    for token in doc:
        token_text = token.text.strip()
        if token_text.lower() in [k.lower() for k in skill_keywords] and token_text not in found_skills:
            found_skills.append(token_text)
    return list(set(found_skills))
