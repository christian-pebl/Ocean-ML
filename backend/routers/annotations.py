"""
Annotation management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from datetime import datetime, timedelta

from models.annotation import (
    Annotation,
    AnnotationCreate,
    AnnotationCompleteRequest
)
from models.video import VideoLockRequest, VideoLockResponse
from services.supabase_client import SupabaseService

router = APIRouter(prefix="/api/annotations", tags=["annotations"])


def get_supabase_service():
    """Dependency to get Supabase service"""
    return SupabaseService()


@router.post("/annotate/{video_id}", response_model=VideoLockResponse)
async def start_annotation(
    video_id: UUID,
    timeout_minutes: int = 60,
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Acquire lock on video to start annotation.

    Args:
        video_id: UUID of the video to annotate
        timeout_minutes: How long to hold the lock (default 60 minutes)

    Returns:
        Lock status and video download URL
    """
    try:
        # Get video
        video = await service.get_video_by_id(str(video_id))
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        # Check if already locked
        if video.get("locked_by") and video.get("lock_expires_at"):
            lock_expires = datetime.fromisoformat(video["lock_expires_at"].replace("Z", "+00:00"))
            if lock_expires > datetime.now():
                return VideoLockResponse(
                    success=False,
                    video_id=video_id,
                    locked_by=video["locked_by"],
                    locked_until=lock_expires,
                    message="Video is currently being annotated by another user"
                )

        # Acquire lock
        lock_expires_at = datetime.now() + timedelta(minutes=timeout_minutes)
        updates = {
            "locked_by": "current_user_id",  # TODO: Get from auth
            "locked_at": datetime.now().isoformat(),
            "lock_expires_at": lock_expires_at.isoformat()
        }

        await service.update_video(str(video_id), updates)

        # Get download URL
        video_url = service.get_public_url("videos", video["storage_path"])

        # Log activity
        await service.log_activity(
            action_type="annotation_started",
            resource_type="video",
            resource_id=str(video_id)
        )

        return VideoLockResponse(
            success=True,
            video_id=video_id,
            locked_by="current_user_id",
            locked_until=lock_expires_at,
            message=f"Video locked for annotation. Download URL: {video_url}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error acquiring lock: {str(e)}")


@router.post("/complete", response_model=Annotation)
async def complete_annotation(
    request: AnnotationCompleteRequest,
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Complete annotation and upload annotation data.

    Args:
        request: Annotation completion data

    Returns:
        Created annotation record
    """
    try:
        # Get video
        video = await service.get_video_by_id(str(request.video_id))
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        # Validate YOLO format (basic check)
        if not request.annotation_data or not isinstance(request.annotation_data, str):
            raise HTTPException(status_code=400, detail="Invalid annotation format")

        # Upload annotation file to storage
        annotation_path = f"annotations/{request.video_id}.txt"
        service.upload_file(
            "annotations",
            annotation_path,
            request.annotation_data.encode("utf-8")
        )

        # Create annotation record
        annotation_data = {
            "video_id": str(request.video_id),
            "frames_annotated": request.frames_annotated,
            "detection_count": request.detection_count,
            "species_counts": request.species_counts,
            "storage_path": annotation_path
        }

        # Use upsert (insert or update if exists)
        response = service.client.table("annotations").upsert(annotation_data).execute()
        annotation = response.data[0] if response.data else None

        if not annotation:
            raise HTTPException(status_code=500, detail="Failed to create annotation")

        # Update video record
        video_updates = {
            "annotated": True,
            "annotated_by": "current_user_id",  # TODO: Get from auth
            "annotated_at": datetime.now().isoformat(),
            "annotation_storage_path": annotation_path,
            "detection_count": request.detection_count,
            "locked_by": None,  # Release lock
            "locked_at": None,
            "lock_expires_at": None
        }

        await service.update_video(str(request.video_id), video_updates)

        # Log activity
        await service.log_activity(
            action_type="annotation_completed",
            resource_type="video",
            resource_id=str(request.video_id),
            metadata={
                "frames_annotated": request.frames_annotated,
                "detection_count": request.detection_count
            }
        )

        return annotation

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing annotation: {str(e)}")


@router.get("/{video_id}", response_model=Annotation)
async def get_annotation(
    video_id: UUID,
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Get annotation for a video.

    Args:
        video_id: UUID of the video

    Returns:
        Annotation details
    """
    try:
        response = service.client.table("annotations").select("*").eq("video_id", str(video_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Annotation not found")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching annotation: {str(e)}")


@router.delete("/{video_id}")
async def delete_annotation(
    video_id: UUID,
    service: SupabaseService = Depends(get_supabase_service)
):
    """
    Delete annotation for a video.

    Args:
        video_id: UUID of the video

    Returns:
        Success message
    """
    try:
        # Get annotation
        response = service.client.table("annotations").select("*").eq("video_id", str(video_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Annotation not found")

        annotation = response.data[0]

        # Delete from storage
        if annotation.get("storage_path"):
            service.delete_file("annotations", annotation["storage_path"])

        # Delete from database
        service.client.table("annotations").delete().eq("video_id", str(video_id)).execute()

        # Update video record
        await service.update_video(str(video_id), {
            "annotated": False,
            "annotated_by": None,
            "annotated_at": None,
            "annotation_storage_path": None,
            "detection_count": 0
        })

        # Log activity
        await service.log_activity(
            action_type="annotation_deleted",
            resource_type="video",
            resource_id=str(video_id)
        )

        return {"message": "Annotation deleted successfully", "video_id": str(video_id)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting annotation: {str(e)}")
