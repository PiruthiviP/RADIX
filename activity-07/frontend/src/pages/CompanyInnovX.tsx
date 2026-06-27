import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Building2, 
  MapPin, 
  Users, 
  GraduationCap,
  GitBranch,
  Lightbulb,
  TrendingUp,
  Target,
  Zap,
  Shield,
  Rocket,
  Globe,
  Clock,
  Star,
  AlertTriangle,
  Layers,
  Sparkles,
  HelpCircle,
  Briefcase
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCompanyFull, useCompanyInnovX } from '@/hooks/useSupabaseData';
import { cn } from '@/lib/utils';

const getTierColor = (tier: string) => {
  switch ((tier || '').toLowerCase()) {
    case 'tier 1':
      return 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30';
    case 'tier 2':
      return 'bg-blue-500/10 text-blue-600 border-blue-500/30';
    case 'tier 3':
      return 'bg-purple-500/10 text-purple-600 border-purple-500/30';
    default:
      return 'bg-muted text-muted-foreground';
  }
};

const getImportanceColor = (imp: string) => {
  switch ((imp || '').toLowerCase()) {
    case 'critical':
      return 'bg-red-100 text-red-700';
    case 'high':
      return 'bg-orange-100 text-orange-700';
    case 'medium':
      return 'bg-amber-100 text-amber-700';
    default:
      return 'bg-blue-100 text-blue-700';
  }
};

