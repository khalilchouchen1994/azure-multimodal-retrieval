import fitz  # PyMuPDF  
import time  
import uuid  
  
class FileReader:  
  
    async def read_pdf(self, blob_client, file_queue, text_queue, csv_writer, worker_id, logger):  
        while True:  
            blob = await file_queue.get()  
            if blob is None:  # Sentinel to end the loop  
                file_queue.task_done()  
                break  

            parent_id = str(uuid.uuid4())  
              
            # Download the blob  
            logger.debug(f"Reader {worker_id}:Reading document {blob.name}")
            start_time = time.time()  
            data = blob_client.get_blob_client(blob.name).download_blob().readall()              
  
            # Read the PDF document  
            with fitz.open(stream=data, filetype="pdf") as doc:  
                text = "".join(page.get_text() for page in doc)  
  
            read_time = time.time() - start_time  
            csv_writer.writerow([parent_id, None, "read_pdf", read_time, worker_id])  
  
            # Put the text into the text queue  
            await text_queue.put((blob.name, text,parent_id))    
              
            file_queue.task_done()  

