import uuid  
import time  
from tenacity import retry, wait_random_exponential, stop_after_attempt  
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

  
class TextEmbedder:  
    def __init__(self, ai_foundry_endpoint, ai_foundry_key, text_embedding_model)  :    

        self.embeddings_client = EmbeddingsClient(  
            endpoint=ai_foundry_endpoint,  
            credential=AzureKeyCredential(ai_foundry_key),  
            model=text_embedding_model)      

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))  
    async def generate_embeddings(self, text):  
        response = self.embeddings_client.embed(  
             input=[text]
             )  
        return response.data[0].embedding
    
    async def vectorize_chunks(self, chunk_queue, vector_queue, worker_id, logger):  
        while True:  
            data = await chunk_queue.get()  
            if data is None:  # Sentinel to end the loop  
                chunk_queue.task_done()  
                break  
  
            blob_name, blob_uri, chunk, parent_id, page_number = data  
            chunk_id = str(uuid.uuid4())  
            logger.info(f"TextEmbedder {worker_id}: Embedding chunk {chunk_id} from document {blob_name} page {page_number}")  
            start_time = time.time()  
  
            # Generate embeddings  
            try:  
                vector = await self.generate_embeddings(chunk)  
                vectorization_time = time.time() - start_time  
                logger.info(f"TextEmbedder {worker_id}: Finished embedding in {vectorization_time:.2f} seconds")  
  
                document = {  
                    "parent_id": parent_id,  
                    "chunk_id": chunk_id,  
                    "chunk": chunk,  
                    "title" : blob_name,
                    "text_vector": vector,  
                    "page_number": page_number,  
                    "content_type": "text",  
                    "source_link": blob_uri,  
                }  
                await vector_queue.put(document)  
            except Exception as e:  
                logger.error(f"TextEmbedder {worker_id}: Error embedding chunk {chunk_id}: {e}")  
            finally:  
                chunk_queue.task_done()  