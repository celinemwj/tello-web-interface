from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.core.pipeline import run_pipeline


router = APIRouter()


class PipelineRequest(BaseModel):
    command: str = Field(
        ...,
        min_length=1,
        description="Natural-language command sent by the user.",
    )
    execution_mode: Literal["mock", "real"] = "mock"


@router.post("/pipeline")
def execute_pipeline(request: PipelineRequest):
    """
    Run the complete Tello command-processing pipeline.
    Use mock mode while the physical drone is unavailable.
    """
    return run_pipeline(
        user_command=request.command,
        execution_mode=request.execution_mode,
    )