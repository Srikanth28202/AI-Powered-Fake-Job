// src/pages/NotFoundPage.jsx
import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-6 text-center px-4">
      <h1 className="text-9xl font-black text-indigo-500 opacity-30">404</h1>
      <h2 className="text-3xl font-bold text-white">Page Not Found</h2>
      <p className="text-gray-400">The page you are looking for doesn't exist or has been moved.</p>
      <Link
        to="/"
        className="mt-4 px-6 py-3 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-500 transition-colors"
      >
        Back to Home
      </Link>
    </div>
  )
}
