import random

def generate_customer_prompts(num_prompts):
    names = [('Rowan','boy'),('Charlotte','girl'),('Aiden','boy'),('Emily','girl'),('James','boy'),('Isabella','girl'), ('Logan','boy'),('Abigail','girl'),('Benjamin','boy'),('Aria','girl'),('Lucas','boy'),('Harper','girl'), ('Mateo','boy'),('Evelyn','girl'),('Elijah','boy'),('Elizabeth','girl'),('Oliver','boy'),('Sofia','girl'), ('Grayson','boy'),('Avery','girl'),('Jace','boy'),('Chloe','girl'),('Levi','boy'),('Natalie','girl'), (' Sebastian','boy'),('Zoey','girl'),('Xavier','boy'),('Addison','girl'),('Hayes','boy'),('Luna','girl'),('Kai','boy'),('Brooklyn','girl'),('Landon','boy'),('Paige','girl'),('Max','boy'),('Violet','girl'),('Theodore','boy'),('Claire','girl'),('Elliott','boy'),('Savannah','girl'),('Ryder','boy'),('Bella','girl'), ('George','boy'),('Aurora','girl'),('Miles','boy'),('Riley','boy')]
    ages = range(1,5)
    genres = ['adventure', 'comedy', 'fantasy', 'educational', 'sci-fi']
    themes = ['courage','honesty','compassion','gratitude','kindness','forgiveness','self-control','perseverance','patience']
    relationships = ['parent', 'grandparent', 'aunt', 'uncle']
    # generate a list of prompts by combining the above variables
    prompts = []
    for i in range(num_prompts):
        name = random.choice(names)
        age = random.choice(ages)
        genre = random.choice(genres)
        theme = random.choice(themes)
        relationship = random.choice(relationships)
        prompts.append(f'CUSTOMER is the {relationship} of a {age} year old {name[1]} named {name[0]} and wants a {genre} story that teaches about {theme}.')
    return prompts

if __name__ == "__main__":
    prompts = generate_customer_prompts(512)
    
    with open('customer_prompts.txt', 'a') as outfile:
        for prompt in prompts:
            outfile.write(prompt+'\n')

