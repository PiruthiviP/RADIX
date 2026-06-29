'use client';

import React from 'react';
import { CompanyEntryPage } from '@/components/CompanyEntryPage';

export default function HiringProcessEntryPage() {
  return (
    <CompanyEntryPage
      title="Hiring Process"
      subtitle="Explore company-specific hiring processes and selection stages"
      targetRoute="process"
      accentClass="from-blue-50 to-blue-100"
    />
  );
}
