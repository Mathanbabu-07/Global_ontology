import { useState, useEffect } from 'react';
import { HiOutlineRefresh } from 'react-icons/hi';
import { getMonitorData } from '../services/api';

export default function DataMonitor() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const res = await getMonitorData();
            setData(res.data);
        } catch {
            setData([]);
        } finally {
            setLoading(false);
        }
    };

    const formatTime = (ts) => {
        if (!ts) return '—';
        const d = new Date(ts);
        return d.toLocaleString([], {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
    };

    return (
        <div>
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1>Data Monitor</h1>
                    <p>Real-time scraped intelligence data</p>
                </div>
                <button className="btn btn-secondary" onClick={loadData} disabled={loading}>
                    <HiOutlineRefresh style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
                    Refresh
                </button>
            </div>

            {loading ? (
                <div className="empty-state"><div className="loading-spinner" /></div>
            ) : data.length > 0 ? (
                <div className="monitor-grid">
                    {data.map((item, i) => (
                        <div className="monitor-card" key={i}>
                            <div className="mc-header">
                                <span className="mc-url" title={item.source_url}>{item.source_url}</span>
                                <span className="mc-time">{formatTime(item.fetched_at)}</span>
                            </div>
                            {item.domain && (
                                <span className={`badge ${item.domain}`} style={{ marginBottom: 10, display: 'inline-flex' }}>
                                    {item.domain}
                                </span>
                            )}
                            <div className="mc-summary">
                                {item.summary || 'No summary available.'}
                            </div>
                            {item.entities && item.entities.length > 0 && (
                                <>
                                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                        Entities Detected
                                    </div>
                                    <div className="mc-entities">
                                        {item.entities.map((e, j) => (
                                            <span className="entity-tag" key={j}>{e}</span>
                                        ))}
                                    </div>
                                </>
                            )}
                        </div>
                    ))}
                </div>
            ) : (
                <div className="card">
                    <div className="empty-state">
                        <div className="empty-icon">📊</div>
                        <h3>No data collected yet</h3>
                        <p>Data will appear here once sources are scraped and analyzed</p>
                    </div>
                </div>
            )}
        </div>
    );
}
