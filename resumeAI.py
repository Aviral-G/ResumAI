import json
import os
from openai import OpenAI
import subprocess
from pathlib import Path


def store_bullet_points(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    bullet_points_by_company = {}
    for role in data["job_experience"]:
        company = role["company"]
        bullet_points_by_company[company] = role["bullet_points"]
    return bullet_points_by_company

def store_project_points(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    bullet_points_by_project = {}
    for project in data["projects"]:
        project_name = project["name"]
        bullet_points_by_project[project_name] = project["bullet_points"]
    return bullet_points_by_project

def modify_job_bullets(client, job_description, bullet_points):

    responses_by_company = {}

    for company, points in bullet_points.items():
        prompt = f"""
        Job description: {job_description}

        Original company and bullet points: {company} {points}

        Rewrite each bullet point to better align with the job description. If there are special characters denote them with a single backslash like 60\%. If something needs to be bolded indicate it as if it was to be written in LaTeX using textbf and curly braces surrounding what needs to be bold. Keep each bullet point the same number of characters it is currently. Return only the modified bullet points.
        """
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional resume editor. "
                        "Use the given job description to add relevant keywords to the bullet points without altering their original meaning or context. "
                        "Do not fabricate or exaggerate any responsibilities, achievements, or details. "
                        "Avoid rephrasing sentences; only insert keywords where appropriate. "
                        "Do not use any markdown syntax for text formatting. Do not bold the text in your response or use double asterisks. Do not end the bullet points with a period. "
                        "Ensure bullet points do not exceed 100 characters."
                    )
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model = "gpt-4o",
            temperature = 0.5,
            max_tokens = 4096,
            top_p = 0.9
        )
        multi_line_bullet_points = response.choices[0].message.content.strip()

        bullet_list = [
            line.strip("- ").strip()
            for line in multi_line_bullet_points.split("\n")
            if line.strip()
        ]
        responses_by_company[company] = bullet_list

    return responses_by_company


def choose_top_projects(client, job_description, bullet_points_by_project):
    prompt = f"""
    Job description: {job_description}

    All Projects:
    {bullet_points_by_project}

    From these, select the 4 most relevant projects. Return their names in a JSON array.
    Example: ["ProjectA", "ProjectB", "ProjectC", "ProjectD"].
    Return the names of the projects in the order of relevance and only return the JSON array, nothing else.
    """

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional resume editor that selects the top 4 most relevant projects based on the job description."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model = "gpt-4o",
        temperature = 0.5,
        max_tokens = 500,
        top_p = 0.9
    )

    return response

def modify_project_bullets(client, job_description, bullet_points):

    # pick top 3 projects
    top_projects_response = choose_top_projects(client, job_description, bullet_points)
    
    try:
        response_content = top_projects_response.choices[0].message.content.strip()
        selected_projects = json.loads(response_content)

        if not isinstance(selected_projects, list) or len(selected_projects) != 4:
            raise ValueError("API did not return a valid list of 4 projects.")
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print("Error parsing the top projects response:", e)
        return {}
    
    # Filter the bullet points to include only the selected projects
    selected_data = {k: v for k, v in bullet_points.items() if k in selected_projects}

    responses_by_project = {}
    for project, points in selected_data.items():
        prompt = f"""
        Job description: {job_description}

        Original project and bullet points: {project} {points}

        Rewrite each bullet point to better align with the job description. If there are special characters denote them with a single backslash like 60\%. If something needs to be bolded indicate it as if it was to be written in LaTeX using textbf and curly braces surrounding what needs to be bold. Keep each bullet point the same number of characters it is currently. Return only the modified bullet points.

        """
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional resume editor."
                        "Use the given job description to make minimal keyword additions or rephrasing. "
                        "Under no circumstances should you invent or falsify any responsibilities, achievements, or results. "
                        "Preserve the original meaning of the bullet point exactly, only adding minor rewording. "
                        "Do not fabricate or drastically alter the experience."
                        "Do not use any markdown syntax for text formatting. Do not bold the text in your response or use double astersisks. Do not end the bullet points with a period."
                        "Do not increase the length of each bullet. Make sure they are not longer than 100 characters."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model = "gpt-4o",
            temperature = 0.7,
            max_tokens = 4096,
            top_p = 0.9
        )
        multi_line_bullet_points = response.choices[0].message.content.strip()

        bullet_list = [
            line.strip("- ").strip()
            for line in multi_line_bullet_points.split("\n")
            if line.strip()
        ]
        responses_by_project[project] = bullet_list
        
    return responses_by_project


