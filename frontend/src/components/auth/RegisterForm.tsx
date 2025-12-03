'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { motion } from 'framer-motion';
import { Loader2, Mail, Lock, User, UserCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useTranslation } from '@/contexts/LanguageContext';

export function RegisterForm() {
  const { t } = useTranslation();
  
  const registerSchema = z.object({
    name: z.string().min(2, t('auth.validation.nameMin')),
    mobile_number: z.string().min(10, t('auth.validation.mobileMin')),
    email_address: z.string().email(t('auth.validation.emailInvalid')),
    password: z.string().min(6, t('auth.validation.passwordMin')),
    repeat_password: z.string().min(6, t('auth.validation.passwordConfirmMin')),
  }).refine((data) => data.password === data.repeat_password, {
    message: t('auth.validation.passwordMismatch'),
    path: ["repeat_password"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { register: registerUser, login } = useAuth();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setError('');
    setSuccessMessage('');
    
    try {
      await registerUser(data);
      setSuccessMessage(t('auth.registrationSuccess'));
      // Auto-login after successful registration
      try {
        const userData = await login(data.email_address, data.password);
        
        // Registration is only for parents, so always go to onboarding
        // Check onboarding status
        try {
          const { examAPI } = await import('@/lib/api');
          const statusResponse = await examAPI.getOnboardingStatus(userData.id);
          const status = statusResponse.data;
          
          // If onboarding is complete, redirect to parent dashboard
          if (status.is_complete) {
            router.push('/parent-dashboard');
          } else {
            // For new registrations, always start with preferences
            router.push('/onboarding/preferences');
          }
        } catch (statusErr) {
          // If status check fails, default to preferences page
          router.push('/onboarding/preferences');
        }
      } catch (loginErr: any) {
        // If auto-login fails, show success message and let user login manually
        setSuccessMessage(t('auth.registrationSuccessLogin'));
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6"
    >
      <div className="space-y-2">
        <Label htmlFor="name">{t('auth.fullName')}</Label>
        <div className="relative">
          <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="name"
            type="text"
            placeholder={t('auth.fullNamePlaceholder')}
            className="pl-10"
            {...register('name')}
          />
        </div>
        {errors.name && (
          <p className="text-sm text-red-500">{errors.name.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="mobile_number">{t('auth.mobileNumber')}</Label>
        <div className="relative">
          <UserCircle className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="mobile_number"
            type="tel"
            placeholder={t('auth.mobileNumberPlaceholder')}
            className="pl-10"
            {...register('mobile_number')}
          />
        </div>
        {errors.mobile_number && (
          <p className="text-sm text-red-500">{errors.mobile_number.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="email_address">{t('auth.email')}</Label>
        <div className="relative">
          <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="email_address"
            type="email"
            placeholder={t('auth.emailPlaceholder')}
            className="pl-10"
            {...register('email_address')}
          />
        </div>
        {errors.email_address && (
          <p className="text-sm text-red-500">{errors.email_address.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">{t('auth.password')}</Label>
        <div className="relative">
          <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            className="pl-10"
            {...register('password')}
          />
        </div>
        {errors.password && (
          <p className="text-sm text-red-500">{errors.password.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="repeat_password">{t('auth.confirmPassword')}</Label>
        <div className="relative">
          <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            id="repeat_password"
            type="password"
            placeholder="••••••••"
            className="pl-10"
            {...register('repeat_password')}
          />
        </div>
        {errors.repeat_password && (
          <p className="text-sm text-red-500">{errors.repeat_password.message}</p>
        )}
      </div>

      <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-md">
        <strong>{t('auth.note')}:</strong> {t('auth.parentPlatformNote')}
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-3 text-sm text-red-500 bg-red-50 rounded-md"
        >
          {error}
        </motion.div>
      )}

      {successMessage && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-3 text-sm text-green-600 bg-green-50 rounded-md"
        >
          {successMessage}
        </motion.div>
      )}

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            {t('auth.creatingAccount')}
          </>
        ) : (
          t('auth.createAccount')
        )}
      </Button>
    </motion.form>
  );
}
