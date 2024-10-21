import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from threading import Thread
import time

class PirateBot:
    def __init__(self, model_name="nvidia/Nemotron-Mini-4B-Instruct"):
        print("Ahoy! Yer pirate bot be loadin' the model. Stand by, ye scurvy dog!")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Move model to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        print(f"Arrr! The model be ready on {self.device}!")
        
        self.messages = [
            {
                "role": "system",
                "content": "You are a friendly chatbot who always responds in the style of a pirate",
            }
        ]

    def generate_response(self, user_input, max_new_tokens=1024):
        self.messages.append({"role": "user", "content": user_input})
        
        tokenized_chat = self.tokenizer.apply_chat_template(
            self.messages, 
            tokenize=True, 
            add_generation_prompt=True, 
            return_tensors="pt"
        ).to(self.device)

        streamer = TextIteratorStreamer(self.tokenizer, timeout=10., skip_prompt=True, skip_special_tokens=True)
        
        generation_kwargs = dict(
            inputs=tokenized_chat,
            max_new_tokens=max_new_tokens,
            streamer=streamer,
            do_sample=True,
            top_p=0.95,
            top_k=50,
            temperature=0.7,
            num_beams=1,
        )

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        print("Pirate's response: ", end="", flush=True)
        generated_text = ""
        for new_text in streamer:
            print(new_text, end="", flush=True)
            generated_text += new_text
            time.sleep(0.05)  # Add a small delay for a more natural feel
        print("\n")

        self.messages.append({"role": "assistant", "content": generated_text.strip()})
        return generated_text.strip()

    def chat(self):
        print("Ahoy, matey! I be yer pirate chatbot. What treasure of knowledge ye be seekin'?")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'goodbye']:
                print("Farewell, ye landlubber! May fair winds find ye!")
                break
            try:
                self.generate_response(user_input)
            except Exception as e:
                print(f"Blimey! We've hit rough seas: {str(e)}")

if __name__ == "__main__":
    bot = PirateBot()
    bot.chat()