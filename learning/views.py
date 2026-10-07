from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from career.models import CareerProfile


def _get_profile_skills(profile):
    if not profile or not profile.skills:
        return []
    return [skill.strip() for skill in profile.skills.split(',') if skill.strip()]


@login_required
def roadmap(request):
    try:
        profile = CareerProfile.objects.get(user=request.user)
    except CareerProfile.DoesNotExist:
        profile = None

    current_skills = _get_profile_skills(profile)
    target_role = profile.target_role if profile else 'your target role'
    current_role = profile.current_role if profile else 'Not added yet'
    experience = profile.get_experience_level_display() if profile else 'Not added yet'

    recommended_skills = current_skills[:]
    if profile and profile.target_role:
        target_lower = profile.target_role.lower()
        if 'cyber' in target_lower or 'security' in target_lower:
            recommended_skills = [
                'Vulnerability scanning',
                'Risk assessment',
                'Incident response',
                'Network security',
                'Threat modeling',
            ]
        elif 'data' in target_lower or 'analyst' in target_lower:
            recommended_skills = [
                'SQL analysis',
                'Excel reporting',
                'Python for data work',
                'Data visualization',
                'Business storytelling',
            ]
        elif 'python' in target_lower or 'developer' in target_lower:
            recommended_skills = [
                'Python testing',
                'REST APIs',
                'Django or Flask',
                'SQL queries',
                'Debugging and profiling',
            ]
        else:
            recommended_skills = [
                'Portfolio projects',
                'Communication and stakeholder feedback',
                'Role-specific technical skills',
                'Problem solving',
                'Continuous learning',
            ]

    return render(
        request,
        'learning/roadmap.html',
        {
            'profile': profile,
            'target_role': target_role,
            'current_role': current_role,
            'experience': experience,
            'current_skills': current_skills,
            'recommended_skills': recommended_skills,
        },
    )


@login_required
def day_detail(request, day_number):
    return redirect('learning:roadmap')
