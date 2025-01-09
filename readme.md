# Building Multimodal Retrieval Systems in Azure

## Introduction  

In the rapidly evolving era of Generative AI (GenAI), multimodality - the ability to handle and integrate diverse data types such as text and images - is a cornerstone of modern GenAI applications.
   
This repository demonstrates how to perform multimodal data ingestion into **Azure AI Search** using two different methods:  
   
- **Pull Method**: Utilizing Azure AI Search Indexers to pull data from data sources, enrich it using skillsets, and index it.  
- **Push Method**: Creating a custom **asynchronous, modular and multi-threaded** indexing pipeline to push data directly into Azure AI Search.  
   
These notebooks showcase how to ingest both text and images, with minimal information loss, to enable advanced search capabilities.  
   
For a detailed explanation of the concepts and implementation, please refer to the accompanying article [here](https://medium.com/@khalilchouchen1994/navigating-multimodal-data-ingestion-for-advanced-retrieval-systems-with-azure-ai-foundry-and-d6b41d6d059c).  
   
## Prerequisites  
   
Before running the notebooks, ensure you have the following:  
   
### Azure Resources  
   
- **Azure AI Search Service**: [An instance of Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-create-service-portal).  
- **Azure Storage Account**: [Blob storage](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) containing your documents (e.g., PDFs).  
- **Azure OpenAI Service** (for the Pull method): For generating text embeddings.  
- **Azure AI Services** (for the Pull method): For generating image embeddings.  
- **Azure AI Foundry** (for the Push method): For generating text and image embeddings in the psuh methods.  
- **Azure Document Intelligence**: For extracting text and images from documents.

   
Ensure that appropriate permissions and roles are assigned, such as the **Storage Blob Data Reader** role for accessing blob data.  
   
### Local Environment  
   
- **Python 3.8 or higher**: The notebooks require Python 3.8+.  
- **Git**: To clone the repository.  
   
## Setup Instructions  
   
Follow these steps to set up your environment and run the notebooks.  
   
### 1. Clone the Repository  
   
```bash  
git clone https://github.com/yourusername/your-repo-name.git  
cd your-repo-name  
```  
   
### 2. Prepare the Environment  
   
Run the setup script corresponding to your operating system to initialize the environment.  
   
#### Windows  
   
Run the `setup.bat` script:  
   
```batch  
.\setup.bat  
```  
   
#### macOS/Linux  
   
Run the `setup.sh` script:  
   
```bash  
chmod +x setup.sh  
./setup.sh  
```  
   
**What the Setup Script Does**:  
   
- **Creates a virtual environment** in the `.venv` directory.  
- **Activates the virtual environment**.  
- **Upgrades `pip`** to the latest version.  
- **Installs the required Python packages** listed in `requirements.txt`.  
- **Extracts Poppler files** needed for PDF processing (Windows users).  
- **Sets the `POPPLER_PATH`** in the `.env` file (Windows users).  
- **Deactivates the virtual environment** (optional).  
   
### 3.Environment Variables  
   
Add the required variables shared in the `.env.template` file to the `.env` file created by the script created by the script in the repository root.

### 4. Activate the Virtual Environment (If Not Already Activated)  
   
If the virtual environment is not activated by the setup script, activate it manually.  
   
#### Windows  
   
```batch  
.\.venv\Scripts\activate  
```  
   
#### macOS/Linux  
   
```bash  
source .venv/bin/activate  
```  
   
### 5. Run the Notebooks  
   
Use Jupyter Notebook or Jupyter Lab to run the notebooks.  
   
```bash  
jupyter notebook  
```  
   
Open the notebooks in the following order:  
   
1. **Pull Method**: `pull_method_notebook.ipynb`  
   - Demonstrates how to use Azure AI Search Indexers to pull data from Azure Blob Storage, enrich it using skillsets (such as splitting documents, generating embeddings, and processing images), and index it.  
   
2. **Push Method**: `push_method_notebook.ipynb`  
   - Shows how to create a custom asynchronous indexing pipeline that reads documents, processes them to extract text and images, generates embeddings using Azure AI Foundry, and pushes the data directly into Azure AI Search.  
   
**Note**: Ensure that all the required environment variables are properly set before running the notebooks.  
   
### 6. Deactivate the Virtual Environment (Optional)  
   
After you have finished running the notebooks, you can deactivate the virtual environment.  
   
```bash  
deactivate  
```  
   
## Contributing  
   
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.  
   
## License  
   
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  