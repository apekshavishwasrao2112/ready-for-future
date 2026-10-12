from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from career.models import CareerProfile
from .models import CareerTaskProgress


SKILLS = [
    {
        'key': 'developer-python-problem-solving',
        'title': 'Python problem-solving',
        'aliases': ['python problem-solving', 'data structures', 'algorithms'],
        'description': 'Practice clear solutions with Python collections, iteration, and edge cases.',
        'why': 'Core problem-solving helps you implement and explain backend features.',
        'focus': 'Practice lists, dictionaries, sets, iteration, and breaking a problem into smaller steps.',
        'practice': 'Write a function that groups words by their first letter, then test empty input and repeated words.',
    },
    {
        'key': 'developer-django-advanced',
        'title': 'Django and ORM',
        'aliases': ['django orm', 'django querysets', 'django permissions'],
        'description': 'Build on Django basics with querysets, relationships, and user-aware data access.',
        'why': 'Real Django work relies on reliable database queries and access control.',
        'focus': 'Review model relationships, queryset filtering, validation, and object-level permissions.',
        'practice': 'Add a private reading-list view where each signed-in user can change only their own entries.',
    },
    {
        'key': 'developer-rest-api-design',
        'title': 'REST APIs',
        'aliases': ['rest api', 'rest apis', 'restful api', 'django rest framework'],
        'description': 'Design predictable HTTP endpoints that exchange validated JSON data.',
        'why': 'APIs connect backend features to browsers and other services.',
        'focus': 'Learn HTTP methods and status codes, JSON responses, input validation, and useful error messages.',
        'practice': 'Build a Django JSON endpoint to create and list a user-owned learning goal with blank-title validation.',
    },
    {
        'key': 'developer-sql-querying',
        'title': 'SQL and databases',
        'aliases': ['sql joins', 'sql queries', 'query optimization', 'database indexing'],
        'description': 'Query related data accurately and understand how query choices affect performance.',
        'why': 'Backend features depend on correct access to related records as data grows.',
        'focus': 'Practice filtering, joins, aggregation, grouping, NULL handling, and indexes.',
        'practice': 'Query users and projects for each user’s project count and most recently updated project.',
    },
    {
        'key': 'developer-testing-debugging',
        'title': 'Testing and debugging',
        'aliases': ['python testing', 'pytest', 'unit testing', 'django test client'],
        'description': 'Use tests and debugging tools to catch regressions and explain failures.',
        'why': 'Reliable tests make code safer to change and easier to review.',
        'focus': 'Practice arrange-act-assert tests, edge cases, Django test clients, and traceback diagnosis.',
        'practice': 'Test an existing Django form with valid data, missing required data, and an invalid choice.',
    },
    {
        'key': 'developer-delivery-basics',
        'title': 'Git and deployment',
        'aliases': ['github actions', 'deployment', 'continuous integration', 'ci cd'],
        'description': 'Track changes, automate checks, and document a repeatable deployment.',
        'why': 'A documented deployment shows how you deliver and maintain working software.',
        'focus': 'Review branches, small commits, environment variables, deployment settings, and basic CI.',
        'practice': 'Push a small Django project to GitHub, run its tests in CI, deploy it, and document the setup.',
    },
]

PRACTICE_TASKS = [
    ('developer-build-api', 'Build a small Django REST API'),
    ('developer-write-tests', 'Write tests for a Python or Django feature'),
    ('developer-practice-sql', 'Practice SQL queries'),
    ('developer-debug-error', 'Debug an intentional error'),
    ('developer-push-github', 'Push a project to GitHub'),
    ('developer-deploy-project', 'Deploy a project and document the process'),
]


def _task_totals(user, task_keys):
    statuses = dict(
        CareerTaskProgress.objects.filter(
            user=user,
            task_key__in=task_keys,
        ).values_list('task_key', 'status')
    )
    completed = sum(
        status == CareerTaskProgress.COMPLETED
        for status in statuses.values()
    )
    total = len(task_keys)
    return statuses, {
        'completed': completed,
        'total': total,
        'percentage': completed * 100 // total if total else 0,
    }


