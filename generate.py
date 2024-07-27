import re
from transformers import AutoTokenizer, GPT2LMHeadModel
import torch


class TitleGenerator:
    def __init__(self):
        #FINE_TUNED_PATH = './output/checkpoint-1104'
        #FINE_TUNED_PATH = './results'
        #FINE_TUNED_PATH = './final'
        FINE_TUNED_PATH = './classified'

        # Initialize fine-tuned model
        self.fine_tuned_tokenizer = AutoTokenizer.from_pretrained(FINE_TUNED_PATH)
        self.fine_tuned_model = GPT2LMHeadModel.from_pretrained(FINE_TUNED_PATH)
        self.fine_tuned_model.to('cpu')

        # Initialize pre-trained model
        self.pretrained_tokenizer = AutoTokenizer.from_pretrained('gpt2')
        self.pretrained_model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.pretrained_model.to('cpu')


    def gen_titles(self, prompt, temperature, top_k, top_p):
        fine_tuned_titles = self.generate_with_model(self.fine_tuned_model, self.fine_tuned_tokenizer, prompt, temperature, top_k, top_p)
        pretrained_titles = self.generate_with_model(self.pretrained_model, self.pretrained_tokenizer, prompt, temperature, top_k, top_p)

        return fine_tuned_titles, pretrained_titles

    def generate_with_model(self, model, tokenizer, prompt, temperature, top_k, top_p):
        model.eval()
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to('cpu')
        attention_mask = inputs["attention_mask"].to('cpu') if "attention_mask" in inputs else None

        with torch.no_grad():
            output = model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_length=30,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                num_return_sequences=1,
                do_sample=True
            )

        # Decode and cleanup titles,  DONT REMOVE PROMPT
        titles = [tokenizer.decode(output_seq, skip_special_tokens=True) for output_seq in output]
        return [self.postprocess_title(title, prompt) for title in titles]
        

    def postprocess_title(self, title, prompt):
        title = title[len(prompt):]  # Remove the prompt from the beginning
        title = title.capitalize()
        title = re.sub(r'\s+', ' ', title)
        title = title.strip()
        return title
