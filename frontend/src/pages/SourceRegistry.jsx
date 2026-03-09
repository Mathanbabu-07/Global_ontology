import { useState, useEffect } from 'react';
import { HiOutlinePlus, HiOutlineTrash, HiOutlinePause, HiOutlinePlay, HiOutlineGlobe } from 'react-icons/hi';
import { addSource, getSources, deleteSource, toggleSource } from '../services/api';

const CATEGORIES = ['geopolitics', 'economics', 'defense', 'technology', 'climate', 'society'];
const FREQUENCIES = [
    { value: '15min', label: 'Every 15 min' },
    { value: '30min', label: 'Every 30 min' },
    { value: '1hour', label: 'Every 1 hour' },
    { value: 'daily', label: 'Daily' },
];

const emptyForm = { url: '', category: 'geopolitics', frequency: '1hour', trust_score: 5 };

export default function SourceRegistry() {
    const [sources, setSources] = useState([]);
    const [form, setForm] = useState({ ...emptyForm });
    const [showForm, setShowForm] = useState(false);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [toast, setToast] = useState(null);

    useEffect(() => {
        loadSources();
    }, []);

    const showToast = (msg, type = 'success') => {
        setToast({ msg, type });
        setTimeout(() => setToast(null), 3000);
    };

    const loadSources = async () => {
        try {
            const res = await getSources();
            setSources(res.data);
        } catch {
            setSources([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.url.trim()) return;
        setSubmitting(true);
        try {
            await addSource(form);
            setForm({ ...emptyForm });
            setShowForm(false);
            showToast('Source added successfully');
            loadSources();
        } catch {
            showToast('Failed to add source', 'error');
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        try {
            await deleteSource(id);
            showToast('Source removed');
            loadSources();
        } catch {
            showToast('Failed to delete', 'error');
        }
    };

    const handleToggle = async (id) => {
        try {
            await toggleSource(id);
            loadSources();
        } catch {
            showToast('Failed to toggle', 'error');
        }
    };

    const formatDate = (d) => {
        if (!d) return '—';
        return new Date(d).toLocaleString([], {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };

    return (
        <div>
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1>Source Registry</h1>
                    <p>Manage monitored intelligence sources</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                    <HiOutlinePlus /> Add Source
                </button>
            </div>

            {/* Add Source Form */}
            {showForm && (
                <div className="card" style={{ marginBottom: 24 }}>
                    <div className="section-title">
                        <HiOutlineGlobe /> Register New Source
                    </div>
                    <form onSubmit={handleSubmit}>
                        <div className="form-row" style={{ marginBottom: 16 }}>
                            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                                <label className="form-label">Source URL</label>
                                <input
                                    className="form-input"
                                    type="url"
                                    placeholder="https://example.com/news-feed"
                                    value={form.url}
                                    onChange={(e) => setForm({ ...form, url: e.target.value })}
                                    required
                                />
                            </div>
                        </div>
                        <div className="form-row" style={{ marginBottom: 16 }}>
                            <div className="form-group">
                                <label className="form-label">Category</label>
                                <select
                                    className="form-select"
                                    value={form.category}
                                    onChange={(e) => setForm({ ...form, category: e.target.value })}
                                >
                                    {CATEGORIES.map(c => (
                                        <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Update Frequency</label>
                                <select
                                    className="form-select"
                                    value={form.frequency}
                                    onChange={(e) => setForm({ ...form, frequency: e.target.value })}
                                >
                                    {FREQUENCIES.map(f => (
                                        <option key={f.value} value={f.value}>{f.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Trust Score</label>
                                <div className="trust-score-slider">
                                    <input
                                        type="range"
                                        min="1"
                                        max="10"
                                        value={form.trust_score}
                                        onChange={(e) => setForm({ ...form, trust_score: parseInt(e.target.value) })}
                                    />
                                    <span className="trust-score-value">{form.trust_score}</span>
                                </div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: 12 }}>
                            <button className="btn btn-primary" type="submit" disabled={submitting}>
                                {submitting ? <><span className="loading-spinner" /> Adding...</> : <><HiOutlinePlus /> Add Source</>}
                            </button>
                            <button className="btn btn-secondary" type="button" onClick={() => setShowForm(false)}>
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Sources Table */}
            <div className="data-table-wrapper">
                {loading ? (
                    <div className="empty-state"><div className="loading-spinner" /></div>
                ) : sources.length > 0 ? (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>URL</th>
                                <th>Category</th>
                                <th>Trust Score</th>
                                <th>Last Checked</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sources.map((s) => (
                                <tr key={s.id}>
                                    <td className="url-cell" title={s.url}>{s.url}</td>
                                    <td><span className={`badge ${s.category}`}>{s.category}</span></td>
                                    <td>
                                        <span style={{
                                            fontWeight: 700,
                                            color: s.trust_score >= 7 ? 'var(--accent-emerald)' :
                                                s.trust_score >= 4 ? 'var(--accent-amber)' : 'var(--accent-rose)'
                                        }}>
                                            {s.trust_score}/10
                                        </span>
                                    </td>
                                    <td style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{formatDate(s.last_checked)}</td>
                                    <td>
                                        <span className={`badge-status ${s.active ? 'active' : 'paused'}`}>
                                            {s.active ? 'Active' : 'Paused'}
                                        </span>
                                    </td>
                                    <td>
                                        <div style={{ display: 'flex', gap: 6 }}>
                                            <button className="btn-icon" onClick={() => handleToggle(s.id)} title={s.active ? 'Pause' : 'Resume'}>
                                                {s.active ? <HiOutlinePause /> : <HiOutlinePlay />}
                                            </button>
                                            <button className="btn-icon danger" onClick={() => handleDelete(s.id)} title="Delete">
                                                <HiOutlineTrash />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="empty-state">
                        <div className="empty-icon">🌐</div>
                        <h3>No sources registered</h3>
                        <p>Click "Add Source" to start monitoring intelligence feeds</p>
                    </div>
                )}
            </div>

            {toast && <div className={`toast ${toast.type}`}>{toast.msg}</div>}
        </div>
    );
}
