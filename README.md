# ResumeAI

**ResumeAI** is a Python-based automated resume refinement system that leverages OpenAI’s GPT-4o to tailor your resume's bullet points to better align with specific job descriptions. The system uses JSON data of your job experiences and projects, refines the bullet points using AI, converts the data into LaTeX format, before compiling it into a polished PDF resume.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Data Format](#data-format)
- [Project Structure](#project-structure)

## Features

- **Automated Bullet Point Refinement:** Utilizes OpenAI's GPT-4o to enhance resume bullet points by adding relevant keywords without altering the original meaning.
- **Project Selection:** Automatically selects the top 4 most relevant projects based on the job description.
- **JSON to LaTeX Conversion:** Converts JSON data of job experiences and projects into LaTeX format for seamless resume generation. LaTeX format compatible with Jake's Resume Template
- **LaTeX Compilation:** Compiles the LaTeX files into a professional PDF resume using `pdflatex`.
- **Environment Variable Management:** Secures sensitive information like API keys using environment variables.
- **Modular Design:** Easily extendable and maintainable codebase.


## Prerequisites

- **Python 3.7+**
- **MacTeX:** Required for LaTeX compilation. Install from [MacTeX Download](https://www.tug.org/mactex/mactex-download.html).
- **OpenAI API Key:** Sign up and obtain an API key from [OpenAI](https://platform.openai.com/account/api-keys). Can also use Github AI models API as is done in this code.
- **Git:** For version control and repository management.

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/ResumeAI.git
    cd ResumeAI/Resume
    ```

2. **Create a Virtual Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install openai
    ```

## Configuration

1. **Environment Variables:**

    Create a `.env` file in the [Resume](http://_vscodecontentref_/0) directory to store your sensitive information.

    ```bash
    cd Resume
    touch .env
    ```

    Add the following to the `.env` file:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    GITHUB_TOKEN=your_github_token
    ```

    *Ensure `.env` is listed in your `.gitignore` to prevent it from being committed to GitHub.*

2. **File Paths:**

    The script uses relative paths based on the location of [resumeAI.py](http://_vscodecontentref_/1). Ensure your JSON data files and LaTeX files are placed correctly in the [Resume](http://_vscodecontentref_/2) directory.

## Usage

1. **Prepare Your Data Files:**

    - **Job Description:**
        - [job_description.txt](http://_vscodecontentref_/3): Contains the job description you are targeting.
    - **Job Experience:**
        - `job_experience.json`: JSON file containing your job experiences.
    - **Projects:**
        - `resume_projects.json`: JSON file containing your projects.

2. **Run the Script:**

    ```bash
    python resumeAI.py
    ```

3. **Follow the Prompts:**

    - The script will display the modified bullet points.
    - When prompted, enter `y` to save the updated LaTeX files.

4. **Compilation:**

    The script automatically compiles the LaTeX files into a PDF resume located in the `AG_Resume_PDF_File` directory.

## Data Format

### `job_experience.json`

This JSON file should contain an array of job experiences (must be in LaTeX format), each with the following structure:

```json
{
    "job_experience": [
        {
            "company": "Company Name",
            "role": "Your Role",
            "dates": "Start Date - End Date",
            "location": "Company Location",
            "bullet_points": [
                "Your \\textbf{first bullet point}.",
                "Your second bullet point.",
                "Your third bullet point."
            ]
        },
        {
            "company": "Another Company",
            "role": "Your Role",
            "dates": "Start Date - End Date",
            "location": "Company Location",
            "bullet_points": [
                "Your first bullet point.",
                "Your second bullet point."
            ]
        }
    ]
}
```

### `resume_projects.json`

This JSON file should contain an array of job experiences (must be in LaTeX format), each with the following structure:

```json
{
    "projects": [
        {
            "name": "Stock Price Predictor",
            "technologies": "Python, pandas, TensorFlow, Keras, LSTM, Matplotlib",
            "bullet_points": [
                "Your \\textbf{first bullet point}.",
                "Your second bullet point.",
                "Your third bullet point."
            ]
        },
        {
            "name": "ResumAI",
            "technologies": "Python, OpenAI API, JSON, LaTeX, MacTeX",
            "bullet_points": [
                "Your \\textbf{first bullet point}.",
                "Your second bullet point.",
                "Your third bullet point."
            ]
        }
    ]
}

```

## Project Structure

```
ResumeAI/ 
│ 
└── Resume/ 
    ├── .gitignore 
    ├── .env 
    ├── AG_Resume.tex 
    ├── job_description.txt 
    ├── job_experience.json 
    ├── resume_projects.json 
    ├── updated_jobs.json 
    ├── updated_projects.json 
    ├── job_bullets.tex 
    ├── project_bullets.tex 
    ├── AG_Resume_PDF_File/ 
    ├── resumeAI.py 
    └── README.md 
```

- **.gitignore:** Specifies files and directories to be ignored by Git.
- **.env:** Stores sensitive environment variables.
- **AG_Resume.tex & resume.tex:** LaTeX files for the resume.
- **JSON Files:** Contain job experiences and project details.
- **.tex Files:** Generated LaTeX files for bullet points.
- **AG_Resume_PDF_File/:** Directory where the compiled PDF resume is saved.
- **resumeAI.py:** Main Python script for processing the resume.
- **README.md:** Project documentation.
- **requirements.txt:** List of Python dependencies.





**Security Note:** Always ensure that sensitive information such as API keys and tokens are never committed to version control systems. Use environment variables and `.gitignore` to manage and protect your private data.
