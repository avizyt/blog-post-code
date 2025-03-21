import { agent, Settings, tool } from "llamaindex";
import { z } from "zod";
import { Ollama, OllamaEmbedding } from "@llamaindex/ollama";
import { Document, VectorStoreIndex } from "llamaindex";
import fs from "fs/promises";

const llama3 = new Ollama({
  model: "llama3.2:1b",
});

// const nomic = new OllamaEmbedding({
//   model: "nomic-embed-text",
// });

// Settings.llm = llama3;
// Settings.embedModel = nomic;

const addNumbers = tool({
  name: "addNubers",
  description: "use this function to sun two numbers",
  parameters: z.object({
    a: z.number().describe("The first number"),
    b: z.number().describe("The second number"),
  }),
  execute: ({ a, b }: { a: number; b: number }) => `${a + b}`,
});

const divideNumbers = tool({
  name: "divideNumber",
  description: "use this function to divide two numbers",
  parameters: z.object({
    a: z.number().describe("The dividend a to divide"),
    b: z.number().describe("The divisor b to divide by"),
  }),
  execute: ({ a, b }: { a: number; b: number }) => `${a / b}`,
});

async function main(query: string) {
  const mathAgent = agent({
    tools: [addNumbers, divideNumbers],
    llm: llama3,
    verbose: false,
  });

  const response = await mathAgent.run(query);
  console.log(response.data);
}
const query =
  "If total number of boy in a class is 50 and girls is 30, what is the total number of students in the class?";
void main(query).then(() => {
  console.log("Done");
});
