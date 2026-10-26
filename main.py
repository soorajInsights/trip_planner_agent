import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.agentic_workflow import GraphBuilder


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    question: str


# Initialize the agent when the application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Travel Planner API")

    try:
        graph_builder = GraphBuilder(model_provider="ollama")
        app.state.travel_agent = graph_builder()

        logger.info("Travel agent initialized successfully")

    except Exception:
        logger.exception("Failed to initialize travel agent")
        raise

    yield

    logger.info("Shutting down Travel Planner API")


# Create FastAPI application
app = FastAPI(lifespan=lifespan)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/query")
async def query_travel_agent(
    query: QueryRequest,
    request: Request,
):
    logger.info("Received travel planning request")

    try:
        react_app = request.app.state.travel_agent

        messages = {"messages": [query.question]}
        output = react_app.invoke(messages)

        if isinstance(output, dict) and output.get("messages"):
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)

        logger.info("Travel planning request completed successfully")

        return {"answer": final_output}

    except Exception as e:
        logger.exception("Travel agent execution failed")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating your travel plan.",
        ) from e