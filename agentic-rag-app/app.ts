import indexAndStorage from "./load-index";
import loadAndQuery from "./query-paul";

function main(query: string) {
  console.log("======================================");
  console.log("Data Indexing....");
  indexAndStorage();
  console.log("Data Indexing Completed!");
  console.log("Please, Wait to get your response or SUBSCRIBE!");
  loadAndQuery(query);
}
const query = "What is Paul taking about?";
main(query);
