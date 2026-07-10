from typing import Literal

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.core.pipeline import run_pipeline
from backend.core.tello_camera_stream import camera_stream


router = APIRouter()


class PipelineRequest(BaseModel):
    command: str = Field(
        ...,
        min_length=1,
        description="Natural-language command sent by the user.",
    )
    execution_mode: Literal["mock", "real", "real_safe", "real_first_flight"] = "mock"


@router.post("/pipeline")
def execute_pipeline(request: PipelineRequest):
    return run_pipeline(
        user_command=request.command,
        execution_mode=request.execution_mode,
    )


@router.get("/video/stream")
def video_stream():
    return StreamingResponse(
        camera_stream.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/video/stop")
def stop_video_stream():
    camera_stream.stop()

    return {
        "success": True,
        "message": "Camera stream stopped.",
    }


@router.get("/video/status")
def video_status():
    return camera_stream.status()