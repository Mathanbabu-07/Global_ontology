import { useState, useEffect } from 'react';
import { HiOutlineRefresh } from 'react-icons/hi';

const MOCK_LOGS = [
    { time: '19:28:05', level: 'info', msg: 'Scheduler started — checking active sources' },
    { time: '19:28:06', level: 'success', msg: 'Connected to Supabase instance' },
    { time: '19:28:08', level: 'info', msg: 'Jina AI reader initialized' },
    { time: '19:28:10', level: 'success', msg: 'OpenRouter API connection verified' },
    { time: '19:27:55', level: 'info', msg: 'Crawling https://reuters.com/world — response 200' },
    { time: '19:27:58', level: 'success', msg: 'Extracted 3 entities from reuters.com content' },
    { time: '19:27:30', level: 'warn', msg: 'Rate limit approaching for Jina API — 85% used' },
    { time: '19:27:00', level: 'info', msg: 'Source registry updated — 12 active, 3 paused' },
    { time: '19:26:45', level: 'error', msg: 'Failed to scrape https://blocked-site.com — 403 Forbidden' },
    { time: '19:26:30', level: 'success', msg: 'AI analysis complete — 5 events extracted from 3 sources' },
    { time: '19:26:00', level: 'info', msg: 'Background scheduler cycle completed in 18.2s' },
    { time: '19:25:30', level: 'info', msg: 'Dashboard stats cache refreshed' },
];

export default function SystemLogs() {
    const [logs, setLogs] = useState(MOCK_LOGS);

    const refreshLogs = () => {
        const now = new Date();
        const dateStr = now.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const newLog = {
            time: `${dateStr} ${timeStr}`,
            level: 'info',
            msg: 'Log view refreshed by user',
        };
        setLogs([newLog, ...logs]);
    };

    return (
        <div>
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1>System Logs</h1>
                    <p>Monitor engine activity and system events</p>
                </div>
                <button className="btn btn-secondary" onClick={refreshLogs}>
                    <HiOutlineRefresh /> Refresh
                </button>
            </div>

            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border-primary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px' }}>
                        Engine Logs
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        {logs.length} entries
                    </span>
                </div>
                {logs.map((log, i) => (
                    <div className="log-entry" key={i}>
                        <span className="log-time">{log.time}</span>
                        <span className={`log-level ${log.level}`}>{log.level}</span>
                        <span className="log-msg">{log.msg}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
