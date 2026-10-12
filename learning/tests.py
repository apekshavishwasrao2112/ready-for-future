from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from career.models import CareerProfile
from .models import CareerTaskProgress


class LearningDashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='learner',
            password='test-password-123',
        )
        self.profile = CareerProfile.objects.create(
            user=self.user,
            full_name='Career Learner',
            current_role='Junior Developer',
            experience_level='fresher',
            target_role='Software Developer',
            skills='Python, Django, HTML, CSS, Docker, React.js, JavaScript',
        )
        self.client.force_login(self.user)
        self.roadmap_url = reverse('learning:roadmap')

    def test_dashboard_uses_the_saved_career_profile(self):
        response = self.client.get(self.roadmap_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.target_role)
        self.assertContains(response, self.profile.current_role)
        self.assertContains(response, 'Fresher')
        self.assertContains(response, 'Python')
        self.assertContains(response, 'REST API design and backend integration')
        self.assertEqual(response.context['total_task_count'], 12)
        self.assertEqual(response.context['progress_percentage'], 0)
        self.assertContains(response, 'not job readiness')

    def test_profile_skills_are_not_recommended_as_generic_duplicates(self):
        self.profile.target_role = 'Data Analyst'
        self.profile.skills = 'SQL joins, Python, Excel'
        self.profile.save()

        response = self.client.get(self.roadmap_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            'data-sql-analysis',
            [task['key'] for task in response.context['learning_tasks']],
        )
        self.assertContains(response, 'Already in your profile')

    def test_skill_and_readiness_progress_persist_and_can_be_reopened(self):
        task_key = 'developer-rest-api-design'
        progress_url = reverse('learning:progress', args=[task_key])

        response = self.client.post(progress_url, {'state': 'complete'})

        self.assertRedirects(
            response,
            f'{self.roadmap_url}#practice-{task_key}',
            fetch_redirect_response=False,
        )
        self.assertTrue(
            CareerTaskProgress.objects.filter(
                user=self.user,
                task_key=task_key,
            ).exists()
        )

        refreshed = self.client.get(self.roadmap_url)
        self.assertEqual(refreshed.context['completed_task_count'], 1)
        self.assertEqual(refreshed.context['progress_percentage'], 8)
        completed_task = next(
            task for task in refreshed.context['learning_tasks']
            if task['key'] == task_key
        )
        self.assertTrue(completed_task['completed'])

        readiness_key = 'developer-write-tests'
        readiness_response = self.client.post(
            reverse('learning:progress', args=[readiness_key]),
            {'state': 'complete'},
        )
        self.assertRedirects(
            readiness_response,
            f'{self.roadmap_url}#readiness-{readiness_key}',
            fetch_redirect_response=False,
        )
        refreshed = self.client.get(self.roadmap_url)
        self.assertEqual(refreshed.context['completed_task_count'], 2)
        self.assertEqual(refreshed.context['progress_percentage'], 16)

        response = self.client.post(progress_url, {'state': 'incomplete'})

        self.assertRedirects(
            response,
            f'{self.roadmap_url}#practice-{task_key}',
            fetch_redirect_response=False,
        )
        self.assertFalse(
            CareerTaskProgress.objects.filter(
                user=self.user,
                task_key=task_key,
            ).exists()
        )

    def test_users_cannot_change_another_users_progress(self):
        other_user = User.objects.create_user(
            username='another-learner',
            password='test-password-456',
        )
        task_key = 'developer-build-api'
        CareerTaskProgress.objects.create(
            user=other_user,
            task_key=task_key,
        )

        response = self.client.post(
            reverse('learning:progress', args=[task_key]),
            {'state': 'incomplete'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CareerTaskProgress.objects.filter(
                user=other_user,
                task_key=task_key,
            ).exists()
        )
        self.assertFalse(
            CareerTaskProgress.objects.filter(
                user=self.user,
                task_key=task_key,
            ).exists()
        )

    def test_progress_endpoint_rejects_unknown_tasks_and_invalid_states(self):
        unknown = self.client.post(
            reverse('learning:progress', args=['other-users-task']),
            {'state': 'complete'},
        )
        invalid_state = self.client.post(
            reverse('learning:progress', args=['developer-build-api']),
            {'state': 'skip'},
        )

        self.assertEqual(unknown.status_code, 400)
        self.assertEqual(invalid_state.status_code, 400)
        self.assertFalse(CareerTaskProgress.objects.exists())

    def test_learning_dashboard_requires_authentication(self):
        self.client.logout()

        response = self.client.get(self.roadmap_url)

        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={self.roadmap_url}',
        )
