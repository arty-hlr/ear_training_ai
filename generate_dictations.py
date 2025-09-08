import os
import glob
import re
import sys
import time
import random
import subprocess
import itertools

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.anthropic import AnthropicModelSettings

from jinja2 import Template

signatures = [f"{num} {acc}{'s' if num > 1 else ''}" for num, acc in list(itertools.product(range(1,8), ('flat','sharp')))]

def create_dictation(dictation_no):
    print(f'Creating dictation no {chapter_no}.{dictation_no}...')
    key_signature = random.choice(signatures)
    prompt = template.render(chapter=chapter, chapter_no=chapter_no, dictations=dictations, new_dictation_no=dictation_no, key_signature=key_signature)

    if os.environ.get('DEBUG', False):
        with open(f'new_dictations/{chapter_no}.{dictation_no:02}_prompt.txt', 'w') as f:
            f.write(prompt)

    res = agent.run_sync(prompt)

    messages = res.all_messages()

    print('REASONING:')
    reasoning = messages[1].parts[0].content
    if os.environ.get('DEBUG', False):
        with open(f'new_dictations/{chapter_no}.{dictation_no:02}_reasoning.txt', 'w') as f:
            f.write(reasoning)
    print(reasoning)
    print()

    print('OUTPUT:')
    output = messages[1].parts[1].content
    if os.environ.get('DEBUG', False):
        with open(f'new_dictations/{chapter_no}.{dictation_no:02}_output.txt', 'w') as f:
            f.write(output)
    xml_pattern = r'<\?xml.*?\?>.*?</score-partwise>'
    matches = re.findall(xml_pattern, output, re.DOTALL)
    with open(f'new_dictations/{chapter_no}.{dictation_no}.musicxml', 'w') as f:
        f.write(matches[0])
    answer_pattern = r'.*<\?xml'
    matches = re.findall(answer_pattern, output, re.DOTALL)
    print(matches[0])
    print()

    print('USAGE:')
    print(messages[1].usage)
    print()

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage: python generate_dictations.py <CHAPTER_NO>')
        exit()

    chapter_no = int(sys.argv[1])

    if os.environ.get('LOCAL', False):
        model = OpenAIChatModel(
            'qwen3-30b-a3b',
            # 'qwen3-4b-thinking-2507-mlx',
            provider=OpenAIProvider(
                base_url='http://localhost:1234/v1', api_key='lmstudio'
            ),
        )
        agent = Agent(model)
    else:
        model = 'anthropic:claude-sonnet-4-0'
        # model = 'anthropic:claude-opus-4-1'

        settings = AnthropicModelSettings(
            anthropic_thinking={'type': 'enabled', 'budget_tokens': 2048},
            temperature=1.0,
            max_tokens=16384,
        )
        agent = Agent(model, model_settings=settings)


    with open(f'chapters/chapter_{chapter_no}.md') as f:
        chapter = f.read()

    with open('contents.txt') as f:
        contents = f.readlines()
        previous_chapters = ''.join(contents[:chapter_no]).strip()
        next_chapters = ''.join(contents[chapter_no:]).strip()

    # chapter 28 was introduced in the 2nd edition and thus missing from 1st edition recordings, further chapters should refer to the dictations of N-1
    dictations = []
    if chapter_no != 28:
        if chapter_no < 28:
            pattern = f'dictations/{chapter_no}.*.musicxml'
        elif chapter_no > 28:
            pattern = f'dictations/{chapter_no-1}.*.musicxml'
        files = glob.glob(pattern)
        for file in files:
            with open(file) as f:
                dictations.append(f.read())

    with open('prompt.j2') as f:
        template = Template(f.read())

    for i in range(len(dictations)+1, len(dictations)+1+len(dictations)):
        create_dictation(i)
        print('Sleeping because of rate limiting...')
        time.sleep(30)

    print('Converting the dictations to mp3...')
    output = subprocess.check_output(f'./play_dictations.sh {chapter_no}', shell=True, text=True)
    print(output)
