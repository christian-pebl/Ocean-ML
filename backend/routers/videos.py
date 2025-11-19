"""
Video management endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List, Optional
from uuid import UUID, uuid4
import os

from models.video import (
    Video,
    VideoCreate,
    VideoUpdate,
    VideoListResponse,
    VideoLockRequest,
    VideoLockResponse
)
from services.supabase_client import SupabaseService, get_supabase_client

router = APIRouter(prefix="/api/videos", tags=["videos"])


def get_supabase_service():
    """Dependency to get Supabase service"""
    return SupabaseService()


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    limit: int = 100,
    offset: int = 0,
    annotated: Optional[bool] = None,
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    List all videos with optional filtering.

    Args:
        limit: Maximum number of videos to return
        offset: Number of videos to skip
        annotated: Filter by annotation status (None = all)
    """
    try:
        videos = await service.get_videos(limit=limit, offset=offset)

        # Filter by annotation status if specified
        if annotated is not None:
            videos = [v for v in videos if v.get("annotated") == annotated]

        return {
            "videos": videos,
            "total": len(videos),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching videos: {str(e)}")


@router.get("/{video_id}", response_model=Video)
async def get_video(
    video_id: UUID,
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Get a specific video by ID.

    Args:
        video_id: UUID of the video

    Returns:
        Video details
    """
    try:
        video = await service.get_video_by_id(str(video_id))

        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        return video
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video: {str(e)}")


@router.post("/", response_model=Video)
async def upload_video(
    file: UploadFile = File(...),
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Upload a new video file.

    Args:
        file: Video file to upload

    Returns:
        Created video record
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Check file size (max 100MB)
    max_size = int(os.getenv("MAX_UPLOAD_SIZE_MB", 100)) * 1024 * 1024
    file_data = await file.read()

    if len(file_data) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {max_size / (1024*1024):.0f}MB"
        )

    try:
        # Generate unique filename
        video_id = uuid4()
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "mp4"
        storage_path = f"videos/{video_id}.{file_extension}"

        # Upload to Supabase Storage
        service.upload_file("videos", storage_path, file_data)

        # Create database record
        video_data = {
            "id": str(video_id),
            "filename": file.filename,
            "storage_path": storage_path,
            "file_size_bytes": len(file_data)
        }

        video = await service.create_video(video_data)

        # Log activity
        await service.log_activity(
            action_type="video_uploaded",
            resource_type="video",
            resource_id=str(video_id),
            metadata={"filename": file.filename, "size": len(file_data)}
        )

        return video

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")


@router.put("/{video_id}", response_model=Video)
async def update_video(
    video_id: UUID,
    updates: VideoUpdate,
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Update video metadata.

    Args:
        video_id: UUID of the video
        updates: Fields to update

    Returns:
        Updated video record
    """
    try:
        # Check if video exists
        existing_video = await service.get_video_by_id(str(video_id))
        if not existing_video:
            raise HTTPException(status_code=404, detail="Video not found")

        # Update video
        update_dict = updates.dict(exclude_unset=True)
        video = await service.update_video(str(video_id), update_dict)

        if not video:
            raise HTTPException(status_code=404, detail="Video not found after update")

        return video

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating video: {str(e)}")


@router.delete("/{video_id}")
async def delete_video(
    video_id: UUID,
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Delete a video and its associated files.

    Args:
        video_id: UUID of the video

    Returns:
        Success message
    """
    try:
        # Get video details
        video = await service.get_video_by_id(str(video_id))
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        # Delete from storage
        if video.get("storage_path"):
            service.delete_file("videos", video["storage_path"])

        # Delete annotation if exists
        if video.get("annotation_storage_path"):
            service.delete_file("annotations", video["annotation_storage_path"])

        # Delete from database
        await service.delete_video(str(video_id))

        # Log activity
        await service.log_activity(
            action_type="video_deleted",
            resource_type="video",
            resource_id=str(video_id),
            metadata={"filename": video.get("filename")}
        )

        return {"message": "Video deleted successfully", "video_id": str(video_id)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting video: {str(e)}")
