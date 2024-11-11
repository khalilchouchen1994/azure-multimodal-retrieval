from langchain_text_splitters import RecursiveCharacterTextSplitter  
import time  
  
class Chunker:  
    def __init__(self, chunk_size=2000, chunk_overlap=500):  
        self.chunk_size = chunk_size  
        self.chunk_overlap = chunk_overlap  
  
    async def chunk_text(self, text_queue, chunk_queue, csv_writer, worker_id, logger):  
        while True:  
            blob_name, text,parent_id = await text_queue.get()  
            if text is None:  # Sentinel to end the loop  
                break  
            logger.debug(f"Chunker {worker_id}:Chunking document {blob_name}")
            start_time = time.time()  
            splitter = RecursiveCharacterTextSplitter(  
                chunk_size=self.chunk_size,  
                chunk_overlap=self.chunk_overlap,  
                length_function=len,  
                is_separator_regex=False,  
            )  
            chunks = splitter.split_text(text)  
            chunk_time = time.time() - start_time  
            csv_writer.writerow([parent_id, None, "chunk_text", chunk_time, worker_id])  
  
            # Put each chunk into the queue  
            for chunk in chunks:  
                await chunk_queue.put((blob_name, chunk, parent_id))  
  
            text_queue.task_done()  
