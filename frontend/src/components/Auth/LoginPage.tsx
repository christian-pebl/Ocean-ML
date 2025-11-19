import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import { supabase } from '../../lib/supabase'

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-2">
            Ocean-ML
          </h1>
          <p className="text-gray-400">
            Fish Detection & Annotation Platform
          </p>
        </div>

        {/* Auth UI */}
        <div className="bg-gray-800 rounded-lg p-8 shadow-xl">
          <Auth
            supabaseClient={supabase}
            appearance={{
              theme: ThemeSupa,
              variables: {
                default: {
                  colors: {
                    brand: '#3b82f6',
                    brandAccent: '#2563eb',
                  },
                },
              },
            }}
            providers={['google']}
            redirectTo={window.location.origin}
          />
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>Marine Biology Research Tool</p>
          <p className="mt-1">Collaborative annotation and training platform</p>
        </div>
      </div>
    </div>
  )
}
