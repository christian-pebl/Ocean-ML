"""
Supabase Client Service

Provides singleton Supabase client instance for database and storage operations.
"""

import os
from supabase import create_client, Client
from typing import Optional
from functools import lru_cache

_supabase_client: Optional[Client] = None

@lru_cache()
def get_supabase_client() -> Client:
    """
    Get Supabase client singleton.

    Returns:
        Supabase client instance

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY not set
    """
    global _supabase_client

    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment"
            )

        _supabase_client = create_client(supabase_url, supabase_key)

    return _supabase_client


def get_supabase_admin_client() -> Client:
    """
    Get Supabase client with service role (admin) permissions.

    Use this for operations that bypass Row Level Security.

    Returns:
        Supabase client with admin permissions

    Raises:
        ValueError: If SUPABASE_SERVICE_KEY not set
    """
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not service_key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment"
        )

    return create_client(supabase_url, service_key)


class SupabaseService:
    """
    High-level Supabase service with common operations.
    """

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()

    # Videos operations
    async def get_videos(self, limit: int = 100, offset: int = 0):
        """Get list of videos"""
        response = self.client.table("videos").select("*").range(offset, offset + limit - 1).execute()
        return response.data

    async def get_video_by_id(self, video_id: str):
        """Get single video by ID"""
        response = self.client.table("videos").select("*").eq("id", video_id).single().execute()
        return response.data

    async def create_video(self, video_data: dict):
        """Create new video record"""
        response = self.client.table("videos").insert(video_data).execute()
        return response.data[0] if response.data else None

    async def update_video(self, video_id: str, updates: dict):
        """Update video record"""
        response = self.client.table("videos").update(updates).eq("id", video_id).execute()
        return response.data[0] if response.data else None

    async def delete_video(self, video_id: str):
        """Delete video record"""
        response = self.client.table("videos").delete().eq("id", video_id).execute()
        return response.data

    # Storage operations
    def upload_file(self, bucket: str, path: str, file_data: bytes):
        """Upload file to storage"""
        response = self.client.storage.from_(bucket).upload(path, file_data)
        return response

    def download_file(self, bucket: str, path: str):
        """Download file from storage"""
        response = self.client.storage.from_(bucket).download(path)
        return response

    def get_public_url(self, bucket: str, path: str):
        """Get public URL for file"""
        response = self.client.storage.from_(bucket).get_public_url(path)
        return response

    def delete_file(self, bucket: str, path: str):
        """Delete file from storage"""
        response = self.client.storage.from_(bucket).remove([path])
        return response

    # Activity logging
    async def log_activity(
        self,
        action_type: str,
        resource_type: str = None,
        resource_id: str = None,
        metadata: dict = None
    ):
        """Log user activity"""
        activity_data = {
            "action_type": action_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "metadata": metadata or {}
        }

        response = self.client.table("activity_log").insert(activity_data).execute()
        return response.data[0] if response.data else None
