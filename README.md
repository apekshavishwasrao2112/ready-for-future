# Ready for Future

**Ready for Future – Tech Career** is a Django web application for exploring career direction, developing role-relevant skills, and preparing for interviews. Users can create a career profile, upload a PDF resume, and request AI feedback based on the text extracted from that PDF.

## Project Overview

The project is built as a beginner-friendly Django application. It demonstrates the flow between Django apps, URLs, views, forms, models, templates, the database, and static/media files. Groq-backed features run through Django on the server; the browser never receives the API key.

## Main Features

- Register, log in, and log out using Django authentication and sessions.
- Create and edit a career profile with current role, experience level, target role, and skills.
- View a dashboard with profile-based career ideas and optional AI career recommendations.
- Upload PDF resumes, see a personal resume list, and download only your own files.
- Extract actual text from an uploaded PDF with PyMuPDF and request structured AI resume feedback.
- View skill-development recommendations informed by the signed-in user's career profile and target role.
- Generate structured, role-specific technical and HR interview questions with Groq using the signed-in user's CareerProfile.
- Start Practice to generate role-specific questions through the same AI question flow used by the Interview page.
- Write answers in practice mode, view a live word count, and reveal an answer tip for each generated question.

## Technologies

| Technology | Use |
|---|---|
| Python and Django | Server-side application, URL routing, views, forms, models, and templates |
| SQLite | Local development database |
| Django ORM and migrations | Database queries and schema changes |
| Django authentication | Registration, login, logout, and protected pages |
| Groq Python SDK | Server-side AI requests |
| PyMuPDF | Extracting text from uploaded PDF resumes |
| python-dotenv | Loading local environment variables from `.env` |
| HTML, CSS, and JavaScript | Templates, page styling, and small browser interactions |

The installed project environment was checked with Django 6.1.1 and Python 3.14.6. `requirements.txt` currently lists `groq`, `python-dotenv`, and `PyMuPDF`; install Django separately as shown in the setup instructions.

## Django Concepts Demonstrated

- **MVT (Model-View-Template):** models represent stored data, views handle requests and prepare data, and templates render pages.
- **URLs and views:** app URL configurations connect page paths to view functions.
- **Models and ORM:** `CareerProfile` and `Resume` support the active profile and resume workflows. `LearningProgress` and `InterviewQuestion` remain in the existing database schema; the former five-day learning roadmap and seeded interview bank are not used by the current Learning or Interview pages.
- **Forms and ModelForms:** Django’s built-in authentication forms handle registration and login; `CareerProfileForm` and `ResumeForm` map submitted form data to models.
- **Templates:** Django templates render pages and insert data supplied by views.
- **Authentication:** Django sessions and `login_required` protect profile, dashboard, resume, learning, and interview pages.
- **Static and media files:** CSS and JavaScript are served from `static/`; uploaded PDF files are stored in `media/`.
- **File uploads:** a `FileField` stores each user’s PDF under `media/resumes/`.
- **Migrations:** migration files create and update database tables. An existing migration seeds legacy interview question records, which are not the source for current Interview or Practice questions.

## Project Structure

```text
ready-for-future/
├── manage.py
├── requirements.txt
├── .gitignore
├── .env.example
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── groq_helper.py
├── accounts/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── career/
│   ├── migrations/
│   │   └── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── resumes/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_resume_resume_file.py
│   │   ├── 0003_alter_resume_resume_file.py
│   │   └── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── learning/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── interview/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_add_sample_questions.py
│   │   └── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── accounts/
│   │   ├── login.html
│   │   └── register.html
│   ├── career/
│   │   ├── dashboard.html
│   │   └── profile.html
│   ├── resumes/
│   │   ├── list.html
│   │   ├── result.html
│   │   └── upload.html
│   ├── learning/
│   │   ├── day.html (legacy template; no active day route)
│   │   └── roadmap.html
│   └── interview/
│       ├── practice.html
│       └── questions.html
├── static/
│   ├── css/
│   │   ├── auth.css
│   │   ├── dashboard.css
│   │   ├── interview.css
│   │   ├── learning.css
│   │   ├── navbar.css
│   │   ├── resume.css
│   │   └── style.css
│   └── js/
│       ├── dashboard.js
│       ├── interview.js
│       ├── learning.js
│       ├── main.js
│       └── resume.js
└── media/
    └── resumes/
```

Local-only files and folders, including `.env`, `db.sqlite3`, `media/`, and the virtual environment, are excluded by `.gitignore`. `.env.example` is the safe template for setting up a local environment file.

## Main Application Workflow

