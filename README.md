# **Smart Resume Analyzer**

The Smart Resume Analyzer is a Python-based web application built with Streamlit that helps recruiters and hiring managers efficiently screen resumes. It automatically parses resumes and job descriptions to extract key information, identify skills, and generate a compatibility score.

### Features

* **Resume Parsing:** Extracts name, email, phone number, and education details from PDF and DOCX files.
* **Skill Matching:** Compares skills from a resume against those in a job description.
* **Compatibility Score:** Calculates a match score to quickly identify the best candidates.
* **Unstructured Data Handling:** Robustly extracts education information even without a dedicated "Education" section header.
* **Multiple File Support:** Allows for uploading and analyzing multiple resumes at once.

### Prerequisites

Before you begin, ensure you have the following installed on your system:

* Python 3.7 or higher
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```
    git clone <your-repository-url>
    cd smart-resume-analyzer
    ```
2.  **Create a virtual environment (recommended):**
    ```
    python -m venv venv
    ```
    * On Windows: `venv\Scripts\activate`
    * On macOS/Linux: `source venv/bin/activate`
3.  **Install the required packages:**
    ```
    pip install -r requirements.txt
    ```
    You can generate the `requirements.txt` file from the following list of libraries:
    * `streamlit`
    * `fuzzywuzzy`
    * `python-docx`
    * `pdfplumber`
    * `spacy`
    * `python-Levenshtein`
    Make sure you also download the necessary SpaCy model by running:
    ```
    python -m spacy download en_core_web_sm
    ```

### Usage

1.  **Run the application:**
    ```
    streamlit run app.py
    ```
    This command will launch the application in your default web browser.
2.  **Use the UI:**
    * Paste the job description text or upload a job description file.
    * Upload one or more resume files (PDF, DOCX).
    * The app will automatically display the parsed information, skill matches, and the overall score for each resume.

### File Structure

smart-resume-analyzer/
├── data/
│   ├── majors.csv
│   └── newSkills.csv
├── resume_parser.py
├── app.py
├── requirements.txt
└── README.md