import { motion } from 'framer-motion';
import { Building2, MapPin, Users, Calendar, TrendingUp } from 'lucide-react';
import { CompanyShort } from '@/types/company';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';

interface CompanyCardProps {
  company: CompanyShort;
  index?: number;
}

export function CompanyCard({ company, index = 0 }: CompanyCardProps) {
  const navigate = useNavigate();

  const getCategoryBadgeClass = (category: string) => {
    switch (category.toLowerCase()) {
      case 'marquee':
        return 'badge-marquee';
      case 'superdream':
        return 'badge-super-dream';
      case 'dream':
        return 'badge-dream';
      case 'regular':
        return 'badge-regular';
      case 'enterprise':
        return 'badge-enterprise';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const headquarters = company.office_locations.split(';')[0]?.trim() || 'N/A';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      whileHover={{ y: -4 }}
      onClick={() => navigate(`/companies/${company.company_id}`)}
      className="bg-card border border-border rounded-2xl p-6 cursor-pointer shadow-card hover:shadow-card-hover transition-all duration-200 group"
    >
      {/* Header with Logo and Category */}
      <div className="flex items-start justify-between mb-4">
        <div className="w-14 h-14 rounded-xl bg-muted flex items-center justify-center overflow-hidden">
          {company.logo_url ? (
            <img 
              src={company.logo_url} 
              alt={company.short_name}
              className="w-10 h-10 object-contain"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
                (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
              }}
            />
          ) : null}
          <Building2 className={cn("w-7 h-7 text-muted-foreground", company.logo_url && "hidden")} />
        </div>
        <span className={cn(
          'px-3 py-1 text-xs font-semibold rounded-full',
          getCategoryBadgeClass(company.category)
        )}>
          {company.category}
        </span>
      </div>

      {/* Company Name */}
      <h3 className="font-display font-bold text-lg text-foreground mb-1 group-hover:text-primary transition-colors">
        {company.short_name}
      </h3>
      <p className="text-sm text-muted-foreground mb-4 line-clamp-1">
        {company.name}
      </p>

      {/* Info Grid */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <MapPin className="w-4 h-4 flex-shrink-0" />
          <span className="truncate">{headquarters}</span>
        </div>
        
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Users className="w-4 h-4 flex-shrink-0" />
          <span>{company.employee_size}</span>
        </div>

        <div className="flex items-center gap-2 text-sm">
          <TrendingUp className={cn(
            "w-4 h-4 flex-shrink-0",
            company.yoy_growth_rate.startsWith('-') ? 'text-destructive' : 'text-accent'
          )} />
          <span className={cn(
            "font-medium",
            company.yoy_growth_rate.startsWith('-') ? 'text-destructive' : 'text-accent'
          )}>
            {company.yoy_growth_rate} YoY Growth
          </span>
        </div>
      </div>
    </motion.div>
  );
}
