import React from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { ButtonHTMLAttributes, ReactNode } from 'react';

interface NeumorphButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  neumorph?: boolean;
}

export const NeumorphButton: React.FC<NeumorphButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  neumorph = true,
  ...props
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg hover:shadow-xl hover:shadow-purple-500/25';
      case 'secondary':
        return 'bg-white/80 text-gray-700 shadow-lg hover:shadow-xl hover:shadow-gray-500/25';
      case 'success':
        return 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg hover:shadow-xl hover:shadow-green-500/25';
      case 'danger':
        return 'bg-gradient-to-r from-red-500 to-rose-600 text-white shadow-lg hover:shadow-xl hover:shadow-red-500/25';
      case 'warning':
        return 'bg-gradient-to-r from-yellow-500 to-amber-600 text-white shadow-lg hover:shadow-xl hover:shadow-yellow-500/25';
      default:
        return 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg hover:shadow-xl hover:shadow-purple-500/25';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'h-8 px-3 text-sm';
      case 'md':
        return 'h-10 px-4 text-sm';
      case 'lg':
        return 'h-12 px-6 text-base';
      case 'xl':
        return 'h-14 px-8 text-lg';
      default:
        return 'h-10 px-4 text-sm';
    }
  };

  const getNeumorphClasses = () => {
    if (!neumorph) return '';
    
    return `
      relative overflow-hidden
      before:absolute before:inset-0 before:rounded-[inherit]
      before:bg-gradient-to-br before:from-white/20 before:to-transparent
      before:opacity-0 before:transition-opacity before:duration-300
      hover:before:opacity-100
      after:absolute after:inset-0 after:rounded-[inherit]
      after:bg-gradient-to-tr after:from-black/10 after:to-transparent
      after:opacity-0 after:transition-opacity after:duration-300
      hover:after:opacity-100
      transform hover:-translate-y-0.5 transition-all duration-200
    `;
  };

  return (
    <Button
      className={cn(
        'rounded-xl border-0 font-medium backdrop-blur-sm',
        getVariantClasses(),
        getSizeClasses(),
        getNeumorphClasses(),
        className
      )}
      {...props}
    >
      <span className="relative z-10">{children}</span>
    </Button>
  );
};