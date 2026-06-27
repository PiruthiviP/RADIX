import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Building2, MapPin, Users } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { CompanyShort } from '@/types/company';
import { cn } from '@/lib/utils';
import { useNavigate } from 'react-router-dom';

interface CompanySearchProps {
  companies: CompanyShort[];
  placeholder?: string;
  onSelect?: (company: CompanyShort) => void;
  onQueryChange?: (query: string) => void;
  className?: string;
}

export function CompanySearch({
  companies,
  placeholder = 'Search by company name (e.g., Amazon, TCS, Microsoft)',
  onSelect,
  onQueryChange,
  className,
}: CompanySearchProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const filteredCompanies = query.length > 0
    ? companies.filter(company =>
        company.name.toLowerCase().includes(query.toLowerCase()) ||
        company.short_name.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 8)
    : [];

  useEffect(() => {
    setSelectedIndex(0);
  }, [filteredCompanies.length]);

  const handleSelect = (company: CompanyShort) => {
    setQuery('');
    setIsOpen(false);
    if (onSelect) {
      onSelect(company);
    } else {
      navigate(`/companies/${company.company_id}`);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || filteredCompanies.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % filteredCompanies.length);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + filteredCompanies.length) % filteredCompanies.length);
        break;
      case 'Enter':
        e.preventDefault();
        handleSelect(filteredCompanies[selectedIndex]);
        break;
      case 'Escape':
        setIsOpen(false);
        break;
    }
  };

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

  return (
    <div className={cn('relative w-full', className)}>
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <Input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            const val = e.target.value;
            setQuery(val);
            setIsOpen(true);
            if (onQueryChange) {
              onQueryChange(val);
            }
          }}
          onFocus={() => setIsOpen(true)}
          onBlur={() => setTimeout(() => setIsOpen(false), 200)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="pl-12 pr-4 py-6 text-base rounded-2xl border-2 border-border bg-card shadow-sm focus:border-primary/50 focus:ring-primary/20 transition-all"
        />
      </div>

      <AnimatePresence>
        {isOpen && filteredCompanies.length > 0 && (
          <motion.div
            ref={listRef}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-2xl shadow-lg overflow-hidden z-50"
          >
            <div className="py-2">
              {filteredCompanies.map((company, index) => (
                <motion.button
                  key={company.company_id}
                  onClick={() => handleSelect(company)}
                  className={cn(
                    'w-full px-4 py-3 flex items-center gap-4 text-left transition-colors',
                    index === selectedIndex ? 'bg-secondary' : 'hover:bg-secondary/50'
                  )}
                >
                  <div className="w-10 h-10 rounded-xl bg-muted flex items-center justify-center overflow-hidden flex-shrink-0">
                    {company.logo_url ? (
                      <img 
                        src={company.logo_url} 
                        alt={company.short_name}
                        className="w-6 h-6 object-contain"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = 'none';
                          (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                        }}
                      />
                    ) : null}
                    <Building2 className={cn("w-5 h-5 text-muted-foreground", company.logo_url && "hidden")} />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-foreground truncate">
                        {company.short_name}
                      </span>
                      <span className={cn(
                        'px-2 py-0.5 text-xs font-medium rounded-full',
                        getCategoryBadgeClass(company.category)
                      )}>
                        {company.category}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {company.office_locations.split(';')[0]}
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {company.employee_size}
                      </span>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
