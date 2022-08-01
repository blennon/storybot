import os
import openai

with open('openaiapikey.txt', 'r') as infile:
    open_ai_api_key = infile.read()
openai.api_key = open_ai_api_key

def complete(prompt, params, max_retry=5):
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    while True:
        try:
            response = openai.Completion.create(prompt=prompt, **params)
            return response
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return 'OPENAI ERROR: max retries exceeded'
            print('Error communicating with OpenAI:', oops)
            sleep(1)

if __name__ == "__main__":
    params = {'model':'text-davinci-002',
            'max_tokens':512,
            'temperature':0.7,
            'top_p':1.0,
            'frequency_penalty':0.0,
            'presence_penalty':0.0,
            'stop':['\n6.']
            }
    prompt = "Brainstorm a list of titles for an children's adventure book:\n1."
    response = complete(prompt, params, max_retry=1)
    print(prompt+response.choices[0].text)