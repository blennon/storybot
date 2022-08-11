"""
storybook base module.
"""
NAME = "storybook"

import os
import re
import logging
from typing import List, Union
from textwrap import dedent
from pydantic import BaseModel
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
    Main character name: {customer_preferences.main_character_name}""".format(customer_preferences)
    return dedent(prompt)

def generate_response(start_prompt, idea_prompt, params):
    prompt = '\n'.join([start_prompt,idea_prompt])
    response = complete(prompt, params)
    return prompt, response

def string_to_list(text: str) -> List[str]:
    return [item.strip() for item in text.split(',')]

def set_ideas_from_list(start_prompt: str, idea_name: str, ideas: List[str], selection: List[int]) -> str:
    if len(selection) > 1:
        ideas_str = "\n".join([f"{i+1}. {ideas[num-1]}" for i, num in enumerate(selection)])
        return '\n'.join([start_prompt, f"\n{idea_name}:\n{ideas_str}"])
    return set_idea(start_prompt, idea_name, ideas[selection[0]-1])

def set_idea(start_prompt, idea_name, idea_value):
    return '\n'.join([start_prompt, f"\n{idea_name}{idea_value.strip()}"])

def parse_list_selection(text: str) -> List[int]:
    return [int(item) for item in text.split(',')]

def brainstorm_and_set(
    start_prompt: str, ideas_prompt: str, idea_name: str, params: dict, 
    retries: int = 5, list: bool = False, multiple: bool = False) -> str:
    """
    Ask GPT3 to brainstorm ideas based on the ideas_prompt.

    start_prompt: the context of the story so far
    ideas_prompt: the prompt to ask GPT3 to brainstorm ideas
    idea_name: the name of the idea to set in the return updated start_prompt
    params: the parameters to pass to GPT3
    retries: the number of times to retry if GPT3 fails to generate a valid list of ideas
    list: if True, brainstorm a list of ideas, brainstorm a single idea
    multiple: if True, allow the user to select multiple ideas
    """
    r = 'more'
    retry = 0
    while r.strip().lower() == 'more':
        _, response = generate_response(start_prompt, ideas_prompt, params)
        text = response.choices[0].text
        if len(text.strip()) == 0:
            retry += 1
            logging.warning("GPT3 failed to generate a non-empty response.")
            if retry >= retries:
                logging.error("#######\nStart Prompt\n#######\n{}".format(start_prompt))
                raise Exception("Too many retries")
            continue
        if list:
            if not check_string_list(text):
                retry +=1
                print("GPT3 failed to generate a valid list of ideas")
                if retry > retries:
                    logging.error("#######\nStart Prompt\n#######\n{}".format(start_prompt))
                    raise Exception("Too many retries")
                continue
            print('1.'+text)
            if multiple:
                r = input("Select one or more ideas (comma separated integers): ")
            else:
                r = input("\nEnter a number to make a selection. If you want a new set of ideas, say 'More'. ")
        else:
            print(text.strip())
            r = input("\nYou can say 'Yes' if you're happy with this. If you want another idea, say 'More'.\n")
    if list:
        ideas = parse_string_list(text)
        return set_ideas_from_list(start_prompt, idea_name, ideas, parse_list_selection(r))
    return set_idea(start_prompt, idea_name, text)

def binary_query(prompt, question, verbose=False):
    """
    Ask GPT3 a Yes/No question based on the prompt and return True or False.
    """
    params = {'model':'text-davinci-002',
    'max_tokens':3,
    'temperature':0.7,
    'top_p':1.0,
    'frequency_penalty':0.0,
    'presence_penalty':0.0,
    'stop':None
    }
    query_prompt = prompt + "\n\n###\n\n" + question + " Answer with Yes or No:"
    response = complete(query_prompt, params)
    logging.debug("# " + question + " Answer: " + response.choices[0].text)
    if 'yes' in response.choices[0].text.lower():
        return True
    if 'no' in response.choices[0].text.lower():
        return False
    return None

def generate_synopsis(start_prompt: str, params: dict, retries: int = 3) -> str:
    """
    Ask GPT3 to generate a synopsis based on the start_prompt.
    """
    synopsis_start = "ACT 1\n1."
    synopsis_prompt = f"Write a detailed synopsis in three Acts.\n\n{synopsis_start}"
    retry = 0
    while retry < retries:
        _, response = generate_response(start_prompt, synopsis_prompt, params)
        synopsis = synopsis_start+response.choices[0].text
        logging.debug(synopsis)
        if check_synopsis(synopsis):
            return synopsis, '\n'.join([start_prompt, synopsis_prompt + response.choices[0].text])
        retry += 1
    raise Exception("Too many retries")

def check_synopsis(text: str) -> bool:
    """
    Check if the text is a valid synopsis.
    """
    if len(text.strip()) == 0:
        return False
    for i in range (3):
        if f"ACT {i+1}" not in text:
            return False
    return True

story_ideas_prompt = "Brainstorm story ideas:\n1."
antag_ideas_prompt = "Brainstorm antagonist ideas:\n1."
char_ideas_prompt = "Brainstorm and develop supporting characters:\n1."
develop_protag_prompt = "Develop the main character:"
develop_antag_prompt = "Name the antagonist and develop the character and their motivations:"
question_antag_prompt = "Has an antagonist been described above?"


if __name__ == "__main__":
    """
    Use chain of thought prompting to incrementally develop and write a story using GPT-3.

    ## Prompt Design ##
    STORY GENERATOR
    Our goal is to gather preferences from a customer and brainstorm children's story ideas.

    Genre: Children's {{genre}}
    Audience: Children ages 2-5
    Themes: {{themes}}
    Tones: {{tones}}
    Main character name: {{main_character_name}}

    Brainstorm story ideas:
    1.

    >> User chooses one or asks for more.

    Develop the main character:

    >> User can input, confirm or regenerate.

    Brainstorm and enumerate antagonist:

    >> User chooses one or asks for more

    Develop and name the antagonist:

    >> User can input, confirm or regenerate.

    Brainstorm and enumerate supporting characters:

    >> User can choose multiple or regenerate

    Write a detailed synopsis in three Acts.

    ACT I
    1.

    Then, use EDIT to revise each Act providing the following instructions: Convert ACT {{ACT_NUM}} into a written narrative for a children’s picture book.
    """
    # TO DO
    # Experiment with adding plot points
    # Fix issue with GPT-3 generating a blank antagonist development
    # Fix issue with GPT-3 generating more than is asked, e.g. multiple lists of ideas
    # Format the structure using # for headers and use this as a stop signal
    params = {'model':'text-davinci-002',
            'max_tokens':512,
            'temperature':1.0,
            'top_p':1.0,
            'frequency_penalty':0.0,
            'presence_penalty':0.0,
            'stop':None
            }

    develop_params = params.copy()
    #develop_params['stop'] = ['\n\n']
    #develop_params['temperature'] = 0.7
    test = True
    while True:

        if not test:
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
        else:
            pref = CustomerPreferences(
                genre="Children's " + "Fantasy", 
                themes=['Bravery', 'Friendship'], 
                tones=['Whimsical', 'Heartwarming'], 
                main_character_name='Rowan, a girl.'
            )
        prompt = make_start_prompt(pref)
        print(prompt)
          
        print("\nOkay, now we'll brainstorm some story ideas. Generating...\n")
        prompt = brainstorm_and_set(prompt, story_ideas_prompt, "Story idea: ", params, list=True)
        
        #print("\nGreat, now we'll develop the main character a bit more. What do you think about this...\n")
        #start_prompt = brainstorm_and_set(start_prompt, develop_protag_prompt, "Main character: ", develop_params)

        answer = binary_query(prompt, question_antag_prompt, verbose=True)
        if answer is None or not answer:
            print("\nNow we'll brainstorm some antagonist ideas. Generating...\n")
            prompt = brainstorm_and_set(prompt, antag_ideas_prompt, "Antagonist idea: ", params, list=True)

        print("\nGreat, now we'll develop the antagonist a bit more. What do you think about this...\n")
        prompt = brainstorm_and_set(prompt, develop_antag_prompt, "Antagonist: ", develop_params)

        # brainstorm and enumerate supporting characters
        print("\nNow we'll brainstorm some supporting characters. Generating...\n")
        prompt = brainstorm_and_set(prompt, char_ideas_prompt, "Supporting characters: ", params, list=True, multiple=True)
        print(prompt)

        # write a detailed synopsis in three Acts.
        print("\nNow we'll outline a detailed synopsis in three Acts.\n")
        synopsis, prompt = generate_synopsis(prompt, params)
        print(synopsis)
        with open("./data/synopsis.txt", "w") as f:
            f.write(prompt)

        # revise each Act using EDIT
        break