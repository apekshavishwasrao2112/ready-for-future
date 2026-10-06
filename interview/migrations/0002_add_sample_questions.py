from django.db import migrations


QUESTIONS = [
    (
        'python',
        'What is the difference between a list and a tuple in Python?',
        'Explain that lists can be changed after creation, while tuples are immutable.',
        'python, list, tuple',
    ),
    (
        'python',
        'How does try and except help handle errors?',
        'Describe putting code that may fail in try and handling a specific error in except.',
        'python, errors, exception',
    ),
    (
        'python',
        'Why might you use a Python virtual environment?',
        'Mention keeping project dependencies separate from other Python projects.',
        'python, environment',
    ),
    (
        'django',
        'What happens when a Django URL matches a request?',
        'Describe Django calling the connected view, which returns a response.',
        'django, url, view',
    ),
    (
        'django',
        'What is a Django model?',
        'Explain that a model describes data and Django uses it to create database tables.',
        'django, model, database',
    ),
    (
        'django',
        'Why do Django projects use migrations?',
        'Explain that migrations apply model changes to the database in a trackable way.',
        'django, migration, database',
    ),
    (
        'sql',
        'What is a primary key in a database table?',
        'Explain that it identifies each row uniquely.',
        'sql, database, key',
    ),
    (
        'sql',
        'When would you use a JOIN?',
        'Describe combining related rows from tables using matching columns.',
        'sql, join, database',
    ),
    (
        'sql',
        'What does GROUP BY do?',
        'Explain that it groups rows so aggregate calculations can be made per group.',
        'sql, group, database',
    ),
    (
        'javascript',
        'What is the difference between let and const?',
        'Explain that both are block-scoped; const cannot be reassigned.',
        'javascript, let, const',
    ),
    (
        'javascript',
        'How do you respond to a button click in JavaScript?',
        'Describe selecting the button and adding a click event listener.',
        'javascript, event',
    ),
    (
        'javascript',
        'What does the map method do for an array?',
        'Explain that map creates a new array by transforming each item.',
        'javascript, array',
    ),
    (
        'hr',
        'Tell me about yourself and your career goals.',
        'Give a short summary of your background, relevant skills, and next goal.',
        'career, communication',
    ),
    (
        'hr',
        'Describe a challenge you faced and how you handled it.',
        'Describe the situation, your actions, and what you learned.',
        'teamwork, problem-solving',
    ),
    (
        'hr',
        'What is one skill you are currently working to improve?',
        'Name a real skill, explain how you practice it, and share your progress.',
        'learning, growth',
    ),
]


def add_questions(apps, schema_editor):
    question_model = apps.get_model('interview', 'InterviewQuestion')

    for topic, question, answer_tip, keywords in QUESTIONS:
        question_model.objects.get_or_create(
            topic=topic,
            question=question,
            defaults={
                'answer_tip': answer_tip,
                'keywords': keywords,
                'is_active': True,
            }
        )


class Migration(migrations.Migration):
    dependencies = [
        ('interview', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_questions,
            migrations.RunPython.noop
        ),
    ]
