import openai
from time import time,sleep
from main import *

openai.api_key = os.environ['OPENAI_API_KEY']

if __name__ == '__main__':
    params = {'model':'davinci:ft-personal:storybot-2022-08-11-20-29-28',
        'max_tokens':256,
        'temperature':0.7,
        'top_p':1.0,
        'frequency_penalty':0.0,
        'presence_penalty':0.0,
        'stop':["CUSTOMER:"]
        }
    prompt = "STORYBOT: Hi, I’m Storybot, a friendly AI that will help write an amazing story for your little one. Since every great story starts with a main character, can you tell me about your’s? It helps to know their name, age and gender."
    conversation = [prompt]
    print(prompt)
    while True:
        a = input('CUSTOMER: ')
        conversation.append(f'CUSTOMER: {a}')
        block = '\n'.join(conversation) + '\nSTORYBOT:'
        completion = complete(block, params)
        text = completion.choices[0].text.strip()
        response = f'STORYBOT: {text}'
        print(response)
        conversation.append(response)
        