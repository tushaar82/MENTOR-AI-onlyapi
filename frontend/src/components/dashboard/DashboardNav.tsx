'use client';

import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Users, GraduationCap, MessageCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useTranslation } from '@/contexts/LanguageContext';
import { LanguageSwitcher } from '@/components/ui/LanguageSwitcher';

export function DashboardNav() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
  const { t } = useTranslation();

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
        {t('dashboard.parent.title')}
      </Button>
      <Button
        variant={!isParentDashboard && !isVidhyaPage ? 'default' : 'outline'}
        size="sm"
        onClick={() => router.push('/dashboard')}
      >
        <GraduationCap className="mr-2 h-4 w-4" />
        {t('dashboard.student.title')}
      </Button>
      <Button
        variant={isVidhyaPage ? 'default' : 'outline'}
        size="sm"
        onClick={() => router.push('/vidhya')}
      >
        <MessageCircle className="mr-2 h-4 w-4" />
        {t('vidhya.title')}
      </Button>
      
      {/* Language Switcher */}
      <div className="ml-auto">
        <LanguageSwitcher />
      </div>
    </div>
  );
}
