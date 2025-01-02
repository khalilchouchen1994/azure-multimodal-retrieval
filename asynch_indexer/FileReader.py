import time  
import uuid  
import os
import asyncio  
from io import BytesIO  
from azure.core.credentials import AzureKeyCredential  
from azure.ai.documentintelligence import DocumentIntelligenceClient  
from pdf2image import convert_from_bytes  
  
class FileReader:  
    def __init__(self, document_intelligence_endpoint, document_intelligence_key):  
        # Initialize the Document Intelligence client  
        self.document_client = DocumentIntelligenceClient(  
            endpoint=document_intelligence_endpoint,  
            credential=AzureKeyCredential(document_intelligence_key)  
        )  
  
    async def read_pdf(self, container_client, file_queue, text_queue, image_queue, worker_id, logger):  
        while True:  
            blob = await file_queue.get()  
            if blob is None:  
                file_queue.task_done()  
                break  
  
            parent_id = str(uuid.uuid4())  
  
            logger.info(f"Reader {worker_id}: Reading document {blob.name}")  
            start_time = time.time()  
  
            blob_client = container_client.get_blob_client(blob)  
  
            # Download the blob data asynchronously  
            stream = await blob_client.download_blob()  
            data = await stream.readall()  
  
            # Run the synchronous analyze_document in a separate thread  
            result = await asyncio.to_thread(self.analyze_document, data)  
            logger.info(f"Reader {worker_id}: Completed analyze_document for {blob.name}")  
  
            # Extract text and images  
            text_pages = []  
            images = []  
  
            for page in result.pages:  
                page_text = "\n".join([line.content for line in page.lines])  
                text_pages.append((blob.name, page_text, parent_id, page.page_number))  
  
            # Convert the PDF pages to images in a separate thread to prevent blocking  
            dpi = 300  # Adjust DPI as needed  
            #poppler_path= r"C:\Users\kchouchen\Desktop\AI-search-multimodality-ip\.venv\Lib\site-packages\poppler-24.08.0\Library\bin"
            poppler_path= os.environ["POPPLER_PATH"] 
            pages_images = await asyncio.to_thread(  
                convert_from_bytes,  
                data,  
                dpi=dpi,  
                poppler_path=poppler_path  
            )   
  
            # Map page numbers to page objects  
            pages_by_number = {page.page_number: page for page in result.pages}  
  
            # Extract images from the page  
            if result.figures:  
                logger.info(f"Reader {worker_id}: Found {len(result.figures)} figures in {blob.name}")  
                for figure in result.figures:  
                    for region in figure.bounding_regions:  
                        page_number = region.page_number  
                        polygon = region.polygon  # List of x, y coordinates  
  
                        # Get the corresponding page image  
                        page_image = pages_images[page_number - 1]  
  
                        # Get the page object to determine units  
                        page = pages_by_number[page_number]  
                        unit = page.unit  # 'pixel' or 'inch'  
  
                        # Map the polygon coordinates to pixel values  
                        x_coords = polygon[0::2]  
                        y_coords = polygon[1::2]  
  
                        if unit == 'pixel':  
                            # Coordinates are already in pixels  
                            pass  
                        elif unit == 'inch':  
                            # Convert inches to pixels (dpi is dots per inch)  
                            x_coords = [x * dpi for x in x_coords]  
                            y_coords = [y * dpi for y in y_coords]  
                        else:  
                            logger.warning(f"Unknown unit '{unit}' in page {page_number}")  
                            continue  
  
                        x_min = min(x_coords)  
                        x_max = max(x_coords)  
                        y_min = min(y_coords)  
                        y_max = max(y_coords)  
  
                        # Ensure coordinates are within image bounds  
                        left = int(max(x_min, 0))  
                        upper = int(max(y_min, 0))  
                        right = int(min(x_max, page_image.width))  
                        lower = int(min(y_max, page_image.height))  
  
                        # Crop the figure from the page image  
                        figure_image = page_image.crop((left, upper, right, lower))  
  
                        # Convert the image to bytes  
                        image_buffer = BytesIO()  
                        figure_image.save(image_buffer, format='PNG')  
                        image_data = image_buffer.getvalue()  
  
                        # Append the image data to the images list  
                        images.append((blob.name, image_data, parent_id, page_number))  
            else:  
                logger.info(f"Reader {worker_id}: No figures found in {blob.name}")  
  
            read_time = time.time() - start_time  
            logger.info(f"Reader {worker_id}: Finished reading {blob.name} in {read_time:.2f} seconds")  
  
            # Put the text pages into the text queue  
            for page_data in text_pages:  
                await text_queue.put(page_data)  
  
            # Put the images into the image queue  
            for image_data in images:  
                await image_queue.put(image_data)  
  
            file_queue.task_done()  
            logger.info(f"Reader {worker_id}: Done processing {blob.name}")  
  
    def analyze_document(self, data):  
        poller = self.document_client.begin_analyze_document(  
            model_id="prebuilt-layout",  
            body=data 
        )  
        result = poller.result()  
        return result  