@login_required
def roadmap(request):
    try:
        profile = CareerProfile.objects.get(user=request.user)
    except CareerProfile.DoesNotExist:
        profile = None

    skills = [dict(skill) for skill in SKILLS]
    readiness_tasks = [
        {'key': key, 'title': title}
        for key, title in PRACTICE_TASKS
    ]
    task_keys = [
        skill['key'] for skill in skills
    ] + [task['key'] for task in readiness_tasks]

    if profile:
        statuses, totals = _task_totals(request.user, task_keys)
        for skill in skills:
            skill['status'] = statuses.get(
                skill['key'],
                'recommended',
            )
            skill['completed'] = (
                skill['status'] == CareerTaskProgress.COMPLETED
            )
            skill['in_progress'] = (
                skill['status'] == CareerTaskProgress.IN_PROGRESS
            )

        for task in readiness_tasks:
            task['completed'] = (
                statuses.get(task['key']) == CareerTaskProgress.COMPLETED
            )

        next_skill = next(
            (skill for skill in skills if skill['in_progress']),
            None,
        )
        if next_skill is None:
            profile_skills = {
                item.strip().casefold()
                for item in profile.skills.split(',')
                if item.strip()
            }
            next_skill = next(
                (
                    skill for skill in skills
                    if not skill['completed']
                    and not profile_skills.intersection(skill['aliases'])
                ),
                None,
            )
        if next_skill is None:
            next_skill = next(
                (skill for skill in skills if not skill['completed']),
                None,
            )
        experience = profile.get_experience_level_display()
    else:
        totals = {'completed': 0, 'total': 0, 'percentage': 0}
        next_skill = None
        experience = 'Not added yet'

    return render(
        request,
        'learning/roadmap.html',
        {
            'profile': profile,
            'experience': experience,
            'skills': skills,
            'next_skill': next_skill,
            'readiness_tasks': readiness_tasks,
            'completed_task_count': totals['completed'],
            'total_task_count': totals['total'],
            'progress_percentage': totals['percentage'],
        },
    )


@login_required
@require_POST
def update_task_progress(request, task_key):
    try:
        CareerProfile.objects.get(user=request.user)
    except CareerProfile.DoesNotExist:
        return redirect('career:profile')

    skill_keys = {skill['key'] for skill in SKILLS}
    allowed_keys = skill_keys | {task[0] for task in PRACTICE_TASKS}
    is_json = request.headers.get('Accept') == 'application/json'

    if task_key not in allowed_keys:
        if is_json:
            return JsonResponse(
                {'error': 'Unknown career preparation task.'},
                status=400,
            )
        return HttpResponseBadRequest('Unknown career preparation task.')

    state = request.POST.get('state')
    if not state:
        state = (
            CareerTaskProgress.COMPLETED
            if 'completed' in request.POST
            else 'incomplete'
        )
    if state == 'complete':
        state = CareerTaskProgress.COMPLETED

    valid_states = {'incomplete', CareerTaskProgress.COMPLETED}
    if task_key in skill_keys:
        valid_states.add(CareerTaskProgress.IN_PROGRESS)
    if state not in valid_states:
        if is_json:
            return JsonResponse(
                {'error': 'Invalid task progress state.'},
                status=400,
            )
        return HttpResponseBadRequest('Invalid task progress state.')

    if state == 'incomplete':
        CareerTaskProgress.objects.filter(
            user=request.user,
            task_key=task_key,
        ).delete()
    else:
        CareerTaskProgress.objects.update_or_create(
            user=request.user,
            task_key=task_key,
            defaults={'status': state},
        )

    if is_json:
        statuses, totals = _task_totals(request.user, allowed_keys)
        return JsonResponse({
            'task_key': task_key,
            'status': statuses.get(task_key, 'recommended'),
            **totals,
            'message': 'Progress saved.',
        })

    messages.success(request, 'Progress saved.')
    return redirect(f"{reverse('learning:roadmap')}#skill-roadmap")
