import { motion } from 'framer-motion';
import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, Filter, ChevronDown, Info } from 'lucide-react';
import { CompanySearch } from '@/components/search/CompanySearch';
import { useCompaniesShort, useAllJobRoles } from '@/hooks/useSupabaseData';
import { cn } from '@/lib/utils';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

const skillSets = [
  { code: 'COD', name: 'Coding', icon: '💻' },
  { code: 'DSA', name: 'Data Structures & Algorithms', icon: '🧮' },
  { code: 'APTI', name: 'Aptitude & Problem Solving', icon: '🧠' },
  { code: 'COMM', name: 'Communication Skills', icon: '💬' },
  { code: 'OOD', name: 'Object-Oriented Design', icon: '🏗️' },
  { code: 'AI', name: 'AI Native Engineering', icon: '🤖' },
  { code: 'SQL', name: 'SQL & Database Design', icon: '🗄️' },
  { code: 'SYSD', name: 'System Design', icon: '📐' },
  { code: 'DEVOPS', name: 'DevOps & Cloud', icon: '☁️' },
  { code: 'SWE', name: 'Software Engineering', icon: '⚙️' },
  { code: 'NET', name: 'Computer Networking', icon: '🌐' },
  { code: 'OS', name: 'Operating Systems', icon: '🖥️' },
];

