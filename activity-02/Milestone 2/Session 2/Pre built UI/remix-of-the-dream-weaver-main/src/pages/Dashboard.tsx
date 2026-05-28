import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Building2, 
  Crown, 
  Sparkles, 
  Star, 
  Briefcase,
  TrendingUp 
} from 'lucide-react';
import { MetricCard } from '@/components/ui/metric-card';
import { CompanySearch } from '@/components/search/CompanySearch';
import { useCompaniesShort } from '@/hooks/useSupabaseData';

const Dashboard = () => {
  const navigate = useNavigate();
  const { data: companies = [], isLoading } = useCompaniesShort();

  const counts = {
    total: companies.length,
    marquee: companies.filter(c => c.category === 'Marquee').length,
    superDream: companies.filter(c => c.category === 'SuperDream').length,
    dream: companies.filter(c => c.category === 'Dream').length,
    regular: companies.filter(c => c.category === 'Regular').length,
    enterprise: companies.filter(c => c.category === 'Enterprise').length,
  };

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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground text-sm">Loading placement ecosystem...</p>
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
      <motion.div variants={itemVariants}>
        <h1 className="font-display text-3xl font-bold text-foreground mb-2">
          Dashboard
        </h1>
        <p className="text-muted-foreground">
          Real-time snapshot of your placement ecosystem
        </p>
      </motion.div>

      {/* Metric Cards */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          <MetricCard
            title="Total Companies"
            value={counts.total}
            description="All recruiting partners"
            icon={Building2}
            onClick={() => navigate('/companies')}
          />
          <MetricCard
            title="Marquee"
            value={counts.marquee}
            description="Top-tier with highest compensation"
            icon={Crown}
            variant="marquee"
            onClick={() => navigate('/companies?category=marquee')}
          />
          <MetricCard
            title="Super Dream"
            value={counts.superDream}
            description="Above threshold compensation"
            icon={Sparkles}
            variant="super-dream"
            onClick={() => navigate('/companies?category=superdream')}
          />
          <MetricCard
            title="Dream"
            value={counts.dream}
            description="Dream-level packages"
            icon={Star}
            variant="dream"
            onClick={() => navigate('/companies?category=dream')}
          />
          <MetricCard
            title="Regular"
            value={counts.regular}
            description="Standard entry-level roles"
            icon={Briefcase}
            variant="regular"
            onClick={() => navigate('/companies?category=regular')}
          />
        </div>
      </motion.div>

      {/* Company Search Section */}
      <motion.div variants={itemVariants} className="pt-4">
        <div className="bg-card border border-border rounded-2xl p-8 shadow-card">
          <div className="max-w-2xl mx-auto text-center mb-6">
            <h2 className="font-display text-xl font-semibold text-foreground mb-2">
              Quick Company Access
            </h2>
            <p className="text-muted-foreground text-sm">
              Search and navigate directly to any company's detailed profile
            </p>
          </div>
          <div className="max-w-2xl mx-auto">
            <CompanySearch companies={companies} />
          </div>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-primary to-primary/80 rounded-2xl p-6 text-primary-foreground">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-primary-foreground/20 rounded-lg">
                <TrendingUp className="w-5 h-5" />
              </div>
              <span className="font-medium">Hiring Velocity</span>
            </div>
            <p className="text-3xl font-display font-bold">31,000+</p>
            <p className="text-sm text-primary-foreground/70 mt-1">Open positions across partners</p>
          </div>

          <div className="bg-gradient-to-br from-accent to-accent/80 rounded-2xl p-6 text-accent-foreground">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-accent-foreground/20 rounded-lg">
                <Sparkles className="w-5 h-5" />
              </div>
              <span className="font-medium">Average Package</span>
            </div>
            <p className="text-3xl font-display font-bold">₹18.5 LPA</p>
            <p className="text-sm text-accent-foreground/70 mt-1">Across all categories</p>
          </div>

          <div className="bg-gradient-to-br from-dream to-dream/80 rounded-2xl p-6 text-white">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-white/20 rounded-lg">
                <Building2 className="w-5 h-5" />
              </div>
              <span className="font-medium">New Partners</span>
            </div>
            <p className="text-3xl font-display font-bold">12</p>
            <p className="text-sm text-white/70 mt-1">Added this quarter</p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;
