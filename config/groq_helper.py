import os

from groq import Groq


class GroqConfigurationError(Exception):
    pass


class GroqResponseError(Exception):
    pass


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
