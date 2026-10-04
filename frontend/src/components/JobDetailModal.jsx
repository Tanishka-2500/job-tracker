import { useState } from 'react'

const STATUSES = ['new', 'saved', 'applied', 'interviewing', 'rejected', 'offer']

export default function JobDetailModal({ job, onClose, onUpdate, onDelete }) {
  const [notes, setNotes] = useState(job.notes || '')
  const [status, setStatus] = useState(job.status || 'new')
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    await onUpdate(job.id, { notes, status })
    setIsSaving(false)
    onClose()
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      await onDelete(job.id)
      onClose()
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="modal-header">
          <h2 className="modal-title">{job.title}</h2>
          <p className="modal-company">{job.company} • {job.location}</p>
        </div>

        <div className="modal-body scrollable">
          <div className="job-meta-grid">
            <div className="meta-box">
              <span className="meta-label">Source</span>
              <span className="meta-value">{job.source}</span>
            </div>
            <div className="meta-box">
              <span className="meta-label">Salary</span>
              <span className="meta-value">{job.salary || 'Not specified'}</span>
            </div>
            <div className="meta-box">
              <span className="meta-label">Posted</span>
              <span className="meta-value">{job.posted_date || 'Unknown'}</span>
            </div>
            <div className="meta-box">
              <span className="meta-label">Category</span>
              <span className="meta-value">{job.role_category}</span>
            </div>
          </div>

          <div className="form-group">
            <label>Application Status</label>
            <select value={status} onChange={e => setStatus(e.target.value)} className="modal-select">
              {STATUSES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>My Notes</label>
            <textarea
              className="modal-textarea"
              placeholder="Add interview notes, recruiter contacts, or next steps here..."
              value={notes}
              onChange={e => setNotes(e.target.value)}
              rows="4"
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <div className="job-description-text">
              {job.description || 'No description available.'}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          <div className="modal-actions-right">
            <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
              View Original ↗
            </a>
            <button className="btn btn-primary" onClick={handleSave} disabled={isSaving}>
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
