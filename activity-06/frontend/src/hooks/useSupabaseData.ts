import { useQuery } from '@tanstack/react-query';
import { supabase } from '@/lib/supabase';
import { CompanyShort, CompanyFull, InnovxData, HiringRoundsData } from '@/types/company';

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
      
      return data.map((row: any) => {
        const short = row.short_json || {};
        return {
          company_id: row.company_id ?? 0,
          name: short.name ?? 'Not Available',
          short_name: short.short_name ?? 'Not Available',
          logo_url: short.logo_url ?? '',
          category: short.category ?? 'Not Available',
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
      
      return data.full_json as CompanyFull;
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
      
      return data.map((row: any) => ({
        company_id: row.company_id,
        job_role_json: row.job_role_json as HiringRoundsData
      }));
    }
  });
}
