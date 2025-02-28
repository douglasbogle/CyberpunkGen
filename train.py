from datasets import Dataset
import os
import re
import torch
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from transformers import GPT2LMHeadModel, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from flask import Flask
from models import db, Video  # Import db from models
from config import Config  # Import your configuration file


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


class VideoTrainer:
    def __init__(self):
        self.device = 'cpu'  # No gpu to use :(, M2 is funky
        self.model_dir = './classified'  # Directory where the fine-tuned model will be/is saved
        self.tokenizer = AutoTokenizer.from_pretrained('gpt2')  # Auto-initialize tokenizer
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')  # Fine tune gpt2
        self.model.to(self.device)

        if self.tokenizer.pad_token is None:
            self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
            self.model.resize_token_embeddings(len(self.tokenizer))


    def get_data(self):
        with app.app_context():
            titles = Video.query.with_entities(Video.title).all()
            raw_titles = [title[0] for title in titles]  # Get Cyberpunk youtube titles stored in db

            # Add general english sentences to dataset to maintain language understanding
            with open('sentences.txt', 'r') as file:
                for line in file:
                    sentence = line.strip()
                    if sentence:
                        raw_titles.append('sentence: ' + sentence)
                        # prefix sentences accordingly

            return raw_titles


    def clean_text(self, text):
        # Remove non-alphanumeric characters except periods, spaces, colons, commas
        text = re.sub(r'[^A-Za-z0-9\s.:,]', '', text)
        text = text.lower().strip()
        return text


    def tokenize_dataset(self, raw_data):
        cleaned_data = [self.clean_text(title) for title in raw_data]  # Preprocess/cleanup titles
        dataset = Dataset.from_dict({"text": cleaned_data})
        tokenized_dataset = dataset.map(  # Use mapping to tokenize entire dataset
            lambda x: self.tokenizer(x['text'], padding="max_length", truncation=True, max_length=128), 
             batched=True
        )

        return tokenized_dataset
    

    def train(self):
        # Load dataset and tokenizer
        combined_data = self.get_data()
        tokenized_data = self.tokenize_dataset(combined_data)

        training_args = TrainingArguments(
            output_dir=self.model_dir,
            overwrite_output_dir=True,
            num_train_epochs=2,  # May overfit if too high, making answers TOO related to cyberpunk and forgetting plain english
            per_device_train_batch_size=4,
            learning_rate=3e-5,
            weight_decay=0.01,  # Add weight decay to prevent overfitting
            save_steps=5000,
            save_total_limit=3,
            logging_steps=100,
            evaluation_strategy='steps',
            eval_steps=5000,
            use_cpu=True
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_data,
            data_collator=DataCollatorForLanguageModeling(tokenizer=self.tokenizer, mlm=False)
        )

        trainer.train()
        # Save tokenizer too so we can actually use the fine tuned model
        self.tokenizer.save_pretrained(training_args.output_dir)


if __name__ == '__main__':  # Call train.py to fine tune gpt2, will take a LONG time
    trainer = VideoTrainer()
    trainer.train()

