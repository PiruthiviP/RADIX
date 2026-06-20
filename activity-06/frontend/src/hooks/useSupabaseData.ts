import { useQuery } from '@tanstack/react-query';
import { supabase } from '@/lib/supabase';
import { CompanyShort, CompanyFull, InnovxData, HiringRoundsData } from '@/types/company';

// Map raw database categories to placement categories for standard display & filtering
export function mapDbCategoryToPlacementCategory(rawCategory: string, companyName: string): string {
  if (!rawCategory) return 'Regular';
  const cat = rawCategory.toLowerCase();
  const name = companyName.toLowerCase();
  
  // 1. Enterprise Category
  if (
    cat.includes('enterprise') || 
    cat.includes('it services') || 
    cat.includes('consulting') || 
    cat.includes('large cap') || 
    cat.includes('telecommunications') || 
    cat.includes('aviation') || 
    cat.includes('multinational') || 
    cat.includes('bank') || 
    cat.includes('aerospace & defence') ||
    cat.includes('corporate') ||
    cat.includes('legal technology') ||
    cat.includes('management')
  ) {
    return 'Enterprise';
  }
  
  // 2. Marquee Category (Top tier tech / AI / high-profile)
  if (
    name.includes('google') || 
    name.includes('microsoft') || 
    name.includes('apple') || 
    name.includes('meta') || 
    name.includes('amazon') || 
    name.includes('netflix') || 
    name.includes('nvidia') || 
    name.includes('openai') || 
    name.includes('servicenow') ||
    name.includes('rubrik') ||
    name.includes('barclays') ||
    cat.includes('artificial intelligence') || 
    cat.includes('cybersecurity') || 
    cat.includes('data security') ||
    cat.includes('cloud security')
  ) {
    return 'Marquee';
  }
  
  // 3. Super Dream Category (Mid-to-high level fintech, SaaS, unicorns)
  if (
    cat.includes('saas') || 
    cat.includes('software as a service') ||
    cat.includes('fintech') || 
    cat.includes('unicorn') || 
    cat.includes('e-commerce') || 
    cat.includes('online travel') || 
    cat.includes('scale-up') ||
    name.includes('blinkit') ||
    name.includes('freshworks')
  ) {
    return 'SuperDream';
  }
  
  // 4. Dream Category (Other tech, healthtech, logistics)
  if (
    cat.includes('technology') || 
    cat.includes('health') || 
    cat.includes('logistics') || 
    cat.includes('edtech') || 
    cat.includes('learning') ||
    cat.includes('e-learning')
  ) {
    return 'Dream';
  }
  
  // 5. Default/Regular Category
  return 'Regular';
}

// Fetch all short JSON representations of companies (for listing, cards, dashboard)
export function useCompaniesShort() {
  return useQuery<CompanyShort[]>({
    queryKey: ['companies', 'short'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('companies_json')
        .select('company_id, short_json');
      
      if (error) {
        console.error('Error fetching short companies:', error);
        throw error;
      }
      if (!data) return [];
      
      return data.map((row: { company_id: number; short_json: any }) => {
        const short = row.short_json || {};
        const compName = short.name ?? 'Not Available';
        return {
          company_id: row.company_id ?? 0,
          name: compName,
          short_name: short.short_name ?? 'Not Available',
          logo_url: short.logo_url ?? '',
          category: mapDbCategoryToPlacementCategory(short.category ?? '', compName),
          operating_countries: short.operating_countries ?? 'Not Available',
          office_locations: short.office_locations ?? 'Not Available',
          employee_size: short.employee_size ?? 'Not Available',
          yoy_growth_rate: short.yoy_growth_rate ?? 'Not Available',
        } as CompanyShort;
      });
    }
  });
}

// Fetch full JSON representation for a single company lazily (overview/details)
export function useCompanyFull(companyId: number | undefined) {
  return useQuery<CompanyFull | null>({
    queryKey: ['company', 'full', companyId],
    queryFn: async () => {
      if (!companyId) return null;
      const { data, error } = await supabase
        .from('companies_json')
        .select('full_json')
        .eq('company_id', companyId)
        .maybeSingle();
      
      if (error) {
        console.error(`Error fetching full company for ID ${companyId}:`, error);
        throw error;
      }
      if (!data || !data.full_json) return null;
      
      const full = data.full_json as CompanyFull;
      if (full) {
        full.category = mapDbCategoryToPlacementCategory(full.category ?? '', full.name ?? '');
      }
      return full;
    },
    enabled: !!companyId
  });
}

// Fetch InnovX JSON representation for a single company
export function useCompanyInnovX(companyId: number | undefined) {
  return useQuery<InnovxData | null>({
    queryKey: ['company', 'innovx', companyId],
    queryFn: async () => {
      if (!companyId) return null;
      const { data, error } = await supabase
        .from('innovx_json')
        .select('json_data')
        .eq('company_id', companyId)
        .maybeSingle();
      
      if (error) {
        console.error(`Error fetching InnovX data for ID ${companyId}:`, error);
        throw error;
      }
      if (!data || !data.json_data) return null;
      
      return data.json_data as InnovxData;
    },
    enabled: !!companyId
  });
}

// Fetch job role and hiring details JSON representation for a single company
export function useCompanyJobRole(companyId: number | undefined) {
  return useQuery<HiringRoundsData | null>({
    queryKey: ['company', 'jobrole', companyId],
    queryFn: async () => {
      if (!companyId) return null;
      const { data, error } = await supabase
        .from('job_role_details_json')
        .select('job_role_json')
        .eq('company_id', companyId)
        .maybeSingle();
      
      if (error) {
        console.error(`Error fetching Job Role data for ID ${companyId}:`, error);
        throw error;
      }
      if (!data || !data.job_role_json) return null;
      
      return data.job_role_json as HiringRoundsData;
    },
    enabled: !!companyId
  });
}

// Fetch all job role JSONs across all companies (for comparative matrix views)
export function useAllJobRoles() {
  return useQuery<{ company_id: number; job_role_json: HiringRoundsData }[]>({
    queryKey: ['jobroles', 'all'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('job_role_details_json')
        .select('company_id, job_role_json');
      
      if (error) {
        console.error('Error fetching all job roles:', error);
        throw error;
      }
      if (!data) return [];
      
      return data.map((row: { company_id: number; job_role_json: any }) => ({
        company_id: row.company_id,
        job_role_json: row.job_role_json as HiringRoundsData
      }));
    }
  });
}
