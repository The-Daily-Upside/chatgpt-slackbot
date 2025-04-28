import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load knowledge data
knowledge_df = pd.read_csv("knowledge_for_rag.csv")

# Setup Chroma client (New architecture)
chroma_client = chromadb.PersistentClient(path="./chroma_data")  

# Set embedding function
embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
)

# Create or get existing collection
knowledge_collection = chroma_client.get_or_create_collection(name="rag", embedding_function=embedding_fn)

# Prepare documents, metadatas, and ids
documents = knowledge_df['text'].tolist()
metadatas = knowledge_df.drop(columns=['text']).to_dict(orient='records')
ids = [str(row["id"]) for _, row in knowledge_df.iterrows()]

# Add documents to Chroma
knowledge_collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

# Persist the data to disk
chroma_client.persist()

print(f"✅ Successfully added {len(documents)} knowledge entries to Chroma!")