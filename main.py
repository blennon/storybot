import os
import openai
import json

openai.api_key = os.environ['OPENAI_API_KEY']

def listdir_nohidden(path):
    dir = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            dir.append(f)
    return dir

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

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

def synthesize_synopses(
    params,
    convo_dir='convos/', 
    synopsis_dir='synopses/',
    template_file='convo_to_synopsis_template.txt'):
    synopses = listdir_nohidden(synopsis_dir)
    for fname in listdir_nohidden(convo_dir):
        if fname in synopses:
            print(f'{fname} already exists, skipping...')
            continue
        convo = open_file(f'{convo_dir}/{fname}')
        prompt = open_file(template_file).replace('<<CONVO>>', convo)
        print(f'Generating synopsis for {fname}...')
        completion = complete(prompt, params)
        save_file(f'{synopsis_dir}/{fname}', completion.choices[0].text.strip())
        print(f'Saving to {synopsis_dir}/{fname}')

def prepare_finetune_data(
        convo_dir='convos/', 
        synopsis_dir='synopses/',
        out_file='finetune_data.jsonl'):
        synopses = listdir_nohidden(synopsis_dir)
        data = []
        for fname in synopses:
            convo = open_file(f'{convo_dir}/{fname}')
            synopsis = open_file(f'{synopsis_dir}/{fname}')
            synopsis = "# STORY SYNOPSIS\n" + synopsis
            data.append({'prompt': convo, 'completion': synopsis})
        with open(out_file, 'w') as outfile:
            for i in data:
                json.dump(i, outfile)
                outfile.write('\n')

if __name__ == "__main__":
    params = {'model':'text-davinci-002',
            'max_tokens':512,
            'temperature':0.7,
            'top_p':1.0,
            'frequency_penalty':0.0,
            'presence_penalty':0.0,
            'stop':None
            }
    synthesize_synopses(params)
    #prepare_finetune_data()
    
