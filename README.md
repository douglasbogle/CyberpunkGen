# Cyberpunk YouTube Title Generator

I wanted to learn more about Machine Learning so I decided to fine tune an LLM (gpt2, yay free) to see if I could 
make a noticable difference in text it generates. Specifically, I decided to feed it Cyberpunk 2077 YouTube titles
(great game), as well as English sentences for its dataset. This is where the project got very interesting. It seems
that, if just trained on titles, the model would severely overfit to Cyberpunk 2077 YouTube titles, forgetting basic 
English. To remedy this, I attempted to give it English sentences as well, and experiment with prefixing these
sentences as well as the Cyberpunk Titles. Specifically, I prefixed the sentences with 'sentence: ' and the YouTube
titles with 'category: '. Knowing this (and I invite the user to do this too) I then experimented with prefixing
generation prompts with things that mimicked the training prefixes. 

Doing all of this was a lot of fun, and there is so much more to explore. My project also lets users explore generation p
arameters such as temperature, top k, and top p. After installing requirements just run app.py to explore the project! I will 
continue to explore this topic and would love to work with a more recent model as well as learn more about how to improve my 
training process!

## Table of Contents


- [Requirements](#requirements)


## Requirements

Before you begin, ensure you have the following installed:

- Python 3.6+
- Flask
- SQLAlchemy
- Transformers
- Datasets
- torch

To install these dependencies, run:
```sh
pip install Flask SQLAlchemy transformers datasets torch
