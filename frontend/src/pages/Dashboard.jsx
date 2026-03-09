import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import StatCard from '../components/StatCard';
import { HiOutlineGlobe, HiOutlineStatusOnline, HiOutlineLightningBolt, HiOutlineDatabase } from 'react-icons/hi';
import { getDashboardStats, getMonitorData } from '../services/api';

export default function Dashboard() {
    const [stats, setStats] = useState({
        total_sources: 0,
        active_crawlers: 0,
        new_updates: 0,
        total_events: 0,
        total_extracted_events: 0,
        top_entities: [],
        most_active_domain: 'N/A',
        recent_intel: [],
    });
    const [activities, setActivities] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [statsRes, monitorRes] = await Promise.allSettled([
                getDashboardStats(),
                getMonitorData(),
            ]);

            if (statsRes.status === 'fulfilled') {
                setStats(statsRes.value.data);
            }
            if (monitorRes.status === 'fulfilled') {
                setActivities(monitorRes.value.data.slice(0, 8));
            }
        } catch (err) {
            console.error('Dashboard load error:', err);
        } finally {
            setLoading(false);
        }
    };

    const formatTime = (ts) => {
        if (!ts) return 'Just now';
        const d = new Date(ts);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div>
            <div className="page-header">
                <h1>Intelligence Dashboard</h1>
                <p>Real-time overview of the Global Ontology Engine</p>
            </div>

            <div className="stats-grid">
                <StatCard
                    icon={<HiOutlineGlobe />}
                    value={stats.total_sources}
                    label="Total Sources Monitored"
                    change="+3 this week"
                    changeType="up"
                    colorClass="purple"
                />
                <StatCard
                    icon={<HiOutlineStatusOnline />}
                    value={stats.active_crawlers}
                    label="Active Crawlers"
                    change="Running"
                    changeType="up"
                    colorClass="cyan"
                />
                <StatCard
                    icon={<HiOutlineLightningBolt />}
                    value={stats.total_extracted_events || stats.new_updates}
                    label="Extracted Events"
                    change={stats.most_active_domain !== 'N/A' ? `Top: ${stats.most_active_domain}` : 'Last 24h'}
                    changeType="up"
                    colorClass="emerald"
                />
                <StatCard
                    icon={<HiOutlineDatabase />}
                    value={stats.total_events}
                    label="Total Scraped Data"
                    change="Growing"
                    changeType="up"
                    colorClass="amber"
                />
            </div>

            {/* Top Entities */}
            {stats.top_entities && stats.top_entities.length > 0 && (
                <div className="card" style={{ marginBottom: 20 }}>
                    <div className="section-title">
                        Top Entities
                        <span className="title-line" />
                    </div>
                    <div className="intel-entity-tags">
                        {stats.top_entities.map((ent, i) => (
                            <span className="entity-tag" key={i}>
                                {ent.name} <span style={{ opacity: 0.5, marginLeft: 4, fontSize: 10 }}>×{ent.count}</span>
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Recent Intelligence */}
            <div className="card" style={{ marginBottom: 20 }}>
                <div className="section-title">
                    Recent Intelligence
                    <span className="title-line" />
                    <Link to="/intelligence" className="btn btn-secondary" style={{ fontSize: 11, padding: '5px 12px' }}>
                        View All
                    </Link>
                </div>

                {loading ? (
                    <div className="empty-state" style={{ padding: 40 }}>
                        <div className="loading-spinner" />
                    </div>
                ) : stats.recent_intel && stats.recent_intel.length > 0 ? (
                    <div className="recent-intel-grid">
                        {stats.recent_intel.map((item, i) => (
                            <div className="recent-intel-mini" key={i}>
                                <div className="rim-header">
                                    <span className={`badge ${item.domain}`}>{item.domain}</span>
                                </div>
                                <h4 className="rim-title">{item.event_title}</h4>
                                <p className="rim-summary">{item.summary}</p>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-state" style={{ padding: 30 }}>
                        <div className="empty-icon">🧠</div>
                        <h3>No intelligence yet</h3>
                        <p>Process sources from the <Link to="/intelligence" style={{ color: 'var(--accent-cyan)' }}>Intelligence Feed</Link> to populate this section</p>
                    </div>
                )}
            </div>

            <div className="card">
                <div className="section-title">
                    Recent Activity
                    <span className="title-line" />
                </div>

                {loading ? (
                    <div className="empty-state">
                        <div className="loading-spinner" />
                    </div>
                ) : activities.length > 0 ? (
                    <div className="activity-feed">
                        {activities.map((item, i) => (
                            <div className="activity-item" key={i}>
                                <span className={`activity-dot ${['green', 'blue', 'amber'][i % 3]}`} />
                                <div className="activity-info">
                                    <div className="activity-text">
                                        Processed: <strong>{item.source_url || 'Unknown source'}</strong>
                                        {item.domain && <span className={`badge ${item.domain}`} style={{ marginLeft: 8 }}>{item.domain}</span>}
                                    </div>
                                    <div className="activity-time">{formatTime(item.fetched_at)}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <div className="empty-icon">📡</div>
                        <h3>No recent activity</h3>
                        <p>Add sources in the Source Registry to start monitoring</p>
                    </div>
                )}
            </div>
        </div>
    );
}