def update_job_json(json_file_path, updated_bullets, output_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for entry in data.get("job_experience", []):
        company = entry.get("company")
        if company in updated_bullets:
            entry["bullet_points"] = updated_bullets[company]


    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def update_project_json(json_file_path, updated_bullets, output_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # removing projects 
    data["projects"] = [p for p in data["projects"] if p["name"] in updated_bullets]

    for entry in data.get("projects", []):
        project = entry.get("name")
        if project in updated_bullets:
            entry["bullet_points"] = updated_bullets[project]


    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def read_job_description(file_path):

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # remove lines that start with '//' if there are any present
        content_lines = [line.strip() for line in lines if not line.strip().startswith('//')]
        job_description = '\n'.join(content_lines)
        
        return job_description

    except IOError as e:
        print(f"An error occurred while reading the file: {e}")
        raise


# converting the JSON to LaTeX for exporting
def job_json_to_latex(job_exp_json):
    latex_code = ""
    for exp in job_exp_json['job_experience']:
        latex_code += f"\\resumeSubheading \n"
        latex_code += f"  {{{exp['role']}}}{{{exp['dates']}}} \n"
        latex_code += f"  {{{exp['company']}}}{{{exp['location']}}} \n"
        latex_code += f"  \\resumeItemListStart \n"
        for point in exp['bullet_points']:
            latex_code += f"    \\resumeItem{{{point}}} \n"
        latex_code += f"  \\resumeItemListEnd \n"
        latex_code += f"\n"
    return latex_code

def project_json_to_latex(project_json):
    latex_code = ""  
    for project in project_json['projects']:
        latex_code += "\\resumeProjectHeading\n"
        latex_code += f"  {{\\textbf{{{project['name']}}} $|$ \\emph{{{project['technologies']}}}}}{{}}\n"
        latex_code += "  \\resumeItemListStart\n"
        for point in project["bullet_points"]:
            latex_code += f"    \\resumeItem{{{point}}}\n"
        latex_code += "  \\resumeItemListEnd\n"
        latex_code += f"\n"
    return latex_code  

def compile_latex(tex_file, output_dir):
    try:
        # pdflatex command
        subprocess.run(
            [
                "pdflatex", 
                "-interaction=nonstopmode",  # prevent stopping on errors
                "-output-directory", str(output_dir), 
                str(tex_file)
            ],
            check=True,
        )
        print(f"Compilation successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")
    except FileNotFoundError:
        print("Error: pdflatex command not found. Ensure MacTeX is installed and available in PATH.")


if __name__ == "__main__":

    github_api_key = os.environ["GITHUB_TOKEN"]
    if not github_api_key:
        raise EnvironmentError("Please set the GITHUB_TOKEN environment variable.")

    #Declaring client
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=github_api_key,
    )

    base_dir = Path(__file__).parent
    job_description_path = base_dir / "job_description.txt"
    original_job_experience = base_dir / "job_experience.json"
    original_projects = base_dir / "resume_projects.json"
    updated_job_experience = base_dir / "updated_jobs.json"
    updated_projects = base_dir / "updated_projects.json"

    bullet_points_dict = store_bullet_points(original_job_experience)

    # Printing out existing bullets -------------------------------------------
    # for company, points in bullet_points_dict.items():
    #     print(f"{company}:")
    #     for point in points:
    #         print(f"  - {point}")   
    # print("\n")

    project_points_dict = store_project_points(original_projects)
    
    # Printing out existing bullets -------------------------------------------
    # for project, points in project_points_dict.items():
    #     print(f"{project}:")
    #     for point in points:
    #         print(f"  - {point}")

    job_description = read_job_description(job_description_path)

    job_updated_bullets = modify_job_bullets(client, job_description, bullet_points_dict)

    project_updated_bullets = modify_project_bullets(client, job_description, project_points_dict)

    # Optionally, print the responses -----------------------------------------
    print("\nModified Job Bullet Points:")
    for company, modified in job_updated_bullets.items():
        print(f"{company}:")
        print(modified)
    
    print("\nModified Project Bullet Points:")
    for project, modified in project_updated_bullets.items():
        print(f"{project}:")
        print(modified)

    # write to output file
    update_job_json(original_job_experience, job_updated_bullets, updated_job_experience)
    update_project_json(original_projects, project_updated_bullets, updated_projects)


    # Load the JSON data from the file
    with open(updated_job_experience, 'r') as file:
        job_exp_json = json.load(file)
    with open(updated_projects, 'r') as file:
        project_json = json.load(file)

    # Convert the JSON data to LaTeX code
    job_latex_code = job_json_to_latex(job_exp_json)
    project_latex_code = project_json_to_latex(project_json)

    # Print the LaTeX code
    print(job_latex_code)
    print(project_latex_code)

    if(input("Do you want to save the updated files? (y/n): ") == 'y'):

        with open(base_dir / 'job_bullets.tex', 'w') as file:
            file.write(job_latex_code)
        with open(base_dir / 'project_bullets.tex', 'w') as file:
            file.write(project_latex_code)
        print("Files saved successfully.")
    else:
        print("Files not saved.")
        
    # compiling th LaTeX files:
    main_tex_file = Path(base_dir / "AG_Resume.tex")  
    output_dir = Path(base_dir / "AG_Resume_PDF_File")  
    # check if output directory exists
    output_dir.mkdir(exist_ok=True)

    # compile the LaTeX file
    if main_tex_file.exists():
        compile_latex(main_tex_file, output_dir)
    else:
        print(f"Error: {main_tex_file} does not exist.")