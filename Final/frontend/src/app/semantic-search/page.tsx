// ====================================================================
// RADIX Semantic Search & Clustering Page component (Next.js)
// Place in: Final/frontend/src/app/semantic-search/page.tsx
// ====================================================================

'use client';

import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Building2, TrendingUp, Network } from 'lucide-react';
import { Layout } from '@/components';
import { fetchApi } from '@/lib/api';
import { getCompaniesShort, CompanyShort } from '@/utils/data';

interface ClusterPoint {
  company_id: number;
  name: string;
  cluster_id: number;
  x: number;
  y: number;
  category: string;
}

interface SearchResult {
  company_id: number;
  name: string;
  score: number;
  metadata: any;
}

export default function SemanticSearchPage() {
  const [companies, setCompanies] = useState<(CompanyShort & { id: string })[]>([]);
  
  // Search state
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  // Competitor mapping state
  const [selectedCompId, setSelectedCompId] = useState<number | ''>('');
  const [similarCompanies, setSimilarCompanies] = useState<any[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);

  // Clustering state
  const [clusters, setClusters] = useState<ClusterPoint[]>([]);
  const [loadingClusters, setLoadingClusters] = useState(false);
  const [hoveredPoint, setHoveredPoint] = useState<ClusterPoint | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadCompanies = async () => {
      try {
        const res = await fetchApi('/api/companies');
        if (!isMounted) return;
        if (res.companies && res.companies.length > 0) {
          const mapped = res.companies.map((c: any) => ({
            id: String(c.company_id),
            company_id: c.company_id,
            name: c.name,
            short_name: c.short_name || c.name.substring(0, 10),
            logo_url: c.logo_url || '',
            website_url: c.website_url || c.website || '',
            category: c.category || 'Enterprise',
            employee_size: c.employee_size || '100+',
            operating_countries: c.operating_countries || c.countries_operating_in || 'Global',
            office_locations: c.office_locations || 'NA',
            yoy_growth_rate: c.yoy_growth_rate || '10%'
          }));
          setCompanies(mapped);
        } else {
          setCompanies(getCompaniesShort());
        }
      } catch (err) {
        console.error("Failed to load companies for semantic search:", err);
        if (isMounted) {
          setCompanies(getCompaniesShort());
        }
      }
    };
    loadCompanies();
    fetchClusters();
    return () => {
      isMounted = false;
    };
  }, []);

  const fetchClusters = async () => {
    setLoadingClusters(true);
    try {
      const res = await fetchApi('/api/clusters');
      setClusters(res.clusters || []);
    } catch (err) {
      console.error("Failed to fetch clusters:", err);
    } finally {
      setLoadingClusters(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    try {
      const res = await fetchApi('/api/search', {
        method: 'POST',
        body: JSON.stringify({ query, top_n: 6 })
      });
      setSearchResults(res.results || []);
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const handleCompanySelect = async (compId: number) => {
    setSelectedCompId(compId);
    setLoadingSimilar(true);
    try {
      const res = await fetchApi(`/api/similarity/${compId}?top_n=5`);
      setSimilarCompanies(res.results || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingSimilar(false);
    }
  };

  // SVG Scatter plot dimension config
  const padding = 40;
  const width = 500;
  const height = 350;

  // Calculate coordinates bounds
  const getBounds = () => {
    if (clusters.length === 0) return { minX: 0, maxX: 10, minY: 0, maxY: 10 };
    const xs = clusters.map(c => c.x);
    const ys = clusters.map(c => c.y);
    return {
      minX: Math.min(...xs),
      maxX: Math.max(...xs),
      minY: Math.min(...ys),
      maxY: Math.max(...ys),
    };
  };

  const bounds = getBounds();
  const scaleX = (x: number) => {
    const range = bounds.maxX - bounds.minX || 1;
    return padding + ((x - bounds.minX) / range) * (width - 2 * padding);
  };
  const scaleY = (y: number) => {
    const range = bounds.maxY - bounds.minY || 1;
    return height - padding - ((y - bounds.minY) / range) * (height - 2 * padding);
  };

  // Harmonious cluster color definitions
  const colors = [
    '#3b82f6', // Blue (Cluster 0)
    '#f59e0b', // Amber (Cluster 1)
    '#10b981', // Emerald (Cluster 2)
    '#ef4444', // Rose (Cluster 3)
    '#6366f1', // Indigo (Cluster 4)
    '#8b5cf6'  // Purple (Fallback)
  ];

  return (
    <Layout>
      <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6 sm:space-y-8 font-sans">
        {/* Title */}
        <div className="pb-4 border-b border-slate-200">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 mb-1">Semantic Company Directory</h1>
          <p className="text-sm text-slate-500">Query and discover placements profiles using vector embeddings and cluster analysis.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
          
          {/* Left Column: Semantic Search & Similarity mapping */}
          <div className="lg:col-span-7 space-y-6 sm:space-y-8">
            
            {/* Card 1: Semantic Search */}
            <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
                <Search className="w-5 h-5 text-blue-600" /> Semantic Matching Engine
              </h2>
              <form onSubmit={handleSearch} className="flex gap-2 mb-6">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="E.g., Logistics company doing dynamic routing and carbon tracking"
                  className="flex-1 px-4 py-2 text-sm rounded-xl border border-slate-200 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder:text-slate-400"
                />
                <button
                  type="submit"
                  disabled={searching || !query.trim()}
                  className="bg-blue-600 text-white text-sm font-semibold px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {searching ? 'Searching...' : 'Search'}
                </button>
              </form>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="space-y-3">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Top Semantic Matches:</p>
                  <div className="grid grid-cols-1 gap-3">
                    {searchResults.map((res) => (
                      <div
                        key={res.company_id}
                        className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100/60 transition-all flex items-center justify-between"
                      >
                        <div>
                          <h4 className="font-bold text-sm text-slate-900">{res.name}</h4>
                          <p className="text-xs text-slate-500">{res.metadata.category || 'NA'} • {res.metadata.nature_of_company || 'Private'}</p>
                        </div>
                        <div className="flex items-center gap-1 bg-blue-50 border border-blue-100 text-blue-600 px-2 py-1 rounded-lg text-xs font-bold">
                          <Sparkles className="w-3.5 h-3.5 animate-pulse" />
                          {Math.round(res.score * 100)}% Match
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {searchResults.length === 0 && !searching && (
                <div className="text-center py-8 text-sm text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                  Enter a business theme or capability description above to query the vector space.
                </div>
              )}
            </div>

            {/* Card 2: Competitor Mapping */}
            <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
                <Network className="w-5 h-5 text-blue-600" /> Competitor & Similarity Mapping
              </h2>
              <div className="mb-6">
                <label className="block text-xs font-bold text-slate-400 uppercase mb-2">Select a reference company:</label>
                <select
                  value={selectedCompId}
                  onChange={(e) => {
                    const val = e.target.value;
                    setSelectedCompId(val ? Number(val) : '');
                    if (val) handleCompanySelect(Number(val));
                  }}
                  className="w-full px-4 py-2 text-sm rounded-xl border border-slate-200 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={companies.length === 0}
                >
                  <option value="">-- Choose Company --</option>
                  {companies.map((c) => {
                    const cid = c.company_id || parseInt(c.id.replace('comp_', '')) || 0;
                    return (
                      <option key={c.id} value={cid}>
                        {c.name}
                      </option>
                    );
                  })}
                </select>
              </div>

              {/* Similarity Results */}
              {loadingSimilar && (
                <div className="text-center py-6 text-sm text-slate-500">
                  Calculating closest competitor embeddings...
                </div>
              )}

              {!loadingSimilar && similarCompanies.length > 0 && (
                <div className="space-y-3">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Top Competitors / Similar Profiles:</p>
                  <div className="space-y-2">
                    {similarCompanies.map((item) => (
                      <div
                        key={item.company_id}
                        className="p-3 rounded-xl border border-slate-100 bg-slate-50/50 flex justify-between items-center"
                      >
                        <div className="flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-slate-400" />
                          <div>
                            <div className="font-bold text-xs text-slate-900">{item.name}</div>
                            <div className="text-[10px] text-slate-500">{item.metadata.category}</div>
                          </div>
                        </div>
                        <span className="text-xs font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-lg border border-green-100">
                          {(item.score * 100).toFixed(1)}% Similarity
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

          </div>

          {/* Right Column: 2D Cluster Visualizer */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-6 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-blue-600" /> Innovation Clustering Space
              </h2>
              <p className="text-xs text-slate-500 mb-4">Dimensionality reduction (PCA) of 768D semantic vectors into a 2D cluster model.</p>

              {loadingClusters && (
                <div className="flex items-center justify-center h-[300px] text-sm text-slate-500">
                  Training cluster models...
                </div>
              )}

              {!loadingClusters && clusters.length > 0 && (
                <div className="relative">
                  {/* SVG Plot */}
                  <svg viewBox={`0 0 ${width} ${height}`} className="w-full border border-slate-100 bg-slate-50/30 rounded-xl">
                    {/* Grid Lines */}
                    <line x1={padding} y1={height / 2} x2={width - padding} y2={height / 2} stroke="#f1f5f9" strokeDasharray="3,3" />
                    <line x1={width / 2} y1={padding} x2={width / 2} y2={height - padding} stroke="#f1f5f9" strokeDasharray="3,3" />

                    {/* Scatter Dots */}
                    {clusters.map((point) => {
                      const color = colors[point.cluster_id % colors.length];
                      const isHovered = hoveredPoint?.company_id === point.company_id;
                      return (
                        <circle
                          key={point.company_id}
                          cx={scaleX(point.x)}
                          cy={scaleY(point.y)}
                          r={isHovered ? 8 : 5}
                          fill={color}
                          stroke={isHovered ? "#fff" : "transparent"}
                          strokeWidth={2}
                          className="transition-all duration-150 cursor-pointer"
                          onMouseEnter={() => setHoveredPoint(point)}
                          onMouseLeave={() => setHoveredPoint(null)}
                          onClick={() => handleCompanySelect(point.company_id)}
                        />
                      );
                    })}
                  </svg>

                  {/* Tooltip Overlay */}
                  {hoveredPoint && (
                    <div className="absolute top-2 left-2 bg-white text-slate-800 border border-slate-200 p-3 rounded-xl shadow-lg text-xs z-10 max-w-[200px] pointer-events-none">
                      <div className="font-bold text-slate-900">{hoveredPoint.name}</div>
                      <div className="text-slate-500 mt-0.5">Category: {hoveredPoint.category}</div>
                      <div className="mt-1 flex items-center gap-1.5">
                        <span
                          className="w-2.5 h-2.5 rounded-full inline-block"
                          style={{ backgroundColor: colors[hoveredPoint.cluster_id % colors.length] }}
                        />
                        <span className="font-bold text-slate-700">Cluster {hoveredPoint.cluster_id}</span>
                      </div>
                    </div>
                  )}
                  
                  {/* Legend */}
                  <div className="grid grid-cols-3 gap-2 mt-4 text-[10px] text-slate-500 font-bold">
                    {colors.slice(0, 5).map((color, idx) => (
                      <div key={idx} className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: color }} />
                        <span>Cluster {idx}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </Layout>
  );
}
