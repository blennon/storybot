# Storybot

Chatbot to help you craft a story starring your kid

Inspired by and forked from https://github.com/daveshap/DalleHelperBot

# How to run from scratch

1. Run synthesize_convos.py to generate synthetic conversations between STORYBOT and CUSTOMER for CUSTOMER to describe what they want in the story.
2. Run main.py and use synthesize_synopses to generate story synopses based on these converations
3. Filter out "bad" synthetic data, e.g. too short
4. Run main.py and use prepare_finetune_data()
4. Create a fine tuned model from prompt to synopses
5. Run chatbot.py using this fine tuned model