from sentence_transformers import SentenceTransformer
from pinecone_config import dense_index

dense_model = SentenceTransformer("intfloat/multilingual-e5-large")  # byo vector provides more control, Indexes with integrated embedding do not support updating or importing with text in Pinecone
NAMESPACE = "voice-chatbot"


def embed_dense(text):
    return dense_model.encode(text, normalize_embeddings=True).tolist()

def upsert_chunk(doc_id, text):
    dense_vec = embed_dense(text)
    dense_index.upsert(
        vectors=[{
            "id": doc_id,
            "values": dense_vec,
            "metadata": {"chunk_text": text}
        }],
        namespace=NAMESPACE
    )

def delete_chunk(doc_id):
    dense_index.delete(ids=[doc_id], namespace=NAMESPACE)

def search_chunks(query, top_k=3):
    dense_vec = embed_dense(query)
    results = dense_index.query(
        vector=dense_vec,
        namespace=NAMESPACE,
        top_k=top_k,
        include_metadata=True
    )
    return [match['metadata']['chunk_text'] for match in results['matches']]


