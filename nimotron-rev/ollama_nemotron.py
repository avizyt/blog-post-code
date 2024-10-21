from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_ollama.chat_models import ChatOllama

# template = """Question: {question}

# Answer: Let's think step by step."""

# prompt = ChatPromptTemplate.from_template(template)

# model = OllamaLLM(model="nemotron-mini")

# chain = prompt | model

# print(chain.invoke({"question": "What is LangChain?"}))

llm = ChatOllama(
    model="nemotron-mini",
    temperature=0.8,
    num_predict=256,
)


messages = [
    ("system", "You are a helpful translator. Translate the user sentence to French."),
    ("human", "I love programming."),
]
response = llm.invoke(messages)
print(response)
