import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { 
  ArrowLeft, 
  Building2, 
  MapPin, 
  Users, 
  GraduationCap,
  GitBranch,
  Lightbulb,
  CheckCircle2,
  Clock,
  Monitor,
  Users2,
  Brain,
  Code,
  MessageSquare,
  HelpCircle,
  Database,
  Cloud,
  Settings,
  Cpu,
  Network,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCompanyFull, useCompanyJobRole } from '@/hooks/useSupabaseData';
import { cn } from '@/lib/utils';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';

const skillMap: Record<string, { name: string; icon: any; color: string }> = {
  'COD': { name: 'Coding & Scripting', icon: Code, color: 'text-blue-500 bg-blue-500/10' },
  'DSA': { name: 'Data Structures & Algorithms', icon: Brain, color: 'text-purple-500 bg-purple-500/10' },
  'APTI': { name: 'Aptitude & Logical Reasoning', icon: Brain, color: 'text-amber-500 bg-amber-500/10' },
  'COMM': { name: 'Communication & Behavioral', icon: MessageSquare, color: 'text-green-500 bg-green-500/10' },
  'OOD': { name: 'Object-Oriented Design', icon: Settings, color: 'text-indigo-500 bg-indigo-500/10' },
  'AI': { name: 'AI & Machine Learning', icon: Cpu, color: 'text-pink-500 bg-pink-500/10' },
  'SQL': { name: 'SQL & Database Design', icon: Database, color: 'text-cyan-500 bg-cyan-500/10' },
  'SYSD': { name: 'System Design', icon: Network, color: 'text-orange-500 bg-orange-500/10' },
  'DEVOPS': { name: 'DevOps & Cloud Systems', icon: Cloud, color: 'text-sky-500 bg-sky-500/10' },
  'SWE': { name: 'Software Engineering Practices', icon: Settings, color: 'text-slate-500 bg-slate-500/10' },
  'NET': { name: 'Computer Networks', icon: Network, color: 'text-teal-500 bg-teal-500/10' },
  'OS': { name: 'Operating Systems', icon: Monitor, color: 'text-rose-500 bg-rose-500/10' },
};

const getRoundIcon = (category: string) => {
  switch ((category || '').toLowerCase()) {
    case 'coding test':
    case 'coding':
      return Code;
    case 'interview':
      return Users2;
    case 'hackathon':
      return Brain;
    default:
      return MessageSquare;
  }
};

const getRoundColor = (type: string) => {
  switch ((type || '').toLowerCase()) {
    case 'technical':
      return 'bg-blue-500 text-white';
    case 'hr':
    case 'managerial':
      return 'bg-green-500 text-white';
    default:
      return 'bg-amber-500 text-white';
  }
};

