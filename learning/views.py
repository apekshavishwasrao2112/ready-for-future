import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from career.models import CareerProfile
from .models import CareerTaskProgress


ROLE_ROADMAPS = {
    'developer': [
        {
            'category': 'Python fundamentals and problem-solving',
            'key': 'python-problem-solving',
            'skill': 'Python data structures and problem-solving',
            'aliases': ['data structures', 'algorithms', 'python problem-solving'],
            'explanation': 'Practice choosing clear, efficient ways to solve common programming problems.',
            'learn': 'Lists, dictionaries, sets, iteration, complexity basics, and breaking a problem into smaller steps.',
            'practice': 'Write a function that groups a list of words by their first letter, then add cases for empty input and repeated words.',
            'why': 'These fundamentals help you reason through backend features and explain implementation choices for {target_role}.',
        },
        {
            'category': 'Django and web development',
            'key': 'django-advanced',
            'skill': 'Django ORM, authentication and permissions',
            'aliases': ['django orm', 'django authentication', 'django permissions'],
            'explanation': 'Go beyond basic Django familiarity by connecting data access to secure, user-aware web features.',
            'learn': 'Model relationships, queryset filtering, form validation, authentication decorators, and object ownership checks.',
            'practice': 'Add a private reading-list view where a signed-in user can see and update only their own entries.',
            'why': 'Real Django work depends on reliable data flows and access control, not only knowing the framework name.',
        },
        {
            'category': 'REST APIs and backend integration',
            'key': 'rest-api-design',
            'skill': 'REST API design and backend integration',
            'aliases': ['rest api', 'rest apis', 'restful api', 'django rest framework', 'drf'],
            'explanation': 'Learn how web clients exchange structured data with a backend using predictable HTTP endpoints.',
            'learn': 'HTTP methods and status codes, JSON responses, input validation, pagination, and clear error responses.',
            'practice': 'Build a small Django JSON endpoint to create and list a user-owned learning goal, with validation for blank titles.',
            'why': 'Many {target_role} projects connect browsers or other services to server-side features through APIs.',
        },
        {
            'category': 'SQL and database management',
            'key': 'sql-querying',
            'skill': 'SQL joins and query optimization',
            'aliases': ['sql joins', 'sql queries', 'query optimization', 'database indexing'],
            'explanation': 'Move from recognizing SQL to retrieving related data accurately and understanding query cost.',
            'learn': 'Filtering, joins, aggregation, grouping, NULL behavior, and when indexes can help.',
            'practice': 'Create users and projects tables, then write queries for each user’s project count and most recently updated project.',
            'why': 'Backend features rely on correct, efficient access to related records as an application grows.',
        },
        {
            'category': 'Testing and debugging',
            'key': 'testing-debugging',
            'skill': 'Automated Python testing and debugging',
            'aliases': ['pytest', 'unit testing', 'django test client', 'automated testing', 'python testing'],
            'explanation': 'Catch regressions early and use reproducible evidence to find the cause of a failure.',
            'learn': 'Arrange-act-assert tests, boundary cases, Django test clients, useful tracebacks, and debugger breakpoints.',
            'practice': 'Write tests for an existing Django form, including valid data, missing required data, and an invalid choice.',
            'why': 'Testing and diagnosis make changes safer to review and maintain in a production codebase.',
        },
        {
            'category': 'Git, deployment and basic CI/CD',
            'key': 'delivery-basics',
            'skill': 'GitHub workflows, deployment and basic CI',
            'aliases': ['github actions', 'deployment', 'continuous integration', 'ci cd'],
            'explanation': 'Learn to share work clearly and automate basic checks before changes are merged.',
            'learn': 'Small commits, branches, environment variables, deployment settings, and a simple automated test workflow.',
            'practice': 'Push a small Django project to GitHub, run its tests in a workflow, deploy it, and document the setup.',
            'why': 'A working, documented project shows how you deliver and maintain software—not just how you write code.',
        },
    ],
    'data': [
        {
            'category': 'Python fundamentals and problem-solving',
            'key': 'python-data-cleaning',
            'skill': 'Python data cleaning and problem-solving',
            'aliases': ['pandas', 'data cleaning', 'python data analysis'],
            'explanation': 'Turn inconsistent raw values into a dataset that can be analyzed reliably.',
            'learn': 'Python collections, missing-value handling, type conversion, and repeatable transformation steps.',
            'practice': 'Clean a small public or synthetic CSV and report how many rows were changed or excluded.',
            'why': 'Reliable data preparation is a foundation for trustworthy analysis in {target_role}.',
        },
        {
            'category': 'Reporting and visualization',
            'key': 'data-visualization',
            'skill': 'Data visualization and clear reporting',
            'aliases': ['data visualization', 'data visualisation', 'dashboard design'],
            'explanation': 'Choose a chart and explanation that make a useful pattern easy to understand.',
            'learn': 'Chart selection, labels, accessible color use, summary statistics, and concise written findings.',
            'practice': 'Create a one-page report with two charts and three evidence-based takeaways from a small dataset.',
            'why': 'Decision-makers need clear, contextual findings rather than charts without interpretation.',
        },
        {
            'category': 'SQL and database management',
            'key': 'sql-analysis',
            'skill': 'SQL joins, aggregation and analysis',
            'aliases': ['sql joins', 'sql queries', 'sql analysis'],
            'explanation': 'Combine related records and summarize them without losing the meaning of the data.',
            'learn': 'Joins, GROUP BY, aggregate functions, NULL handling, and checking for duplicate rows.',
            'practice': 'Query a sample orders dataset for monthly revenue and top products, then verify totals against a second query.',
            'why': 'SQL is a common way to explore operational data used by {target_role}.',
        },
        {
            'category': 'Tools and data workflows',
            'key': 'repeatable-data-workflow',
            'skill': 'Repeatable analysis workflows',
            'aliases': ['reproducible analysis', 'data pipeline', 'scheduled reports'],
            'explanation': 'Make an analysis repeatable so another person can follow its inputs and steps.',
            'learn': 'Separating inputs from outputs, documenting assumptions, and organizing notebooks or scripts.',
            'practice': 'Turn a one-off analysis into a script with a README explaining the input, transformations, and output.',
            'why': 'Repeatable methods make analysis easier to review, update, and trust.',
        },
        {
            'category': 'Testing and data validation',
            'key': 'data-validation',
            'skill': 'Data validation and analysis checks',
            'aliases': ['data validation', 'schema validation', 'analysis testing'],
            'explanation': 'Check assumptions about data before relying on a result.',
            'learn': 'Range checks, required fields, duplicate detection, and tests for transformation functions.',
            'practice': 'Add validation checks to your CSV analysis and write tests for one transformation.',
            'why': 'Showing how you detect incorrect or incomplete inputs builds confidence in your conclusions.',
        },
        {
            'category': 'Git and portfolio delivery',
            'key': 'data-delivery',
            'skill': 'Git and portfolio-ready reporting',
            'aliases': ['git', 'github', 'portfolio reporting'],
            'explanation': 'Share an analysis with enough context for someone else to review and reproduce it.',
            'learn': 'Version control basics, a focused README, sanitized sample data, and clear project structure.',
            'practice': 'Publish a small analysis project with its assumptions, reproducible steps, and final findings.',
            'why': 'A well-documented project demonstrates both analytical thinking and dependable communication.',
        },
    ],
    'security': [
        {
            'category': 'Python fundamentals and problem-solving',
            'key': 'security-scripting',
            'skill': 'Python scripting for defensive security',
            'aliases': ['python security scripting', 'security automation', 'python automation'],
            'explanation': 'Use small scripts to inspect and summarize data from authorized defensive workflows.',
            'learn': 'File handling, parsing structured logs, safe input validation, and clear output summaries.',
            'practice': 'Write a local script that summarizes synthetic authentication logs by outcome and date.',
            'why': 'Automation helps {target_role} investigate routine signals consistently.',
        },
        {
            'category': 'Systems and network fundamentals',
            'key': 'network-fundamentals',
            'skill': 'Network fundamentals and security controls',
            'aliases': ['network security', 'tcp ip', 'network fundamentals'],
            'explanation': 'Understand common network concepts and how defensive controls fit into a system.',
            'learn': 'DNS, TCP/IP basics, ports, TLS concepts, least privilege, and network segmentation.',
            'practice': 'Draw a simple web-service data flow and annotate trust boundaries and defensive controls.',
            'why': 'A clear systems model helps connect security findings to practical risk.',
        },
        {
            'category': 'Risk assessment and threat modeling',
            'key': 'threat-modeling',
            'skill': 'Threat modeling and risk assessment',
            'aliases': ['threat modeling', 'risk assessment', 'security risk analysis'],
            'explanation': 'Identify what needs protection and prioritize plausible risks before they become incidents.',
            'learn': 'Assets, trust boundaries, threat scenarios, likelihood, impact, and mitigations.',
            'practice': 'Threat-model a toy web application and document three risks with proportionate mitigations.',
            'why': 'Risk-based reasoning helps {target_role} explain which controls matter and why.',
        },
        {
            'category': 'Incident response and analysis',
            'key': 'incident-analysis',
            'skill': 'Incident response and log analysis',
            'aliases': ['incident response', 'log analysis', 'siem'],
            'explanation': 'Use a repeatable process to review alerts, preserve context, and communicate findings.',
            'learn': 'Triage notes, event timelines, evidence handling, escalation criteria, and concise reports.',
            'practice': 'Analyze a synthetic incident timeline and write a short report separating observations from hypotheses.',
            'why': 'Clear, evidence-led incident notes support coordinated response and follow-up.',
        },
        {
            'category': 'Testing and defensive validation',
            'key': 'defensive-validation',
            'skill': 'Safe security testing and validation',
            'aliases': ['security testing', 'vulnerability assessment', 'defensive validation'],
            'explanation': 'Validate defensive controls only in systems and environments you are authorized to test.',
            'learn': 'Test scope, safe lab practices, baseline checks, evidence, and remediation verification.',
            'practice': 'In a local toy application, verify that a documented defensive control rejects invalid input.',
            'why': 'Careful validation demonstrates disciplined, authorized security practice.',
        },
        {
            'category': 'Git and security documentation',
            'key': 'security-documentation',
            'skill': 'Git and security finding documentation',
            'aliases': ['git', 'github', 'security documentation'],
            'explanation': 'Track changes and communicate findings with enough detail to reproduce and resolve them.',
            'learn': 'Version history, clear reproduction steps, impact descriptions, and remediation notes.',
            'practice': 'Publish a sanitized lab report with scope, evidence, remediation, and verification steps.',
            'why': 'Actionable documentation helps teams prioritize and confirm security improvements.',
        },
    ],
    'general': [
        {
            'category': 'Role fundamentals and problem-solving',
            'key': 'role-fundamentals',
            'skill': 'Core concepts for your target role',
            'aliases': ['role fundamentals', 'core concepts'],
            'explanation': 'Identify the core concepts and vocabulary used in your target field.',
            'learn': 'Choose a focused beginner resource and summarize the concepts most often used in your target role.',
            'practice': 'Create a short glossary with one example showing how each of five concepts is used.',
            'why': 'A clear grasp of fundamentals helps you explain how your work supports {target_role}.',
        },
        {
            'category': 'Tools and workflow',
            'key': 'role-tools',
            'skill': 'Tools used in your target role',
            'aliases': ['role tools', 'professional tools'],
            'explanation': 'Build practical familiarity with a tool that appears in job descriptions for your target role.',
            'learn': 'Select one commonly requested tool, learn its basic workflow, and record the assumptions you make.',
            'practice': 'Complete a small task with the tool and save a short, reproducible walkthrough.',
            'why': 'A concrete example helps connect your profile to the day-to-day work of {target_role}.',
        },
        {
            'category': 'Data and systems awareness',
            'key': 'data-systems',
            'skill': 'Working with relevant data and systems',
            'aliases': ['data systems', 'systems awareness'],
            'explanation': 'Understand the inputs, outputs, and constraints of a typical task in your field.',
            'learn': 'Map the people, data, tools, and decisions involved in a representative workflow.',
            'practice': 'Document one end-to-end workflow and identify where an error or delay could occur.',
            'why': 'Systems awareness helps you explain the wider impact of your work.',
        },
        {
            'category': 'Quality checks and review',
            'key': 'quality-review',
            'skill': 'Quality checks and peer review',
            'aliases': ['quality assurance', 'peer review', 'quality checks'],
            'explanation': 'Use a repeatable review process to catch mistakes before delivering work.',
            'learn': 'Define success criteria, review edge cases, and record how feedback changes the result.',
            'practice': 'Review a small deliverable against a checklist and document one improvement.',
            'why': 'Reliable quality practices matter across roles and make your work easier to trust.',
        },
        {
            'category': 'Problem-solving and iteration',
            'key': 'problem-solving',
            'skill': 'Structured problem-solving',
            'aliases': ['problem solving', 'root cause analysis'],
            'explanation': 'Break an unclear request into a testable problem and evaluate possible solutions.',
            'learn': 'Clarifying questions, root-cause thinking, evidence gathering, and small iterations.',
            'practice': 'Choose a small problem in your field, compare two possible approaches, and explain your choice.',
            'why': 'Structured reasoning helps {target_role} deliver useful work when requirements are incomplete.',
        },
        {
            'category': 'Portfolio and delivery',
            'key': 'portfolio-delivery',
            'skill': 'Portfolio documentation and delivery',
            'aliases': ['portfolio', 'project documentation', 'github'],
            'explanation': 'Present a focused example of your work and make your process easy to follow.',
            'learn': 'Project framing, concise documentation, evidence of outcomes, and version history.',
            'practice': 'Publish a small role-relevant project with a README that states the problem, approach, and outcome.',
            'why': 'A clear work sample gives recruiters a concrete way to discuss your approach.',
        },
    ],
}

