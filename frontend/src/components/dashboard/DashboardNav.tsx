'use client';

import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Users, GraduationCap, MessageCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

export function DashboardNav() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();

  if (!user || user.role !== 'parent') {
    return null;
  }

  const isParentDashboard = pathname === '/parent-dashboard';
  const isVidhyaPage = pathname === '/vidhya';

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <Button
        variant={isParentDashboard ? 'default' : 'outline'}
        size="sm"
        onClick={() => router.push('/parent-dashboard')}
      >
        <Users className="mr-2 h-4 w-4" />
        Parent View
      </Button>
      <Button
        variant={!isParentDashboard && !isVidhyaPage ? 'default' : 'outline'}
        size="sm"
        onClick={() => router.push('/dashboard')}
      >
        <GraduationCap className="mr-2 h-4 w-4" />
        Student View
      </Button>
      <Button
        variant={isVidhyaPage ? 'default' : 'outline'}
        size="sm"
        onClick={() => router.push('/vidhya')}
      >
        <MessageCircle className="mr-2 h-4 w-4" />
        Vidhya AI
      </Button>
    </div>
  );
}
