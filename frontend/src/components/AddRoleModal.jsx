import { useState } from 'react'

export default function AddRoleModal({ onClose, onAdd }) {
  const [name, setName] = useState('')
  const [keywords, setKeywords] = useState('')
  const [category, setCategory] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name || !keywords || !category) return

    setIsSubmitting(true)
    await onAdd({
      name,
      keywords,
      category: category.toLowerCase().replace(/\s+/g, '_')
    })
    setIsSubmitting(false)
    onClose()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-content--small" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="modal-header">
          <h2 className="modal-title">Track a New Role</h2>
          <p className="modal-subtitle">Add a new role to fetch jobs for.</p>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          <div className="form-group">
            <label>Display Name</label>
            <input
              type="text"
              className="modal-input"
              placeholder="e.g. Frontend Developer"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Category Key</label>
            <input
              type="text"
              className="modal-input"
              placeholder="e.g. frontend_dev"
              value={category}
              onChange={e => setCategory(e.target.value)}
              required
            />
            <small className="form-help">Internal ID for grouping (no spaces).</small>
          </div>

          <div className="form-group">
            <label>Search Keywords</label>
            <textarea
              className="modal-textarea"
              placeholder="e.g. react developer, frontend engineer, ui developer"
              value={keywords}
              onChange={e => setKeywords(e.target.value)}
              rows="3"
              required
            />
            <small className="form-help">Comma-separated keywords used for searching.</small>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Adding...' : 'Add Role'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
