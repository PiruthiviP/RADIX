import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Lightbulb, 
  Rocket, 
  Building2, 
  MapPin,
  TrendingUp,
  Cpu,
  Globe,
  Zap 
} from 'lucide-react';
import { CompanySearch } from '@/components/search/CompanySearch';
import { useCompaniesShort } from '@/hooks/useSupabaseData';
import { cn } from '@/lib/utils';

const InnovX = () => {
  const navigate = useNavigate();
  const { data: companies = [], isLoading } = useCompaniesShort();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  const features = [
    {
      icon: TrendingUp,
      title: 'Industry Trends',
      description: 'Discover emerging technologies and market shifts',
    },
    {
      icon: Cpu,
      title: 'Innovation Roadmap',
      description: 'Explore strategic innovation pillars and projects',
    },
    {
      icon: Globe,
      title: 'Competitive Landscape',
      description: 'Understand competitor positioning and strategies',
    },
    {
      icon: Zap,
      title: 'Student Projects',
      description: 'Find project ideas aligned with company focus',
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground text-sm">Loading innovation roadmap...</p>
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
      {/* Hero Section */}
      <motion.div 
        variants={itemVariants}
        className="relative overflow-hidden rounded-3xl gradient-primary p-8 md:p-12 text-primary-foreground"
      >
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary-foreground/10 rounded-full text-sm mb-4">
            <Rocket className="w-4 h-4" />
            Innovation Accelerator
          </div>
          <h1 className="font-display text-3xl md:text-4xl font-bold mb-4">
            INNOVX
          </h1>
          <p className="text-primary-foreground/80 text-lg mb-6">
            Explore industry trends, innovation roadmaps, and discover what companies are building next. 
            Align yourself with the future of technology.
          </p>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-foreground/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-48 h-48 bg-accent/20 rounded-full blur-2xl" />
      </motion.div>

      {/* Search */}
      <motion.div variants={itemVariants} className="max-w-2xl mx-auto">
        <CompanySearch 
          companies={companies}
          placeholder="Search company to explore their innovation insights..."
          onSelect={(company) => navigate(`/companies/${company.company_id}/innovx`)}
        />
      </motion.div>

      {/* Features Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {features.map((feature, index) => (
          <div 
            key={index}
            className="bg-card border border-border rounded-2xl p-6 hover:shadow-card-hover transition-all"
          >
            <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mb-4">
              <feature.icon className="w-6 h-6 text-accent" />
            </div>
            <h3 className="font-display font-semibold text-foreground mb-2">{feature.title}</h3>
            <p className="text-sm text-muted-foreground">{feature.description}</p>
          </div>
        ))}
      </motion.div>

      {/* Company Cards */}
      <motion.div variants={itemVariants}>
        <h2 className="font-display text-xl font-semibold mb-4">
          Explore Company Innovations
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.slice(0, 6).map((company, index) => (
            <motion.div
              key={company.company_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              whileHover={{ y: -4 }}
              onClick={() => navigate(`/companies/${company.company_id}/innovx`)}
              className="bg-card border border-border rounded-2xl p-6 cursor-pointer shadow-card hover:shadow-card-hover transition-all duration-200 group"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-14 h-14 rounded-xl bg-muted flex items-center justify-center overflow-hidden flex-shrink-0">
                  {company.logo_url ? (
                    <img 
                      src={company.logo_url} 
                      alt={company.short_name}
                      className="w-10 h-10 object-contain"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  ) : (
                    <Building2 className="w-7 h-7 text-muted-foreground" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-display font-semibold text-foreground group-hover:text-primary transition-colors">
                    {company.short_name}
                  </h3>
                  <p className="text-sm text-muted-foreground">{company.name}</p>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-accent/10 text-accent text-xs rounded-lg">
                  🚀 Innovation Leader
                </span>
                <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-lg">
                  🤖 AI Focus
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default InnovX;
