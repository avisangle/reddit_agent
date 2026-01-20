'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';

export function AdminHeader() {
    const pathname = usePathname();
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

    const handleLogout = async () => {
        try {
            await fetch(`${API_BASE}/admin/logout`, { method: 'GET', credentials: 'include' });
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            window.location.href = '/login';
        }
    };

    const navItems = [
        { href: '/admin/dashboard', label: 'Dashboard' },
        { href: '/admin/settings', label: 'Settings' },
        { href: '/workflow', label: 'Workflow' },
    ];

    return (
        <header className="sticky top-0 z-50 w-full border-b border-border bg-card">
            <div className="container mx-auto flex h-14 items-center justify-between px-4">
                <div className="flex items-center gap-8">
                    <Link href="/admin/dashboard" className="font-bold text-lg text-foreground">
                        Reddit Agent
                    </Link>
                    <nav className="hidden md:flex items-center gap-1">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${pathname === item.href
                                    ? 'bg-secondary text-foreground'
                                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                                    }`}
                            >
                                {item.label}
                            </Link>
                        ))}
                    </nav>
                </div>
                <Button size="sm" onClick={handleLogout}>
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                </Button>
            </div>
        </header>
    );
}
