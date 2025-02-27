import os
from dotenv import load_dotenv
import chromadb
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core import Settings
from copy import deepcopy
from llama_index.core.schema import TextNode
from llama_index.core import SimpleDirectoryReader
import nest_asyncio
from llama_index.core import SummaryIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.ollama import Ollama

from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

load_dotenv()

# LLAMAPARSE_API_KEY = os.getenv("LLAMAPARSE_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")


documents = SimpleDirectoryReader("./data").load_data()

embed_model = OllamaEmbedding(model_name="nomic-embed-text")
llm = Gemini(api_key=GEMINI_API_KEY, model_name="models/gemini-2.0-flash")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("financial_collection")  # type: ignore

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


# vector_index = VectorStoreIndex.from_documents(documents=documents, storage_context=storage_context, embed_model=embed_model)

vector_index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store, embed_model=embed_model
)


def get_page_nodes(docs, separator="\n---\n"):
    """Split each document into page node, by separator."""
    nodes = []
    for doc in docs:
        doc_chunks = doc.text.split(separator)
        for doc_chunk in doc_chunks:
            node = TextNode(
                text=doc_chunk,
                metadata=deepcopy(doc.metadata),
            )
            nodes.append(node)

    return nodes


file_path = "./data/Motorsport_Games_Financial_report.pdf"

len(documents)

page_nodes = get_page_nodes(documents)


query_engine = vector_index.as_query_engine(llm=llm, similarity_top_k=5)

response = query_engine.query("what is the revenue of on 2022 Year Ended December 31?")

print(str(response))

# ![image.png](attachment:image.png)


response = query_engine.query(
    "what is the Net Loss Attributable to Motossport Games Inc. on 2022 Year Ended December 31?"
)

print(str(response))


# ![image.png](attachment:image.png)


response = query_engine.query(
    "What are the Liquidity and Going concern for the Company on December 31, 2023"
)

print(str(response))


response = query_engine.query(
    "What was revenues on Gaming for the Year Ended on December 31?"
)

print(str(response))


response = query_engine.query(
    "Summarise the Principal versus agent considerations of the company?"
)

print(str(response))


# ![image.png](attachment:image.png)


response = query_engine.query(
    "Summarise the Net Loss Per Common Share of the company with financial data?"
)

print(str(response))


# ![image.png](attachment:image.png)


response = query_engine.query(
    "Summarise Property and equipment consist of the following balances as of December 31, 2023 and 2022 of the company with financial data?"
)

print(str(response))


# ![image.png](attachment:image.png)


response = query_engine.query(
    "Summarise The Intangible Assets on December 21, 2023 of the company with financial data?"
)

print(str(response))

response = query_engine.query(
    "What are leases of the company with yearwise financial data?"
)

print(str(response))

# ![image.png](attachment:image.png)
response = query_engine.query(
    "Plot chart of Accrued expenses and other liabilities using the financial data of the company"
)

print(str(response))


#

# ![image.png](attachment:image.png)


# ## Query using LLama3.2


local_llm = Ollama(model="llama3.2:1b", request_timeout=1000.0)
local_query_engine = vector_index.as_query_engine(llm=local_llm, similarity_top_k=3)


response = local_query_engine.query(
    "Plot chart of Accrued expenses and other liabilities using the financial data of the company"
)

print(str(response))


# ## Summary Index


nest_asyncio.apply()


summary_index = SummaryIndex(nodes=page_nodes)

summary_query_engine = summary_index.as_query_engine(
    llm=llm, response_mode="tree_summarize", use_async=True
)


summary_tool = QueryEngineTool.from_defaults(
    query_engine=summary_query_engine,
    description=(
        "Useful for summarization questions related to Motorsport Games Company."
    ),
)


vector_tool = QueryEngineTool.from_defaults(
    query_engine=local_query_engine,
    description=(
        "Useful for retriving specific context from the Motorsport Games Company."
    ),
)


adv_query_engine = RouterQueryEngine(
    llm=llm,
    selector=LLMSingleSelector.from_defaults(llm=llm),
    query_engine_tools=[summary_tool, vector_tool],
    verbose=True,
)


response = adv_query_engine.query(
    "Summarize the charts describing the revenure of the company."
)
print(str(response))

# response = adv_query_engine.query(
#     "What is the consolidated balance sheet of the company?"
# )
# print(str(response))

response = adv_query_engine.query("What is the Total Assets of the company Yearwise?")
print(str(response))
