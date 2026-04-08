from flask import Flask, render_template, request
import PyPDF2
import os

app = Flask(__name__)

# Folder to store uploaded resumes
app.config['UPLOAD_FOLDER'] = 'uploads'

# Make sure upload folder exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# -------------------------------
# SKILLS DATABASE
# -------------------------------
skills_db = [
    "python", "java", "c++", "html", "css",
    "javascript", "machine learning"
]

# -------------------------------
# EXTRACT TEXT FROM PDF
# -------------------------------
def extract_text(filepath):
    text = ""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text()
    except Exception as e:
        print("Error reading PDF:", e)

    return text.lower()


# -------------------------------
# SKILL ANALYSIS
# -------------------------------
def analyze_resume(text):
    found_skills = []

    for skill in skills_db:
        if skill in text:
            found_skills.append(skill)

    score = 0
    if len(skills_db) > 0:
        score = (len(found_skills) / len(skills_db)) * 100

    return found_skills, round(score, 2)


# -------------------------------
# ACHIEVEMENT EXTRACTION (IMPROVED)
# -------------------------------
def extract_achievements(text):
    achievements = []
    lines = text.split('\n')

    capture = False

    for line in lines:
        line = line.strip()

        # Start capturing when "achievement" section is found
        if "achievement" in line or "achievements" in line:
            capture = True
            continue

        # Stop when new section starts
        if capture and (line.isupper() and len(line) < 30):
            break

        # Collect lines under achievements section
        if capture and line:
            achievements.append(line)

    return achievements


# -------------------------------
# ROUTES
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return "No file uploaded"

    file = request.files['resume']

    if file.filename == '':
        return "No selected file"

    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Extract text
    text = extract_text(filepath)

    # Analyze
    skills, score = analyze_resume(text)
    achievements = extract_achievements(text)

    # Debug (optional)
    print("Skills:", skills)
    print("Achievements:", achievements)

    return render_template(
        'result.html',
        skills=skills,
        score=score,
        achievements=achievements
    )


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)