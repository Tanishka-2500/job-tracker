import { useState, useEffect, useCallback } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import JobBoard from './components/JobBoard'
import StatsBar from './components/StatsBar'
import JobDetailModal from './components/JobDetailModal'
import AddRoleModal from './components/AddRoleModal'
import { jobsAPI, rolesAPI, statsAPI, scrapeAPI } from './api'

export default function App() {
  const [jobs, setJobs] = useState([])
  const [roles, setRoles] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [scraping, setScraping] = useState(false)
  const [selectedJob, setSelectedJob] = useState(null)
  const [showAddRole, setShowAddRole] = useState(false)
  const [filters, setFilters] = useState({
    role_category: '',
    status: '',
    source: '',
    search: '',
    location: '',
    sort_by: 'newest',
    bookmarked: null,
    page: 1,
  })
  const [pagination, setPagination] = useState({ total: 0, pages: 1 })
  const [scrapeStatus, setScrapeStatus] = useState(null)
  const [toast, setToast] = useState(null)

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  const fetchJobs = useCallback(async () => {
    setLoading(true)
    try {
      const data = await jobsAPI.getAll(filters)
      setJobs(data.jobs)
      setPagination({ total: data.total, pages: data.pages })
    } catch (e) {
      showToast('Failed to load jobs', 'error')
    } finally {
      setLoading(false)
    }
  }, [filters])

  const fetchRoles = async () => {
    try {
      const data = await rolesAPI.getAll()
      setRoles(data)
    } catch (e) {
      console.error('Failed to load roles', e)
    }
  }

  const fetchStats = async () => {
    try {
      const data = await statsAPI.get()
      setStats(data)
    } catch (e) {
      console.error('Failed to load stats', e)
    }
  }

  const fetchScrapeStatus = async () => {
    try {
      const data = await scrapeAPI.status()
      setScrapeStatus(data)
    } catch (e) {
      console.error('Failed to fetch scrape status', e)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  useEffect(() => {
    fetchRoles()
    fetchStats()
    fetchScrapeStatus()
  }, [])

  const handleRefresh = async () => {
    setScraping(true)
    showToast('🔄 Fetching fresh job listings... This may take a minute.', 'info')
    try {
      await scrapeAPI.trigger()
      // Poll for completion
      const pollInterval = setInterval(async () => {
        const status = await scrapeAPI.status()
        setScrapeStatus(status)
        if (!status.is_running) {
          clearInterval(pollInterval)
          setScraping(false)
          fetchJobs()
          fetchStats()
          showToast('✅ Job listings refreshed!', 'success')
        }
      }, 3000)
    } catch (e) {
      setScraping(false)
      showToast('Refresh failed — check API keys in .env', 'error')
    }
  }

  const handleUpdateJob = async (jobId, update) => {
    try {
      const updated = await jobsAPI.update(jobId, update)
      setJobs(prev => prev.map(j => j.id === jobId ? updated : j))
      if (selectedJob?.id === jobId) setSelectedJob(updated)
      fetchStats()
    } catch (e) {
      showToast('Failed to update job', 'error')
    }
  }

  const handleDeleteJob = async (jobId) => {
    try {
      await jobsAPI.delete(jobId)
      setJobs(prev => prev.filter(j => j.id !== jobId))
      if (selectedJob?.id === jobId) setSelectedJob(null)
      fetchStats()
      showToast('Job removed', 'success')
    } catch (e) {
      showToast('Failed to delete job', 'error')
    }
  }

  const handleAddRole = async (roleData) => {
    try {
      await rolesAPI.create(roleData)
      fetchRoles()
      showToast(`Role "${roleData.name}" added!`, 'success')
    } catch (e) {
      showToast('Failed to add role', 'error')
    }
  }

  const handleToggleRole = async (roleId) => {
    try {
      await rolesAPI.toggle(roleId)
      fetchRoles()
    } catch (e) {
      showToast('Failed to toggle role', 'error')
    }
  }

  const handleDeleteRole = async (roleId) => {
    try {
      await rolesAPI.delete(roleId)
      fetchRoles()
      showToast('Role deleted', 'success')
    } catch (e) {
      showToast('Failed to delete role', 'error')
    }
  }

  const updateFilters = (newFilters) => {
    setFilters(prev => {
      // If we are only updating the page, keep it. Otherwise, reset to page 1.
      const isPageChangeOnly = Object.keys(newFilters).length === 1 && 'page' in newFilters;
      return { ...prev, ...newFilters, page: isPageChangeOnly ? newFilters.page : 1 };
    })
  }

  return (
    <div className="app">
      {/* Toast Notification */}
      {toast && (
        <div className={`toast toast--${toast.type}`}>
          {toast.msg}
        </div>
      )}

      <header className="app-header">
        <div className="header-brand">
          <div className="header-logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 7H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </svg>
          </div>
          <div>
            <h1 className="header-title">JobTracker</h1>
            <p className="header-subtitle">India Fresher Job Monitor</p>
          </div>
        </div>
        <div className="header-actions">
          <div className="scrape-info">
            {scrapeStatus?.last_log && (
              <span className="last-refresh">
                Last refresh: {new Date(scrapeStatus.last_log.time).toLocaleDateString('en-IN')}
              </span>
            )}
          </div>
          <button
            className={`btn btn-refresh ${scraping ? 'btn-refresh--loading' : ''}`}
            onClick={handleRefresh}
            disabled={scraping}
          >
            {scraping ? (
              <>
                <span className="spinner" />
                Fetching...
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                  <path d="M23 4v6h-6"/>
                  <path d="M1 20v-6h6"/>
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                </svg>
                Refresh Jobs
              </>
            )}
          </button>
          <button className="btn btn-add-role" onClick={() => setShowAddRole(true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 8v8M8 12h8"/>
            </svg>
            Add Role
          </button>
        </div>
      </header>

      {stats && <StatsBar stats={stats} />}

      <div className="app-body">
        <Sidebar
          roles={roles}
          filters={filters}
          onFilterChange={updateFilters}
          onToggleRole={handleToggleRole}
          onDeleteRole={handleDeleteRole}
          stats={stats}
        />
        <main className="main-content">
          <JobBoard
            jobs={jobs}
            loading={loading}
            filters={filters}
            pagination={pagination}
            onFilterChange={updateFilters}
            onSelectJob={setSelectedJob}
            onUpdateJob={handleUpdateJob}
            onDeleteJob={handleDeleteJob}
          />
        </main>
      </div>

      {selectedJob && (
        <JobDetailModal
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
          onUpdate={handleUpdateJob}
          onDelete={handleDeleteJob}
        />
      )}

      {showAddRole && (
        <AddRoleModal
          onClose={() => setShowAddRole(false)}
          onAdd={handleAddRole}
        />
      )}
    </div>
  )
}
