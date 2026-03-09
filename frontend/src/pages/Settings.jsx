import { useState } from 'react';
import { HiOutlineCog, HiOutlineKey, HiOutlineClock, HiOutlineShieldCheck } from 'react-icons/hi';

export default function Settings() {
    const [defaults, setDefaults] = useState({
        frequency: '1hour',
        trust_score: 5,
        auto_scrape: true,
        notifications: true,
    });

    return (
        <div>
            <div className="page-header">
                <h1>Settings</h1>
                <p>Configure system preferences and API connections</p>
            </div>

            {/* Default Preferences */}
            <div className="card settings-section">
                <div className="section-title">
                    <HiOutlineClock /> Default Preferences
                </div>
                <div className="settings-item">
                    <div>
                        <div className="si-label">Default Update Frequency</div>
                        <div className="si-desc">Applied to new sources by default</div>
                    </div>
                    <select
                        className="form-select"
                        style={{ width: '180px' }}
                        value={defaults.frequency}
                        onChange={(e) => setDefaults({ ...defaults, frequency: e.target.value })}
                    >
                        <option value="15min">Every 15 min</option>
                        <option value="30min">Every 30 min</option>
                        <option value="1hour">Every 1 hour</option>
                        <option value="daily">Daily</option>
                    </select>
                </div>
                <div className="settings-item">
                    <div>
                        <div className="si-label">Default Trust Score</div>
                        <div className="si-desc">Initial trust level for new sources</div>
                    </div>
                    <div className="trust-score-slider" style={{ width: '200px' }}>
                        <input
                            type="range"
                            min="1"
                            max="10"
                            value={defaults.trust_score}
                            onChange={(e) => setDefaults({ ...defaults, trust_score: parseInt(e.target.value) })}
                        />
                        <span className="trust-score-value">{defaults.trust_score}</span>
                    </div>
                </div>
            </div>

            {/* System */}
            <div className="card settings-section">
                <div className="section-title">
                    <HiOutlineShieldCheck /> System
                </div>
                <div className="settings-item">
                    <div>
                        <div className="si-label">Auto-Scrape on Source Add</div>
                        <div className="si-desc">Immediately scrape new sources when added</div>
                    </div>
                    <label style={{ position: 'relative', display: 'inline-block', width: 44, height: 24 }}>
                        <input
                            type="checkbox"
                            checked={defaults.auto_scrape}
                            onChange={(e) => setDefaults({ ...defaults, auto_scrape: e.target.checked })}
                            style={{ opacity: 0, width: 0, height: 0 }}
                        />
                        <span style={{
                            position: 'absolute', cursor: 'pointer', inset: 0, borderRadius: 12,
                            background: defaults.auto_scrape ? 'var(--accent-primary)' : 'var(--bg-tertiary)',
                            transition: 'background 0.2s',
                        }}>
                            <span style={{
                                position: 'absolute', height: 18, width: 18, left: defaults.auto_scrape ? 22 : 3, bottom: 3,
                                background: 'white', borderRadius: '50%', transition: 'left 0.2s',
                            }} />
                        </span>
                    </label>
                </div>
                <div className="settings-item">
                    <div>
                        <div className="si-label">System Notifications</div>
                        <div className="si-desc">Show alerts for errors and completed scrapes</div>
                    </div>
                    <label style={{ position: 'relative', display: 'inline-block', width: 44, height: 24 }}>
                        <input
                            type="checkbox"
                            checked={defaults.notifications}
                            onChange={(e) => setDefaults({ ...defaults, notifications: e.target.checked })}
                            style={{ opacity: 0, width: 0, height: 0 }}
                        />
                        <span style={{
                            position: 'absolute', cursor: 'pointer', inset: 0, borderRadius: 12,
                            background: defaults.notifications ? 'var(--accent-primary)' : 'var(--bg-tertiary)',
                            transition: 'background 0.2s',
                        }}>
                            <span style={{
                                position: 'absolute', height: 18, width: 18, left: defaults.notifications ? 22 : 3, bottom: 3,
                                background: 'white', borderRadius: '50%', transition: 'left 0.2s',
                            }} />
                        </span>
                    </label>
                </div>
            </div>
        </div>
    );
}
