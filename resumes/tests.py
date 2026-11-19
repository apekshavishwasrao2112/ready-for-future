import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from career.models import CareerProfile

from .models import Resume


class ResumeTests(TestCase):
    def make_pdf(self, text):
        escaped_text = (
            text.replace('\\', '\\\\')
            .replace('(', '\\(')
            .replace(')', '\\)')
            .replace('\n', r'\n')
            .replace('\r', r'\r')
        )
        content = (
            f'BT /F1 12 Tf 72 720 Td ({escaped_text}) Tj ET'
        ).encode('ascii')
        objects = [
            b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            (
                b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
                b'/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>'
            ),
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
            (
                f'<< /Length {len(content)} >>\n'.encode('ascii')
                + b'stream\n'
                + content
                + b'\nendstream'
            ),
        ]
        pdf = bytearray(b'%PDF-1.4\n')
        offsets = [0]
        for object_number, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(
                f'{object_number} 0 obj\n'.encode('ascii')
                + obj
                + b'\nendobj\n'
            )

        xref_offset = len(pdf)
        pdf.extend(f'xref\n0 {len(objects) + 1}\n'.encode('ascii'))
        pdf.extend(b'0000000000 65535 f \n')
        for offset in offsets[1:]:
            pdf.extend(f'{offset:010d} 00000 n \n'.encode('ascii'))
        pdf.extend(
            (
                f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n'
                f'startxref\n{xref_offset}\n%%EOF\n'
            ).encode('ascii')
        )
        return bytes(pdf)

    def setUp(self):
        self.media_dir = tempfile.mkdtemp()
        self.media_override = override_settings(
            MEDIA_ROOT=self.media_dir
        )
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(shutil.rmtree, self.media_dir)

        self.user = User.objects.create_user(
            username='resume-learner',
            password='test-password-123'
        )

    def test_resume_pages_require_login(self):
        for url_name in (
            'resumes:list',
            'resumes:list_page',
            'resumes:upload'
        ):
            response = self.client.get(reverse(url_name))
            self.assertRedirects(
                response,
                f'{reverse("accounts:login")}?next={reverse(url_name)}'
            )

        resume = Resume.objects.create(
            user=self.user,
            resume_file=SimpleUploadedFile(
                'resume.pdf',
                b'My sample resume'
            )
        )
        for url_name in ('resumes:result', 'resumes:download'):
            resume_url = reverse(url_name, args=[resume.id])
            response = self.client.get(
                resume_url
            )
            self.assertRedirects(
                response,
                f'{reverse("accounts:login")}?next={resume_url}'
            )

    def test_user_can_upload_and_view_their_resume(self):
        CareerProfile.objects.create(
            user=self.user,
            full_name='Resume Learner',
            experience_level='fresher',
            target_role='Python Developer',
            skills='Python, Git'
        )
        self.client.login(
            username='resume-learner',
            password='test-password-123'
        )

        response = self.client.get(reverse('resumes:upload'))
        self.assertContains(response, 'Choose PDF')
        self.assertContains(response, 'class="btn btn-primary"')
        self.assertContains(response, 'static/css/resume.css')

        response = self.client.post(
            reverse('resumes:upload'),
            {
                'resume_file': SimpleUploadedFile(
                    'resume.pdf',
                    self.make_pdf('My sample resume')
                )
            }
        )

        resume = Resume.objects.get(user=self.user        )
        self.assertRedirects(
            response,
            reverse('resumes:result', args=[resume.id]),
            fetch_redirect_response=False
        )
        self.assertTrue(resume.resume_file.name.startswith('resumes/'))

        response = self.client.get(
            reverse('resumes:result', args=[resume.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resume uploaded successfully.')
        self.assertContains(response, 'class="btn btn-primary"')
        self.assertNotContains(response, 'Resume Score')
        self.assertNotContains(response, 'Matched Skills')

        response = self.client.get(
            reverse('resumes:download', args=[resume.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b''.join(response.streaming_content).startswith(b'%PDF-')
        )

        response = self.client.get(reverse('resumes:list'))
        self.assertContains(response, 'resume.pdf')
        self.assertContains(response, 'class="btn btn-primary"')

    def test_upload_rejects_unsupported_file_extension(self):
        self.client.login(
            username='resume-learner',
            password='test-password-123'
        )

        for file_name in ('not-a-resume.exe', 'not-a-resume.docx'):
            response = self.client.post(
                reverse('resumes:upload'),
                {
                    'resume_file': SimpleUploadedFile(
                        file_name,
                        b'Not a PDF resume'
                    )
                }
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'File extension')
        self.assertFalse(Resume.objects.filter(user=self.user).exists())

    def test_pdf_processing_shows_error_when_pypdf_is_unavailable(self):
        resume = Resume.objects.create(
            user=self.user,
            resume_file=SimpleUploadedFile(
                'resume.pdf',
                b'PDF contents'
            )
        )
        self.client.force_login(self.user)

        with patch.dict('sys.modules', {'pypdf': None}):
            response = self.client.post(
                reverse('resumes:result', args=[resume.id])
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'PDF text extraction is currently unavailable.'
        )

    @patch('resumes.views.get_groq_response')
    def test_ai_feedback_uses_extracted_pdf_text(self, groq_response):
        groq_response.return_value = (
            '{"overall_feedback":"Clear experience summary.",'
            '"strengths":["Python project described."],'
            '"areas_to_improve":["Add project outcomes."],'
            '"recommended_actions":["Add measurable results."]}'
        )
        profile = CareerProfile.objects.create(
            user=self.user,
            full_name='Resume Learner',
            experience_level='fresher',
            target_role='Python Developer',
            current_role='Student',
            skills='Profile skills must not be used'
        )
        resume = Resume.objects.create(
            user=self.user,
            resume_file=SimpleUploadedFile(
                'resume.pdf',
                self.make_pdf(
                    'Jane Doe\nPython developer\nBuilt a Django project '
                    'that serves a REST API.'
                )
            )
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('resumes:result', args=[resume.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clear experience summary.')
        self.assertContains(response, 'Python project described.')
        self.assertContains(response, 'Recommended Actions')
        prompt = groq_response.call_args.args[1]
        self.assertIn(profile.target_role, prompt)
        self.assertIn(profile.current_role, prompt)
        self.assertIn(
            'Built a Django project that serves a REST API.',
            prompt
        )
        self.assertNotIn(profile.skills, prompt)
        self.assertTrue(groq_response.call_args.kwargs['json_mode'])
        self.assertNotIn('score', response.context)
        self.assertNotIn('matched_skills', response.context)
        self.assertNotIn('missing_skills', response.context)

    @patch('resumes.views.get_groq_response')
    def test_empty_pdf_does_not_call_groq(self, groq_response):
        resume = Resume.objects.create(
            user=self.user,
            resume_file=SimpleUploadedFile(
                'empty.pdf',
                self.make_pdf('')
            )
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('resumes:result', args=[resume.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Could not extract readable text from this PDF'
        )
        groq_response.assert_not_called()

    @patch('resumes.views.get_groq_response')
    def test_unreadable_pdf_does_not_call_groq(self, groq_response):
        resume = Resume.objects.create(
            user=self.user,
            resume_file=SimpleUploadedFile(
                'broken.pdf',
                b'not a real PDF'
            )
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('resumes:result', args=[resume.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Could not read this PDF')
        groq_response.assert_not_called()

    @patch('resumes.views.get_groq_response')
    def test_invalid_groq_json_shows_friendly_error(self, groq_response):
        groq_response.return_value = 'not JSON'
        resume = Resume.objects.create(
            user=self.user,
            resume_file=SimpleUploadedFile(
                'resume.pdf',
                self.make_pdf('Resume text that can be extracted.')
            )
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('resumes:result', args=[resume.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'AI feedback could not be processed right now.'
        )

    def test_user_cannot_view_another_users_resume(self):
        other_user = User.objects.create_user(
            username='another-learner',
            password='test-password-123'
        )
        resume = Resume.objects.create(
            user=other_user,
            resume_file=SimpleUploadedFile(
                'private.pdf',
                b'Private resume'
            )
        )
        self.client.login(
            username='resume-learner',
            password='test-password-123'
        )

        response = self.client.get(
            reverse('resumes:result', args=[resume.id])
        )

        self.assertEqual(response.status_code, 404)
        response = self.client.get(
            reverse('resumes:download', args=[resume.id])
        )
        self.assertEqual(response.status_code, 404)
