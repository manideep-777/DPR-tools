/**
 * Main Navigation Component
 */
'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';
import { Button } from '@/components/ui/button';
import { LogOut, User } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // Hide navbar on PDF routes
  if (pathname?.startsWith('/pdf')) {
    return null;
  }

  return (
    <nav className="border-b bg-white notranslate">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-primary">
            MSME DPR Generator
          </Link>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link href="/dashboard">
                  <Button variant={pathname === '/dashboard' ? 'default' : 'ghost'}>
                    Dashboard
                  </Button>
                </Link>
                
                <div className="flex items-center gap-2 border-l pl-4">
                  <User className="h-5 w-5 text-muted-foreground" />
                  <span className="text-sm font-medium">{user?.full_name}</span>
                  <Button variant="ghost" size="sm" onClick={handleLogout}>
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant={pathname === '/login' ? 'default' : 'ghost'}>
                    Login
                  </Button>
                </Link>
                <Link href="/register">
                  <Button variant={pathname === '/register' ? 'default' : 'outline'}>
                    Register
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
