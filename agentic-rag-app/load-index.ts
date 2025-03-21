import { Settings, storageContextFromDefaults } from "llamaindex";
import { Ollama, OllamaEmbedding } from "@llamaindex/ollama";
import { Document, VectorStoreIndex } from "llamaindex";
import fs from "fs/promises";
import constant from "./constant";

const llama3 = new Ollama({
  model: "llama3.2:1b",
});

const nomic = new OllamaEmbedding({
  model: "nomic-embed-text",
});

Settings.llm = llama3;
Settings.embedModel = nomic;

async function indexAndStorage() {
  try {
    // set up persistance storage
    const storageContext = await storageContextFromDefaults({
      persistDir: constant.STORAGE_DIR,
    });

    // load docs
    const essay = await fs.readFile(constant.DATA_FILE, "utf-8");
    const document = new Document({
      text: essay,
      id_: "essay",
    });

    // create and persist index
    await VectorStoreIndex.fromDocuments([document], {
      storageContext,
    });

    console.log("index and embeddings stored successfully!");
  } catch (error) {
    console.log("Error during indexing: ", error);
  }
}

export default indexAndStorage;
