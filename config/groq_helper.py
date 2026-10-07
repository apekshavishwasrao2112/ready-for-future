import json
import os
import re

from groq import Groq


class GroqConfigurationError(Exception):
    pass


class GroqResponseError(Exception):
    pass


def _strip_markdown_tokens(value):
    cleaned = value.strip()
    cleaned = re.sub(r'^(?:[*#\-]+|\d+\.|[A-Za-z ]+:)\s*', '', cleaned)
    cleaned = cleaned.replace('**', '').replace('__', '').replace('\\n', ' ')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def _fallback_markdown_to_json(response_text):
    lines = [line.strip() for line in response_text.splitlines() if line.strip()]
    lower_lines = [line.lower() for line in lines]

    if any('career' in line or 'skills to improve' in line for line in lower_lines):
        career_directions = []
        key_skills = []
        current_heading = None
        buffer = []

        for line in lines:
            normalized = line.lower()
            if 'career direction' in normalized or 'career directions' in normalized:
                if buffer:
                    career_directions.append({
                        'title': 'Career direction',
                        'why_it_fits': ' '.join(buffer),
                        'skills_to_improve': [],
                    })
                    buffer = []
                current_heading = 'career'
                continue
            if 'skill' in normalized and 'improve' in normalized:
                if buffer:
                    career_directions.append({
                        'title': 'Career direction',
                        'why_it_fits': ' '.join(buffer),
                        'skills_to_improve': [],
                    })
                    buffer = []
                current_heading = 'skills'
                continue
            if current_heading == 'career':
                cleaned = _strip_markdown_tokens(line)
                if cleaned:
                    buffer.append(cleaned)
            elif current_heading == 'skills':
                cleaned = _strip_markdown_tokens(line)
                if cleaned:
                    key_skills.append(cleaned)

        if buffer:
            career_directions.append({
                'title': 'Career direction',
                'why_it_fits': ' '.join(buffer),
                'skills_to_improve': [],
            })

        if not career_directions:
            career_directions.append({
                'title': 'Career direction',
                'why_it_fits': ' '.join(_strip_markdown_tokens(line) for line in lines if _strip_markdown_tokens(line)),
                'skills_to_improve': [],
            })

        if not key_skills and any('skills to improve' in line.lower() for line in lines):
            key_skills = [
                item for item in [_strip_markdown_tokens(line) for line in lines]
                if item and not item.lower().startswith('career')
            ]

        return {
            'career_directions': career_directions,
            'key_skills_to_improve': key_skills,
        }

    if any('technical questions' in line.lower() for line in lower_lines):
        technical = []
        hr = []
        current_heading = None

        for line in lines:
            normalized = line.lower()
            if 'technical questions' in normalized:
                current_heading = 'technical'
                continue
            if 'hr questions' in normalized:
                current_heading = 'hr'
                continue
            if re.match(r'^\d+\.', line):
                cleaned = re.sub(r'^\d+\.\s*', '', line)
                cleaned = _strip_markdown_tokens(cleaned)
                if current_heading == 'technical':
                    technical.append({'question': cleaned, 'topic': 'General'})
                elif current_heading == 'hr':
                    hr.append({'question': cleaned})

        if not technical and not hr:
            technical = [{'question': ' '.join(_strip_markdown_tokens(line) for line in lines), 'topic': 'General'}]
        return {'technical_questions': technical, 'hr_questions': hr}

    return {'technical_questions': [{'question': response_text, 'topic': 'General'}], 'hr_questions': []}


def parse_json_response(response_text):
    if response_text is None:
        raise GroqResponseError('Groq returned an empty response.')

    cleaned = response_text.strip()
    if cleaned.startswith('```'):
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```\s*$', '', cleaned, flags=re.IGNORECASE | re.DOTALL)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return _fallback_markdown_to_json(cleaned)


def get_groq_response(system_prompt, user_prompt, json_mode=False):
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise GroqConfigurationError(
            'GROQ_API_KEY is missing from the server environment.'
        )

    client = Groq(api_key=api_key)
    request = {
        'model': 'qwen/qwen3.8-27b',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'temperature': 0.4,
        'max_completion_tokens': 900,
    }
    if json_mode:
        request['response_format'] = {'type': 'json_object'}

    response = client.chat.completions.create(**request)
    answer = response.choices[0].message.content

    if not answer:
        raise GroqResponseError('Groq returned an empty response.')

    return answer.strip()