const CompanyProcess = () => {
  const { companyId } = useParams();
  const navigate = useNavigate();
  const cid = Number(companyId);

  const { data: company, isLoading: isLoadingCompany } = useCompanyFull(cid);
  const { data: jobRoleData, isLoading: isLoadingJobRole } = useCompanyJobRole(cid);

  const [activeRoleIndex, setActiveRoleIndex] = useState<string>('0');

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

  const isLoading = isLoadingCompany || isLoadingJobRole;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground text-sm">Loading process timeline...</p>
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

  const roles = jobRoleData?.job_role_details || [];
  const activeRole = roles[Number(activeRoleIndex)];
  const rounds = activeRole?.hiring_rounds || [];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
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
            <Button variant="default" size="sm" className="gap-2">
              <GitBranch className="w-4 h-4" />
              Hiring Process
            </Button>
            <Button variant="outline" size="sm" className="gap-2" onClick={() => navigate(`/companies/${companyId}/innovx`)}>
              <Lightbulb className="w-4 h-4" />
              INNOVX
            </Button>
          </div>
        </div>
      </div>

      {/* Page Title */}
      <div>
        <h2 className="font-display text-2xl font-bold mb-2">Hiring Process</h2>
        <p className="text-muted-foreground">
          Step-by-step interview rounds, timelines, and evaluation guidelines
        </p>
      </div>

      {roles.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-8 text-center text-muted-foreground">
          <AlertCircle className="w-8 h-8 mx-auto mb-2 text-muted-foreground/60" />
          <p>Hiring process details are not available for this company at this time.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Roles Selector Tabs */}
          {roles.length > 1 && (
            <Tabs value={activeRoleIndex} onValueChange={setActiveRoleIndex} className="w-full">
              <TabsList className="bg-secondary/40 p-1 rounded-xl">
                {roles.map((role, idx) => (
                  <TabsTrigger key={idx} value={String(idx)} className="rounded-lg">
                    {role.role_title || `Role ${idx + 1}`}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          )}

          {activeRole && (
            <div className="space-y-6">
              {/* Role Quick Meta */}
              <div className="bg-card border border-border rounded-2xl p-6 flex flex-wrap gap-6 items-center justify-between shadow-sm">
                <div>
                  <h3 className="font-semibold text-base text-foreground">{activeRole.role_title || 'Not Available'}</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{activeRole.role_category || 'Not Available'} • {activeRole.opportunity_type || 'Not Available'}</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-primary/5 rounded-xl border border-primary/10">
                  <GitBranch className="w-4 h-4 text-primary" />
                  <span className="text-sm font-medium">{rounds.length} hiring rounds</span>
                </div>
              </div>

              {/* Timeline */}
              {rounds.length === 0 ? (
                <div className="bg-card border border-border rounded-2xl p-8 text-center text-muted-foreground">
                  <HelpCircle className="w-8 h-8 mx-auto mb-2 text-muted-foreground/60" />
                  <p>No rounds mapped to this role's hiring timeline.</p>
                </div>
              ) : (
                <div className="relative pl-6 sm:pl-8 space-y-6">
                  {/* Vertical Timeline Line */}
                  <div className="absolute left-9 sm:left-11 top-4 bottom-4 w-0.5 bg-border" />

                  {rounds.map((round, index) => {
                    const Icon = getRoundIcon(round.round_category);
                    const nodeColor = getRoundColor(round.evaluation_type);
                    
                    return (
                      <motion.div
                        key={round.round_number}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="relative pl-12 sm:pl-16"
                      >
                        {/* Timeline Node */}
                        <div className={cn(
                          'absolute left-5 sm:left-7 w-8 h-8 rounded-full flex items-center justify-center z-10 border border-card shadow-sm font-semibold',
                          nodeColor
                        )}>
                          <Icon className="w-4 h-4" />
                        </div>

                        {/* Round Details Card */}
                        <div className="bg-card border border-border rounded-2xl p-6 shadow-card hover:shadow-card-hover transition-all duration-200">
                          {/* Round Header */}
                          <div className="flex flex-wrap items-start justify-between gap-4 mb-4 pb-3 border-b border-border">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                                  Round {round.round_number}
                                </span>
                                <span className={cn(
                                  'px-2 py-0.5 text-[10px] font-semibold rounded-full uppercase',
                                  round.evaluation_type?.toLowerCase() === 'technical' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                                )}>
                                  {round.evaluation_type || 'Technical'}
                                </span>
                              </div>
                              <h3 className="font-display font-bold text-lg text-foreground">{round.round_name || 'Not Available'}</h3>
                            </div>
                            
                            <div className="flex items-center gap-3 text-xs text-muted-foreground bg-secondary/30 px-3 py-1.5 rounded-xl border border-secondary/50">
                              <span className="flex items-center gap-1.5 font-medium">
                                <Monitor className="w-3.5 h-3.5 text-primary" />
                                {round.assessment_mode || 'Online'}
                              </span>
                              {round.round_category && (
                                <>
                                  <span className="text-muted-foreground/30">|</span>
                                  <span className="font-medium bg-primary/5 text-primary px-1.5 py-0.5 rounded text-[10px] uppercase font-mono">
                                    {round.round_category}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>

                          {/* Skill sets evaluated in this round */}
                          {(!round.skill_sets || round.skill_sets.length === 0) ? (
                            <p className="text-xs text-muted-foreground italic">No evaluation topics mapped to this round.</p>
                          ) : (
                            <div className="space-y-4">
                              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Evaluated Competencies</h4>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {round.skill_sets.map((skill, skillIndex) => {
                                  const details = skillMap[skill.skill_set_code] || {
                                    name: `Skill: ${skill.skill_set_code}`,
                                    icon: HelpCircle,
                                    color: 'text-muted-foreground bg-muted',
                                  };
                                  const SkillIcon = details.icon;
                                  
                                  const questionsList = skill.typical_questions
                                    ? skill.typical_questions
                                        .split(';')
                                        .map(q => q.trim())
                                        .filter(q => q.length > 0)
                                    : [];

                                  return (
                                    <div key={skillIndex} className="bg-secondary/25 border border-secondary/40 rounded-xl p-4 space-y-3">
                                      <div className="flex items-center gap-2.5">
                                        <div className={cn('p-1.5 rounded-lg', details.color)}>
                                          <SkillIcon className="w-4 h-4" />
                                        </div>
                                        <div>
                                          <h5 className="font-semibold text-sm">{details.name}</h5>
                                          <span className="text-[10px] text-muted-foreground font-mono">{skill.skill_set_code}</span>
                                        </div>
                                      </div>
                                      
                                      <div className="space-y-1.5">
                                        <span className="text-[10px] font-medium text-muted-foreground block">Key Questions / Focus Areas</span>
                                        {questionsList.length === 0 ? (
                                          <p className="text-xs text-muted-foreground italic">No questions listed.</p>
                                        ) : (
                                          <div className="space-y-1">
                                            {questionsList.map((q, qi) => (
                                              <div key={qi} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald flex-shrink-0 mt-0.5" />
                                                <span className="leading-relaxed">{q}</span>
                                              </div>
                                            ))}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default CompanyProcess;
