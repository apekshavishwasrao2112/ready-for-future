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
        self.assertContains(response, 'class="feature-link action-link"')
        self.assertContains(response, 'Explore Platform')

    def test_edit_profile_action_link_keeps_the_profile_destination(self):
        response = self.client.get(reverse('career:dashboard'))

        self.assertContains(
            response,
            f'href="{reverse("career:profile")}"',
        )
        self.assertContains(response, 'Edit Profile')
        self.assertContains(response, 'class="action-link"')
