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
  Brain,
  Code,
  MessageSquare,
  Database,
  Cloud,
  Settings,
  Cpu,
  Network,
  Monitor,
  HelpCircle,
  Briefcase,
  DollarSign,
  Gift,
  PlusCircle,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCompanyFull, useCompanyJobRole } from '@/hooks/useSupabaseData';
import { cn } from '@/lib/utils';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

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

const CompanySkills = () => {
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
          <p className="text-muted-foreground text-sm">Loading hiring metrics...</p>
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

  // Aggregate all skills for the active role
  const aggregatedSkills: Record<string, {
    skill_set_code: string;
    questions: string[];
    rounds: { round_number: number; round_name: string }[];
  }> = {};

  if (activeRole && activeRole.hiring_rounds) {
    activeRole.hiring_rounds.forEach(round => {
      if (round.skill_sets) {
        round.skill_sets.forEach(skill => {
          const code = skill.skill_set_code;
          if (!aggregatedSkills[code]) {
            aggregatedSkills[code] = {
              skill_set_code: code,
              questions: [],
              rounds: []
            };
          }
          
          if (skill.typical_questions) {
            const splitQs = skill.typical_questions
              .split(';')
              .map(q => q.trim())
              .filter(q => q.length > 0);
            
            splitQs.forEach(q => {
              if (!aggregatedSkills[code].questions.includes(q)) {
                aggregatedSkills[code].questions.push(q);
              }
            });
          }
          
          aggregatedSkills[code].rounds.push({
            round_number: round.round_number,
            round_name: round.round_name
          });
        });
      }
    });
  }

  const uniqueSkills = Object.values(aggregatedSkills);

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
            <Button variant="default" size="sm" className="gap-2">
              <GraduationCap className="w-4 h-4" />
              Skill Sets
            </Button>
            <Button variant="outline" size="sm" className="gap-2" onClick={() => navigate(`/companies/${companyId}/process`)}>
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
        <h2 className="font-display text-2xl font-bold mb-2">Hiring Skill Sets</h2>
        <p className="text-muted-foreground">
          Analyze required skills, interview questions, and test metrics
        </p>
      </div>

      {roles.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-8 text-center text-muted-foreground">
          <AlertCircle className="w-8 h-8 mx-auto mb-2 text-muted-foreground/60" />
          <p>Hiring skill requirements are not available for this company at this time.</p>
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
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Job Role Details */}
              <div className="lg:col-span-1 space-y-6">
                <div className="bg-card border border-border rounded-2xl p-6 space-y-4">
                  <div className="flex items-center gap-3 border-b border-border pb-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Briefcase className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-display font-semibold text-base">{activeRole.role_title || 'Not Available'}</h3>
                      <p className="text-xs text-muted-foreground">{activeRole.role_category || 'Not Available'}</p>
                    </div>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div>
                      <span className="text-muted-foreground block text-xs">Opportunity Type</span>
                      <span className="font-medium text-foreground">{activeRole.opportunity_type || 'Not Available'}</span>
                    </div>

                    <div>
                      <span className="text-muted-foreground block text-xs">Compensation</span>
                      <span className="font-medium text-foreground flex items-center gap-1">
                        <DollarSign className="w-4 h-4 text-emerald" />
                        {activeRole.ctc_or_stipend 
                          ? `${activeRole.compensation === 'Stipend' ? '₹' : '₹'}${activeRole.ctc_or_stipend.toLocaleString()}${activeRole.compensation === 'Stipend' ? '/mo' : ''}`
                          : 'Not Available'}
                      </span>
                    </div>

                    <div>
                      <span className="text-muted-foreground block text-xs">Bonus details</span>
                      <span className="font-medium text-foreground text-xs leading-relaxed block">
                        {activeRole.bonus || 'Not Available'}
                      </span>
                    </div>

                    <div>
                      <span className="text-muted-foreground block text-xs flex items-center gap-1">
                        <Gift className="w-3.5 h-3.5 text-accent" />
                        Benefits & Perks
                      </span>
                      <p className="text-xs text-muted-foreground leading-relaxed mt-1">
                        {activeRole.benefits_summary || 'Not Available'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-card border border-border rounded-2xl p-6">
                  <h4 className="font-semibold text-sm mb-3">Job Description</h4>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {activeRole.job_description || 'Not Available'}
                  </p>
                </div>
              </div>

              {/* Right Column: Skill details & questions */}
              <div className="lg:col-span-2 space-y-4">
                <h3 className="font-display font-semibold text-lg">Expected Skills & Sample Questions</h3>
                {uniqueSkills.length === 0 ? (
                  <div className="bg-card border border-border rounded-2xl p-8 text-center text-muted-foreground">
                    <HelpCircle className="w-8 h-8 mx-auto mb-2 text-muted-foreground/60" />
                    <p>No skill sets mapped to this role's hiring rounds.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {uniqueSkills.map((skill, index) => {
                      const details = skillMap[skill.skill_set_code] || {
                        name: `Skill: ${skill.skill_set_code}`,
                        icon: HelpCircle,
                        color: 'text-muted-foreground bg-muted',
                      };
                      const Icon = details.icon;

                      return (
                        <motion.div
                          key={skill.skill_set_code}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="bg-card border border-border rounded-2xl p-6 space-y-4"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex items-center gap-3">
                              <div className={cn('p-2.5 rounded-xl flex items-center justify-center', details.color)}>
                                <Icon className="w-5 h-5" />
                              </div>
                              <div>
                                <h4 className="font-semibold text-base">{details.name}</h4>
                                <span className="inline-block px-2 py-0.5 bg-secondary text-secondary-foreground text-xs font-mono rounded mt-0.5">
                                  {skill.skill_set_code}
                                </span>
                              </div>
                            </div>
                            
                            <div className="text-right">
                              <span className="text-xs text-muted-foreground block">Evaluation Rounds</span>
                              <div className="flex flex-wrap gap-1 mt-1 justify-end">
                                {skill.rounds.map((r, ri) => (
                                  <span key={ri} className="px-2 py-0.5 bg-primary/10 text-primary rounded-md text-[10px] font-medium">
                                    R{r.round_number}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>

                          <div className="space-y-2.5">
                            <span className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                              <HelpCircle className="w-3.5 h-3.5 text-accent" />
                              Typical Questions Asked
                            </span>
                            {skill.questions.length === 0 ? (
                              <p className="text-xs text-muted-foreground italic">No sample questions available.</p>
                            ) : (
                              <ul className="space-y-2">
                                {skill.questions.map((question, qi) => (
                                  <li key={qi} className="text-sm text-foreground/80 bg-secondary/30 rounded-lg px-3 py-2 flex items-start gap-2 border border-secondary/50">
                                    <span className="text-primary font-bold mt-0.5">•</span>
                                    <span className="leading-relaxed">{question}</span>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default CompanySkills;
