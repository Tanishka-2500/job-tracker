const ROLE_COLORS = {
  data_analyst: '#6366f1',
  business_analyst: '#8b5cf6',
  pmo: '#06b6d4',
  hr_it: '#10b981',
  software_engineer: '#f59e0b',
  internship: '#ec4899',
}

export default function Sidebar({ roles, filters, onFilterChange, onToggleRole, onDeleteRole, stats }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <h2 className="sidebar-title">Tracked Roles</h2>
        <ul className="role-list">
          <li
            className={`role-item ${filters.role_category === '' ? 'role-item--active' : ''}`}
            onClick={() => onFilterChange({ role_category: '' })}
          >
            <div className="role-color-dot" style={{ background: '#cbd5e1' }} />
            <span className="role-name">All Roles</span>
            <span className="role-count">{stats?.total || 0}</span>
          </li>

          {roles.map(role => (
            <li
              key={role.id}
              className={`role-item ${filters.role_category === role.category ? 'role-item--active' : ''} ${!role.is_active ? 'role-item--inactive' : ''}`}
            >
              <div
                className="role-clickable-area"
                onClick={() => onFilterChange({ role_category: role.category })}
              >
                <div className="role-color-dot" style={{ background: ROLE_COLORS[role.category] || '#94a3b8' }} />
                <span className="role-name" title={role.name}>{role.name}</span>
                <span className="role-count">{stats?.by_role?.[role.name] || 0}</span>
              </div>
              
              <div className="role-actions">
                <button
                  className="icon-btn-small"
                  title={role.is_active ? "Pause scraping" : "Resume scraping"}
                  onClick={(e) => { e.stopPropagation(); onToggleRole(role.id) }}
                >
                  {role.is_active ? '⏸' : '▶️'}
                </button>
                <button
                  className="icon-btn-small icon-btn-small--danger"
                  title="Delete role"
                  onClick={(e) => { 
                    e.stopPropagation()
                    if (window.confirm(`Delete ${role.name}? This doesn't delete existing jobs.`)) {
                      onDeleteRole(role.id)
                    }
                  }}
                >
                  ×
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-section">
        <h2 className="sidebar-title">Sources</h2>
        <ul className="source-list">
          {stats?.by_source && Object.entries(stats.by_source).map(([source, count]) => (
            <li
              key={source}
              className={`source-item ${filters.source === source ? 'source-item--active' : ''}`}
              onClick={() => onFilterChange({ source: filters.source === source ? '' : source })}
            >
              <span>{source}</span>
              <span className="source-count">{count}</span>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  )
}
