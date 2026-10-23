// src/components/layout/Footer.jsx
export default function Footer() {
  return (
    <footer className="border-t border-gray-800 py-6 text-center text-sm text-gray-600">
      <p>
        &copy; {new Date().getFullYear()}{' '}
        <span className="text-indigo-400 font-medium">AI Fake Job Detection System</span>. All rights reserved.
      </p>
    </footer>
  )
}
