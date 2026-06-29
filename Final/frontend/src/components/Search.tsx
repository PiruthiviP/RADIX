import React, { useMemo, useState } from 'react';
import { Search } from 'lucide-react';
import { Input } from './UI';

interface SearchResult {
  id: string;
  name: string;
  short_name: string;
}

interface GlobalSearchProps {
  companies: SearchResult[];
  onSelect: (companyId: string) => void;
  placeholder?: string;
  query?: string;
  onQueryChange?: (query: string) => void;
}

export const GlobalSearch: React.FC<GlobalSearchProps> = ({
  companies,
  onSelect,
  placeholder = 'Search by company name...',
  query: controlledQuery,
  onQueryChange,
}) => {
  const [internalQuery, setInternalQuery] = useState('');
  const query = controlledQuery !== undefined ? controlledQuery : internalQuery;
  const setQuery = onQueryChange || setInternalQuery;
  const [isOpen, setIsOpen] = useState(false);
  const filteredResults = useMemo(() => {
    if (!query.trim()) return [];

    const lowerQuery = query.toLowerCase();
    return companies
      .filter(
        (company) =>
          company.name.toLowerCase().includes(lowerQuery) ||
          company.short_name.toLowerCase().includes(lowerQuery)
      )
      .sort((a, b) => a.name.localeCompare(b.name))
      .slice(0, 10);
  }, [query, companies]);

  const handleSelect = (companyId: string) => {
    onSelect(companyId);
    setQuery('');
    setIsOpen(false);
  };

  const handleEnterKeySelect = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key !== 'Enter' || filteredResults.length === 0) return;
    event.preventDefault();
    handleSelect(filteredResults[0].id);
  };

  return (
    <div className="relative w-full">
      <Input
        icon={<Search className="h-4 w-4" />}
        type="text"
        placeholder={placeholder}
        value={query}
        onChange={(e) => {
          const nextQuery = e.target.value;
          setQuery(nextQuery);
          setIsOpen(Boolean(nextQuery.trim()));
        }}
        onKeyDown={handleEnterKeySelect}
        onFocus={() => query.trim() && setIsOpen(true)}
        onBlur={() => setTimeout(() => setIsOpen(false), 200)}
        className="w-full text-lg py-3 pl-11 pr-4"
      />

      {isOpen && filteredResults.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl border border-slate-200 shadow-xl z-50 overflow-hidden">
          <div className="max-h-80 overflow-y-auto">
            {filteredResults.map((result) => (
              <button
                key={result.id}
                type="button"
                onMouseDown={(event) => {
                  // Use mousedown so selection still works even if input blur fires first.
                  event.preventDefault();
                  handleSelect(result.id);
                }}
                className="w-full px-4 py-3 text-left hover:bg-blue-50 transition-colors border-b border-slate-100 last:border-0"
              >
                <p className="font-semibold text-slate-900">{result.name}</p>
                <p className="text-xs text-slate-600">{result.short_name}</p>
              </button>
            ))}
          </div>

          {filteredResults.length === 0 && (
            <div className="px-4 py-6 text-center text-slate-600">
              <p>No companies found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

interface QuickSearchProps {
  companies: SearchResult[];
  onSelect: (companyId: string) => void;
}

export const AlphabeticalSearch: React.FC<QuickSearchProps> = ({ companies, onSelect }) => {
  const [selectedLetter, setSelectedLetter] = useState<string | null>(null);

  const groupedByLetter: Record<string, SearchResult[]> = {};
  companies.forEach((company) => {
    const letter = company.name.charAt(0).toUpperCase();
    if (!groupedByLetter[letter]) {
      groupedByLetter[letter] = [];
    }
    groupedByLetter[letter].push(company);
  });

  const letters = Object.keys(groupedByLetter).sort();
  const filteredCompanies = selectedLetter ? groupedByLetter[selectedLetter] : [];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {letters.map((letter) => (
          <button
            key={letter}
            onClick={() => setSelectedLetter(selectedLetter === letter ? null : letter)}
            className={`px-3 py-1.5 rounded-lg font-semibold text-sm transition-all ${
              selectedLetter === letter
                ? 'bg-blue-600 text-white'
                : 'bg-slate-200 text-slate-900 hover:bg-slate-300'
            }`}
          >
            {letter}
          </button>
        ))}
      </div>

      {selectedLetter && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {filteredCompanies.map((company) => (
            <button
              key={company.id}
              onClick={() => onSelect(company.id)}
              className="text-left px-4 py-3 rounded-lg bg-white border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-all"
            >
              <p className="font-semibold text-slate-900">{company.name}</p>
              <p className="text-xs text-slate-600">{company.short_name}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
