import os
import requests
import json
import random
from tqdm import tqdm
from web import db
from web.models import User, Publication, Comment

if not os.path.exists('data/russian_words.json'):
    response = requests.get('https://raw.githubusercontent.com/danakt/russian-words/master/russian.txt')

    text = response.content.decode('cp1251')
    words = text.split()
    with open('data/russian_words.json', 'w') as f:
        json.dump(words, f)

else:
    with open('data/russian_words.json', 'r') as f:
        words = json.load(f)

user_ids = User.get()
if not user_ids:
    user_ids = [User(f'User{i}', 'Password').id for i in range(10)]

punctuation = ['_,', '_!', '_.', '_?', '"_"', '\'_\'', '(_)', ]

def get_word():
    return random.choice(words)

def add_punc(word):
    punc = random.choice(punctuation)
    return punc.replace('_', word)

def get_text():
     n_words = random.randint(10, 50)
     return ' '.join([
         add_punc(get_word()) if random.randint(1, 5) == 1 else get_word()
     for _ in range(n_words)])

for i in tqdm(range(1000)):
    n_images = random.randint(0, 4)
    image_paths = [f'path{i}_{j}' for j in range(n_images)]
    image_texts = [get_text() for _ in range(n_images)]
    pub = Publication(random.choice(user_ids), get_text(), image_paths, image_texts)
    n_comments = random.randint(0, 4)
    for _ in range(n_comments):
        Comment(get_text(), pub.id, random.choice(user_ids))