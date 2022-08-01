"""
Unfinished experiment. The basic idea is that we create two GPT-3 powered agents, one for writing
and one for critiquing. The writer iteratively incorporates the critic's response into the story.

The critic can be fine tuned, e.g. https://github.com/daveshap/CreativeWritingCoach/tree/main/stories
"""

synopsis_template = """
<<UUID>>
<<CONVO>>

Based on the conversation above, write a detailed synopsis for the story. Include the name of the characters, the setting, the antagonist, the plot, and the ending.
"""

critic_template = """
<<UUID>>
You are a creative writing coach. Critics are looking for a creative and fully fleshed out synopsis of a story.

SYNOPOSIS
<<SYNOPSIS>>

What areas of the SYNOPSIS need to be further developed?
"""

writer_template = """
<<UUID>>
You are an author and creative writer. You provided a creative writing coach with the following synopsis:
<<SYNOPSIS>>

The creative writing coach wants to improve the following areas of the synopsis:
<<CRITIQUE>>

Develop these areas of the synopsis.
"""

template = """
ORIGINAL SYNOPSIS
<<SYNOPSIS>>

NEW IDEAS
<<IDEAS>>

Write a new synopsis using these new ideas.
"""

if __name__ == "__main__":
    critic_prompt = critic_template.replace('<<SYNOPSIS>>', response.choices[0].text).replace('<<UUID>>', str(uuid4()))
    critic_response = complete(critic_prompt, params, max_retry=1)
    print(critic_response.choices[0].text)

    writer_prompt = writer_template.replace('<<SYNOPSIS>>', synopsis_response.choices[0].text).replace('<<UUID>>', str(uuid4())).replace('<<CRITIQUE>>', critic_response.choices[0].text)
    synopsis_response = complete(writer_prompt, params, max_retry=1)
    print(synopsis_response.choices[0].text)

    og_synopsis = """The story is about a strong female character who overcomes challenges. The character's name is Harper and she is three years old. Harper loves to play make believe and dress up. The story takes place in Harper's imagination. The antagonist is a mean character who tries to stop Harper from being brave and never giving up. In the end, Harper defeats the antagonist and learns the importance of being brave and never giving up."""
    prompt = template.replace('<<SYNOPSIS>>', og_synopsis).replace('<<IDEAS>>', synopsis_response.choices[0].text)
    response = complete(prompt, params, max_retry=1)
    print(response.choices[0].text)