const bloomLevels: Record<string, { name: string; color: string }> = {
  'RE': { name: 'Remember', color: 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300' },
  'UN': { name: 'Understand', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' },
  'AP': { name: 'Apply', color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' },
  'AN': { name: 'Analyze', color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300' },
  'EV': { name: 'Evaluate', color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300' },
  'CR': { name: 'Create', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' },
};

const getBloomWeight = (level: string): number => {
  const weights: Record<string, number> = { RE: 1, UN: 2, AP: 3, AN: 4, EV: 5, CR: 6 };
  return weights[level] || 1;
};

const getBloomFromWeight = (weight: number): string => {
  const levels = ['', 'RE', 'UN', 'AP', 'AN', 'EV', 'CR'];
  return levels[weight] || 'RE';
};

const mapRoundToBloom = (roundName: string, roundCategory: string, evalType: string): string => {
  const name = roundName.toLowerCase();
  const category = roundCategory.toLowerCase();
  const evType = evalType.toLowerCase();

  if (name.includes('system design') || name.includes('architecture') || category.includes('architecture')) {
    return 'CR'; // Design/Architecture is Create
  }
  if (name.includes('design') || category.includes('design')) {
    return 'EV'; // Design is Evaluate
  }
  if (name.includes('coding') || category.includes('coding') || name.includes('test') || category.includes('test')) {
    return 'EV'; // Coding / Tests are Evaluate
  }
  if (name.includes('interview')) {
    if (evType === 'technical') {
      return 'AN'; // Technical interviews require Analyze
    }
    return 'AP'; // Behavioral/HR interviews require Apply
  }
  if (name.includes('aptitude') || category.includes('aptitude') || name.includes('mcq') || name.includes('written')) {
    return 'UN'; // MCQ/Aptitude/Written is Understand
  }
  return 'RE'; // Fallback is Remember
};

const HiringSkills = () => {
  const navigate = useNavigate();
  const [selectedSkills, setSelectedSkills] = useState<string[]>(skillSets.map(s => s.code));

  const { data: companiesShort = [], isLoading: isCompaniesLoading } = useCompaniesShort();
  const { data: allJobRoles = [], isLoading: isRolesLoading } = useAllJobRoles();

  const toggleSkill = (code: string) => {
    if (selectedSkills.includes(code)) {
      if (selectedSkills.length > 1) {
        setSelectedSkills(selectedSkills.filter(s => s !== code));
      }
    } else {
      setSelectedSkills([...selectedSkills, code]);
    }
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 8) return 'text-emerald font-bold';
    if (rating >= 6) return 'text-amber-500 font-semibold';
    if (rating >= 4) return 'text-muted-foreground';
    return 'text-muted-foreground/50';
  };

  // Dynamically compute ratings map: company_id -> skill_code -> { rating, bloom }
  const ratingsMap = useMemo(() => {
    const map: Record<number, Record<string, { rating: number; bloom: string }>> = {};

    const companyAggregates: Record<number, { 
      occurrences: Record<string, number>; 
      maxBloomWeight: Record<string, number> 
    }> = {};

    allJobRoles.forEach(roleItem => {
      const compId = roleItem.company_id;
      if (!compId) return;
      if (!companyAggregates[compId]) {
        companyAggregates[compId] = { occurrences: {}, maxBloomWeight: {} };
      }
      
      const details = roleItem.job_role_json?.job_role_details || [];
      details.forEach(detail => {
        const rounds = detail.hiring_rounds || [];
        rounds.forEach(round => {
          const skills = round.skill_sets || [];
          skills.forEach(skillItem => {
            const code = skillItem.skill_set_code?.toUpperCase();
            if (code) {
              companyAggregates[compId].occurrences[code] = (companyAggregates[compId].occurrences[code] || 0) + 1;
              const bloom = mapRoundToBloom(
                round.round_name || '', 
                round.round_category || '', 
                round.evaluation_type || ''
              );
              const weight = getBloomWeight(bloom);
              companyAggregates[compId].maxBloomWeight[code] = Math.max(companyAggregates[compId].maxBloomWeight[code] || 0, weight);
            }
          });
        });
      });
    });

    Object.keys(companyAggregates).forEach(compIdStr => {
      const compId = parseInt(compIdStr);
      map[compId] = {};
      const { occurrences, maxBloomWeight } = companyAggregates[compId];
      
      Object.keys(occurrences).forEach(code => {
        const count = occurrences[code];
        // Occurrence to rating map: 1 -> 4, 2 -> 6, 3 -> 8, 4+ -> 10
        const rating = Math.min(10, 4 + (count - 1) * 2);
        const bloom = getBloomFromWeight(maxBloomWeight[code] || 1);
        map[compId][code] = { rating, bloom };
      });
    });

    return map;
  }, [allJobRoles]);

  if (isCompaniesLoading || isRolesLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground text-sm">Loading skills comparison matrix...</p>
        </div>
      </div>
    );
  }

  return (
    <TooltipProvider>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-6"
      >
        {/* Page Header */}
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground mb-2">
            Hiring Skill Sets
          </h1>
          <p className="text-muted-foreground">
            Compare skill expectations and cognitive depth across recruiters
          </p>
        </div>

        {/* Search */}
        <CompanySearch 
          companies={companiesShort} 
          placeholder="Search company to view detailed skills..."
          onSelect={(company) => navigate(`/companies/${company.company_id}/skills`)}
        />

        {/* Skill Set Selector */}
        <div className="bg-card border border-border rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-muted-foreground" />
              <h3 className="font-medium">Filter Skill Sets</h3>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={() => setSelectedSkills(skillSets.map(s => s.code))}
                className="text-sm text-primary hover:underline"
              >
                Select All
              </button>
              <span className="text-muted-foreground">|</span>
              <button 
                onClick={() => setSelectedSkills(['COD', 'DSA'])}
                className="text-sm text-primary hover:underline"
              >
                Reset
              </button>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {skillSets.map(skill => (
              <button
                key={skill.code}
                onClick={() => toggleSkill(skill.code)}
                className={cn(
                  'px-3 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2',
                  selectedSkills.includes(skill.code)
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                )}
              >
                <span>{skill.icon}</span>
                {skill.name}
              </button>
            ))}
          </div>
        </div>

        {/* Bloom's Taxonomy Legend */}
        <div className="flex flex-wrap items-center gap-3 text-sm">
          <span className="font-medium text-muted-foreground">Bloom's Levels:</span>
          {Object.entries(bloomLevels).map(([code, { name, color }]) => (
            <span key={code} className={cn('px-2 py-0.5 rounded text-xs', color)}>
              {code} = {name}
            </span>
          ))}
        </div>

        {/* Comparison Table */}
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-secondary/50">
                <tr>
                  <th className="px-6 py-4 text-left font-medium text-muted-foreground sticky left-0 bg-secondary/50 z-10">
                    Company
                  </th>
                  {skillSets
                    .filter(s => selectedSkills.includes(s.code))
                    .map(skill => (
                      <th key={skill.code} className="px-4 py-4 text-center font-medium text-muted-foreground min-w-[100px]">
                        <Tooltip>
                          <TooltipTrigger className="cursor-help">
                            <div className="flex flex-col items-center gap-1">
                              <span className="text-lg">{skill.icon}</span>
                              <span className="text-xs">{skill.code}</span>
                            </div>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{skill.name}</p>
                          </TooltipContent>
                        </Tooltip>
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {companiesShort.map((company, index) => {
                  const companyRatings = ratingsMap[company.company_id] || {};
                  return (
                    <tr key={company.company_id} className={cn(index % 2 === 0 ? 'bg-card' : 'bg-secondary/20')}>
                      <td className="px-6 py-4 font-medium sticky left-0 bg-inherit z-10">
                        <button
                          onClick={() => navigate(`/companies/${company.company_id}/skills`)}
                          className="text-left font-semibold text-foreground hover:text-primary transition-colors cursor-pointer"
                        >
                          {company.name}
                        </button>
                      </td>
                      {skillSets
                        .filter(s => selectedSkills.includes(s.code))
                        .map(skill => {
                          const data = companyRatings[skill.code];
                          if (!data) return <td key={skill.code} className="px-4 py-4 text-center text-muted-foreground">-</td>;
                          
                          return (
                            <td key={skill.code} className="px-4 py-4 text-center">
                              <Tooltip>
                                <TooltipTrigger>
                                  <div className="flex flex-col items-center gap-1">
                                    <span className={cn('text-xl', getRatingColor(data.rating))}>
                                      {data.rating}
                                    </span>
                                    <span className={cn(
                                      'px-1.5 py-0.5 rounded text-xs',
                                      bloomLevels[data.bloom]?.color || 'bg-muted'
                                    )}>
                                      {data.bloom}
                                    </span>
                                  </div>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Rating: {data.rating}/10</p>
                                  <p>Level: {bloomLevels[data.bloom]?.name}</p>
                                </TooltipContent>
                              </Tooltip>
                            </td>
                          );
                        })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Info */}
        <div className="flex items-start gap-3 p-4 bg-primary/5 border border-primary/10 rounded-xl">
          <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
          <div className="text-sm text-muted-foreground">
            <p className="font-medium text-foreground mb-1">How to read this table</p>
            <p>Each cell shows the Rating (1-10) and Bloom's Taxonomy level. Higher ratings indicate stronger expectations. Click on any company name to view their detailed skill matrix with topic breakdowns.</p>
          </div>
        </div>
      </motion.div>
    </TooltipProvider>
  );
};

export default HiringSkills;
