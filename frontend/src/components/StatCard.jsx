export default function StatCard({ icon, value, label, change, changeType, colorClass }) {
    return (
        <div className="stat-card">
            <div className={`stat-icon ${colorClass || 'purple'}`}>
                {icon}
            </div>
            <div className="stat-info">
                <span className="stat-value">{value}</span>
                <span className="stat-label">{label}</span>
                {change && (
                    <span className={`stat-change ${changeType || 'up'}`}>
                        {changeType === 'up' ? '↑' : '↓'} {change}
                    </span>
                )}
            </div>
        </div>
    );
}
