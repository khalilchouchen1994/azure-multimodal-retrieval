import asyncio  
import uuid  
import base64  
import io  
from PIL import Image  
from azure.ai.inference import ImageEmbeddingsClient  
from azure.ai.inference.models import EmbeddingInput
from azure.core.credentials import AzureKeyCredential  
  
class ImageEmbedder:  
    def __init__(self, ai_foundry_endpoint, ai_foundry_key,image_embedding_model):  
  
        # Initialize the EmbeddingsClient for Coheremebed  
        self.embeddings_client = ImageEmbeddingsClient(  
                    endpoint=ai_foundry_endpoint,  
                    credential=AzureKeyCredential(ai_foundry_key),  
                    model=image_embedding_model
        )  
  
    async def embed_images(self,image_queue,uploader_queue,worker_id, logger):  
        while True:  
            image_info = await image_queue.get()  
            if image_info is None:  
                image_queue.task_done()  
                break  
  
            blob_name, image_data, parent_id, page_number = image_info  
            image_id = str(uuid.uuid4())  
  
            try:  
                logger.info(f"ImageEmbedder {worker_id}:Embedding image {image_id} from document {blob_name} page {page_number}")  
  
                # Convert image data to base64 encoded data URL  
                image_base64 = self.convert_to_base64_data_url(image_data)  


                # Generate embeddings using Coheremebed  
                response = self.embeddings_client.embed(  
                    input=[EmbeddingInput(image=image_base64)]  
                ) 
  
                # Create document for indexing  
                document = {  
                    "parent_id": parent_id,  
                    "chunk_id": image_id,  
                    "title": blob_name,  
                    "image_embedding": response.data[0].embedding,  
                    "page_number": page_number  
                }  
  
                # Add to uploader queue  
                await uploader_queue.put(document)  
                logger.info(f"ImageEmbedder {worker_id}: Successfully processed image {image_id} using model {response.model}. Token consumption {response.usage}")  
  
            except Exception as e:  
                logger.error(f"ImageEmbedder {worker_id}: Error processing image {image_id}: {e}")  
            finally:  
                image_queue.task_done()  
  
    def convert_to_base64_data_url(self, image_data):  
        # Open the image from bytes  
        image = Image.open(io.BytesIO(image_data))  
        # Save the image to a bytes buffer in PNG format  
        buffered = io.BytesIO()  
        image.save(buffered, format="PNG")  
        # Get the base64 encoded string  
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')  
        # Create the base64 data URL  
        data_url = f"data:image/png;base64,{img_str}"  
        return data_url  