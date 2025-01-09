from azure.search.documents import SearchIndexingBufferedSender  
from azure.core.credentials import AzureKeyCredential  
  
class FileUploader:  
    def __init__(self, service_endpoint, index_name, api_key):  
        # Initialize the SearchIndexingBufferedSender  
        self.sender = SearchIndexingBufferedSender(  
            endpoint=service_endpoint,  
            index_name=index_name,  
            credential=AzureKeyCredential(api_key),  
            auto_flush_interval=2,  # Automatically flush every 2 seconds  
            on_error=self.on_error,  
        )  
  
    def on_error(self, index_documents_batch, index_documents_result):  
        # Handle errors during indexing  
        for doc, result in zip(index_documents_batch, index_documents_result):  
            if not result.succeeded:  
                print(f"Failed to index document: {doc.get('chunk_id')} - Error: {result.error.message}")  
  
    async def upload_documents(self, vector_queue, worker_id, logger):  
        while True:  
            document = await vector_queue.get()  
            if document is None:  # Sentinel to end the loop  
                vector_queue.task_done()  
                break  
  
            logger.info(f"Uploader {worker_id}: Uploading chunk {document['chunk_id']} of document {document['parent_id']}")  
  
            try:  
                # Prepare the document for indexing  
                index_document = {  
                    "parent_id": document["parent_id"],  
                    "chunk_id": document["chunk_id"],  
                    "title": document.get("title", ""),  
                    "chunk": document.get("chunk", ""),  
                    "text_vector": document.get("text_vector"),  
                    "image_vector": document.get("image_vector"),  
                    "page_number": document.get("page_number"),  
                    "content_type": document.get("content_type"),  
                    "source_link": document.get("source_link"),  
                }  
  
                # Remove fields with None values to prevent indexing errors  
                index_document = {k: v for k, v in index_document.items() if v is not None}  
  
                # Upload the document  
                self.sender.upload_documents([index_document])  
                logger.info(f"Uploader {worker_id}: Successfully uploaded {document['chunk_id']}")  
            except Exception as e:  
                logger.error(f"Uploader {worker_id}: Error uploading document {document['chunk_id']}: {e}")  
            finally:  
                vector_queue.task_done()  
  
    async def close(self):  
        # Flush any remaining documents and close the sender  
        self.sender.close()