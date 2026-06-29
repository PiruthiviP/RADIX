'use client';

import React from 'react';
import { Mail, Phone, MapPin, Calendar, Camera, X } from 'lucide-react';

interface AccountModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AccountModal: React.FC<AccountModalProps> = ({ isOpen, onClose }) => {
  const profileData = {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    department: 'Computer Science',
    groupName: 'Team Alpha',
    endDate: 'May 30, 2025',
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop with Blur */}
      <div
        className="fixed inset-0 bg-white/30 backdrop-blur-sm z-[9998] transition-opacity duration-200"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-[9999] p-4 pointer-events-none">
        <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-full max-w-xs pointer-events-auto animate-in fade-in slide-in-from-bottom-4 duration-300">
          {/* Close Button */}
          <div className="absolute top-4 right-4">
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              aria-label="Close modal"
            >
              <X className="h-5 w-5 text-slate-600" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Profile Picture */}
            <div className="flex flex-col items-center">
              <div className="relative group">
                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 text-white flex items-center justify-center text-4xl font-bold shadow-lg">
                  {profileData.firstName[0]}{profileData.lastName[0]}
                </div>
                <button className="absolute bottom-0 right-0 w-10 h-10 bg-white rounded-full shadow-lg border-2 border-blue-600 flex items-center justify-center hover:bg-blue-50 transition-colors">
                  <Camera className="h-5 w-5 text-blue-600" />
                </button>
              </div>

              <h2 className="text-2xl font-bold text-slate-900 mt-4 text-center">
                {profileData.firstName} {profileData.lastName}
              </h2>
              <p className="text-slate-600 text-sm mt-1 text-center">{profileData.department}</p>
              <p className="text-slate-500 text-xs mt-1 text-center">{profileData.groupName}</p>
            </div>

            {/* Quick Stats */}
            <div className="mt-6 pt-6 border-t border-slate-200 space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <Mail className="h-4 w-4 text-blue-600" />
                <span className="text-slate-700 truncate">{profileData.email}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Phone className="h-4 w-4 text-blue-600" />
                <span className="text-slate-700">{profileData.phone}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <MapPin className="h-4 w-4 text-blue-600" />
                <span className="text-slate-700">{profileData.location}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="h-4 w-4 text-blue-600" />
                <span className="text-slate-700">End Date: {profileData.endDate}</span>
              </div>
            </div>

            {/* Account Status */}
            <div className="mt-6 pt-6 border-t border-slate-200">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Account Status</span>
                <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                  Active
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
