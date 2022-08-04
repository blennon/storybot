from typing import List, Union
import re
from textwrap import dedent
import openai
from main import complete
from synthesize_convos import open_file
from uuid import uuid4
from pydantic import BaseModel

def check_string_list(text: str, min_items: int = 3):
    text = '1.'+text
    if len(text)<10:
        return False
    for i in range(min_items):
        if str(i+1)+'.' not in text:
            return False
    return True

def parse_string_list(text: str) -> List[str]:
    """
    >>> parse_string_list("1. this is the first line\n2. this is the second line\n3. this is the third line")
    ['this is the first line', 'this is the second line', 'this is the third line']
    """
    clean_lines = []
    lines = re.split(r"\n*\d+\.", text)
    for line in lines:
        if len(line.strip()) > 0:
            clean_lines.append(line.strip())
    return clean_lines

class CustomerPreferences(BaseModel):
    genre: str
    themes: List[str]
    tones: List[str]
    main_character_name: str
    audience: Union[str, None] = "Children ages 2-5"

def make_start_prompt(customer_preferences: CustomerPreferences):
    prompt = f"""\
    STORY GENERATOR
    Our goal is to gather preferences from a customer and brainstorm children's story ideas.

    Genre: {customer_preferences.genre}
    Audience: {customer_preferences.audience}
    Themes: {', '.join(customer_preferences.themes)}
    Tones: {', '.join(customer_preferences.tones)}
    Main character name: {customer_preferences.main_character_name}
    """.format(customer_preferences)
    return dedent(prompt)

def generate_response(start_prompt, idea_prompt, params):
    prompt = '\n'.join([start_prompt,idea_prompt])
    response = complete(prompt, params)
    return prompt, response

def string_to_list(text: str) -> List[str]:
    return [item.strip() for item in text.split(',')]

def set_idea_from_list(start_prompt, idea_name, story_ideas, selection):
    return '\n'.join([start_prompt, f"\n{idea_name}: {story_ideas[selection].strip()}"])

def set_idea(start_prompt, idea_name, idea_value):
    return '\n'.join([start_prompt, f"\n{idea_name}: {idea_value.strip()}"])

def brainstorm_and_set(start_prompt, ideas_prompt, idea_name, params, retries=3, list=False):
    r = 'more'
    retry = 0
    while r.strip().lower() == 'more':
        _, response = generate_response(start_prompt, ideas_prompt, params)
        text = response.choices[0].text
        if list:
            if not check_string_list(text):
                retry +=1
                if retry > retries:
                    raise Exception("Too many retries")
                continue
            print('1.'+text)
            r = input("\nEnter a number to make a selection. If you want a new set of ideas, say 'More'. ")
        else:
            print(text.strip())
            r = input("\nYou can say 'Yes' if you're happy with this. If you want another idea, say 'More'.\n")
    if list:
        ideas = parse_string_list(text)
        return set_idea_from_list(start_prompt, idea_name, ideas, int(r)-1)
    return set_idea(start_prompt, idea_name, text)

story_ideas_prompt = "Brainstorm story ideas:\n1."
antag_ideas_prompt = "Brainstorm antagonist ideas:\n1."
char_ideas_prompt = "Brainstorm supporting characters:\n1."
develop_protag_prompt = "Develop the main character:"
develop_antag_prompt = "Develop and name the antagonist:"
if __name__ == '__main__':

    params = {'model':'text-davinci-002',
            'max_tokens':512,
            'temperature':1.0,
            'top_p':1.0,
            'frequency_penalty':0.0,
            'presence_penalty':0.0,
            'stop':None
            }

    develop_params = params.copy()
    develop_params['stop'] = ['\n','\r']
    while True:
        print("Hi, I'm StoryBot and I'm here to help you write a great story. Let's start by telling me what your preferences are.\n")
        main_character_name = input('What is the name of your main character and their gender? E.g. Leila, a girl. ')
        genre = input('What is your desired genre? It could be Adventure, Comedy, Fantasy, Sci-fi, etc.: ')
        themes = input('What themes do you want in your story? E.g. Bravery, Friendship, etc.: ')
        tones = input('What tones do you want in your story? E.g. Whimsical, Serious, Heartwarming, etc.: ')

        pref = CustomerPreferences(
            genre="Children's " + genre, 
            themes=string_to_list(themes), 
            tones=string_to_list(tones), 
            main_character_name=main_character_name
            )
        start_prompt = make_start_prompt(pref)
          
        print("\nOkay, now we'll brainstorm some story ideas. Generating...\n")
        start_prompt = brainstorm_and_set(start_prompt, story_ideas_prompt, "Story idea", params, list=True)
        print(start_prompt)
        
        print("\nGreat, now we'll develop the main character a bit more. What do you think about this...\n")
        start_prompt = brainstorm_and_set(start_prompt, develop_protag_prompt, "Main character", develop_params)
        print(start_prompt)