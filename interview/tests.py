from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from career.models import CareerProfile
from resumes.models import Resume

from .models import InterviewQuestion


class InterviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='interview-learner',
            password='test-password-123'
        )
        self.client.force_login(self.user)

    def test_question_bank_has_each_requested_topic(self):
        response = self.client.get(reverse('interview:questions'))

        self.assertEqual(response.status_code, 200)
        topics = set(
            InterviewQuestion.objects.values_list('topic', flat=True)
        )
        self.assertEqual(
            topics,
            {'python', 'django', 'sql', 'javascript', 'hr'}
        )

    def test_profile_and_uploaded_resume_create_personal_questions(self):
        CareerProfile.objects.create(
            user=self.user,
            full_name='Interview Learner',
            experience_level='fresher',
            target_role='Python Developer',
            skills='Python, Django'
        )
        Resume.objects.create(
            user=self.user,
            resume_file=SimpleUploadedFile(
                'resume.pdf',
                b'Resume test file'
            )
        )

        response = self.client.get(reverse('interview:questions'))

        self.assertContains(response, 'Python Developer')
        self.assertContains(response, 'uploaded resume')
        self.assertContains(response, 'How have you used Python')
        self.assertTrue(response.context['matching_questions'])

    def test_practice_page_displays_answer_tips(self):
        response = self.client.get(reverse('interview:practice'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Show answer tip')
        self.assertContains(response, 'immutable')

    @patch('interview.views.get_groq_response')
    def test_interview_page_can_generate_ai_questions(self, groq_response):
        profile = CareerProfile.objects.create(
            user=self.user,
            full_name='Interview Learner',
            experience_level='fresher',
            target_role='Python Developer',
            skills='Python, Django'
        )
        groq_response.return_value = (
            'Technical questions\n1. What is a Django model?\n\n'
            'HR questions\n1. Tell me about yourself.'
        )

        response = self.client.post(reverse('interview:questions'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'What is a Django model?')
        prompt = groq_response.call_args.args[1]
        self.assertIn(profile.target_role, prompt)
        self.assertIn(profile.skills, prompt)
