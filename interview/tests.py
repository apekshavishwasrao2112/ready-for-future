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

    @patch('interview.views.get_groq_response')
    def test_practice_page_generates_profile_specific_questions(self, groq_response):
        profile = CareerProfile.objects.create(
            user=self.user,
            full_name='Interview Learner',
            current_role='Cybersecurity Analyst Intern',
            experience_level='junior',
            target_role='Cybersecurity Analyst',
            skills=(
                'Vulnerability Scanning, Penetration Testing, Ethical Hacking, '
                'Root Cause Analysis'
            ),
        )
        groq_response.return_value = (
            '{"technical_questions": ['
            '{"question": "How would you investigate a suspicious login alert?", '
            '"topic": "SOC / Incident Response", "answer_tip": "Explain your triage steps."}'
            '], "hr_questions": ['
            '{"question": "Why do you want to work as a Cybersecurity Analyst?", '
            '"answer_tip": "Connect your experience and motivation."}'
            ']}'
        )

        response = self.client.get(reverse('interview:practice'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cybersecurity Analyst')
        self.assertContains(response, 'suspicious login alert')
        self.assertContains(response, 'SOC / Incident Response')
        self.assertContains(response, 'Why do you want to work as a Cybersecurity Analyst?')
        self.assertNotContains(response, 'What is a Django model?')
        self.assertNotContains(response, 'What is the difference between let and const?')
        self.assertNotContains(response, 'What is the difference between a list and a tuple')
        self.assertNotContains(response, 'What is a primary key in a database table?')
        self.assertContains(response, 'Show answer tip')
        self.assertContains(response, 'Explain your triage steps.')
        self.assertContains(response, 'class="practice-answer"')
        self.assertContains(response, 'answer-count')

        system_prompt, user_prompt = groq_response.call_args.args
        self.assertIn('generating interview questions for this candidate', system_prompt)
        self.assertIn(profile.target_role, user_prompt)
        self.assertIn(profile.current_role, user_prompt)
        self.assertIn(profile.get_experience_level_display(), user_prompt)
        self.assertIn(profile.skills, user_prompt)
        self.assertTrue(groq_response.call_args.kwargs['json_mode'])

    def test_practice_page_requires_a_complete_profile(self):
        response = self.client.get(reverse('interview:practice'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your career profile')
        self.assertNotContains(response, 'What is a Django model?')

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
