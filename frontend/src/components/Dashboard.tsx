import { Session } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import VideoLibrary from './VideoLibrary/VideoLibrary'

interface DashboardProps {
  session: Session
}

export default function Dashboard({ session }: DashboardProps) {
  const handleSignOut = async () => {
    await supabase.auth.signOut()
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-white">
                Ocean-ML
              </h1>
              <span className="ml-3 text-sm text-gray-400">
                v0.1.0
              </span>
            </div>

            {/* User menu */}
            <div className="flex items-center space-x-4">
              <span className="text-gray-300">
                {session.user.email}
              </span>
              <button
                onClick={handleSignOut}
                className="btn-secondary text-sm"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <VideoLibrary />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-gray-400 text-sm">
            Ocean-ML - Collaborative Fish Detection Platform
          </p>
        </div>
      </footer>
    </div>
  )
}
