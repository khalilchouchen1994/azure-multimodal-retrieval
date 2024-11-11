import asyncio  
import csv  
import logging  
import time  


from .FileReader import FileReader
from .Chunker import Chunker
from .Embedder import Embedder
from .FileUploader import FileUploader 

from azure.identity import DefaultAzureCredential  

from azure.storage.blob import BlobServiceClient

  
class AsynchronousIndexer:  
    def __init__(self, index_name, ai_search_endpoint, ai_search_key, storage_account_name, storage_account_container_name, aoai_endpoint, aoai_key):  
        
        # Initialize the Azure credentials and clients for AI saerch 
        self.index_name = index_name  
        self.ai_search_endpoint = ai_search_endpoint  
        self.ai_search_key = ai_search_key  
        #self.credential = AzureKeyCredential(self.key) 
        
        # Initialize the Azure credentials and clients for AOAI
        self.aoai_endpoint = aoai_endpoint  
        self.aoai_key = aoai_key  
          
        # Initialize the Azure credentials and clients for storage  
        self.storage_account_url = f"https://{storage_account_name}.blob.core.windows.net"  
        self.storage_account_container_name= storage_account_container_name
        self.credential = DefaultAzureCredential()  
        blob_service_client = BlobServiceClient(account_url=self.storage_account_url, credential= self.credential)  
        self.storage_container_client = blob_service_client.get_container_client(self.storage_account_container_name)  
        
        # Initialize the ReadingSkillset  
        self.file_reader = FileReader()  

        # Initialize the ChunkingSkillSet  
        self.chuncker = Chunker()
          
        # Initialize the EmbeddingSkillset  
        self.embedder = Embedder(self.aoai_key, self.aoai_endpoint)  
          
        # Initialize the DocumentUploader  
        self.file_uploader = FileUploader(self.ai_search_endpoint, self.index_name, self.ai_search_key)  
          
        # Set up logging  
        logging.basicConfig(level=logging.WARNING)  
        self.logger = logging.getLogger(__name__)  
          
        # Initialize queues
        self.file_queue = asyncio.Queue()   
        self.text_queue = asyncio.Queue()  
        self.chunk_queue = asyncio.Queue()  
        self.vector_queue = asyncio.Queue() 

    async def run_indexing(self,):  
        start_time = time.time()  
        blob_list = list(self.storage_container_client.list_blobs())  
        # Set up CSV writer for unified logging  
        csv_file = "operation_times.csv"  
        with open(csv_file, mode='w', newline='') as file:  
            csv_writer = csv.writer(file)  
            csv_writer.writerow(["parent_id", "chunk_id", "operation_type", "time_seconds", "worker_id"]) 

            # Populate the file queue with blobs  
            for blob in blob_list:  
                if blob.name.endswith('.pdf'):  
                    await self.file_queue.put(blob)   
  
            # Create worker tasks for reading, chunking, vectorizing, and uploading  
            num_workers = 5  
            read_tasks = [  
                asyncio.create_task(self.file_reader.read_pdf(self.storage_container_client, self.file_queue, self.text_queue, csv_writer, f"read_worker_{i}", self.logger))  
                for i in range(num_workers)  
            ] 
            chunking_workers = [  
                asyncio.create_task(self.chuncker.chunk_text(self.text_queue, self.chunk_queue, csv_writer, f"chunk_worker_{i}",self.logger))  
                for i in range(num_workers)  
            ]  
            vectorize_workers = [  
                asyncio.create_task(self.embedder.vectorize_chunks(self.chunk_queue, self.vector_queue, csv_writer, f"vectorize_worker_{i}", self.logger))  
                for i in range(num_workers)  
            ]  
            upload_workers = [  
                asyncio.create_task(self.file_uploader.upload_documents(self.vector_queue, self.logger, csv_writer, f"upload_worker_{i}"))  
                for i in range(num_workers)  
            ]  

            # Wait for all read tasks to complete  
            await self.file_queue.join() 
  
            # Push sentinels to stop the chunking, vectorizing, and uploading tasks  
            for _ in range(num_workers):  
                await self.file_queue.put(None) 
                await self.text_queue.put((None, None, None))  # Sentinel for chunk_text  
                await self.chunk_queue.put((None, None, None))  # Sentinel for vectorize_chunks  
                await self.vector_queue.put(None)  # Sentinel for upload_documents  
  
            # Wait for the worker tasks to complete  
            await asyncio.gather(*read_tasks) 
            await asyncio.gather(*chunking_workers)  
            await asyncio.gather(*vectorize_workers) 
            await asyncio.gather(*upload_workers)  
  
        # Close the DocumentUploader to ensure all documents are flushed and the sender is properly closed  
        await self.uploading_skillset.close()  
  
        total_time = time.time() - start_time  
        print(f"Total indexing time: {total_time} seconds")   

