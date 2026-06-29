import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const shortPath = path.join(root, 'src', 'data', 'company_short.json');
const fullPath = path.join(root, 'src', 'data', 'company_full.json');

const requiredCompanies = [
  'Mitsubishi UFJ Financial Group, Inc.',
  'Commonwealth Bank of Australia',
  'Larsen & Toubro Infotech Limited',
  'Tata Consultancy Services Limited',
  'The Bank of New York Mellon Corporation',
  'Nutanix, Inc.',
  'MintAir Corp',
  'NVIDIA Corporation',
  'HCL Technologies Limited',
  'Freshworks Inc.',
  'Koninklijke Philips N.V.',
  'Warner Bros. Discovery, Inc.',
  'Electronic Arts',
  'Optum',
  'Concentrix Corporation',
  'Dunzo Digital Private Limited',
  'ZS Associates, Inc.',
  'Hexagon Capability Center India',
  'BigBasket',
  'Ecom Express',
  'One MobiKwik Systems Limited',
];

const forbiddenProviders = [
  'google.com/s2/favicons',
  'unavatar.io',
  'favicon.ico',
  'tse1.mm.bing.net',
  'images.search.yahoo.com',
];

const shortData = JSON.parse(fs.readFileSync(shortPath, 'utf8'));
const fullData = JSON.parse(fs.readFileSync(fullPath, 'utf8'));

function normalizeLogoUrl(raw = '') {
  const markdownLinkMatch = raw.match(/\((https?:\/\/[^\s)]+)\)/i);
  const candidate = markdownLinkMatch?.[1] || raw;
  const withoutOuterBrackets =
    candidate.startsWith('[') && candidate.endsWith(']') ? candidate.slice(1, -1) : candidate;

  const firstUrl = withoutOuterBrackets
    .split(/[;,]\s*/)
    .map((part) => part.trim().replace(/^['"]|['"]$/g, ''))
    .find((part) => /^https?:\/\//i.test(part));

  return firstUrl || '';
}

function isDirectSvgUrl(url) {
  return /\.svg(?:\?|$)/i.test(url);
}

async function fetchWithTimeout(url, timeoutMs = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, {
      method: 'GET',
      signal: controller.signal,
      redirect: 'follow',
      headers: { 'User-Agent': 'Mozilla/5.0' },
    });
  } finally {
    clearTimeout(timer);
  }
}

test('required companies exist in short and full datasets', () => {
  for (const name of requiredCompanies) {
    assert.ok(shortData.some((c) => c.name === name), `Missing in short data: ${name}`);
    assert.ok(fullData.some((c) => c.name === name), `Missing in full data: ${name}`);
  }
});

test('required companies use direct SVG logo URLs and not fallback providers', () => {
  const failures = [];

  for (const name of requiredCompanies) {
    const shortCompany = shortData.find((c) => c.name === name);
    const fullCompany = fullData.find((c) => c.name === name);

    for (const [source, company] of [
      ['short', shortCompany],
      ['full', fullCompany],
    ]) {
      const normalized = normalizeLogoUrl(company.logo_url);
      if (!normalized) {
        failures.push(`${source}: ${name} has empty/invalid logo_url`);
        continue;
      }

      if (!isDirectSvgUrl(normalized)) {
        failures.push(`${source}: ${name} is not a direct SVG URL -> ${normalized}`);
      }

      const lower = normalized.toLowerCase();
      const forbidden = forbiddenProviders.find((provider) => lower.includes(provider));
      if (forbidden) {
        failures.push(`${source}: ${name} uses forbidden fallback provider (${forbidden}) -> ${normalized}`);
      }
    }
  }

  assert.equal(
    failures.length,
    0,
    `Logo URL policy failures:\n${failures.map((line) => `- ${line}`).join('\n')}`
  );
});

test('required companies SVG URLs return SVG content', async () => {
  const failures = [];

  for (const name of requiredCompanies) {
    const shortCompany = shortData.find((c) => c.name === name);
    const logoUrl = normalizeLogoUrl(shortCompany.logo_url);

    if (!logoUrl || !isDirectSvgUrl(logoUrl)) {
      failures.push(`${name}: skipped fetch check because URL is not a direct SVG -> ${logoUrl || '(empty)'}`);
      continue;
    }

    try {
      const response = await fetchWithTimeout(logoUrl);
      const contentType = response.headers.get('content-type') || '';
      const isSvgResponse = /svg|xml/i.test(contentType);

      if (!response.ok) {
        failures.push(`${name}: HTTP ${response.status} for ${logoUrl}`);
      } else if (!isSvgResponse) {
        failures.push(`${name}: content-type is not SVG (${contentType || 'unknown'}) for ${logoUrl}`);
      }
    } catch (error) {
      failures.push(`${name}: request failed for ${logoUrl} (${error?.name || 'Error'})`);
    }
  }

  assert.equal(
    failures.length,
    0,
    `SVG fetch validation failures:\n${failures.map((line) => `- ${line}`).join('\n')}`
  );
});
