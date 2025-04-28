import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load knowledge data
knowledge_df = pd.read_csv("knowledge_for_rag.csv")

# Setup Chroma client (File-based backend)
chroma_client = chromadb.Client(
    chromadb.config.Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./chroma_data"  # Directory to store Chroma data
    )
)

# Set embedding function
embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
)

# Create or get existing collection
try:
    knowledge_collection = chroma_client.get_collection(name="rag", embedding_function=embedding_fn)
except:
    knowledge_collection = chroma_client.create_collection(name="rag", embedding_function=embedding_fn)

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