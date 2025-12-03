'use client';

import { motion } from 'framer-motion';
import { Target, Zap, BarChart3, Users, Calendar, Award } from 'lucide-react';
import { useTranslation } from '@/contexts/LanguageContext';

export function Features() {
  const { t } = useTranslation();
  
  const features = [
    {
      icon: Target,
      title: t('features.feature1.title'),
      description: t('features.feature1.description'),
    },
    {
      icon: Zap,
      title: t('features.feature2.title'),
      description: t('features.feature2.description'),
    },
    {
      icon: BarChart3,
      title: t('features.feature3.title'),
      description: t('features.feature3.description'),
    },
    {
      icon: Users,
      title: t('features.feature4.title'),
      description: t('features.feature4.description'),
    },
    {
      icon: Calendar,
      title: t('features.feature5.title'),
      description: t('features.feature5.description'),
    },
    {
      icon: Award,
      title: t('features.feature6.title'),
      description: t('features.feature6.description'),
    },
  ];
  return (
    <section id="features" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            {t('features.title')}
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            {t('features.subtitle')}
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="group p-8 rounded-2xl border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all duration-300"
            >
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:bg-blue-600 transition-colors">
                <feature.icon className="w-7 h-7 text-blue-600 group-hover:text-white transition-colors" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
