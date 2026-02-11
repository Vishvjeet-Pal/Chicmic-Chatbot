from vector_data import vector_store

print(vector_store._collection.count())
docs = vector_store.similarity_search("leave policy", k=5)
for d in docs:
    print("----")
    print(d.metadata)
    print(d.page_content)
