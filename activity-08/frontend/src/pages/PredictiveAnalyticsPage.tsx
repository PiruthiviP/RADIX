import React, { useState, useEffect } from 'react';
import { Brain, BarChart3, TrendingUp, Lightbulb, CheckCircle2, RefreshCcw } from 'lucide-react';
import { fetchApi } from '@/lib/api';
import { useCompaniesShort } from '@/hooks/useSupabaseData';

interface FeatureImportance {
  feature: string;
  importance: number;
}

export default function PredictiveAnalyticsPage() {
  const { data: companies = [] } = useCompaniesShort();

  // Descriptive state: Aggregate categories
  const getCategoryCounts = () => {
    const counts: Record<string, number> = {};
    companies.forEach(c => {
      const cat = c.category || 'Other';
      counts[cat] = (counts[cat] || 0) + 1;
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  };
  const categoryCounts = getCategoryCounts();

  // ML Metadata & Importances
  const [featureImportances, setFeatureImportances] = useState<FeatureImportance[]>([]);
  const [loadingMetadata, setLoadingMetadata] = useState(false);

  // Predictive form inputs
  const [category, setCategory] = useState('Enterprise');
  const [employeeSize, setEmployeeSize] = useState('500');
  const [aiAdoption, setAiAdoption] = useState('High');
  const [nature, setNature] = useState('Private');
  const [age, setAge] = useState(10);
  const [socialFollowers, setSocialFollowers] = useState(10000);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [predicting, setPredicting] = useState(false);

  // Prescriptive state
  const [selectedRecommendId, setSelectedRecommendId] = useState<number | ''>('');
  const [recommendationReport, setRecommendationReport] = useState('');
  const [loadingRecommend, setLoadingRecommend] = useState(false);

  useEffect(() => {
    fetchMlMetadata();
  }, [companies]);

  const fetchMlMetadata = async () => {
    setLoadingMetadata(true);
    try {
      const res = await fetchApi('/api/ml-metadata');
      setFeatureImportances(res.feature_importances || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingMetadata(false);
    }
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setPredicting(true);
    try {
      const res = await fetchApi('/api/predict', {
        method: 'POST',
        body: JSON.stringify({
          category,
          employee_size: employeeSize,
          ai_adoption: aiAdoption,
          nature,
          age: Number(age),
          social_followers: Number(socialFollowers)
        })
      });
      setPrediction(res.prediction);
    } catch (err) {
      console.error(err);
    } finally {
      setPredicting(false);
    }
  };

  const handleGenerateRecommendation = async () => {
    if (!selectedRecommendId) return;
    setLoadingRecommend(true);
    setRecommendationReport('');
    try {
      const res = await fetchApi(`/api/recommend/${selectedRecommendId}`);
      setRecommendationReport(res.recommendation || 'No report generated.');
    } catch (err) {
      console.error(err);
      setRecommendationReport("Failed to contact the Prescriptive AI recommendation engine. Verify the server is active.");
    } finally {
      setLoadingRecommend(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8 font-sans">
      {/* Title */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Vector Intelligence & ML Analytics</h1>
        <p className="text-muted-foreground">Run machine learning growth forecasts, explore core feature importances, and generate strategic recommendations.</p>
      </div>

      {/* Analytics Tabs Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Descriptive and Feature Importance */}
        <div className="lg:col-span-6 space-y-8">
          
          {/* Section 1: Descriptive Analytics */}
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <BarChart3 className="w-5 h-5 text-primary" /> Descriptive Intelligence (Profile Distribution)
            </h2>
            <div className="space-y-4">
              {categoryCounts.slice(0, 5).map(([cat, count]) => {
                const percentage = Math.round((count / (companies.length || 1)) * 100);
                return (
                  <div key={cat} className="space-y-1">
                    <div className="flex justify-between text-xs font-semibold">
                      <span>{cat}</span>
                      <span className="text-muted-foreground">{count} ({percentage}%)</span>
                    </div>
                    <div className="h-2 w-full bg-accent/40 rounded-full overflow-hidden">
                      <div className="h-full bg-primary rounded-full" style={{ width: `${percentage}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section 2: Feature Importance */}
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-2">
              <Brain className="w-5 h-5 text-primary" /> ML Model Feature Importance (YoY Growth Drivers)
            </h2>
            <p className="text-xs text-muted-foreground mb-4">Relative impact of company metrics on predicted YoY growth rate (trained via Random Forest Regressor).</p>

            {loadingMetadata && (
              <div className="text-center py-6 text-sm text-muted-foreground">
                Analyzing feature weightings...
              </div>
            )}

            {!loadingMetadata && featureImportances.length > 0 && (
              <div className="space-y-4">
                {featureImportances.map((f) => {
                  const percentage = Math.round(f.importance * 100);
                  // Format label name
                  const displayFeature = f.feature
                    .replace('_', ' ')
                    .replace('social followers', 'Social Followers')
                    .replace('employee size', 'Employee Size')
                    .replace('ai adoption', 'AI/ML Adoption Level')
                    .replace('age', 'Company Age')
                    .replace('category', 'Category')
                    .replace('nature', 'Nature (Public/Private)');
                  return (
                    <div key={f.feature} className="space-y-1">
                      <div className="flex justify-between text-xs font-semibold">
                        <span>{displayFeature}</span>
                        <span className="text-muted-foreground">{percentage}% weight</span>
                      </div>
                      <div className="h-2 w-full bg-accent/40 rounded-full overflow-hidden">
                        <div className="h-full bg-amber-500 rounded-full" style={{ width: `${percentage}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            
            {!loadingMetadata && featureImportances.length === 0 && (
              <div className="text-center py-6 text-sm text-muted-foreground bg-accent/15 border border-border rounded-xl">
                Deploy backend and load companies to compute ML feature importances.
              </div>
            )}
          </div>

        </div>

        {/* Right Column: Predictive Form & Prescriptive AI Report */}
        <div className="lg:col-span-6 space-y-8">
          
          {/* Section 3: Predictive ML Engine */}
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-primary" /> Predictive ML Engine (YoY Growth Forecaster)
            </h2>
            <form onSubmit={handlePredict} className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs rounded-xl border border-border bg-background"
                >
                  <option value="Enterprise">Enterprise</option>
                  <option value="Enterprise SaaS">Enterprise SaaS</option>
                  <option value="Logistics & Supply Chain">Logistics & Supply Chain</option>
                  <option value="Fintech">Fintech</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="E-commerce">E-commerce</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Employee Size</label>
                <select
                  value={employeeSize}
                  onChange={(e) => setEmployeeSize(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs rounded-xl border border-border bg-background"
                >
                  <option value="50">50 employees</option>
                  <option value="500">500 employees</option>
                  <option value="5000">5,000 employees</option>
                  <option value="50000">50,000+ employees</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">AI/ML Level</label>
                <select
                  value={aiAdoption}
                  onChange={(e) => setAiAdoption(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs rounded-xl border border-border bg-background"
                >
                  <option value="Low">Low / Limited</option>
                  <option value="Medium">Medium Adoption</option>
                  <option value="High">High (AI First)</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Nature of Company</label>
                <select
                  value={nature}
                  onChange={(e) => setNature(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs rounded-xl border border-border bg-background"
                >
                  <option value="Private">Private Startup</option>
                  <option value="Public">Public Enterprise</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Company Age (Years)</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                  className="w-full px-3 py-1.5 text-xs rounded-xl border border-border bg-background"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Social Followers</label>
                <input
                  type="number"
                  value={socialFollowers}
                  onChange={(e) => setSocialFollowers(Number(e.target.value))}
                  className="w-full px-3 py-1.5 text-xs rounded-xl border border-border bg-background"
                />
              </div>

              <div className="col-span-2 pt-2">
                <button
                  type="submit"
                  disabled={predicting}
                  className="w-full bg-primary text-primary-foreground text-xs font-semibold py-2 rounded-xl hover:bg-primary/95 transition-colors disabled:opacity-50"
                >
                  {predicting ? 'Calculating Predictors...' : 'Execute YoY Growth Forecast'}
                </button>
              </div>
            </form>

            {/* Prediction Output */}
            {prediction !== null && (
              <div className="mt-4 p-4 rounded-xl bg-primary/10 border border-primary/20 text-center flex flex-col justify-center items-center">
                <span className="text-xs text-primary font-semibold uppercase tracking-wider">Forecasted YoY Growth Rate:</span>
                <span className="text-3xl font-extrabold text-primary mt-1">{(prediction * 100).toFixed(2)}%</span>
              </div>
            )}
          </div>

          {/* Section 4: Prescriptive AI Report */}
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <Lightbulb className="w-5 h-5 text-primary" /> Prescriptive AI (Strategic Recommendations)
            </h2>
            <div className="flex gap-2 mb-4">
              <select
                value={selectedRecommendId}
                onChange={(e) => setSelectedRecommendId(e.target.value ? Number(e.target.value) : '')}
                className="flex-1 px-4 py-2 text-xs rounded-xl border border-border bg-background"
                disabled={companies.length === 0}
              >
                <option value="">-- Select Target Company --</option>
                {companies.map((c) => (
                  <option key={c.company_id} value={c.company_id}>
                    {c.name}
                  </option>
                ))}
              </select>
              <button
                onClick={handleGenerateRecommendation}
                disabled={loadingRecommend || !selectedRecommendId}
                className="bg-primary text-primary-foreground text-xs font-semibold px-4 py-2 rounded-xl hover:bg-primary/95 transition-colors disabled:opacity-50"
              >
                {loadingRecommend ? 'Generating...' : 'Analyze'}
              </button>
            </div>

            {/* Prescriptive Report Output */}
            {recommendationReport && (
              <div className="p-4 rounded-xl border border-border bg-background/50 text-xs leading-relaxed max-h-[300px] overflow-y-auto whitespace-pre-wrap scrollbar-thin shadow-inner">
                {recommendationReport}
              </div>
            )}
            
            {loadingRecommend && (
              <div className="text-center py-10 text-sm text-muted-foreground flex flex-col items-center justify-center gap-2">
                <RefreshCcw className="w-6 h-6 animate-spin text-primary" />
                <span>Running deep SWOT & competitor alignment analysis...</span>
              </div>
            )}
            
            {!recommendationReport && !loadingRecommend && (
              <div className="text-center py-6 text-xs text-muted-foreground bg-accent/10 rounded-xl border border-dashed border-border">
                Select a company above and generate strategic growth prescriptions.
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
