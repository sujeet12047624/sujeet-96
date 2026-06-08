"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { authService } from "@/services/auth";
import type { User } from "@/types";

export default function Navbar() {
  const [user, setUser] = useState<User | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    authService
      .getProfile()
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  const handleLogout = async () => {
    try {
      await authService.logout();
      setUser(null);
      window.location.href = "/";
    } catch {
      // ignore
    }
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="text-xl font-bold text-primary-700">
            UPSC Blog
          </Link>

          <div className="hidden md:flex items-center space-x-6">
            <Link href="/blog" className="text-gray-700 hover:text-primary-600 font-medium">
              Articles
            </Link>
            <Link
              href="/blog?category=prelims"
              className="text-gray-700 hover:text-primary-600 font-medium"
            >
              Prelims
            </Link>
            <Link
              href="/blog?category=mains"
              className="text-gray-700 hover:text-primary-600 font-medium"
            >
              Mains
            </Link>
            <Link href="/quiz" className="text-gray-700 hover:text-primary-600 font-medium">
              Daily Quiz
            </Link>
            <Link href="/pricing" className="text-gray-700 hover:text-primary-600 font-medium">
              Premium
            </Link>

            {user ? (
              <div className="flex items-center space-x-4">
                {user.is_premium && (
                  <span className="badge-premium">Premium</span>
                )}
                <span className="text-sm text-gray-600">{user.username}</span>
                <button onClick={handleLogout} className="text-sm text-red-600 hover:text-red-700">
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link href="/auth/login" className="text-sm font-medium text-primary-600">
                  Login
                </Link>
                <Link href="/auth/signup" className="btn-primary text-sm py-1.5 px-4">
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden py-4 space-y-3">
            <Link href="/blog" className="block text-gray-700 hover:text-primary-600">Articles</Link>
            <Link href="/quiz" className="block text-gray-700 hover:text-primary-600">Daily Quiz</Link>
            <Link href="/pricing" className="block text-gray-700 hover:text-primary-600">Premium</Link>
            {user ? (
              <button onClick={handleLogout} className="block text-red-600">Logout</button>
            ) : (
              <>
                <Link href="/auth/login" className="block text-primary-600">Login</Link>
                <Link href="/auth/signup" className="block text-primary-600">Sign Up</Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
