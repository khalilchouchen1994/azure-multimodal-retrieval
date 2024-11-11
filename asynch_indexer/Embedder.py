from tenacity import retry, wait_random_exponential, stop_after_attempt 
from openai import AzureOpenAI
import uuid 
import time

class Embedder: 

    def __init__(self, aoai_key, aoai_endpoint, aoai_api_version="2024-02-01"):  
        self.aoai_client = AzureOpenAI(  
            api_key=aoai_key,  
            api_version=aoai_api_version,  
            azure_endpoint=aoai_endpoint  
        )  
  
    @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(10))  
    def generate_embeddings(self, text):  
        response = self.aoai_client.embeddings.create(input=[text], model="text-embedding-3-large").data[0].embedding  
        return response  
  
    async def vectorize_chunks(self, chunk_queue, vector_queue, csv_writer, worker_id, logger):  
        while True:  
            blob_name, chunk, parent_id = await chunk_queue.get() 
            if chunk is None:  # Sentinel to end the loop  
                break  
            chunk_id = str(uuid.uuid4())  
            logger.debug(f"Embedder {worker_id}: Embedding chunck {chunk_id} from document {blob_name}")
            start_time = time.time()  
            vector = self.generate_embeddings(chunk)  
            vectorization_time = time.time() - start_time  
            csv_writer.writerow([parent_id, chunk_id, "embedding", vectorization_time, worker_id])  
  
            document = {  
                "parent_id": parent_id,  
                "chunk_id": chunk_id,  
                "chunk": chunk,  
                "vector": vector  
            }  
  
            await vector_queue.put(document)  
            chunk_queue.task_done()  

