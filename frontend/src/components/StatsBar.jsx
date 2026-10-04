export default function StatsBar({ stats }) {
  if (!stats) return null

  const statItems = [
    { label: 'Total Jobs', value: stats.total, color: '#3b82f6', icon: '📊' },
    { label: 'New', value: stats.new, color: '#6366f1', icon: '✨' },
    { label: 'Bookmarked', value: stats.bookmarked, color: '#06b6d4', icon: '🔖' },
    { label: 'Applied', value: stats.applied, color: '#10b981', icon: '✅' },
    { label: 'Interviewing', value: stats.interviewing, color: '#f59e0b', icon: '🎯' },
  ]

  return (
    <div className="stats-bar">
      {statItems.map((item, idx) => (
        <div key={idx} className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: `${item.color}22` }}>
            {item.icon}
          </div>
          <div className="stat-content">
            <span className="stat-value" style={{ color: item.color }}>{item.value}</span>
            <span className="stat-label">{item.label}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
