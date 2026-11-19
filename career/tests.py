import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CareerProfile


class CareerAiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='career-learner',
            password='test-password-123'
        )
        self.profile = CareerProfile.objects.create(
            user=self.user,
            full_name='Career Learner',
            experience_level='junior',
            target_role='Backend Developer',
            skills='Python, Django, SQL'
        )
        self.client.force_login(self.user)

    @patch('career.views.get_groq_response')
    def test_dashboard_can_show_ai_career_recommendations(self, groq_response):
        groq_response.return_value = (
            'Career directions\nBackend developer\n\n'
            'Skills to improve\nREST APIs and testing'
        )

        response = self.client.post(reverse('career:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'REST APIs and testing')
        prompt = groq_response.call_args.args[1]
        self.assertIn(self.profile.target_role, prompt)
        self.assertIn(self.profile.get_experience_level_display(), prompt)
        self.assertIn(self.profile.skills, prompt)

    @patch('career.views.get_groq_response')
    def test_dashboard_renders_structured_role_specific_recommendations(
        self,
        groq_response,
    ):
        groq_response.return_value = json.dumps({
            'career_directions': [{
                'title': 'Backend Developer',
                'description': 'Build reliable web services.',
                'why_it_fits': '<script>alert(1)</script>',
                'required_skills': ['Python', 'Django'],
                'skills_to_improve': [{
                    'skill': 'REST APIs',
                    'priority': 'High',
                    'why': 'Practice designing endpoints.',
                }],
                'recommended_projects': ['Build a documented API.'],
                'learning_roadmap': ['Review request validation.'],
                'growth_opportunities': ['Progress to owning backend features.'],
            }],
            'skill_gap_analysis': [{
                'category': 'Backend development',
                'existing_skills': ['Python', 'Django'],
                'needs_improvement': [],
                'missing_skills': [{
                    'skill': 'REST APIs',
                    'priority': 'High',
                    'why': 'This is central to the target role.',
                }],
            }],
            'learning_roadmap': [{
                'topic': 'REST APIs',
                'why_important': 'Backend services exchange data through APIs.',
                'what_to_learn': 'HTTP methods and validation.',
                'practical_task': 'Add a validated endpoint.',
                'expected_outcome': 'A tested endpoint with clear responses.',
            }],
            'technical_questions': [{
                'question': 'How do Django querysets avoid repeated queries?',
                'topic': 'Django ORM',
                'difficulty': 'Intermediate',
                'why_important': 'Query behavior affects endpoint performance.',
                'key_concepts': ['select_related', 'prefetch_related'],
            }],
            'readiness_overview': [{
                'category': 'Backend development',
                'status': 'developing',
                'explanation': 'The profile lists Python and Django.',
            }],
            'additional_insights': {
                'recommended_projects': ['Document the API setup.'],
                'technologies_to_learn': [],
                'mistakes_to_avoid': [],
                'interview_strategy': [],
                'github_improvements': [],
                'resume_improvements': [],
                'next_steps': ['Add automated endpoint tests.'],
            },
        })

        response = self.client.post(reverse('career:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Career directions')
        self.assertContains(response, 'Skill gap analysis')
        self.assertContains(response, 'Personalized learning roadmap')
        self.assertContains(response, 'Technical questions to prepare')
        self.assertContains(response, 'Additional career insights')
        self.assertContains(response, 'REST APIs')
        self.assertContains(
            response,
            '&lt;script&gt;alert(1)&lt;/script&gt;',
        )
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertEqual(
            groq_response.call_args.kwargs['max_completion_tokens'],
            3600,
        )


class CareerButtonLinkTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='navigation-learner',
            password='test-password-123',
        )
        CareerProfile.objects.create(
            user=self.user,
            full_name='Navigation Learner',
            experience_level='fresher',
            target_role='Software Developer',
            skills='Python, Django',
        )
        self.client.force_login(self.user)

    def test_home_action_links_keep_their_django_destinations(self):
        response = self.client.get(reverse('career:home'))

        self.assertContains(
            response,
            f'href="{reverse("career:dashboard")}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("resumes:upload")}"',
        )
        self.assertContains(response, 'class="btn btn-primary"')
        self.assertContains(response, 'class="btn btn-secondary"')
        self.assertContains(response, 'Explore Platform')
        self.assertNotContains(response, 'class="feature-link"')
        self.assertContains(response, 'href="/static/css/style.css?v=20261119.1"')

    def test_edit_profile_action_link_keeps_the_profile_destination(self):
        response = self.client.get(reverse('career:dashboard'))

        self.assertContains(
            response,
            f'href="{reverse("career:profile")}"',
        )
        self.assertContains(response, 'Edit Profile')
        self.assertContains(response, 'class="btn btn-secondary"')
        self.assertContains(response, 'class="btn btn-primary"')

    def test_primary_navigation_marks_the_current_application_section(self):
        paths = (
            reverse('career:home'),
            reverse('career:dashboard'),
            reverse('career:profile'),
            reverse('resumes:list'),
            reverse('learning:roadmap'),
            reverse('interview:questions'),
        )

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.content.count(b'aria-current="page"'),
                    1,
                )
                self.assertEqual(
                    response.content.count(b'class="is-active"'),
                    1,
                )

    def test_primary_application_pages_remain_available(self):
        paths = (
            reverse('career:home'),
            reverse('career:dashboard'),
            reverse('career:profile'),
            reverse('resumes:list'),
            reverse('resumes:upload'),
            reverse('learning:roadmap'),
            reverse('interview:questions'),
            reverse('interview:practice'),
        )

        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
