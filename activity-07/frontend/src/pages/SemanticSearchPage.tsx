import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Building2, TrendingUp, HelpCircle, Network } from 'lucide-react';
import { fetchApi } from '@/lib/api';
import { useCompaniesShort } from '@/hooks/useSupabaseData';

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
  const { data: companies = [], isLoading: loadingCompanies } = useCompaniesShort();
  
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
    fetchClusters();
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
    // Invert Y coordinate for screen coordinates representation
    return height - padding - ((y - bounds.minY) / range) * (height - 2 * padding);
  };

  // Harmonious cluster color definitions
  const colors = [
    '#6366F1', // Indigo (Cluster 0)
    '#F59E0B', // Amber (Cluster 1)
    '#10B981', // Emerald (Cluster 2)
    '#EF4444', // Rose (Cluster 3)
    '#0EA5E9', // Sky (Cluster 4)
    '#8B5CF6'  // Purple (Fallback)
  ];

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8 font-sans">
      {/* Title */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Semantic Company Directory</h1>
        <p className="text-muted-foreground">Search and discover corporate profiles using vector embeddings and cluster analysis.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Semantic Search & Similarity mapping */}
        <div className="lg:col-span-7 space-y-8">
          
          {/* Card 1: Semantic Search */}
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <Search className="w-5 h-5 text-primary" /> Semantic Matching Engine
            </h2>
            <form onSubmit={handleSearch} className="flex gap-2 mb-6">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="E.g., Logistics company doing dynamic routing and carbon tracking"
                className="flex-1 px-4 py-2 text-sm rounded-xl border border-border bg-background focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <button
                type="submit"
                disabled={searching || !query.trim()}
                className="bg-primary text-primary-foreground text-sm font-medium px-4 py-2 rounded-xl hover:bg-primary/95 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {searching ? 'Searching...' : 'Search'}
              </button>
            </form>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="space-y-3">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Top Semantic Matches:</p>
                <div className="grid grid-cols-1 gap-3">
                  {searchResults.map((res) => (
                    <div
                      key={res.company_id}
                      className="p-4 rounded-xl border border-border bg-background/50 hover:bg-accent/20 transition-all flex items-center justify-between"
                    >
                      <div>
                        <h4 className="font-semibold text-sm">{res.name}</h4>
                        <p className="text-xs text-muted-foreground">{res.metadata.category || 'NA'} • {res.metadata.nature_of_company || 'Private'}</p>
                      </div>
                      <div className="flex items-center gap-1.5 bg-primary/10 border border-primary/20 text-primary px-2 py-1 rounded-lg text-xs font-bold">
                        <Sparkles className="w-3.5 h-3.5" />
                        {Math.round(res.score * 100)}% Match
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {searchResults.length === 0 && !searching && (
              <div className="text-center py-6 text-sm text-muted-foreground bg-accent/10 rounded-xl border border-dashed border-border">
                Enter a business theme or capability description above to query the vector space.
              </div>
            )}
          </div>

          {/* Card 2: Competitor Mapping */}
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <Network className="w-5 h-5 text-primary" /> Competitor & Similarity Mapping
            </h2>
            <div className="mb-6">
              <label className="block text-xs font-medium text-muted-foreground mb-2">Select a reference company:</label>
              <select
                value={selectedCompId}
                onChange={(e) => {
                  const val = e.target.value;
                  setSelectedCompId(val ? Number(val) : '');
                  if (val) handleCompanySelect(Number(val));
                }}
                className="w-full px-4 py-2 text-sm rounded-xl border border-border bg-background focus:outline-none focus:ring-1 focus:ring-primary"
                disabled={companies.length === 0}
              >
                <option value="">-- Choose Company --</option>
                {companies.map((c) => (
                  <option key={c.company_id} value={c.company_id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Similarity Results */}
            {loadingSimilar && (
              <div className="text-center py-6 text-sm text-muted-foreground">
                Calculating closest competitor embeddings...
              </div>
            )}

            {!loadingSimilar && similarCompanies.length > 0 && (
              <div className="space-y-3">
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Top Competitors / Similar Profiles:</p>
                <div className="space-y-2">
                  {similarCompanies.map((item) => (
                    <div
                      key={item.company_id}
                      className="p-3 rounded-xl border border-border/60 bg-background/30 flex justify-between items-center"
                    >
                      <div className="flex items-center gap-2">
                        <Building2 className="w-4 h-4 text-muted-foreground" />
                        <div>
                          <div className="font-semibold text-xs">{item.name}</div>
                          <div className="text-[10px] text-muted-foreground">{item.metadata.category}</div>
                        </div>
                      </div>
                      <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-lg border border-emerald-100">
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
          <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-primary" /> Innovation Clustering space
            </h2>
            <p className="text-xs text-muted-foreground mb-4">Dimensionality reduction (PCA) of 768D semantic vectors into a 2D cluster model.</p>

            {loadingClusters && (
              <div className="flex items-center justify-center h-[300px] text-sm text-muted-foreground">
                Training cluster models...
              </div>
            )}

            {!loadingClusters && clusters.length > 0 && (
              <div className="relative">
                {/* SVG Plot */}
                <svg viewBox={`0 0 ${width} ${height}`} className="w-full border border-border/80 bg-background rounded-xl">
                  {/* Grid Lines */}
                  <line x1={padding} y1={height / 2} x2={width - padding} y2={height / 2} stroke="#E5E7EB" strokeDasharray="3,3" />
                  <line x1={width / 2} y1={padding} x2={width / 2} y2={height - padding} stroke="#E5E7EB" strokeDasharray="3,3" />

                  {/* Scatter Dots */}
                  {clusters.map((point) => {
                    const color = colors[point.cluster_id % colors.length];
                    const isHovered = hoveredPoint?.company_id === point.company_id;
                    return (
                      <circle
                        key={point.company_id}
                        cx={scaleX(point.x)}
                        cy={scaleY(point.y)}
                        r={isHovered ? 8 : 4.5}
                        fill={color}
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
                  <div className="absolute top-2 left-2 bg-popover text-popover-foreground border border-border p-3 rounded-lg shadow-md text-xs z-10 max-w-[200px] pointer-events-none">
                    <div className="font-bold">{hoveredPoint.name}</div>
                    <div className="text-muted-foreground mt-0.5">Category: {hoveredPoint.category}</div>
                    <div className="mt-1 flex items-center gap-1.5">
                      <span
                        className="w-2.5 h-2.5 rounded-full inline-block"
                        style={{ backgroundColor: colors[hoveredPoint.cluster_id % colors.length] }}
                      />
                      <span className="font-bold">Cluster {hoveredPoint.cluster_id}</span>
                    </div>
                  </div>
                )}
                
                {/* Legend */}
                <div className="grid grid-cols-3 gap-2 mt-4 text-[10px] text-muted-foreground font-medium">
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
  );
}
