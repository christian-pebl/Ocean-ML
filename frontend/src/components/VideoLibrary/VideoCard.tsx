import { useState } from 'react'
import { supabase } from '../../lib/supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Video {
  id: string
  filename: string
  storage_path: string
  thumbnail_path?: string
  duration_seconds?: number
  annotated: boolean
  annotated_by?: string
  annotated_at?: string
  detection_count: number
  locked_by?: string
  uploaded_at: string
  file_size_bytes?: number
}

interface VideoCardProps {
  video: Video
  onUpdate: () => void
}

export default function VideoCard({ video, onUpdate }: VideoCardProps) {
  const [isAnnotating, setIsAnnotating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnnotate = async () => {
    setIsAnnotating(true)
    setError(null)

    try {
      // Get auth token
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        throw new Error('Not authenticated')
      }

      // Call backend to acquire lock
      const response = await fetch(`${API_URL}/api/annotations/annotate/${video.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ timeout_minutes: 60 })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Failed to start annotation')
      }

      if (!data.success) {
        // Video is locked by someone else
        alert(data.message)
        setIsAnnotating(false)
        return
      }

      // Open desktop app via protocol handler
      const protocol = import.meta.env.VITE_PROTOCOL || 'oceanml'
      const url = `${protocol}://annotate?video=${video.id}&token=${session.access_token}`

      // Try to open the protocol URL
      window.location.href = url

      // Show message
      alert('Desktop app should launch now. If not, please install the desktop app first.')

      // Poll for completion
      setTimeout(() => {
        onUpdate()
        setIsAnnotating(false)
      }, 5000)

    } catch (err) {
      setError((err as Error).message)
      setIsAnnotating(false)
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown'
    const mb = bytes / (1024 * 1024)
    return `${mb.toFixed(1)} MB`
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  return (
    <div className="video-card">
      {/* Thumbnail placeholder */}
      <div className="w-full h-40 bg-gray-700 rounded-lg mb-3 flex items-center justify-center">
        <svg
          className="w-16 h-16 text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
      </div>

      {/* Video info */}
      <h3 className="text-white font-medium truncate mb-2" title={video.filename}>
        {video.filename}
      </h3>

      <div className="text-sm text-gray-400 space-y-1 mb-3">
        <p>Size: {formatFileSize(video.file_size_bytes)}</p>
        {video.duration_seconds && (
          <p>Duration: {video.duration_seconds}s</p>
        )}
        <p>Uploaded: {formatDate(video.uploaded_at)}</p>
      </div>

      {/* Status */}
      <div className="mb-3">
        {video.annotated ? (
          <div className="flex items-center text-green-400">
            <svg
              className="w-5 h-5 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="font-medium">
              Annotated ({video.detection_count} detections)
            </span>
          </div>
        ) : video.locked_by ? (
          <div className="flex items-center text-yellow-400">
            <svg
              className="w-5 h-5 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                clipRule="evenodd"
              />
            </svg>
            <span>Being annotated...</span>
          </div>
        ) : (
          <div className="flex items-center text-gray-400">
            <svg
              className="w-5 h-5 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <span>Not annotated</span>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-3 p-2 bg-red-900 border border-red-700 rounded text-red-200 text-sm">
          {error}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex space-x-2">
        <button
          onClick={handleAnnotate}
          disabled={isAnnotating || !!video.locked_by}
          className={`flex-1 py-2 px-4 rounded font-medium transition-colors ${
            isAnnotating || video.locked_by
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {isAnnotating ? 'Starting...' : video.locked_by ? 'Locked' : 'Annotate'}
        </button>

        {video.annotated && (
          <button
            className="py-2 px-4 rounded bg-gray-700 hover:bg-gray-600 text-white font-medium"
            title="View annotations"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}
