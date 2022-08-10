from storybook.base import NAME, set_ideas_from_list


def test_base():
    assert NAME == "storybook"

def test_set_ideas_from_list():
    start_prompt = 'Start Prompt'
    idea_name = 'Plot devices'
    ideas = ['a plot device', 'another plot device', 'a third plot device']
    selection = [1,3]
    out = set_ideas_from_list(start_prompt, idea_name, ideas, selection)
    actual = "Start Prompt\n\nPlot devices:\n1. a plot device\n2. a third plot device"
    assert out == actual