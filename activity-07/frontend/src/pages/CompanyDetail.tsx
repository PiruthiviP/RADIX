import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useState } from 'react';
import {
  Building2,
  MapPin,
  Users,
  Calendar,
  Globe,
  Linkedin,
  Twitter,
  ExternalLink,
  ArrowLeft,
  GraduationCap,
  GitBranch,
  Lightbulb,
  Star,
  TrendingUp,
  DollarSign,
  Shield,
  Award,
  Target,
  Briefcase,
  Heart,
  Zap,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useCompanyFull, useCompaniesShort } from '@/hooks/useSupabaseData';
import { cn } from '@/lib/utils';

const CompanyDetail = () => {
  const { companyId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  const cid = Number(companyId);
  const { data: company, isLoading: isLoadingFull } = useCompanyFull(cid);
  const { data: companiesShort = [], isLoading: isLoadingShort } = useCompaniesShort();
  const shortCompany = companiesShort.find(c => c.company_id === cid);

  const isLoading = isLoadingFull || isLoadingShort;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground text-sm">Loading company profile...</p>
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-center py-16">
        <Building2 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="font-display text-lg font-semibold">Company not found</h3>
      </div>
    );
  }

  const getCategoryBadgeClass = (category: string) => {
    switch (category.toLowerCase()) {
      case 'marquee': return 'badge-marquee';
      case 'superdream': return 'badge-super-dream';
      case 'dream': return 'badge-dream';
      case 'regular': return 'badge-regular';
      case 'enterprise': return 'badge-enterprise';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const InfoCard = ({ icon: Icon, label, value, className }: { icon: any; label: string; value: string; className?: string }) => (
    <div className={cn("bg-secondary/50 rounded-xl p-4", className)}>
      <div className="flex items-center gap-2 text-muted-foreground mb-1">
        <Icon className="w-4 h-4" />
        <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
      </div>
      <p className="font-medium text-foreground">{value}</p>
    </div>
  );

  const SectionCard = ({ title, icon: Icon, children }: { title: string; icon: any; children: React.ReactNode }) => (
    <div className="bg-card border border-border rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-primary/10 rounded-lg">
          <Icon className="w-5 h-5 text-primary" />
        </div>
        <h3 className="font-display font-semibold text-lg">{title}</h3>
      </div>
      {children}
    </div>
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Back Button */}
      <Button 
        variant="ghost" 
        onClick={() => navigate('/companies')}
        className="gap-2"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Companies
      </Button>

      {/* Company Header */}
      <div className="bg-card border border-border rounded-2xl p-8 shadow-card">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Left: Logo + Info */}
          <div className="flex items-start gap-6">
            <div className="w-20 h-20 rounded-2xl bg-muted flex items-center justify-center overflow-hidden flex-shrink-0">
              {company.logo_url ? (
                <img 
                  src={company.logo_url} 
                  alt={company.short_name}
                  className="w-14 h-14 object-contain"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              ) : (
                <Building2 className="w-10 h-10 text-muted-foreground" />
              )}
            </div>
            
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="font-display text-2xl font-bold text-foreground">
                  {company.short_name}
                </h1>
                <span className={cn(
                  'px-3 py-1 text-xs font-semibold rounded-full',
                  getCategoryBadgeClass(company.category)
                )}>
                  {company.category}
                </span>
              </div>
              <p className="text-muted-foreground mb-4">{company.name}</p>
              
              <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4" />
                  {company.headquarters_address}
                </span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  Est. {company.incorporation_year}
                </span>
                <span className="flex items-center gap-1.5">
                  <Users className="w-4 h-4" />
                  {company.employee_size}
                </span>
              </div>
            </div>
          </div>

          {/* Right: Action Buttons */}
          <div className="flex flex-wrap gap-3">
            <Button 
              onClick={() => navigate(`/companies/${companyId}/skills`)}
              className="gap-2"
            >
              <GraduationCap className="w-4 h-4" />
              Hiring Skill Sets
            </Button>
            <Button 
              variant="outline"
              onClick={() => navigate(`/companies/${companyId}/process`)}
              className="gap-2"
            >
              <GitBranch className="w-4 h-4" />
              Hiring Process
            </Button>
            <Button 
              variant="outline"
              onClick={() => navigate(`/companies/${companyId}/innovx`)}
              className="gap-2"
            >
              <Lightbulb className="w-4 h-4" />
              INNOVX
            </Button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="bg-card border border-border p-1 rounded-xl">
          <TabsTrigger value="overview" className="rounded-lg">Overview</TabsTrigger>
          <TabsTrigger value="business" className="rounded-lg">Business Model</TabsTrigger>
          <TabsTrigger value="financials" className="rounded-lg">Financials</TabsTrigger>
          <TabsTrigger value="culture" className="rounded-lg">Culture & Values</TabsTrigger>
          <TabsTrigger value="technology" className="rounded-lg">Technology</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <InfoCard icon={Globe} label="Operating In" value={company.office_count ? `${company.office_count} offices` : 'Not Available'} />
            <InfoCard icon={TrendingUp} label="YoY Growth" value={typeof company.yoy_growth_rate === 'number' ? `${(company.yoy_growth_rate * 100).toFixed(0)}%` : (company.yoy_growth_rate || 'Not Available')} />
            <InfoCard icon={Star} label="Glassdoor" value={typeof company.glassdoor_rating === 'number' ? `${company.glassdoor_rating.toFixed(1)} / 5` : (company.glassdoor_rating || 'Not Available')} />
            <InfoCard icon={Users} label="Retention" value={company.avg_retention_tenure || 'Not Available'} />
          </div>

          {/* About */}
          <SectionCard title="About" icon={Building2}>
            <p className="text-muted-foreground leading-relaxed">{company.overview_text}</p>
          </SectionCard>

          {/* Vision & Mission */}
          <div className="grid md:grid-cols-2 gap-6">
            <SectionCard title="Vision" icon={Target}>
              <p className="text-muted-foreground">{company.vision_statement}</p>
            </SectionCard>
            <SectionCard title="Mission" icon={Zap}>
              <p className="text-muted-foreground">{company.mission_statement}</p>
            </SectionCard>
          </div>

          {/* Core Values */}
          <SectionCard title="Core Values" icon={Heart}>
            <div className="flex flex-wrap gap-2">
              {(company.core_values || 'Not Available').split(';').map((value, i) => (
                <span key={i} className="px-3 py-1.5 bg-primary/10 text-primary rounded-lg text-sm font-medium">
                  {value.trim()}
                </span>
              ))}
            </div>
          </SectionCard>

          {/* Focus Sectors */}
          <SectionCard title="Focus Sectors" icon={Briefcase}>
            <div className="flex flex-wrap gap-2">
              {(company.focus_sectors || 'Not Available').split(';').map((sector, i) => (
                <span key={i} className="px-3 py-1.5 bg-secondary text-secondary-foreground rounded-lg text-sm">
                  {sector.trim()}
                </span>
              ))}
            </div>
          </SectionCard>
        </TabsContent>

        <TabsContent value="business" className="space-y-6">
          <SectionCard title="Offerings" icon={Briefcase}>
            <div className="flex flex-wrap gap-2">
              {(company.offerings_description || 'Not Available').split(';').map((offering, i) => (
                <span key={i} className="px-3 py-1.5 bg-accent/10 text-accent rounded-lg text-sm font-medium">
                  {offering.trim()}
                </span>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Top Customers" icon={Users}>
            <p className="text-muted-foreground">{company.top_customers}</p>
          </SectionCard>

          <SectionCard title="Competitive Advantages" icon={Shield}>
            <p className="text-muted-foreground">{company.competitive_advantages}</p>
          </SectionCard>

          <SectionCard title="Key Competitors" icon={Target}>
            <div className="flex flex-wrap gap-2">
              {(company.key_competitors || 'Not Available').split(';').map((comp, i) => (
                <span key={i} className="px-3 py-1.5 bg-destructive/10 text-destructive rounded-lg text-sm">
                  {comp.trim()}
                </span>
              ))}
            </div>
          </SectionCard>
        </TabsContent>

        <TabsContent value="financials" className="space-y-6">
          <div className="grid md:grid-cols-3 gap-4">
            <InfoCard icon={DollarSign} label="Annual Revenue" value={company.annual_revenue} />
            <InfoCard icon={TrendingUp} label="Net Profit" value={company.annual_profit} />
            <InfoCard icon={Target} label="Valuation" value={company.valuation} />
          </div>

          <SectionCard title="Revenue Mix" icon={DollarSign}>
            <p className="text-muted-foreground">{(company.revenue_mix || 'Not Available').replace(/;/g, ' | ')}</p>
          </SectionCard>

          <SectionCard title="Key Investors" icon={Users}>
            <p className="text-muted-foreground">{company.key_investors}</p>
          </SectionCard>
        </TabsContent>

        <TabsContent value="culture" className="space-y-6">
          <div className="grid md:grid-cols-2 gap-4">
            <InfoCard icon={Heart} label="Work Culture" value={company.work_culture_summary} />
            <InfoCard icon={Users} label="Remote Policy" value={company.remote_policy_details} />
            <InfoCard icon={Award} label="Diversity" value={company.diversity_metrics} />
            <InfoCard icon={Shield} label="Psychological Safety" value={company.psychological_safety} />
          </div>

          <SectionCard title="Awards & Recognition" icon={Award}>
            <div className="flex flex-wrap gap-2">
              {(company.awards_recognitions || 'Not Available').split(';').map((award, i) => (
                <span key={i} className="px-3 py-1.5 bg-amber-500/10 text-amber-600 rounded-lg text-sm font-medium">
                  🏆 {award.trim()}
                </span>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Benefits & Perks" icon={Heart}>
            <p className="text-muted-foreground">{company.lifestyle_benefits}</p>
          </SectionCard>
        </TabsContent>

        <TabsContent value="technology" className="space-y-6">
          <SectionCard title="Tech Stack" icon={Zap}>
            <div className="flex flex-wrap gap-2">
              {(company.tech_stack || 'Not Available').split(';').map((tech, i) => (
                <span key={i} className="px-3 py-1.5 bg-blue-500/10 text-blue-600 rounded-lg text-sm font-medium">
                  {tech.trim()}
                </span>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Technology Partners" icon={Users}>
            <div className="flex flex-wrap gap-2">
              {(company.technology_partners || 'Not Available').split(';').map((partner, i) => (
                <span key={i} className="px-3 py-1.5 bg-purple-500/10 text-purple-600 rounded-lg text-sm font-medium">
                  {partner.trim()}
                </span>
              ))}
            </div>
          </SectionCard>

          <div className="grid md:grid-cols-2 gap-4">
            <InfoCard icon={Zap} label="AI/ML Adoption" value={company.ai_ml_adoption_level} />
            <InfoCard icon={Shield} label="Security Posture" value={company.cybersecurity_posture} />
          </div>

          <SectionCard title="R&D Investment" icon={Target}>
            <p className="text-muted-foreground">{company.r_and_d_investment}</p>
          </SectionCard>
        </TabsContent>
      </Tabs>

      {/* External Links */}
      <div className="bg-card border border-border rounded-2xl p-6">
        <h3 className="font-display font-semibold mb-4">External Links</h3>
        <div className="flex flex-wrap gap-3">
          <a 
            href={company.website_url || '#'} 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-xl text-sm hover:bg-secondary/80 transition-colors"
          >
            <Globe className="w-4 h-4" />
            Website
            <ExternalLink className="w-3 h-3" />
          </a>
          <a 
            href={company.linkedin_url || '#'} 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-xl text-sm hover:bg-secondary/80 transition-colors"
          >
            <Linkedin className="w-4 h-4" />
            LinkedIn
            <ExternalLink className="w-3 h-3" />
          </a>
          <a 
            href={company.twitter_handle ? `https://twitter.com/${company.twitter_handle.replace('@', '')}` : '#'} 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-xl text-sm hover:bg-secondary/80 transition-colors"
          >
            <Twitter className="w-4 h-4" />
            Twitter
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </motion.div>
  );
};

export default CompanyDetail;
