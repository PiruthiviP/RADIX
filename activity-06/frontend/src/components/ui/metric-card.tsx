import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: number | string;
  description?: string;
  icon: LucideIcon;
  variant?: 'default' | 'marquee' | 'super-dream' | 'dream' | 'regular' | 'enterprise';
  onClick?: () => void;
}

const variantStyles = {
  default: {
    bg: 'bg-card',
    icon: 'bg-primary/10 text-primary',
    border: 'border-border',
    hover: 'hover:shadow-card-hover hover:border-primary/30',
  },
  marquee: {
    bg: 'bg-card',
    icon: 'bg-marquee/10 text-marquee',
    border: 'border-marquee/20',
    hover: 'hover:shadow-card-hover hover:border-marquee/40',
  },
  'super-dream': {
    bg: 'bg-card',
    icon: 'bg-super-dream/10 text-super-dream',
    border: 'border-super-dream/20',
    hover: 'hover:shadow-card-hover hover:border-super-dream/40',
  },
  dream: {
    bg: 'bg-card',
    icon: 'bg-dream/10 text-dream',
    border: 'border-dream/20',
    hover: 'hover:shadow-card-hover hover:border-dream/40',
  },
  regular: {
    bg: 'bg-card',
    icon: 'bg-regular/10 text-regular',
    border: 'border-regular/20',
    hover: 'hover:shadow-card-hover hover:border-regular/40',
  },
  enterprise: {
    bg: 'bg-card',
    icon: 'bg-enterprise/10 text-enterprise',
    border: 'border-enterprise/20',
    hover: 'hover:shadow-card-hover hover:border-enterprise/40',
  },
};

export function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  variant = 'default',
  onClick,
}: MetricCardProps) {
  const styles = variantStyles[variant];

  return (
    <motion.div
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        'p-6 rounded-2xl border shadow-card cursor-pointer transition-all duration-200',
        styles.bg,
        styles.border,
        styles.hover
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={cn('p-3 rounded-xl', styles.icon)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      
      <div>
        <h3 className="text-sm font-medium text-muted-foreground mb-1">{title}</h3>
        <p className="text-3xl font-display font-bold text-foreground">{value}</p>
        {description && (
          <p className="text-xs text-muted-foreground mt-2">{description}</p>
        )}
      </div>
    </motion.div>
  );
}
