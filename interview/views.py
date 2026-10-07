from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from groq import GroqError

from career.models import CareerProfile
from config.groq_helper import (
    GroqConfigurationError,
    GroqResponseError,
    get_groq_response,
    parse_json_response,
)
from resumes.models import Resume


def generate_ai_questions(profile):
    system_prompt = (
        'You are generating interview questions for this candidate based on '
        'their target role, experience level, and skills. Return ONLY valid '
        'JSON with this structure: {"technical_questions": [{"question": "...", '
        '"topic": "...", "answer_tip": "..."}], "hr_questions": '
        '[{"question": "...", "answer_tip": "..."}]}. Make every question '
        'specific to the candidate profile and appropriate for their experience.'
    )
    user_prompt = (
        'Target role: {target_role}\n'
        'Current role: {current_role}\n'
        'Experience level: {experience_level} ({experience_label})\n'
        'Skills: {skills}\n\n'
        'Generate five role-specific technical questions and three role-specific '
        'HR questions. Include a concise answer_tip for each question. Do not '
        'use unrelated generic developer questions.'
    ).format(
        target_role=profile.target_role,
        current_role=profile.current_role or 'Not provided',
        experience_level=profile.experience_level,
        experience_label=profile.get_experience_level_display(),
        skills=profile.skills,
    )
    response = get_groq_response(
        system_prompt,
        user_prompt,
        json_mode=True,
    )
    result = parse_json_response(response)
    if not isinstance(result, dict):
        raise GroqResponseError('Groq returned an unexpected response structure.')
    return result


def get_practice_questions(ai_questions):
    questions = []
    for question in ai_questions.get('technical_questions', []):
        if isinstance(question, dict) and question.get('question'):
            questions.append({
                'question': question['question'],
                'topic': question.get('topic') or 'Technical',
                'answer_tip': question.get('answer_tip')
                or 'Explain your approach, relevant concepts, and an example from your experience.',
            })

    for question in ai_questions.get('hr_questions', []):
        if isinstance(question, dict) and question.get('question'):
            questions.append({
                'question': question['question'],
                'topic': 'HR',
                'answer_tip': question.get('answer_tip')
                or 'Structure your response around a specific example, your actions, and the result.',
            })
    return questions


def build_profile_questions(profile):
    role = (profile.target_role or '').strip()
    skills = [
        skill.strip()
        for skill in (profile.skills or '').split(',')
        if skill.strip()
    ]
    experience = profile.get_experience_level_display()

    if not role and not skills:
        return []

    if 'cyber' in role.lower() or 'security' in role.lower():
        return [
            'What is vulnerability scanning, and why is it important in a cybersecurity program?',
            'How is vulnerability scanning different from penetration testing?',
            'What is the purpose of ethical hacking during a security assessment?',
            'How would you prioritize vulnerabilities found during a security assessment?',
            'What is root cause analysis and how does it help after a security incident?',
        ]

    if 'data' in role.lower() or 'analyst' in role.lower():
        return [
            f'How would you explain the difference between descriptive and predictive analysis for a {role} role?',
            'How do you validate the quality of a dataset before building a report?',
            'Which SQL concepts are most important for analyzing trends and anomalies?',
            'How would you use Python or Excel to clean and summarize business data?',
            'How do you explain a key insight from a dashboard to a non-technical stakeholder?',
        ]

    if 'python' in role.lower() or 'developer' in role.lower():
        return [
            f'How would you explain the difference between a list and a tuple in a {role} project?',
            'What is the role of Django models and migrations in a web application?',
            'How do you structure a clean API response and validate input data?',
            'What trade-offs would you consider when choosing between SQL and in-memory processing?',
            'How would you debug a failing Django request that returns a 500 error?',
        ]

    questions = [
        f'Why are you interested in working as a {role}?',
        f'How would you describe your experience level as a {experience} candidate for a {role} role?',
    ]

    for skill in skills[:4]:
        questions.append(
            f'Can you describe a project or task where you used {skill} in a {role} context?'
        )

    if len(questions) < 5:
        questions.append(
            f'What would you like to improve next to become stronger in {role} roles?'
        )

    return questions[:5]


@login_required
def questions(request):
    matching_questions = []
    target_role = ''
    has_resume = Resume.objects.filter(user=request.user).exists()
    profile = None

    try:
        profile = CareerProfile.objects.get(user=request.user)
        target_role = profile.target_role
        matching_questions = build_profile_questions(profile)
    except CareerProfile.DoesNotExist:
        profile = None

    custom_questions = []
    ai_questions = {}
    ai_error = ''

    if request.method == 'POST':
        if profile is None:
            ai_error = (
                'Create your career profile before requesting interview questions.'
            )
        elif not profile.target_role or not profile.experience_level or not profile.skills:
            ai_error = (
                'Complete your target role, experience level, and skills in your '
                'career profile before requesting interview questions.'
            )
        else:
            try:
                ai_questions = generate_ai_questions(profile)
            except GroqConfigurationError:
                ai_error = (
                    'AI questions are not configured. Check the server .env file.'
                )
            except (GroqError, GroqResponseError, ValueError):
                ai_error = (
                    'Groq could not generate questions right now. Please try again.'
                )

    if profile:
        custom_questions.append(
            f'Why are you interested in working as a {profile.target_role}?'
        )
        if has_resume:
            custom_questions.append(
                'Which experience or project from your uploaded resume '
                f'best prepares you for a {profile.target_role} role?'
            )
        for skill in profile.skills.split(','):
            skill = skill.strip()
            if skill:
                custom_questions.append(
                    f'How have you used {skill} in a project or at work?'
                )

    return render(
        request,
        'interview/questions.html',
        {
            'matching_questions': matching_questions,
            'custom_questions': custom_questions,
            'target_role': target_role,
            'ai_questions': ai_questions,
            'ai_error': ai_error,
            'profile': profile,
        }
    )


@login_required
def practice(request):
    try:
        profile = CareerProfile.objects.get(user=request.user)
    except CareerProfile.DoesNotExist:
        profile = None

    questions = []
    ai_error = ''
    if profile is None:
        ai_error = 'Create your career profile before starting interview practice.'
    elif not profile.target_role or not profile.experience_level or not profile.skills:
        ai_error = (
            'Complete your target role, experience level, and skills in your '
            'career profile before starting interview practice.'
        )
    else:
        try:
            questions = get_practice_questions(generate_ai_questions(profile))
            if not questions:
                ai_error = (
                    'AI could not generate practice questions right now. Please try again.'
                )
        except GroqConfigurationError:
            ai_error = (
                'AI questions are not configured. Check the server .env file.'
            )
        except (GroqError, GroqResponseError, ValueError):
            ai_error = (
                'Groq could not generate practice questions right now. Please try again.'
            )

    return render(
        request,
        'interview/practice.html',
        {
            'profile': profile,
            'questions': questions,
            'ai_error': ai_error,
        }
    )
