from transformers import GPT2LMHeadModel, AutoTokenizer
import torch

# Path to the directory where the fine-tuned model is saved
MODEL_PATH = './output/checkpoint-1104'

def load_model_and_tokenizer(model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = GPT2LMHeadModel.from_pretrained(model_path)
    return model, tokenizer


def generate_titles(model, tokenizer, prompts):
    model.eval()  # Set model to evaluation mode
    generated_titles = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt")
        attention_mask = inputs["attention_mask"] if "attention_mask" in inputs else None
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=attention_mask,
                max_length=25,  # Adjust as needed
                num_return_sequences=1,
                temperature=.7,  # Adjust temperature for randomness
                top_p=0.6,  # Nucleus sampling
                top_k=35,  # Top-K sampling
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        generated_title = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_titles.append(generated_title)
    return generated_titles



def main():
    # Load the fine-tuned model and tokenizer
    fine_tuned_model, fine_tuned_tokenizer = load_model_and_tokenizer(MODEL_PATH)
    
    # Load the pre-trained model and tokenizer
    pretrained_model = GPT2LMHeadModel.from_pretrained('gpt2')
    pretrained_tokenizer = AutoTokenizer.from_pretrained('gpt2')

    # Define some test prompts to evaluate the models
    test_prompts = [
        "Generate a general sentence cyberpunk sanvestian title",
    ]
    
    # Generate titles using the fine-tuned model
    fine_tuned_titles = generate_titles(fine_tuned_model, fine_tuned_tokenizer, test_prompts)

    # Generate titles using the pre-trained model
    pretrained_titles = generate_titles(pretrained_model, pretrained_tokenizer, test_prompts)

    print("Fine-tuned Model Results:")
    for prompt, title in zip(test_prompts, fine_tuned_titles):
        print(f"Prompt: {prompt}")
        print(f"Generated Title: {title}")
        print()

    print("Pre-trained Model Results:")
    for prompt, title in zip(test_prompts, pretrained_titles):
        print(f"Prompt: {prompt}")
        print(f"Generated Title: {title}")
        print()

if __name__ == '__main__':
    main()


