import { useState, useEffect } from 'react';
import {
    HiOutlineLightningBolt,
    HiOutlineGlobeAlt,
    HiOutlineLink,
    HiOutlineClock,
    HiOutlineExclamationCircle,
    HiOutlineTrash,
    HiOutlineDatabase,
} from 'react-icons/hi';
import {
    TbWorld,
    TbCurrencyDollar,
    TbShield,
    TbCpu,
    TbLeaf,
    TbUsers
} from 'react-icons/tb';
import { processSource, processBulkSources, getIntelligenceFeed, deleteIntelligenceEvent } from '../services/api';

export default function IntelligenceFeed() {
    const [feed, setFeed] = useState([]);
    const [loading, setLoading] = useState(true);

    // Extraction State
    const [extractMode, setExtractMode] = useState('url'); // 'url' or 'registry'
    const [extracting, setExtracting] = useState(false);
    const [url, setUrl] = useState('');
    const [bulkDomain, setBulkDomain] = useState('All');
    const [bulkProgressMsg, setBulkProgressMsg] = useState('');

    const [toast, setToast] = useState(null);
    const [deletedIds, setDeletedIds] = useState(new Set());

    // Filters
    const [domainFilter, setDomainFilter] = useState('All');
    const [dateFilter, setDateFilter] = useState('All Time');

    useEffect(() => {
        loadFeed();
    }, []);

    const loadFeed = async () => {
        try {
            const res = await getIntelligenceFeed();
            setFeed(res.data || []);
        } catch (err) {
            console.error('Feed load error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleExtractURL = async (e) => {
        e.preventDefault();
        if (!url.trim() || extracting) return;

        setExtracting(true);
        setToast(null);

        try {
            const res = await processSource(url.trim());
            const data = res.data;

            if (data.success) {
                setToast({ type: 'success', message: `Intelligence extracted: ${data.intelligence?.event_title || 'Done'}` });
                setUrl('');
                await loadFeed();
            } else {
                setToast({ type: 'success', message: data.warning || 'Extracted (storage may have issues)' });
                await loadFeed();
            }
        } catch (err) {
            const msg = err.response?.data?.error || 'Extraction failed';
            setToast({ type: 'error', message: msg });
        } finally {
            setExtracting(false);
            setTimeout(() => setToast(null), 4000);
        }
    };

    const handleExtractBulk = async (e) => {
        e.preventDefault();
        if (extracting) return;

        setExtracting(true);
        setBulkProgressMsg('Fetching sources and starting bulk extraction...');
        setToast(null);

        try {
            const res = await processBulkSources(bulkDomain.toLowerCase());
            const data = res.data;

            setToast({ type: 'success', message: `Analyzed ${data.total_count} sources. ${data.success_count} new events found!` });
            await loadFeed();
        } catch (err) {
            const msg = err.response?.data?.error || 'Bulk extraction failed';
            setToast({ type: 'error', message: msg });
        } finally {
            setExtracting(false);
            setBulkProgressMsg('');
            setTimeout(() => setToast(null), 5000);
        }
    };

    const domainColors = {
        geopolitics: '#ef4444',
        economics: '#f59e0b',
        defense: '#6366f1',
        technology: '#22d3ee',
        climate: '#10b981',
        society: '#a855f7',
        unknown: '#64748b'
    };

    const getDomainColor = (domain) => domainColors[domain] || domainColors.unknown;

    const domainIcons = {
        geopolitics: <TbWorld />,
        economics: <TbCurrencyDollar />,
        defense: <TbShield />,
        technology: <TbCpu />,
        climate: <TbLeaf />,
        society: <TbUsers />,
        unknown: <HiOutlineExclamationCircle />
    };

    const getDomainIcon = (domain) => domainIcons[domain] || domainIcons.unknown;

    const handleDelete = async (id) => {
        // Optimistic UI update
        setDeletedIds(prev => new Set(prev).add(id));

        try {
            await deleteIntelligenceEvent(id);
        } catch (err) {
            console.error('Delete failed:', err);
            // Revert on failure
            setDeletedIds(prev => {
                const next = new Set(prev);
                next.delete(id);
                return next;
            });
            setToast({ type: 'error', message: 'Failed to delete event permanently.' });
        }
    };

    const formatTime = (ts) => {
        if (!ts) return '';
        const d = new Date(ts);
        return d.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' }) +
            ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const getEntityTypeBadge = (type) => {
        const map = {
            country: '🏳️',
            organization: '🏢',
            person: '👤',
            technology: '⚙️',
            resource: '💎',
            location: '📍',
        };
        return map[type] || '🔹';
    };

    // Derived filtered feed
    const filteredFeed = feed.filter((event) => {
        if (deletedIds.has(event.id)) return false;

        // Domain Filter
        if (domainFilter !== 'All' && event.domain !== domainFilter.toLowerCase()) {
            return false;
        }

        // Date Filter
        if (dateFilter !== 'All Time') {
            const eventDate = new Date(event.created_at);
            const now = new Date();
            const msPerDay = 24 * 60 * 60 * 1000;

            // Normalize "today" to start of day
            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

            if (dateFilter === 'Today') {
                if (eventDate < todayStart) return false;
            } else if (dateFilter === 'Yesterday') {
                const yesterdayStart = new Date(todayStart.getTime() - msPerDay);
                if (eventDate < yesterdayStart || eventDate >= todayStart) return false;
            } else if (dateFilter === 'Last Week') {
                const lastWeekStart = new Date(todayStart.getTime() - 7 * msPerDay);
                if (eventDate < lastWeekStart) return false;
            }
        }

        return true;
    });

    return (
        <div>
            <div className="page-header">
                <h1>Intelligence Feed</h1>
                <p>AI-extracted strategic intelligence from monitored sources</p>
            </div>

            {/* Extract Component */}
            <div className="intel-extract-container" style={{ marginBottom: '28px', background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 'var(--border-radius)', overflow: 'hidden' }}>
                <div style={{ display: 'flex', borderBottom: '1px solid var(--border-primary)', background: 'rgba(10, 14, 26, 0.4)' }}>
                    <button
                        onClick={() => setExtractMode('url')}
                        style={{ flex: 1, padding: '12px', background: extractMode === 'url' ? 'rgba(99, 102, 241, 0.1)' : 'transparent', border: 'none', color: extractMode === 'url' ? 'var(--accent-primary)' : 'var(--text-secondary)', fontWeight: 600, fontSize: 13, cursor: 'pointer', borderBottom: extractMode === 'url' ? '2px solid var(--accent-primary)' : '2px solid transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, transition: 'all 0.2s' }}
                    >
                        <HiOutlineLink size={16} /> Extract from Single URL
                    </button>
                    <button
                        onClick={() => setExtractMode('registry')}
                        style={{ flex: 1, padding: '12px', background: extractMode === 'registry' ? 'rgba(99, 102, 241, 0.1)' : 'transparent', border: 'none', color: extractMode === 'registry' ? 'var(--accent-primary)' : 'var(--text-secondary)', fontWeight: 600, fontSize: 13, cursor: 'pointer', borderBottom: extractMode === 'registry' ? '2px solid var(--accent-primary)' : '2px solid transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, transition: 'all 0.2s' }}
                    >
                        <HiOutlineDatabase size={16} /> Bulk Extract from Source Registry
                    </button>
                </div>

                {extractMode === 'url' ? (
                    <form className="intel-extract-bar" style={{ marginBottom: 0, border: 'none', background: 'transparent' }} onSubmit={handleExtractURL}>
                        <div className="intel-extract-input-wrap">
                            <HiOutlineLink className="intel-extract-icon" />
                            <input
                                type="url"
                                className="form-input intel-extract-input"
                                placeholder="Paste article URL to extract intelligence..."
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                disabled={extracting}
                                id="intel-url-input"
                            />
                        </div>
                        <button
                            type="submit"
                            className="btn btn-primary intel-extract-btn"
                            disabled={extracting || !url.trim()}
                            id="intel-extract-btn"
                        >
                            {extracting ? (
                                <>
                                    <span className="loading-spinner" />
                                    Extracting<span className="loading-dots" />
                                </>
                            ) : (
                                <>
                                    <HiOutlineLightningBolt />
                                    Extract Intelligence
                                </>
                            )}
                        </button>
                    </form>
                ) : (
                    <form className="intel-extract-bar" style={{ marginBottom: 0, border: 'none', background: 'transparent' }} onSubmit={handleExtractBulk}>
                        <div className="intel-extract-input-wrap" style={{ gap: 12 }}>
                            <span style={{ fontSize: 13, color: 'var(--text-secondary)', whiteSpace: 'nowrap', paddingLeft: 10 }}>Target Domain:</span>
                            <select
                                value={bulkDomain}
                                onChange={(e) => setBulkDomain(e.target.value)}
                                className="form-input"
                                disabled={extracting}
                                style={{ flex: 1 }}
                            >
                                <option value="All">All Domains</option>
                                <option value="geopolitics">Geopolitics</option>
                                <option value="economics">Economics</option>
                                <option value="defense">Defense</option>
                                <option value="technology">Technology</option>
                                <option value="climate">Climate</option>
                                <option value="society">Society</option>
                            </select>
                        </div>
                        <button
                            type="submit"
                            className="btn btn-primary intel-extract-btn"
                            disabled={extracting}
                            style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)' }}
                        >
                            {extracting ? (
                                <>
                                    <span className="loading-spinner" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    <HiOutlineDatabase />
                                    Bulk Extract
                                </>
                            )}
                        </button>
                    </form>
                )}

                {extracting && extractMode === 'registry' && bulkProgressMsg && (
                    <div style={{ padding: '12px 20px', background: 'rgba(10, 14, 26, 0.6)', borderTop: '1px solid var(--border-secondary)', fontSize: 12, color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span className="loading-spinner" style={{ width: 14, height: 14, borderWidth: 2 }}></span> {bulkProgressMsg}
                    </div>
                )}
            </div>

            {/* Filters Bar */}
            <div className="intel-filters-bar" style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
                <div className="filter-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Domain:</label>
                    <select
                        value={domainFilter}
                        onChange={(e) => setDomainFilter(e.target.value)}
                        className="form-input"
                        style={{ width: 'auto', minWidth: '150px' }}
                    >
                        <option value="All">All Domains</option>
                        <option value="geopolitics">Geopolitics</option>
                        <option value="economics">Economics</option>
                        <option value="defense">Defense</option>
                        <option value="technology">Technology</option>
                        <option value="climate">Climate</option>
                        <option value="society">Society</option>
                        <option value="unknown">Unknown</option>
                    </select>
                </div>

                <div className="filter-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Date:</label>
                    <select
                        value={dateFilter}
                        onChange={(e) => setDateFilter(e.target.value)}
                        className="form-input"
                        style={{ width: 'auto', minWidth: '150px' }}
                    >
                        <option value="All Time">All Time</option>
                        <option value="Today">Today</option>
                        <option value="Yesterday">Yesterday</option>
                        <option value="Last Week">Last Week</option>
                    </select>
                </div>
            </div>

            {/* Feed */}
            {loading ? (
                <div className="empty-state">
                    <div className="loading-spinner" />
                </div>
            ) : filteredFeed.length > 0 ? (
                <div className="intel-feed-grid">
                    {filteredFeed.map((event) => (
                        <div className="intel-card" key={event.id} style={{ '--domain-color': getDomainColor(event.domain) }}>
                            <div className="intel-card-accent" />
                            <div className="intel-card-header">
                                <span className={`badge ${event.domain}`}>
                                    {getDomainIcon(event.domain)} {event.domain}
                                </span>
                                {event.timestamp && (
                                    <span className="intel-card-time">
                                        <HiOutlineClock /> {event.timestamp}
                                    </span>
                                )}
                                {event.domain === 'unknown' && (
                                    <button
                                        className="btn-icon danger"
                                        onClick={() => handleDelete(event.id)}
                                        title="Delete Error Entry"
                                        style={{ marginLeft: 'auto', width: 28, height: 28, fontSize: 14 }}
                                    >
                                        <HiOutlineTrash />
                                    </button>
                                )}
                            </div>

                            <h3 className="intel-card-title">{event.event_title}</h3>
                            <p className="intel-card-summary">{event.summary}</p>

                            {/* Entities */}
                            {event.entities && event.entities.length > 0 && (
                                <div className="intel-entities">
                                    <span className="intel-section-label">Entities</span>
                                    <div className="intel-entity-tags">
                                        {event.entities.map((ent, i) => (
                                            <span className="entity-tag" key={i}>
                                                {getEntityTypeBadge(ent.entity_type || ent.type)}
                                                {' '}{ent.entity_name || ent.name}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Impact */}
                            {event.impact && (
                                <div className="intel-impact">
                                    <HiOutlineExclamationCircle />
                                    <span>{event.impact}</span>
                                </div>
                            )}

                            {/* Relationships */}
                            {event.relationships && event.relationships.length > 0 && (
                                <div className="intel-relationships">
                                    <span className="intel-section-label">Relationships</span>
                                    {event.relationships.map((rel, i) => (
                                        <div className="intel-rel-row" key={i}>
                                            <span className="intel-rel-entity">{rel.source_entity || rel.source}</span>
                                            <span className="intel-rel-arrow">→</span>
                                            <span className="intel-rel-type">{rel.relation}</span>
                                            <span className="intel-rel-arrow">→</span>
                                            <span className="intel-rel-entity">{rel.target_entity || rel.target}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Source */}
                            <div className="intel-card-footer">
                                <a
                                    href={event.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="intel-source-link"
                                >
                                    <HiOutlineGlobeAlt />
                                    {event.source_url ? new URL(event.source_url).hostname : 'Source'}
                                </a>
                                <span className="intel-card-created">{formatTime(event.created_at)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <div className="empty-icon">🔍</div>
                    <h3>No intelligence extracted yet</h3>
                    <p>Paste a URL above and click "Extract Intelligence" to begin</p>
                </div>
            )}

            {/* Toast */}
            {toast && (
                <div className={`toast ${toast.type}`} id="intel-toast">
                    {toast.message}
                </div>
            )}
        </div>
    );
}
