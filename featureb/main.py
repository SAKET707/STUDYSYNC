import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from vectorstore.client_factory import QdrantClientFactory
from vectorstore.qdrant_client import QdrantVectorStore
from retrieval.chapter_fetcher import ChapterContextFetcher
from retrieval.retrieval_service import RetrievalService
from mcq.generator import MCQGenerator
from mcq.validator import MCQValidator
from mcq.consistency_checker import MCQConsistencyChecker
from mcq.faithfulness_checker import MCQFaithfulnessChecker
from mcq.service import MCQService
from api.routes import router as mcq_router, register_mcq_service


from config.settings import settings


logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Manager.
    Handles the instantiation and wiring of the entire RAG Architecture on startup.
    """
    logger.info("🚀 Booting up NEET Biology MCQ Engine...")

    try:
      
        qdrant_client = QdrantClientFactory.create()
        vector_store = QdrantVectorStore(client=qdrant_client)
        logger.info("Database connection established.")

       
        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model="llama-3.3-70b-versatile", 
            temperature=0.2
        )
        logger.info("Groq LLM (llama-3.3-70b-versatile) initialized.")

       
        chapter_fetcher = ChapterContextFetcher(vector_store=vector_store)
        retrieval_service = RetrievalService(chapter_fetcher=chapter_fetcher)

      
        generator = MCQGenerator(llm=llm)
        validator = MCQValidator()
        consistency_checker = MCQConsistencyChecker(llm=llm)
        faithfulness_checker = MCQFaithfulnessChecker(llm=llm)

       
        mcq_service = MCQService(
            retrieval_service=retrieval_service,
            generator=generator,
            validator=validator,
            consistency_checker=consistency_checker,
            faithfulness_checker=faithfulness_checker
        )

    
        register_mcq_service(mcq_service)
        logger.info(" Architecture successfully wired. Server ready to accept requests.")
        
        yield  
        
    except Exception as e:
        logger.error(f" Failed to initialize application: {e}")
        raise e
    finally:
        logger.info("Shutting down server. Cleaning up resources...")


app = FastAPI(
    title="NEET MCQ Generation API",
    description="Automated chapter-based RAG pipeline for NTA-standard Biology questions.",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mcq_router)

@app.get("/health", tags=["System"])
def health_check():
    """Simple health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "service": "neet-mcq-engine",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)