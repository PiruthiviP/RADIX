import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { GitBranch, Search, Building2, MapPin, Users } from 'lucide-react';
import { CompanySearch } from '@/components/search/CompanySearch';
import { useCompaniesShort } from '@/hooks/useSupabaseData';
import { cn } from '@/lib/utils';

const HiringProcess = () => {
  const navigate = useNavigate();
  const { data: companies = [], isLoading } = useCompaniesShort();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
      },
    },
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground text-sm">Loading hiring processes...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-8"
    >
      {/* Page Header */}
      <div className="text-center max-w-2xl mx-auto">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 mb-4">
          <GitBranch className="w-8 h-8 text-primary" />
        </div>
        <h1 className="font-display text-3xl font-bold text-foreground mb-2">
          Hiring Process
        </h1>
        <p className="text-muted-foreground">
          Explore company-specific hiring processes and selection stages
        </p>
      </div>

      {/* Search */}
      <div className="max-w-2xl mx-auto">
        <CompanySearch 
          companies={companies}
          placeholder="Search company to view their hiring process..."
          onSelect={(company) => navigate(`/companies/${company.company_id}/process`)}
        />
      </div>

      {/* Company Cards */}
      <div>
        <h2 className="font-display text-xl font-semibold mb-4">
          Browse Companies
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {companies.slice(0, 8).map((company, index) => (
            <motion.div
              key={company.company_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              whileHover={{ y: -4 }}
              onClick={() => navigate(`/companies/${company.company_id}/process`)}
              className="bg-card border border-border rounded-2xl p-6 cursor-pointer shadow-card hover:shadow-card-hover transition-all duration-200 group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center overflow-hidden flex-shrink-0">
                  {company.logo_url ? (
                    <img 
                      src={company.logo_url} 
                      alt={company.short_name}
                      className="w-8 h-8 object-contain"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  ) : (
                    <Building2 className="w-6 h-6 text-muted-foreground" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                    {company.short_name}
                  </h3>
                  <p className="text-sm text-muted-foreground flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {company.office_locations.split(';')[0]?.split(',')[1]?.trim() || 'Global'}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default HiringProcess;
