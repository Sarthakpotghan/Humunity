import { useState } from 'react';
import { MaterialIcon, Avatar } from '../components/ui';
import { formatDate } from '../utils/format';

export default function NGOPendingRow({ ngo, busy, onDecide }) {
  const [expanded, setExpanded] = useState(false);
  
  const formatDateSafe = (dateStr) => {
    if (!dateStr) return '—';
    try {
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  const toggleExpand = (e) => {
    e.stopPropagation();
    setExpanded(!expanded);
  };

  return (
    <div className="border-t border-outline-variant/20">
      <div 
        className="flex flex-col md:flex-row md:items-center gap-3 px-5 py-4 cursor-pointer"
        onClick={toggleExpand}
        style={{ backgroundColor: expanded ? 'var(--sys-surface-container-highest)' : 'transparent' }}
      >
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <Avatar name={ngo.ngo_name || `NGO #${ngo.id}`} size={40} />
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <p className="font-label-lg text-on-surface truncate">{ngo.ngo_name || `NGO #${ngo.id}`}</p>
              {ngo.has_profile && (
                <span className="chip bg-tertiary-container text-on-tertiary-container font-label-sm">
                  Profile Submitted
                </span>
              )}
              {!ngo.has_profile && (
                <span className="chip bg-surface-container-high text-on-surface-variant font-label-sm">
                  No Profile Yet
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-1.5 mt-1 text-body-sm text-on-surface-variant">
              <span className="flex items-center gap-1">
                <MaterialIcon name="email" size={14} /> {ngo.email}
              </span>
              {ngo.phone && (
                <span className="flex items-center gap-1">
                  <MaterialIcon name="phone" size={14} /> {ngo.phone}
                </span>
              )}
            </div>
            {ngo.focus_areas?.length > 0 && (
              <div className="flex gap-1.5 mt-1 flex-wrap">
                {ngo.focus_areas.map((a) => (
                  <span key={a} className="chip bg-surface-container-high text-on-surface-variant">{a}</span>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            disabled={busy === `verify-${ngo.id}-false`}
            onClick={(e) => { e.stopPropagation(); onDecide(ngo.id, false, { name: ngo.ngo_name }); }}
            className="btn-outline px-4 py-2 text-error"
          >
            Reject
          </button>
          <button
            type="button"
            disabled={busy === `verify-${ngo.id}-true`}
            onClick={(e) => { e.stopPropagation(); onDecide(ngo.id, true, { name: ngo.ngo_name }); }}
            className="btn-primary px-4 py-2"
          >
            Verify
          </button>
          <MaterialIcon 
            name={expanded ? 'expand_less' : 'expand_more'} 
            size={24} 
            className="text-on-surface-variant"
          />
        </div>
      </div>
      
      {expanded && (
        <div className="px-5 pb-5 bg-surface-container-highest/50 animate-slide-down">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <h4 className="font-label-md text-on-surface">Profile Information</h4>
              <div className="grid grid-cols-2 gap-3 text-body-sm">
                <div>
                  <span className="text-on-surface-variant">Registration Number</span>
                  <p className="font-label-md text-on-surface">{ngo.reg_number || 'Not submitted'}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Status</span>
                  <p className="font-label-md text-on-surface capitalize">{ngo.has_profile ? 'Submitted' : 'Not Submitted'}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Reliability Score</span>
                  <p className="font-label-md text-on-surface">{ngo.reliability_score?.toFixed(1)}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Verification</span>
                  <p className="font-label-md text-on-surface">{ngo.verified ? 'Verified' : 'Pending'}</p>
                </div>
                {ngo.reg_doc_url && (
                  <div className="md:col-span-2">
                    <span className="text-on-surface-variant">Registration Document</span>
                    <a href={ngo.reg_doc_url} target="_blank" rel="noopener noreferrer" className="font-label-md text-primary hover:underline flex items-center gap-1">
                      <MaterialIcon name="picture_as_pdf" size={16} /> View Document
                    </a>
                  </div>
                )}
                {ngo.focus_areas?.length > 0 && (
                  <div className="md:col-span-2">
                    <span className="text-on-surface-variant">Focus Areas</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {ngo.focus_areas.map((a) => (
                        <span key={a} className="chip bg-tertiary-container text-on-tertiary-container">{a}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="font-label-md text-on-surface">Contact & Location</h4>
              <div className="grid grid-cols-2 gap-3 text-body-sm">
                <div>
                  <span className="text-on-surface-variant">Email</span>
                  <p className="font-label-md text-on-surface">{ngo.email}</p>
                </div>
                {ngo.phone && (
                  <div>
                    <span className="text-on-surface-variant">Phone</span>
                    <p className="font-label-md text-on-surface">{ngo.phone}</p>
                  </div>
                )}
                {ngo.address && (
                  <div className="md:col-span-2">
                    <span className="text-on-surface-variant">Address</span>
                    <p className="font-label-md text-on-surface">{ngo.address}</p>
                  </div>
                )}
                {ngo.lat !== null && ngo.lng !== null && (
                  <div className="md:col-span-2">
                    <span className="text-on-surface-variant">Coordinates</span>
                    <p className="font-label-md text-on-surface">{ngo.lat.toFixed(4)}, {ngo.lng.toFixed(4)}</p>
                  </div>
                )}
                <div>
                  <span className="text-on-surface-variant">Account Created</span>
                  <p className="font-label-md text-on-surface">{ngo.created_at ? new Date(ngo.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}