READINESS_TASKS = {
    'developer': [
        ('build-api', 'Build a small Django REST API', 'Demonstrates endpoint design, validation, and backend fundamentals.'),
        ('write-tests', 'Write tests for an existing Python or Django feature', 'Shows how you protect behavior and verify edge cases.'),
        ('practice-sql', 'Practice SQL queries', 'Demonstrates comfort retrieving and combining structured data.'),
        ('debug-error', 'Debug an intentional error', 'Shows a systematic approach to investigating and explaining a bug.'),
        ('push-github', 'Push a project to GitHub', 'Gives recruiters a reviewable example of your code and commit history.'),
        ('deploy-project', 'Deploy a project and document the process', 'Shows you can explain configuration and delivery beyond local development.'),
    ],
    'data': [
        ('build-analysis', 'Build a small data-cleaning and reporting project', 'Demonstrates a complete path from raw data to clear findings.'),
        ('write-tests', 'Validate an existing analysis with tests or checks', 'Shows how you check transformations and protect against bad inputs.'),
        ('practice-sql', 'Practice SQL queries', 'Demonstrates how you retrieve, join, and summarize structured data.'),
        ('debug-error', 'Debug an intentional data-quality issue', 'Shows how you trace an unexpected result back to its cause.'),
        ('push-github', 'Publish a documented project to GitHub', 'Gives recruiters a reproducible sample of your analytical process.'),
        ('deploy-project', 'Share a report and document how it was produced', 'Shows you can communicate findings and make the analysis repeatable.'),
    ],
    'security': [
        ('build-api', 'Complete a small, authorized defensive lab', 'Demonstrates safe, scoped practice and a clear record of what you tested.'),
        ('write-tests', 'Write checks for a defensive control', 'Shows how you verify a control and preserve expected behavior.'),
        ('practice-sql', 'Practice querying synthetic security events', 'Demonstrates evidence-led review of structured event data.'),
        ('debug-error', 'Investigate an intentional logging or configuration issue', 'Shows a methodical approach to diagnosis without guessing.'),
        ('push-github', 'Publish a sanitized lab project to GitHub', 'Lets recruiters review your documentation without exposing sensitive data.'),
        ('deploy-project', 'Document a safe lab setup and teardown', 'Shows care for scope, reproducibility, and responsible cleanup.'),
    ],
    'general': [
        ('build-api', 'Build a small project relevant to your target role', 'Demonstrates practical application of role-specific concepts.'),
        ('write-tests', 'Review a deliverable against explicit quality checks', 'Shows how you verify work before sharing it.'),
        ('practice-sql', 'Practice a relevant data or tool workflow', 'Demonstrates that you can apply the tools used in your target field.'),
        ('debug-error', 'Investigate and resolve an intentional issue', 'Shows structured problem-solving and evidence-based decisions.'),
        ('push-github', 'Publish a documented work sample', 'Gives recruiters a concrete example they can discuss with you.'),
        ('deploy-project', 'Share your work and document how to reproduce it', 'Shows clear communication and dependable delivery.'),
    ],
}


