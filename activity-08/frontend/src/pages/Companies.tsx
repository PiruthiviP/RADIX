import { useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Building2, Filter, Grid3X3, List } from 'lucide-react';
import { CompanySearch } from '@/components/search/CompanySearch';
import { CompanyCard } from '@/components/companies/CompanyCard';
import { useCompaniesShort } from '@/hooks/useSupabaseData';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const categoryFilters = [
  { key: null, label: 'All', count: 0 },
  { key: 'marquee', label: 'Marquee', count: 0 },
  { key: 'superdream', label: 'Super Dream', count: 0 },
  { key: 'dream', label: 'Dream', count: 0 },
  { key: 'regular', label: 'Regular', count: 0 },
  { key: 'enterprise', label: 'Enterprise', count: 0 },
];

const Companies = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryParam = searchParams.get('category');
  const [searchQuery, setSearchQuery] = useState('');
  
  const { data: companies = [], isLoading } = useCompaniesShort();

  // Calculate counts
  const countsMap = useMemo(() => {
    const counts: Record<string, number> = { all: companies.length };
    companies.forEach(company => {
      if (company.category) {
        const key = company.category.toLowerCase();
        counts[key] = (counts[key] || 0) + 1;
      }
    });
    return counts;
  }, [companies]);

  // Filter companies
  const filteredCompanies = useMemo(() => {
    let list = companies;
    
    if (categoryParam) {
      list = list.filter(company => 
        company.category && company.category.toLowerCase() === categoryParam.toLowerCase()
      );
    }
    
    if (searchQuery) {
      list = list.filter(company =>
        company.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        company.short_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    return list;
  }, [companies, categoryParam, searchQuery]);

  const handleFilterChange = (category: string | null) => {
    if (category) {
      setSearchParams({ category });
    } else {
      setSearchParams({});
    }
  };

  const getCategoryBadgeClass = (key: string | null) => {
    if (!key) return 'bg-primary text-primary-foreground';
    switch (key) {
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
          <p className="text-muted-foreground text-sm">Loading partners directory...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-6"
    >
      {/* Page Header */}
      <div>
        <h1 className="font-display text-3xl font-bold text-foreground mb-2">
          Companies
        </h1>
        <p className="text-muted-foreground">
          Explore and discover our recruiting partners
        </p>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        <CompanySearch 
          companies={companies}
          placeholder="Search companies..."
          onQueryChange={setSearchQuery}
        />

        {/* Category Filters */}
        <div className="flex flex-wrap gap-2">
          {categoryFilters.map((filter) => {
            const count = filter.key === null 
              ? countsMap.all 
              : (countsMap[filter.key] || 0);
            const isActive = categoryParam === filter.key || (!categoryParam && !filter.key);
            
            return (
              <button
                key={filter.key || 'all'}
                onClick={() => handleFilterChange(filter.key)}
                className={cn(
                  'px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-2',
                  isActive
                    ? getCategoryBadgeClass(filter.key)
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                )}
              >
                {filter.label}
                <span className={cn(
                  'px-1.5 py-0.5 rounded-md text-xs',
                  isActive ? 'bg-white/20' : 'bg-muted'
                )}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing <span className="font-medium text-foreground">{filteredCompanies.length}</span> companies
        </p>
      </div>

      {/* Companies Grid */}
      {filteredCompanies.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredCompanies.map((company, index) => (
            <CompanyCard key={company.company_id} company={company} index={index} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <Building2 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="font-display text-lg font-semibold text-foreground mb-2">
            No companies found
          </h3>
          <p className="text-muted-foreground">
            Try adjusting your search or filters
          </p>
        </div>
      )}
    </motion.div>
  );
};

export default Companies;
