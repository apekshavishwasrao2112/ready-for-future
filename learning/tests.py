from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import LearningProgress


class LearningTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='learner',
            password='test-password-123'
        )
        self.client.force_login(self.user)

    def test_roadmap_shows_fresher_days_by_default(self):
        response = self.client.get(reverse('learning:roadmap'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['roadmap_type'], 'fresher')
        self.assertContains(response, 'Python Basics')

    def test_user_can_mark_a_roadmap_day_complete_and_undo_it(self):
        day_url = f'{reverse("learning:day", args=[1])}?track=fresher'

        response = self.client.get(day_url)
        self.assertFalse(response.context['completed'])
        self.assertFalse(LearningProgress.objects.exists())

        response = self.client.post(day_url)
        self.assertRedirects(response, day_url)
        self.assertTrue(
            LearningProgress.objects.filter(
                user=self.user,
                roadmap_type='fresher',
                day_number=1
            ).exists()
        )

        response = self.client.post(day_url)
        self.assertRedirects(response, day_url)
        self.assertFalse(LearningProgress.objects.exists())

    def test_experienced_roadmap_is_available(self):
        response = self.client.get(
            reverse('learning:roadmap'),
            {'track': 'experienced'}
        )

        self.assertEqual(response.context['roadmap_type'], 'experienced')
        self.assertContains(response, 'Review Core Concepts')