def _get_profile_skills(profile):
    if not profile or not profile.skills:
        return []
    return [skill.strip() for skill in profile.skills.split(',') if skill.strip()]


def _normalize_skill(skill):
    return re.sub(r'[^a-z0-9]+', ' ', skill.casefold()).strip()


def _role_family(target_role):
    role = target_role.casefold()
    if any(word in role for word in ('cyber', 'security', 'soc analyst')):
        return 'security'
    if any(word in role for word in ('data', 'analyst', 'business intelligence')):
        return 'data'
    if any(word in role for word in ('developer', 'engineer', 'software', 'backend', 'frontend', 'web')):
        return 'developer'
    return 'general'


def _build_skill_categories(profile, current_skills, completed_keys, family):
    target_role = profile.target_role
    normalized_skills = {_normalize_skill(skill) for skill in current_skills}
    categories = []
    learning_tasks = []

    for recommendation in ROLE_ROADMAPS[family]:
        aliases = {
            _normalize_skill(alias)
            for alias in recommendation['aliases']
        } | {_normalize_skill(recommendation['skill'])}
        is_existing = bool(aliases & normalized_skills)
        skill = {
            **recommendation,
            'is_existing': is_existing,
            'why': recommendation['why'].format(target_role=target_role),
        }
        skill['key'] = f'{family}-{recommendation["key"]}'
        skill['completed'] = skill['key'] in completed_keys
        if not is_existing:
            learning_tasks.append(skill)

        category = next(
            (item for item in categories if item['name'] == skill['category']),
            None,
        )
        if category is None:
            category = {'name': skill['category'], 'skills': []}
            categories.append(category)
        category['skills'].append(skill)

    return categories, learning_tasks


