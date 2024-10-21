from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the tokenizer and model
tokenizer  = AutoTokenizer.from_pretrained("nvidia/Nemotron-Mini-4B-Instruct")
model = AutoModelForCausalLM.from_pretrained("nvidia/Nemotron-Mini-4B-Instruct")

# Use the prompt template
messages = [
    {
        "role": "system",
        "content": "You are friendly chatbot, reply on style of a Professor",
    },
    {"role": "user", "content": "What is Quantum Entanglement?"},
 ]
tokenized_chat = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")

outputs = model.generate(tokenized_chat, max_new_tokens=128)
print(tokenizer.decode(outputs[0]))