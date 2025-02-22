from duckduckgo_api_haystack import DuckduckgoApiWebSearch

websearch = DuckduckgoApiWebSearch(top_k=2)

results = websearch.run("What is the mass of Proton and Neutron?")

documents = results["documents"]
links = results["links"]
print(documents)
print(links)
