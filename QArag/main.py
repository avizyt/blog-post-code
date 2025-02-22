import os
from pathlib import Path

# Core haystack components
from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from haystack.components.joiners import BranchJoiner
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.converters import PyPDFToDocument
from haystack.components.routers import ConditionalRouter
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter

# ChromaDB integration
from haystack_integrations.document_stores.chroma import ChromaDocumentStore
from haystack_integrations.components.retrievers.chroma import (
    ChromaEmbeddingRetriever,
)

# Ollama integration
from haystack_integrations.components.embedders.ollama.document_embedder import (
    OllamaDocumentEmbedder,
)
from haystack_integrations.components.embedders.ollama.text_embedder import (
    OllamaTextEmbedder,
)
from haystack_integrations.components.generators.ollama import OllamaGenerator

# Duckduckgo search integration
from duckduckgo_api_haystack import DuckduckgoApiWebSearch


document_store = ChromaDocumentStore(persist_path="QApipeline/embeddings")
HERE = Path(__file__).resolve().parent
file_path = [HERE / "data" / Path(name) for name in os.listdir("QApipeline/data")]

embedder = OllamaDocumentEmbedder(
    model="nomic-embed-text", url="http://localhost:11434"
)


cleaner = DocumentCleaner()
splitter = DocumentSplitter()
file_converter = PyPDFToDocument()
writer = DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE)

indexing_pipeline = Pipeline()

# add component to pipeline
indexing_pipeline.add_component("embedder", embedder)
indexing_pipeline.add_component("converter", file_converter)
indexing_pipeline.add_component("cleaner", cleaner)
indexing_pipeline.add_component("splitter", splitter)
indexing_pipeline.add_component("writer", writer)

# connect component in pipeline
indexing_pipeline.connect("converter", "cleaner")
indexing_pipeline.connect("cleaner", "splitter")
indexing_pipeline.connect("splitter", "embedder")
indexing_pipeline.connect("embedder", "writer")


# draw pipeline
image_param = {
    "format": "img",
    "type": "png",
    "theme": "forest",
    "bgColor": "f2f3f4",
}
# indexing_pipeline.draw("indexing_pipeline.png", params=image_param)  # type: ignore


routes = [
    {
        "condition": "{{'no_answer' in replies[0]}}",
        "output": "{{query}}",
        "output_name": "go_to_websearch",
        "output_type": str,
    },
    {
        "condition": "{{'no_answer' not in replies[0]}}",
        "output": "{{replies[0]}}",
        "output_name": "answer",
        "output_type": str,
    },
]

router = ConditionalRouter(routes=routes)

websearch = DuckduckgoApiWebSearch(top_k=5)


template_qa = """
Given ONLY the following information, answer the question.
Do not your knowledge.
If the answer is not contained within the documents reply with "no_answer".
If the answer is contained within the documents, start the answer with "FROM THE KNOWLEDGE BASE: ".

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ query }}?
"""
template = """
Given ONLY the following context, answer the question.
If the answer is not contained within the documents reply with "no_answer".
If the answer is contained within the documents, start the answer with "FROM THE KNOWLEDGE BASE: ".

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{ query }}
"""

template_websearch = """
Answer the following query given the documents retrieved from the web.
Start the answer with "FROM THE WEB: ".

Documents:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Query: {{query}}

"""
prompt_qa = PromptBuilder(template=template_qa)
prompt_builder_websearch = PromptBuilder(template=template_websearch)

prompt_joiner = BranchJoiner(str)


query_pipeline = Pipeline()

# add component to pipeline
query_pipeline.add_component("text_embedder", OllamaTextEmbedder())
query_pipeline.add_component(
    "retriever", ChromaEmbeddingRetriever(document_store=document_store)
)
query_pipeline.add_component("prompt_builder", prompt_qa)
query_pipeline.add_component("prompt_joiner", prompt_joiner)
query_pipeline.add_component(
    "llm",
    OllamaGenerator(model="llama3.2:3b", timeout=500, url="http://localhost:11434"),
)
query_pipeline.add_component("router", router)
query_pipeline.add_component("websearch", websearch)
query_pipeline.add_component("prompt_builder_websearch", prompt_builder_websearch)


# connect component in pipeline
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever", "prompt_builder.documents")
query_pipeline.connect("prompt_builder", "prompt_joiner")
query_pipeline.connect("prompt_joiner", "llm")
query_pipeline.connect("llm.replies", "router.replies")
query_pipeline.connect("router.go_to_websearch", "websearch.query")
query_pipeline.connect("router.go_to_websearch", "prompt_builder_websearch.query")
query_pipeline.connect("websearch.documents", "prompt_builder_websearch.documents")
query_pipeline.connect("prompt_builder_websearch", "prompt_joiner")

# run pipeline
# indexing_pipeline.run({"converter": {"sources": file_path}})

# query_pipeline.draw("agentic_qa_pipeline.png", params=image_param)  # type: ignore


# query = "what is the current affairs on National Human rights commission?"
# query = """
# A battery of 10 V and negligible internal resistance is
# connected across the diagonally opposite corners of a cubical network
# consisting of 12 resistors each of resistance 1 W (Fig. 3.16). Determine
# the equivalent resistance of the network and the current along each
# edge of the cube.
# """
# result = query_pipeline.run({"text_embedder": {"text": query}})
# print(result["retriever"]["documents"][0].content)

# response = query_pipeline.run(
#     {"text_embedder": {"text": query}, "prompt_builder": {"query": query}}
# )
# print(response["llm"]["replies"][0])


def get_answer(query: str):
    response = query_pipeline.run(
        {
            "text_embedder": {"text": query},
            "prompt_builder": {"query": query},
            "router": {"query": query},
        }
    )
    return response["router"]["answer"]


if __name__ == "__main__":
    query = (
        "Tell me what is DRIFT OF ELECTRONS AND THE ORIGIN OF RESISTIVITY from the book"
    )
    print(get_answer(query))