const CompanyInnovX = () => {
  const { companyId } = useParams();
  const navigate = useNavigate();
  const cid = Number(companyId);

  const { data: company, isLoading: isLoadingCompany } = useCompanyFull(cid);
  const { data: innovxData, isLoading: isLoadingInnovX } = useCompanyInnovX(cid);

  const getCategoryBadgeClass = (category: string) => {
    switch ((category || '').toLowerCase()) {
      case 'marquee': return 'badge-marquee';
      case 'superdream': return 'badge-super-dream';
      case 'dream': return 'badge-dream';
      case 'regular': return 'badge-regular';
      case 'enterprise': return 'badge-enterprise';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const isLoading = isLoadingCompany || isLoadingInnovX;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground text-sm">Loading innovation intelligence...</p>
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

  const master = innovxData?.innovx_master;
  const trends = innovxData?.industry_trends || [];
  const competitors = innovxData?.competitive_landscape || [];
  const projects = innovxData?.innovx_projects || [];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      {/* Sticky Header */}
      <div className="bg-card border border-border rounded-2xl p-6 shadow-card sticky top-0 z-10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center overflow-hidden flex-shrink-0">
              {company.logo_url ? (
                <img src={company.logo_url} alt={company.short_name} className="w-8 h-8 object-contain" />
              ) : (
                <Building2 className="w-6 h-6 text-muted-foreground" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-display font-bold text-xl">{company.short_name || 'Not Available'}</h1>
                <span className={cn('px-2 py-0.5 text-xs rounded-full', getCategoryBadgeClass(company.category))}>
                  {company.category || 'Not Available'}
                </span>
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{company.headquarters_address || 'Not Available'}</span>
                <span className="flex items-center gap-1"><Users className="w-3 h-3" />{company.employee_size || 'Not Available'}</span>
              </div>
            </div>
          </div>
          
          {/* Tab Navigation */}
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2" onClick={() => navigate(`/companies/${companyId}/skills`)}>
              <GraduationCap className="w-4 h-4" />
              Skill Sets
            </Button>
            <Button variant="outline" size="sm" className="gap-2" onClick={() => navigate(`/companies/${companyId}/process`)}>
              <GitBranch className="w-4 h-4" />
              Hiring Process
            </Button>
            <Button variant="default" size="sm" className="gap-2">
              <Lightbulb className="w-4 h-4" />
              INNOVX
            </Button>
          </div>
        </div>
      </div>

      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl gradient-primary p-8 text-primary-foreground">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-primary-foreground/10 rounded-full text-sm mb-4">
            <Rocket className="w-4 h-4 text-accent" />
            Innovation Intelligence
          </div>
          <h2 className="font-display text-2xl md:text-3xl font-bold mb-2">INNOVX Analysis</h2>
          <p className="text-primary-foreground/80 max-w-2xl leading-relaxed text-sm">
            Discover emerging industry trends, competitive mapping, and prospective projects. 
            Align your technology specialization with the future strategic roadmap of {company.short_name}.
          </p>

          {master && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-primary-foreground/20 text-xs">
              <div>
                <span className="text-primary-foreground/60 block mb-0.5">Industry Sector</span>
                <span className="font-semibold">{master.industry || 'Not Available'}</span>
              </div>
              <div>
                <span className="text-primary-foreground/60 block mb-0.5">Core Business Model</span>
                <span className="font-semibold">{master.core_business_model || 'Not Available'}</span>
              </div>
              <div>
                <span className="text-primary-foreground/60 block mb-0.5">Target Market</span>
                <span className="font-semibold">{master.target_market || 'Not Available'}</span>
              </div>
              <div>
                <span className="text-primary-foreground/60 block mb-0.5">Geographic Focus</span>
                <span className="font-semibold">{master.geographic_focus || 'Not Available'}</span>
              </div>
            </div>
          )}
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-foreground/5 rounded-full blur-3xl" />
      </div>

      {!innovxData ? (
        <div className="bg-card border border-border rounded-2xl p-8 text-center text-muted-foreground">
          <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-muted-foreground/60" />
          <p>Innovation intelligence data is not available for this company at this time.</p>
        </div>
      ) : (
        <>
          {/* Industry Trends */}
          <section className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-500/10 rounded-lg">
                <TrendingUp className="w-5 h-5 text-amber-500" />
              </div>
              <h3 className="font-display text-xl font-bold text-foreground">Industry Trends</h3>
            </div>
            
            {trends.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">No industry trends available.</p>
            ) : (
              <div className="grid md:grid-cols-3 gap-4">
                {trends.map((trend, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-card border border-border rounded-2xl p-6 flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-start justify-between mb-3">
                        <span className={cn(
                          'px-2 py-0.5 text-[10px] font-semibold rounded-full uppercase',
                          getImportanceColor(trend.strategic_importance)
                        )}>
                          {trend.strategic_importance || 'Medium'}
                        </span>
                        {trend.time_horizon_years && (
                          <span className="text-xs text-muted-foreground flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            {trend.time_horizon_years}yr horizon
                          </span>
                        )}
                      </div>
                      <h4 className="font-semibold mb-2 text-foreground">{trend.trend_name || 'Not Available'}</h4>
                      <p className="text-xs text-muted-foreground leading-relaxed mb-4">{trend.trend_description || 'Not Available'}</p>
                    </div>

                    <div className="space-y-2 pt-3 border-t border-border/60">
                      {trend.trend_drivers && trend.trend_drivers.length > 0 && (
                        <div>
                          <span className="text-[10px] font-medium text-muted-foreground uppercase block mb-1">Key Drivers</span>
                          <div className="flex flex-wrap gap-1">
                            {trend.trend_drivers.map((driver, i) => (
                              <span key={i} className="px-2 py-0.5 bg-secondary text-[10px] rounded-md text-foreground">
                                {driver}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {trend.impact_areas && trend.impact_areas.length > 0 && (
                        <div className="pt-1.5">
                          <span className="text-[10px] font-medium text-muted-foreground uppercase block mb-1">Impact Areas</span>
                          <div className="flex flex-wrap gap-1">
                            {trend.impact_areas.map((area, i) => (
                              <span key={i} className="px-2 py-0.5 bg-primary/5 text-primary text-[10px] rounded-md font-medium">
                                {area}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </section>

          {/* Competitive Landscape */}
          <section className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-rose-500/10 rounded-lg">
                <Target className="w-5 h-5 text-rose-500" />
              </div>
              <h3 className="font-display text-xl font-bold text-foreground">Competitive Landscape</h3>
            </div>
            
            {competitors.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">No competitor mappings available.</p>
            ) : (
              <div className="grid md:grid-cols-3 gap-4">
                {competitors.map((comp, index) => (
                  <div key={index} className="bg-card border border-border rounded-2xl p-6 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-3 border-b border-border pb-2">
                        <div>
                          <h4 className="font-semibold text-foreground">{comp.competitor_name || 'Not Available'}</h4>
                          <span className="text-[10px] text-muted-foreground bg-secondary px-1.5 py-0.5 rounded font-medium mt-0.5 inline-block">
                            {comp.competitor_type || 'Direct'} Competitor
                          </span>
                        </div>
                        {comp.threat_level && (
                          <span className={cn(
                            'px-2 py-0.5 text-[10px] font-semibold rounded-full flex items-center gap-1 uppercase',
                            comp.threat_level.toLowerCase() === 'high' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                          )}>
                            <AlertTriangle className="w-3.5 h-3.5" />
                            {comp.threat_level}
                          </span>
                        )}
                      </div>
                      
                      <div className="space-y-2 text-xs">
                        <div>
                          <span className="text-muted-foreground block font-medium">Core Advantage</span>
                          <p className="text-foreground leading-relaxed mt-0.5">{comp.core_strength || 'Not Available'}</p>
                        </div>
                        {comp.market_positioning && (
                          <div>
                            <span className="text-muted-foreground block font-medium">Market Position</span>
                            <p className="text-foreground leading-relaxed mt-0.5">{comp.market_positioning}</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {comp.bet_name && (
                      <div className="mt-4 pt-3 border-t border-border/80">
                        <span className="text-[10px] text-muted-foreground uppercase font-medium block">Strategic Play / Bet</span>
                        <p className="text-xs font-semibold text-primary mt-0.5">{comp.bet_name}</p>
                        <p className="text-[11px] text-muted-foreground leading-relaxed mt-1">{comp.bet_description}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Student Innovation Projects */}
          <section className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent/10 rounded-lg">
                <Zap className="w-5 h-5 text-accent" />
              </div>
              <div>
                <h3 className="font-display text-xl font-bold text-foreground">Student Innovation Projects</h3>
                <p className="text-xs text-muted-foreground">
                  Project blueprints aligned with the company's strategic pillars and engineering requirements
                </p>
              </div>
            </div>
            
            {projects.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">No student projects mapped.</p>
            ) : (
              <div className="space-y-6">
                {['Tier 1', 'Tier 2', 'Tier 3'].map(tier => {
                  const filtered = projects.filter(p => (p.tier_level || '').toLowerCase() === tier.toLowerCase());
                  if (filtered.length === 0) return null;

                  return (
                    <div key={tier} className="space-y-3">
                      <div className="flex items-center gap-2 border-b border-border pb-1.5">
                        <Layers className="w-4 h-4 text-primary" />
                        <h4 className="font-semibold text-sm uppercase tracking-wider">
                          {tier} — {tier === 'Tier 1' ? 'Foundational Prototypes' : tier === 'Tier 2' ? 'Advanced Implementations' : 'Breakthrough / Futuristic Projects'}
                        </h4>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-4">
                        {filtered.map((project, index) => {
                          const backend = project.backend_technologies || [];
                          const frontend = project.frontend_technologies || [];
                          const ai = project.ai_ml_technologies || [];
                          const combinedTech = [...backend, ...frontend, ...ai];

                          return (
                            <motion.div
                              key={index}
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="bg-card border border-border rounded-2xl p-6 hover:shadow-card-hover transition-all flex flex-col justify-between"
                            >
                              <div className="space-y-3">
                                <div className="flex items-start justify-between gap-4">
                                  <h5 className="font-display font-semibold text-base text-foreground">{project.project_name || 'Not Available'}</h5>
                                  <span className={cn(
                                    'px-2 py-0.5 text-[10px] font-semibold rounded-full border uppercase',
                                    getTierColor(project.tier_level)
                                  )}>
                                    {project.tier_level || 'Tier 1'}
                                  </span>
                                </div>
                                
                                <p className="text-xs text-muted-foreground leading-relaxed">
                                  <strong>Problem:</strong> {project.problem_statement || 'Not Available'}
                                </p>
                                
                                <p className="text-xs leading-relaxed text-foreground">
                                  <strong>Objective:</strong> {project.innovation_objective || 'Not Available'}
                                </p>
                                
                                {combinedTech.length > 0 && (
                                  <div className="flex flex-wrap gap-1 pt-1">
                                    {combinedTech.map((tech, i) => (
                                      <span key={i} className="px-2 py-0.5 bg-blue-100 text-blue-700 text-[10px] rounded font-medium">
                                        {tech}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                              
                              <div className="pt-3 border-t border-border mt-4 flex justify-between items-center text-xs">
                                <div>
                                  <span className="text-[10px] text-muted-foreground block uppercase">Business Value</span>
                                  <p className="font-semibold text-accent">{project.business_value || 'Not Available'}</p>
                                </div>
                                {project.data_storage_processing && (
                                  <div className="text-right">
                                    <span className="text-[10px] text-muted-foreground block uppercase">Storage / Data</span>
                                    <p className="font-medium text-foreground">{project.data_storage_processing}</p>
                                  </div>
                                )}
                              </div>
                            </motion.div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        </>
      )}
    </motion.div>
  );
};

export default CompanyInnovX;
