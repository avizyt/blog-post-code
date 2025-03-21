import {
  Settings,
  storageContextFromDefaults,
  VectorStoreIndex,
} from "llamaindex";
import constant from "./constant";
import { Ollama, OllamaEmbedding } from "@llamaindex/ollama";
import { agent } from "llamaindex";

const llama3 = new Ollama({
  model: "llama3.2:1b",
});

const nomic = new OllamaEmbedding({
  model: "nomic-embed-text",
});

Settings.llm = llama3;
Settings.embedModel = nomic;

async function loadAndQuery(query: string) {
  try {
    // load the stored index from persistent storage
    const storageContext = await storageContextFromDefaults({
      persistDir: constant.STORAGE_DIR,
    });

    /// load the existing index
    const index = await VectorStoreIndex.init({ storageContext });

    // create a retriever and query engine
    const retriever = index.asRetriever();
    const queryEngine = index.asQueryEngine({ retriever });

    const tools = [
      index.queryTool({
        metadata: {
          name: "paul_graham_essay_tool",
          description: `This tool can answer detailed questions about the essay by Paul Graham.`,
        },
      }),
    ];
    const ragAgent = agent({ tools });

    // query the stored embeddings
    const response = await queryEngine.query({ query });
    let toolResponse = await ragAgent.run(query);

    console.log("Response: ", response.message);
    console.log("Tool Response: ", toolResponse);
  } catch (error) {
    console.log("Error during retrieval: ", error);
  }
}

export default loadAndQuery;
