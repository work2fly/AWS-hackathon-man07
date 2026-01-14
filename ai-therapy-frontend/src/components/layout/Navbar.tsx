'use client';

// Navigation bar component
// 🏆 Breaking Barriers UK 2026 compliant

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Heart, Menu, X, User, LogOut } from 'lucide-react';
import Link from 'next/link';

interface NavbarProps {
  onNavigate?: (section: string) => void;
}

export function Navbar({ onNavigate }: NavbarProps) {
  const { isAuthenticated, user, signOut } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSignOut = async () => {
    await signOut();
    setMobileMenuOpen(false);
  };

  const handleNavClick = (section: string) => {
    setMobileMenuOpen(false);
    if (onNavigate) {
      onNavigate(section);
    }
  };

  const navLinks = [
    { name: 'Home', href: '#home' },
    { name: 'Services', href: '#services' },
    { name: 'About', href: '#about' },
    { name: 'Contact', href: '#contact' },
  ];

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => handleNavClick('home')}>
            <Heart className="h-8 w-8 text-purple-600" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">UKind AI Therapy</h1>
              <p className="text-xs text-gray-600 hidden sm:block">Empowering healing through innovation</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {!isAuthenticated ? (
              <>
                {navLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    onClick={(e) => {
                      e.preventDefault();
                      handleNavClick(link.href.replace('#', ''));
                    }}
                    className="text-gray-700 hover:text-purple-600 font-medium transition-colors"
                  >
                    {link.name}
                  </a>
                ))}
                <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                  🏆 Breaking Barriers UK 2026
                </Badge>
              </>
            ) : (
              <>
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-gray-600" />
                  <span className="text-sm text-gray-700">
                    {user?.profile.firstName || '[firstName]'}
                  </span>
                </div>
                <Badge variant="outline" className="border-purple-200 text-purple-700">
                  {user?.role === 'client' ? 'Client' : 
                   user?.role === 'therapist' ? 'Therapist' : 'Admin'}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleSignOut}
                  className="text-gray-600 hover:text-gray-900"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6 text-gray-700" />
            ) : (
              <Menu className="h-6 w-6 text-gray-700" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-100">
            {!isAuthenticated ? (
              <div className="space-y-3">
                {navLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    onClick={(e) => {
                      e.preventDefault();
                      handleNavClick(link.href.replace('#', ''));
                    }}
                    className="block px-4 py-2 text-gray-700 hover:bg-purple-50 hover:text-purple-600 rounded-lg transition-colors"
                  >
                    {link.name}
                  </a>
                ))}
                <div className="px-4 py-2">
                  <Badge variant="secondary" className="bg-purple-100 text-purple-800 w-full justify-center py-2">
                    🏆 Breaking Barriers UK 2026
                  </Badge>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="px-4 py-2 flex items-center space-x-2">
                  <User className="h-4 w-4 text-gray-600" />
                  <span className="text-sm text-gray-700">
                    {user?.profile.firstName || '[firstName]'}
                  </span>
                  <Badge variant="outline" className="border-purple-200 text-purple-700 ml-auto">
                    {user?.role === 'client' ? 'Client' : 
                     user?.role === 'therapist' ? 'Therapist' : 'Admin'}
                  </Badge>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleSignOut}
                  className="w-full justify-start text-gray-600 hover:text-gray-900"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
