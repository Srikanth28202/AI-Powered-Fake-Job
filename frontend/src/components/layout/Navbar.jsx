// src/components/layout/Navbar.jsx
import { Link, NavLink } from 'react-router-dom'
import { ShieldCheck } from 'lucide-react'

const navLinks = [
  { label: 'Home', to: '/' },
  // Add more nav links as features are built
]

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-800 backdrop-blur bg-gray-950/80">
      <nav className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 font-bold text-white text-lg">
          <ShieldCheck className="w-6 h-6 text-indigo-400" />
          <span className="hidden sm:inline">FakeJobDetect</span>
        </Link>

        {/* Nav Links */}
        <ul className="flex items-center gap-6">
          {navLinks.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                className={({ isActive }) =>
                  `text-sm font-medium transition-colors ${
                    isActive ? 'text-indigo-400' : 'text-gray-400 hover:text-white'
                  }`
                }
              >
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  )
}
