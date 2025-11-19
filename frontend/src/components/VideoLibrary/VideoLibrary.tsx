import { useQuery } from '@tanstack/react-query'
import VideoCard from './VideoCard'
import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Video {
  id: string
  filename: string
  storage_path: string
  thumbnail_path?: string
  duration_seconds?: number
  frame_count?: number
  resolution?: string
  fps?: number
  file_size_bytes?: number
  annotated: boolean
  annotated_by?: string
  annotated_at?: string
  detection_count: number
  locked_by?: string
  uploaded_at: string
}

export default function VideoLibrary() {
  const [filter, setFilter] = useState<'all' | 'annotated' | 'unannotated'>('all')

  // Fetch videos
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['videos', filter],
    queryFn: async () => {
      const url = filter === 'all'
        ? `${API_URL}/api/videos`
        : `${API_URL}/api/videos?annotated=${filter === 'annotated'}`

      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('Failed to fetch videos')
      }
      return response.json()
    }
  })

  const videos: Video[] = data?.videos || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white">Video Library</h2>
          <p className="text-gray-400 mt-1">
            {videos.length} videos total
            {filter !== 'all' && ` (filtered)`}
          </p>
        </div>

        {/* Filters */}
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('annotated')}
            className={`px-4 py-2 rounded ${
              filter === 'annotated'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Annotated
          </button>
          <button
            onClick={() => setFilter('unannotated')}
            className={`px-4 py-2 rounded ${
              filter === 'unannotated'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Not Annotated
          </button>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 rounded bg-gray-700 text-gray-300 hover:bg-gray-600"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="text-white text-xl">Loading videos...</div>
        </div>
      )}

      {/* Error state */}
      {error && (
        <div className="text-center py-12">
          <div className="text-red-400 text-xl">
            Error loading videos: {(error as Error).message}
          </div>
          <button
            onClick={() => refetch()}
            className="mt-4 btn-primary"
          >
            Retry
          </button>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !error && videos.length === 0 && (
        <div className="text-center py-12 bg-gray-800 rounded-lg">
          <div className="text-gray-400 text-xl mb-4">
            No videos found
          </div>
          <p className="text-gray-500 mb-6">
            Upload your first video to get started
          </p>
          <button className="btn-primary">
            Upload Video
          </button>
        </div>
      )}

      {/* Video grid */}
      {!isLoading && !error && videos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {videos.map((video) => (
            <VideoCard key={video.id} video={video} onUpdate={refetch} />
          ))}
        </div>
      )}
    </div>
  )
}
