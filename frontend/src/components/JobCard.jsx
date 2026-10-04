const ROLE_COLORS = {
  data_analyst: '#6366f1',
  business_analyst: '#8b5cf6',
  pmo: '#06b6d4',
  hr_it: '#10b981',
  software_engineer: '#f59e0b',
  internship: '#ec4899',
}

const STATUS_CONFIG = {
  new: { label: 'New', color: '#6366f1', bg: 'rgba(99,102,241,0.15)' },
  saved: { label: 'Saved', color: '#06b6d4', bg: 'rgba(6,182,212,0.15)' },
  applied: { label: 'Applied', color: '#10b981', bg: 'rgba(16,185,129,0.15)' },
  interviewing: { label: 'Interview', color: '#f59e0b', bg: 'rgba(245,158,11,0.15)' },
  rejected: { label: 'Rejected', color: '#ef4444', bg: 'rgba(239,68,68,0.15)' },
  offer: { label: 'Offer 🎉', color: '#22c55e', bg: 'rgba(34,197,94,0.15)' },
}

const SOURCE_ICONS = {
  Adzuna: '🔍',
  JSearch: '🌐',
  'Google Jobs': '🔎',
  Internshala: '🎓',
  'EY Careers': '🏢',
  'Deloitte Careers': '🏢',
  'KPMG Careers': '🏢',
  'TCS Careers': '🏢',
  'Infosys Careers': '🏢',
  'Accenture Careers': '🏢',
  'Wipro Careers': '🏢',
  'HCL Careers': '🏢',
}

export default function JobCard({ job, onSelect, onUpdate, onDelete }) {
  const roleColor = ROLE_COLORS[job.role_category] || '#6366f1'
  const statusCfg = STATUS_CONFIG[job.status] || STATUS_CONFIG.new
  const sourceIcon = SOURCE_ICONS[job.source] || '🔗'

  const timeSince = (dateStr) => {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    const diff = Date.now() - d.getTime()
    const days = Math.floor(diff / 86400000)
    if (days === 0) return 'Today'
    if (days === 1) return 'Yesterday'
    if (days < 7) return `${days}d ago`
    if (days < 30) return `${Math.floor(days / 7)}w ago`
    return `${Math.floor(days / 30)}mo ago`
  }

  return (
    <div className={`job-card ${job.is_bookmarked ? 'job-card--bookmarked' : ''}`} onClick={() => onSelect(job)}>
      <div className="job-card-accent" style={{ background: roleColor }} />

      <div className="job-card-header">
        <div className="job-card-company-wrap">
          <div className="job-card-avatar" style={{ background: `${roleColor}22`, color: roleColor }}>
            {(job.company || '?')[0].toUpperCase()}
          </div>
          <div style={{ minWidth: 0, flex: 1 }}>
            <h3 className="job-card-title">{job.title}</h3>
            <p className="job-card-company">{job.company}</p>
          </div>
        </div>
        <div className="job-card-actions" onClick={e => e.stopPropagation()}>
          <button
            className={`icon-btn ${job.is_bookmarked ? 'icon-btn--active' : ''}`}
            title={job.is_bookmarked ? 'Remove bookmark' : 'Bookmark'}
            onClick={() => onUpdate(job.id, { is_bookmarked: !job.is_bookmarked })}
          >
            <svg viewBox="0 0 24 24" fill={job.is_bookmarked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" width="16" height="16">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
          </button>
        </div>
      </div>

      <div className="job-card-meta">
        <span className="job-meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="12" height="12">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          {job.location}
        </span>
        {job.salary && (
          <span className="job-meta-item job-meta-salary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="12" height="12">
              <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
            {job.salary}
          </span>
        )}
        <span className="job-meta-item">
          {sourceIcon} {job.source}
        </span>
        {job.created_at && (
          <span className="job-meta-item job-meta-time">{timeSince(job.created_at)}</span>
        )}
      </div>

      <div className="job-card-footer">
        <div
          className="job-status-badge"
          style={{ color: statusCfg.color, background: statusCfg.bg }}
        >
          {statusCfg.label}
        </div>

        <div className="job-card-quick-actions" onClick={e => e.stopPropagation()}>
          <select
            className="status-select"
            value={job.status}
            onChange={e => onUpdate(job.id, { status: e.target.value })}
          >
            {Object.entries(STATUS_CONFIG).map(([val, cfg]) => (
              <option key={val} value={val}>{cfg.label}</option>
            ))}
          </select>
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-apply"
            onClick={e => e.stopPropagation()}
          >
            Apply →
          </a>
        </div>
      </div>
    </div>
  )
}