```text
Browser
  → Django URL
  → View
  → Form (when data is submitted)
  → Model / ORM
  → SQLite or media storage
  → View
  → Template
  → Browser
```

### Authentication Workflow

Registration uses Django’s `UserCreationForm` and signs the new user in. Login uses Django’s `AuthenticationForm` and session authentication. After authentication, `login_required` protects private application pages. Logging out clears the Django session and redirects to the home page.

### Career Profile Workflow

The signed-in user opens the profile page and submits `CareerProfileForm`. The view saves or updates the user’s `CareerProfile` through the ORM, then redirects to the dashboard. The dashboard uses profile fields for local career suggestions and can submit a separate request for Groq-generated career recommendations.

### Learning Workflow

The Learning page retrieves the signed-in user's `CareerProfile` and displays current skills and suggested skills based on the target role. It is a skill-development recommendations page; it does not provide the former fixed five-day roadmap, day links, or completion tracking.

### Resume Upload Workflow

The signed-in user uploads a PDF through `ResumeForm`. Django validates its file extension, associates the `Resume` record with the current user, stores the file under `media/resumes/`, and redirects to its review page. Resume list, review, and download views restrict records to their owner.

### AI Resume Review Workflow

The AI review analyzes the **actual text extracted from the uploaded PDF**:

```text
User uploads PDF
  → Django stores PDF
  → PyMuPDF extracts text
  → Extracted resume text + optional career context
  → Groq API
  → Structured JSON
  → Django parses response
  → Feedback displayed in HTML
```

Optional context is limited to target role, current role, and experience level. Profile skills are not used as a replacement for the resume text. The extracted text is limited to 12,000 characters before the request; PDFs larger than 10 MB are rejected for review. Scanned PDFs without extractable text are not processed.

Groq returns four fields: `overall_feedback`, `strengths`, `areas_to_improve`, and `recommended_actions`. Django validates and parses this JSON before passing each field to the result template. Invalid JSON produces a user-friendly error instead of displaying raw JSON.

### Interview and Practice Workflow

Both the Interview page's **Generate AI Questions** action and **Start Practice** use the signed-in user's `CareerProfile`. Django sends these profile fields to Groq:

- Target role
- Current role
- Experience level
- Skills

Groq is asked for structured JSON containing `technical_questions` (each with a question and topic) and `hr_questions` (each with a question). The practice flow uses the same question-generation function as the Interview page and also requests an answer tip for each question.

```text
User Profile
  ↓
CareerProfile
  ↓
Target Role + Current Role + Experience + Skills
  ↓
Groq AI
  ↓
Structured Interview Questions
  ↓
Interview Page
  ↓
Start Practice
  ↓
Role-Specific Practice Questions
```

Practice mode renders each generated question with a text area for the user's answer, a live word count, and a button to reveal its answer tip. Answers are not saved. The old fixed Django/HR/JavaScript/Python/SQL question list is not used by either the Interview page or Start Practice.

## Groq and API Key Security

- The Groq key belongs in the local `.env` file as `GROQ_API_KEY=your_key`.
- `.env` is listed in `.gitignore`; do not commit it or paste a real key into source code.
- `.env.example` contains only a placeholder and can be copied to create a local `.env`.
- Django loads the variable on the server and `config/groq_helper.py` uses it for Groq API calls.
- The key is not included in HTML, templates, JavaScript, or browser requests.
- Resume text and optional career context are sent to Groq only when the user requests AI review. Avoid submitting information you do not want processed by the external API provider.

## Database

The project uses SQLite for local development, configured in `config/settings.py`. Models are stored and queried with Django’s ORM. Migration files are kept in each app’s `migrations/` folder and applied with `migrate`.

Application models:

- `CareerProfile` in `career`
- `Resume` in `resumes`
- `LearningProgress` in `learning` (legacy roadmap data; not used by the current Learning page)
- `InterviewQuestion` in `interview` (legacy seeded records; not used as the current Interview or Practice question source)

Django’s built-in authentication and administration apps also create their own tables.

## Installation and Setup

### 1. Clone the repository

Replace `<repository-url>` with the repository URL:

