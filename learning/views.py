from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from career.models import CareerProfile

from .models import LearningProgress


ROADMAPS = {
    'fresher': [
        {
            'title': 'Python Basics',
            'content': 'Learn variables, data types, conditions, loops, and functions.',
            'task': 'Write a small program that asks for a name and prints a greeting.',
        },
        {
            'title': 'Django Basics',
            'content': 'Learn how Django projects, apps, URLs, and views fit together.',
            'task': 'Create a simple view that returns a welcome page.',
        },
        {
            'title': 'SQL Basics',
            'content': 'Practice SELECT, INSERT, UPDATE, and simple table relationships.',
            'task': 'Write a query that finds all records matching a condition.',
        },
        {
            'title': 'REST APIs',
            'content': 'Understand HTTP requests, responses, status codes, and JSON.',
            'task': 'Sketch the request and response for a simple books endpoint.',
        },
        {
            'title': 'Build a Small Project',
            'content': 'Combine your skills in a small project and save it with Git.',
            'task': 'Build a small to-do list and write a README describing it.',
        },
    ],
    'experienced': [
        {
            'title': 'Review Core Concepts',
            'content': 'Refresh language fundamentals and identify one topic to deepen.',
            'task': 'Explain a core concept from your target role in your own words.',
        },
        {
            'title': 'Design an Application',
            'content': 'Practice breaking an application into clear, maintainable parts.',
            'task': 'Draw a simple design for a small application you know.',
        },
        {
            'title': 'Databases and Performance',
            'content': 'Review query design, indexes, and common performance trade-offs.',
            'task': 'Find one slow query pattern and describe how you would investigate it.',
        },
        {
            'title': 'APIs and Reliability',
            'content': 'Review API design, validation, errors, and automated tests.',
            'task': 'List tests for a create-record API endpoint.',
        },
        {
            'title': 'Portfolio Project',
            'content': 'Improve a project that demonstrates decisions and results.',
            'task': 'Document a technical decision and its trade-offs in your project.',
        },
    ],
}


def get_roadmap_type(user):
    try:
        profile = CareerProfile.objects.get(user=user)
    except CareerProfile.DoesNotExist:
        return 'fresher'

    if profile.experience_level == 'fresher':
        return 'fresher'
    return 'experienced'


@login_required
def roadmap(request):
    roadmap_type = request.GET.get(
        'track',
        get_roadmap_type(request.user)
    )
    if roadmap_type not in ROADMAPS:
        roadmap_type = get_roadmap_type(request.user)

    days = ROADMAPS[roadmap_type]
    completed_days = set(
        LearningProgress.objects.filter(
            user=request.user,
            roadmap_type=roadmap_type
        ).values_list('day_number', flat=True)
    )
    day_list = [
        {
            'number': number,
            'title': day['title'],
            'completed': number in completed_days,
        }
        for number, day in enumerate(days, start=1)
    ]

    return render(
        request,
        'learning/roadmap.html',
        {
            'roadmap_type': roadmap_type,
            'day_list': day_list,
            'completed_count': len(completed_days),
            'total_days': len(days),
        }
    )


@login_required
def day_detail(request, day_number):
    roadmap_type = request.GET.get(
        'track',
        get_roadmap_type(request.user)
    )
    if roadmap_type not in ROADMAPS:
        roadmap_type = get_roadmap_type(request.user)

    if day_number < 1 or day_number > len(ROADMAPS[roadmap_type]):
        return redirect('learning:roadmap')

    day = ROADMAPS[roadmap_type][day_number - 1]
    progress = LearningProgress.objects.filter(
        user=request.user,
        roadmap_type=roadmap_type,
        day_number=day_number
    )
    completed = progress.exists()

    if request.method == 'POST':
        if completed:
            progress.delete()
        else:
            LearningProgress.objects.create(
                user=request.user,
                roadmap_type=roadmap_type,
                day_number=day_number
            )
        return HttpResponseRedirect(
            f'{reverse("learning:day", args=[day_number])}'
            f'?track={roadmap_type}'
        )

    return render(
        request,
        'learning/day.html',
        {
            'day': day,
            'day_number': day_number,
            'roadmap_type': roadmap_type,
            'completed': completed,
        }
    )
