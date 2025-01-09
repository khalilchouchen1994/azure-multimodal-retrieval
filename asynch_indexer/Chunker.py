from langchain.text_splitter import RecursiveCharacterTextSplitter  
import time  
  
class Chunker:  
    def __init__(self, chunk_size=2000, chunk_overlap=500):  
        self.chunk_size = chunk_size  
        self.chunk_overlap = chunk_overlap  
  
    async def chunk_text(self, text_queue, chunk_queue, worker_id, logger):  
        while True:  
            data = await text_queue.get()  
            if data is None:  # Sentinel to end the loop  
                text_queue.task_done()  
                break  
  
            blob_name, blob_uri, text, parent_id, page_number = data  
            logger.info(f"Chunker {worker_id}: Chunking document {blob_name} page {page_number}")  
  
            start_time = time.time()  
            splitter = RecursiveCharacterTextSplitter(  
                chunk_size=self.chunk_size,  
                chunk_overlap=self.chunk_overlap,  
                length_function=len  
            )  
            chunks = splitter.split_text(text)  
            chunk_time = time.time() - start_time  
            logger.info(f"Chunker {worker_id}: Finished chunking in {chunk_time:.2f} seconds")  
  
            # Put each chunk into the chunk queue  
            for chunk in chunks:  
                await chunk_queue.put((blob_name, blob_uri, chunk, parent_id, page_number))  
  
            text_queue.task_done()  