```powershell
git clone <repository-url>
cd ready-for-future
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, run the commands with the virtual environment’s Python executable directly, for example `.venv\Scripts\python.exe`.

### 3. Install dependencies

```powershell
python -m pip install Django
python -m pip install -r requirements.txt
```

`Django` is installed separately because it is used by the project but is not currently listed in `requirements.txt`.

### 4. Configure the environment

```powershell
Copy-Item .env.example .env
```

Open `.env` locally and replace the placeholder with your Groq API key. Never commit `.env` or share its contents.

### 5. Apply migrations

```powershell
python manage.py migrate
```

The repository includes migration files for application models. The legacy migration that seeded interview questions remains in the project, but current Interview and Practice questions are generated from the user's profile.

### 6. Start the development server

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser.

## Important Routes

| Route | Purpose | Sign-in required |
|---|---|---|
| `/` | Home page | No |
| `/accounts/register/` | Create an account | No |
| `/accounts/login/` | Sign in | No |
| `/accounts/logout/` | Sign out | No |
| `/profile/` | Create or edit career profile | Yes |
| `/dashboard/` | Career dashboard and AI recommendations | Yes |
| `/resumes/` | Resume list | Yes |
| `/resumes/list/` | Resume list (alternate route) | Yes |
| `/resumes/upload/` | Upload a PDF | Yes |
| `/resumes/<resume_id>/` | Review a resume and request AI feedback | Yes |
| `/resumes/<resume_id>/file/` | Download an owned resume | Yes |
| `/learning/` | View profile-informed skill-development recommendations | Yes |
| `/interview/` | View profile-aligned prompts and request AI-generated technical and HR questions | Yes |
| `/interview/practice/` | Generate and practice role-specific questions with answers, word counts, and answer tips | Yes |
| `/admin/` | Django admin | Staff account |

## How to Use the Application

1. Register, then sign in.
2. Create a career profile with your current role, experience, target role, and skills.
3. Use the dashboard to view career ideas or request AI recommendations.
4. Upload a PDF from the Resume section. Open its review page and select **Get AI Feedback** to analyze the PDF’s extracted text.
5. Open Learning to review profile-informed skill recommendations for your target role.
6. Open Interview and select **Generate AI Questions** to receive structured technical and HR questions based on your CareerProfile.
7. Select **Start Practice** to generate role-specific questions through the same AI question flow. Type answers, check the word count, and reveal answer tips. Answers are not saved.

## Testing and Verification

The current project state was verified with:

| Check | Result |
|---|---|
| `python manage.py check` | Passed; no system issues |
| `python manage.py test interview.tests` | Passed; 5 interview tests, including role-specific practice generation and profile data passed to Groq |
| `python manage.py test` | 14 of 17 tests passed; 3 legacy Learning tests still expect the removed fixed roadmap and day URL |

## Current Limitations

- Resume review only accepts PDF files. It does not run OCR, so scanned PDFs without selectable text cannot be reviewed.
- Resume extraction is limited to 10 MB files and 12,000 characters of extracted text.
- Groq features require a valid API key, internet access, and an available model.
- AI-generated feedback and recommendations can be imperfect; users should review them critically.
- Learning skill suggestions are based on profile details; the page does not include a scheduled roadmap or completion tracker.
- Practice answers are not saved or automatically evaluated.
- Interview and Practice question generation requires a valid Groq API key, internet access, and an available model.
- The current Django settings are for local development, not production deployment.

## Future Improvements

- Add OCR support for scanned resumes and clearly report extraction coverage.
- Allow users to edit, replace, or remove their uploaded resumes.
- Let users save interview practice answers and track learning history in more detail.
- Add broader tests for browser interactions and API error scenarios.
- Prepare production settings, including environment-managed Django secrets, host configuration, and production static/media storage.

## What I Learned

- How Django apps, URLs, views, models, templates, and forms work together.
- How the ORM and migrations connect Python models to SQLite tables.
- How Django session authentication protects private pages.
- How to receive and store files using a `ModelForm` and `FileField`.
- How to extract text from a PDF with PyMuPDF.
- How a Django server can call an external API without exposing its key to the browser.
- How to request structured JSON, validate it in Python, and render its fields in a template.

## Project Explanation

Ready for Future is a Django career-preparation application. A user creates a career profile to view target-role-informed skill recommendations and generate interview questions based on target role, current role, experience level, and skills. The Interview page and Start Practice share the same Groq question-generation flow. Practice mode provides answer text areas, live word counts, and answer tips; practice answers are not saved. Users can also upload a PDF resume. For resume feedback, Django stores the PDF, PyMuPDF extracts its text, and Django sends that text with optional career context to Groq. Groq returns structured JSON, which Django validates and displays as overall feedback, strengths, improvement areas, and recommended actions.

## Developed By

**Apeksha Vishwasrao**  
Python Full Stack Developer | AI-Powered Web Applications

- LinkedIn: [linkedin.com/in/apeksha-vishwasrao-10a5a1343](https://www.linkedin.com/in/apeksha-vishwasrao-10a5a1343/)
- GitHub: [github.com/apekshavishwasrao2112](https://github.com/apekshavishwasrao2112)
