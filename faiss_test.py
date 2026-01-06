import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pandas as pd

# 1. Load a pre-trained model to create word/sentence embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Define your vocabulary
data = {
    'Name': ['Lukas', 'Sofia', 'Hiroshi', 'Marta', 'Yannis', np.nan, 'Elena'],
    'City': ['Berlin', 'Madrid', 'Tokyo', 'Warsaw', 'Athens', 'Oslo', 'Lisbon']
}

# Create the DataFrame
df = pd.DataFrame(data)

word_embeddings = model.encode(df['City']).astype('float32')
print(word_embeddings.shape)
# 3. Initialize the FAISS index
# 'd' is the dimension of the vectors (384 for this specific model)
d = word_embeddings.shape[1]
index = faiss.IndexFlatL2(d) 

# 4. Add vectors to the index
index.add(word_embeddings)

# 5. Search for the top 2 most similar words to "smartphone"
query_text = ["smartphone"]
query_embedding = model.encode(query_text).astype('float32')

distances, indices = index.search(query_embedding, k=1)

# Output results
print(f"Query: {query_text[0]}")
for i in range(len(indices[0])):
    print(f"Match: {df['City'][i]} (Distance: {distances[0][i]:.4f})")