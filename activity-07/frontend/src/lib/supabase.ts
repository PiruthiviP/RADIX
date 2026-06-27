import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-supabase-project.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-supabase-anon-key';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Self-executing connection health check
(async () => {
  try {
    if (supabaseUrl.includes('your-supabase-project.supabase.co')) {
      console.warn('⚠️ Supabase is not configured yet! Please update VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
      return;
    }
    
    // Attempt a minimal query to verify connectivity and schema existence
    const { error } = await supabase
      .from('companies_json')
      .select('company_id')
      .limit(1);
      
    if (error) {
      console.error('❌ Supabase connection failed:', error.message);
    } else {
      console.log('✅ Supabase connected successfully!');
    }
  } catch (err) {
    console.error('❌ Supabase connection error:', err);
  }
})();
