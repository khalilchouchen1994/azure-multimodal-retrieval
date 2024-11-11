from azure.search.documents import SearchIndexingBufferedSender  
from azure.core.credentials import AzureKeyCredential  
import time
  
class FileUploader:  
    def __init__(self, service_endpoint, index_name, key):  
        self.sender_async = SearchIndexingBufferedSender(  
            endpoint=service_endpoint,  
            index_name=index_name,  
            credential=AzureKeyCredential(key),  
            on_error=self.on_error,  
            auto_flush_interval=5  
        )  
  
    def on_error(self, result):  
        logger.error(f"Failed to index document: {result['title']} {result['chunk_id']}")  
  
    async def upload_documents(self, vector_queue, logger, csv_writer, worker_id):  
        while True:  
            document = await vector_queue.get()  
            if document is None:  # Sentinel to end the loop  
                break  
            logger.debug(f"Uploader {worker_id}:Uploading chunck {document['chunk_id']} of document {document['parent_id']}")
            start_time = time.time()  
            try:  
                self.sender_async.upload_documents([document])  
                operation_time = time.time() - start_time  
                csv_writer.writerow([document['parent_id'], document['chunk_id'], "pushing to index", operation_time, worker_id])
                vector_queue.task_done()    
            except Exception as e:  
                logger.error(f"Error uploading document {document.get('title', 'unknown')} {document['chunk_id']}: {e}")  
  
    async def close(self):  
        self.sender_async.close()  
