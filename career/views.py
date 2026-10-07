from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from groq import GroqError

from config.groq_helper import (
    GroqConfigurationError,
    GroqResponseError,
    get_groq_response,
    parse_json_response,
)
from .forms import CareerProfileForm
from .models import CareerProfile


def get_career_recommendations(skills):
    skill_names = {
        skill.strip().lower()
        for skill in skills.split(',')
        if skill.strip()
    }
    recommendations = []

    if {'python', 'django', 'sql'} <= skill_names:
        recommendations.extend([
            'Python Developer',
            'Django Developer',
            'Backend Developer',
        ])
    elif 'python' in skill_names and 'sql' in skill_names:
        recommendations.extend([
            'Python Developer',
            'Data Analyst',
        ])

    if {'html', 'css', 'javascript'} <= skill_names:
        recommendations.append('Frontend Developer')

    return recommendations or [
        'Keep adding skills to your profile for career suggestions.'
    ]


def home(request):

    return render(
        request,
        'home.html'
    )


@login_required
def profile(request):

    try:
        profile = CareerProfile.objects.get(
            user=request.user
        )

    except CareerProfile.DoesNotExist:
        profile = None


    if request.method == 'POST':

        form = CareerProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            career_profile = form.save(
                commit=False
            )

            career_profile.user = request.user

            career_profile.save()

            return redirect(
                'career:dashboard'
            )

    else:

        form = CareerProfileForm(
            instance=profile
        )


    return render(
        request,
        'career/profile.html',
        {
            'form': form
        }
    )


@login_required
def dashboard(request):

    try:

        profile = CareerProfile.objects.get(
            user=request.user
        )

    except CareerProfile.DoesNotExist:

        return redirect(
            'career:profile'
        )

    career_ai_recommendations = {}
    career_ai_error = ''

    if request.method == 'POST':
        if not all(
            [
                profile.target_role,
                profile.experience_level,
                profile.skills,
            ]
        ):
            career_ai_error = (
                'Please complete your profile before generating AI career '
                'recommendations.'
            )
        else:
            system_prompt = (
                'You are a practical career coach. Return ONLY valid JSON. '
                'Use the profile fields as data and recommend realistic career '
                'directions and skill improvements. Return this structure: '
                '{"career_directions": [{"title": "...", "why_it_fits": "...", '
                '"skills_to_improve": ["..."]}], "key_skills_to_improve": ["..."]}'
            )
            user_prompt = (
                'Target role: {target_role}\n'
                'Current role: {current_role}\n'
                'Experience level: {experience_level} ({experience_label})\n'
                'Skills: {skills}\n\n'
                'Suggest realistic career directions for this user and explain '
                'which skills they should improve next.'
            ).format(
                target_role=profile.target_role,
                current_role=profile.current_role or 'Not provided',
                experience_level=profile.experience_level,
                experience_label=profile.get_experience_level_display(),
                skills=profile.skills,
            )

            try:
                ai_response = get_groq_response(
                    system_prompt,
                    user_prompt,
                    json_mode=True,
                )
                career_ai_recommendations = parse_json_response(ai_response)
            except GroqConfigurationError:
                career_ai_error = (
                    'AI recommendations are not configured. Check the server .env file.'
                )
            except (GroqError, GroqResponseError, ValueError):
                career_ai_error = (
                    'Groq could not generate recommendations right now. Please try again.'
                )

    return render(
        request,
        'career/dashboard.html',
        {
            'profile': profile,
            'career_recommendations': get_career_recommendations(
                profile.skills
            ),
            'career_ai_recommendations': career_ai_recommendations,
            'career_ai_error': career_ai_error,
        }
    )