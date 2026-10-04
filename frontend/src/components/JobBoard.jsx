import JobCard from './JobCard'

const SOURCES = ['Adzuna', 'JSearch', 'Google Jobs', 'Internshala', 'EY Careers', 'Deloitte Careers', 'KPMG Careers', 'TCS Careers', 'Infosys Careers', 'Accenture Careers', 'Wipro Careers', 'HCL Careers']
const STATUSES = ['new', 'saved', 'applied', 'interviewing', 'rejected', 'offer']

export default function JobBoard({ jobs, loading, filters, pagination, onFilterChange, onSelectJob, onUpdateJob, onDeleteJob }) {
  return (
    <div className="job-board">
      {/* Search + Filters Bar */}
      <div className="job-board-toolbar">
        <div className="search-wrap">
          <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            className="search-input"
            type="text"
            placeholder="Search jobs, companies..."
            value={filters.search}
            onChange={e => onFilterChange({ search: e.target.value })}
            style={{ width: '60%' }}
          />
          <input
            className="search-input"
            type="text"
            placeholder="Location..."
            value={filters.location || ''}
            onChange={e => onFilterChange({ location: e.target.value })}
            style={{ width: '38%', marginLeft: '2%' }}
          />
        </div>
        <div className="filter-row">
          <select
            className="filter-select"
            value={filters.status}
            onChange={e => onFilterChange({ status: e.target.value })}
          >
            <option value="">All Statuses</option>
            {STATUSES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
          </select>
          <select
            className="filter-select"
            value={filters.source}
            onChange={e => onFilterChange({ source: e.target.value })}
          >
            <option value="">All Sources</option>
            {SOURCES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <select
            className="filter-select"
            value={filters.sort_by || 'newest'}
            onChange={e => onFilterChange({ sort_by: e.target.value })}
          >
            <option value="newest">Fresh to Old</option>
            <option value="oldest">Old to Fresh</option>
          </select>
          <button
            className={`filter-btn ${filters.bookmarked ? 'filter-btn--active' : ''}`}
            onClick={() => onFilterChange({ bookmarked: filters.bookmarked ? null : true })}
          >
            <svg viewBox="0 0 24 24" fill={filters.bookmarked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" width="14" height="14">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
            </svg>
            Bookmarked
          </button>
        </div>
      </div>

      {/* Results Count */}
      <div className="results-bar">
        <span className="results-count">
          {loading ? 'Loading...' : `${pagination.total} jobs found`}
        </span>
      </div>

      {/* Job Grid */}
      {loading ? (
        <div className="loading-grid">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="job-card-skeleton">
              <div className="skeleton-line skeleton-line--title" />
              <div className="skeleton-line skeleton-line--subtitle" />
              <div className="skeleton-line skeleton-line--short" />
            </div>
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>No jobs found</h3>
          <p>Try clicking <strong>Refresh Jobs</strong> to fetch the latest listings, or adjust your filters.</p>
        </div>
      ) : (
        <div className="job-grid">
          {jobs.map(job => (
            <JobCard
              key={job.id}
              job={job}
              onSelect={onSelectJob}
              onUpdate={onUpdateJob}
              onDelete={onDeleteJob}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {pagination.pages > 1 && (
        <div className="pagination">
          <button
            className="page-btn"
            disabled={filters.page <= 1}
            onClick={() => onFilterChange({ page: filters.page - 1 })}
          >
            ← Prev
          </button>
          <span className="page-info">Page {filters.page} of {pagination.pages}</span>
          <button
            className="page-btn"
            disabled={filters.page >= pagination.pages}
            onClick={() => onFilterChange({ page: filters.page + 1 })}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