@login_required
def roadmap(request):
    try:
        profile = CareerProfile.objects.get(user=request.user)
    except CareerProfile.DoesNotExist:
        profile = None

    current_skills = _get_profile_skills(profile)
    target_role = profile.target_role if profile else 'your target role'
    current_role = (
        profile.current_role or 'Not added yet'
        if profile
        else 'Not added yet'
    )
    experience = profile.get_experience_level_display() if profile else 'Not added yet'

    family = _role_family(target_role)
    skill_recommendations = ROLE_ROADMAPS[family]
    skill_keys = [
        f'{family}-{recommendation["key"]}'
        for recommendation in skill_recommendations
    ]
    readiness_tasks = [
        {
            'key': f'{family}-{key}',
            'title': title,
            'proof': proof,
        }
        for key, title, proof in READINESS_TASKS[family]
    ]
    possible_task_keys = skill_keys + [task['key'] for task in readiness_tasks]
    completed_keys = set(
        CareerTaskProgress.objects.filter(
            user=request.user,
            task_key__in=possible_task_keys,
        ).values_list('task_key', flat=True)
    )

    skill_categories = []
    learning_tasks = []
    if profile:
        skill_categories, learning_tasks = _build_skill_categories(
            profile,
            current_skills,
            completed_keys,
            family,
        )

    for task in readiness_tasks:
        task['completed'] = task['key'] in completed_keys

    tracked_tasks = learning_tasks + readiness_tasks if profile else []
    completed_task_count = sum(task['completed'] for task in tracked_tasks)
    total_task_count = len(tracked_tasks)
    progress_percentage = (
        completed_task_count * 100 // total_task_count
        if total_task_count
        else 0
    )

    if not profile:
        next_action = {
            'title': 'Add your career profile',
            'description': 'Save a target role and your current skills to personalize this roadmap.',
            'href': reverse('career:profile'),
        }
    else:
        next_task = next(
            (task for task in tracked_tasks if not task['completed']),
            None,
        )
        if next_task:
            next_action = {
                'title': next_task.get('skill', next_task.get('title')),
                'description': (
                    f"Start with: {next_task['practice']}"
                    if 'practice' in next_task
                    else next_task['proof']
                ),
                'href': (
                    f"#practice-{next_task['key']}"
                    if 'practice' in next_task
                    else f"#readiness-{next_task['key']}"
                ),
            }
        else:
            next_action = {
                'title': 'Practice your interview story',
                'description': 'Your listed practice checklist is complete. Try explaining one project and the decisions behind it.',
                'href': reverse('interview:questions'),
            }

    return render(
        request,
        'learning/roadmap.html',
        {
            'profile': profile,
            'target_role': target_role,
            'current_role': current_role,
            'experience': experience,
            'current_skills': current_skills,
            'skill_categories': skill_categories,
            'learning_tasks': learning_tasks,
            'readiness_tasks': readiness_tasks,
            'completed_task_count': completed_task_count,
            'total_task_count': total_task_count,
            'progress_percentage': progress_percentage,
            'next_action': next_action,
        },
    )


@login_required
@require_POST
def update_task_progress(request, task_key):
    try:
        profile = CareerProfile.objects.get(user=request.user)
    except CareerProfile.DoesNotExist:
        return redirect('career:profile')

    family = _role_family(profile.target_role)
    skill_task_keys = {
        f'{family}-{recommendation["key"]}'
        for recommendation in ROLE_ROADMAPS[family]
    }
    allowed_keys = skill_task_keys | {
        f'{family}-{task[0]}'
        for task in READINESS_TASKS[family]
    }
    if task_key not in allowed_keys:
        return HttpResponseBadRequest('Unknown career preparation task.')

    state = request.POST.get('state')
    if state == 'complete':
        CareerTaskProgress.objects.get_or_create(
            user=request.user,
            task_key=task_key,
        )
    elif state == 'incomplete':
        CareerTaskProgress.objects.filter(
            user=request.user,
            task_key=task_key,
        ).delete()
    else:
        return HttpResponseBadRequest('Invalid task progress state.')

    anchor = 'practice' if task_key in skill_task_keys else 'readiness'
    return redirect(f"{reverse('learning:roadmap')}#{anchor}-{task_key}")
