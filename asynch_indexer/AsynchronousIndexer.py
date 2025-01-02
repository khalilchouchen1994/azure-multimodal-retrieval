import asyncio  
import logging  
import time  
  
from azure.identity.aio import DefaultAzureCredential  
from azure.storage.blob.aio import BlobServiceClient  
  
from .FileReader import FileReader  
from .Chunker import Chunker  
from .TextEmbedder import TextEmbedder  
from .ImageEmbedder import ImageEmbedder  
from .FileUploader import FileUploader  
  
class AsynchronousIndexer:  
    def __init__(self, index_name, search_endpoint, search_api_key,  
                 storage_account_name, storage_container_name,  
                 ai_foundry_endpoint, ai_foundry_key, 
                 text_embedding_model, image_embedding_model, 
                 document_intelligence_endpoint, document_intelligence_key):  
  
        # Initialize the Azure Blob Storage client  
        self.storage_account_url = f"https://{storage_account_name}.blob.core.windows.net"  
        self.storage_container_name = storage_container_name  
        self.credential = DefaultAzureCredential()  
        self.blob_service_client = BlobServiceClient(  
            account_url=self.storage_account_url,  
            credential=self.credential  
        )  
        self.storage_container_client = self.blob_service_client.get_container_client(self.storage_container_name)  
  
        # Initialize pipeline components  
        self.file_reader = FileReader(document_intelligence_endpoint, document_intelligence_key)  
        self.chunker = Chunker()  
        self.text_embedder = TextEmbedder(ai_foundry_endpoint, ai_foundry_key, text_embedding_model)  
        self.image_embedder = ImageEmbedder(ai_foundry_endpoint, ai_foundry_key,image_embedding_model)  
        self.file_uploader = FileUploader(search_endpoint, index_name, search_api_key)  
  
        # Set up logging  
        self.logger = logging.getLogger(__name__)  
  
        # Initialize queues  
        self.file_queue = asyncio.Queue()  
        self.text_queue = asyncio.Queue()  
        self.image_queue = asyncio.Queue()  
        self.chunk_queue = asyncio.Queue()  
        self.vector_queue = asyncio.Queue()  
  
    async def run_indexing(self):  
        start_time = time.time()  
        blob_list = self.storage_container_client.list_blobs()  
  
        # Populate the file queue with blobs  
        async for blob in blob_list:  
            if blob.name.endswith('.pdf'):  
                await self.file_queue.put(blob)  
  
        # Number of workers for each task  
        num_workers = 3  
  
        # Create worker tasks  
        read_tasks = [  
            asyncio.create_task(self.file_reader.read_pdf(  
                self.storage_container_client, self.file_queue, self.text_queue, self.image_queue, f"read_worker_{i}", self.logger))  
            for i in range(num_workers)  
        ]  
        chunk_tasks = [  
            asyncio.create_task(self.chunker.chunk_text(  
                self.text_queue, self.chunk_queue, f"chunk_worker_{i}", self.logger))  
            for i in range(num_workers)  
        ]  
        text_embedding_tasks = [  
            asyncio.create_task(self.text_embedder.vectorize_chunks(  
                self.chunk_queue, self.vector_queue, f"text_embedder_{i}", self.logger))  
            for i in range(num_workers)  
        ]  
        image_embedding_tasks = [  
            asyncio.create_task(self.image_embedder.embed_images(  
                self.image_queue, self.vector_queue, f"image_embedder_{i}", self.logger))  
            for i in range(num_workers)  
        ]  
        upload_tasks = [  
            asyncio.create_task(self.file_uploader.upload_documents(  
                self.vector_queue, f"uploader_{i}", self.logger))  
            for i in range(num_workers)  
        ]  
  
        # Wait for all tasks to complete  
        await self.file_queue.join()  
        await self.text_queue.join()  
        await self.chunk_queue.join()  
        await self.image_queue.join()  
        await self.vector_queue.join()  
  
        # Add sentinels to stop workers  
        for _ in range(num_workers):  
            await self.file_queue.put(None)  
            await self.text_queue.put(None)  
            await self.chunk_queue.put(None)  
            await self.image_queue.put(None)  
            await self.vector_queue.put(None)  
  
        # Wait for worker tasks to finish  
        await asyncio.gather(*read_tasks)  
        await asyncio.gather(*chunk_tasks)  
        await asyncio.gather(*text_embedding_tasks)  
        await asyncio.gather(*image_embedding_tasks)  
        await asyncio.gather(*upload_tasks)  
  
        # Close the uploader  
        await self.file_uploader.close()  
  
        total_time = time.time() - start_time  
        self.logger.info(f"Total indexing time: {total_time:.2f} seconds")  