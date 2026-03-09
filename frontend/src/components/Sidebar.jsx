import { NavLink } from 'react-router-dom';
import {
    HiOutlineViewGrid,
    HiOutlineCollection,
    HiOutlineStatusOnline,
    HiOutlineLightningBolt,
    HiOutlineChatAlt2,
    HiOutlineDocumentText,
    HiOutlineCog,
    HiOutlineShare
} from 'react-icons/hi';
import logoUrl from '../assets/logo.png';

const navItems = [
    { path: '/', icon: <HiOutlineViewGrid />, label: 'Dashboard' },
    { path: '/sources', icon: <HiOutlineCollection />, label: 'Source Registry', badge: null },
    { path: '/monitor', icon: <HiOutlineStatusOnline />, label: 'Data Monitor' },
    { path: '/intelligence', icon: <HiOutlineLightningBolt />, label: 'Intelligence Feed' },
    { path: '/query', icon: <HiOutlineChatAlt2 />, label: 'AI Query Console' },
    { path: '/logs', icon: <HiOutlineDocumentText />, label: 'System Logs' },
    { path: '/graph', icon: <HiOutlineShare />, label: 'Knowledge Graph' },
    { path: '/settings', icon: <HiOutlineCog />, label: 'Settings' },
];

export default function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="logo-icon spinning-logo-container">
                    <img src={logoUrl} alt="Logo" className="spinning-logo" style={{ width: '100%', height: '100%', borderRadius: '10px', objectFit: 'cover' }} />
                </div>
                <div className="logo-text">
                    <span className="logo-title">Global Ontology</span>
                    <span className="logo-subtitle">Intelligence Engine</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                <span className="sidebar-section-label">Navigation</span>
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        end={item.path === '/'}
                        className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span>{item.label}</span>
                        {item.badge && <span className="nav-badge">{item.badge}</span>}
                    </NavLink>
                ))}
            </nav>

            <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-primary)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                        width: '8px', height: '8px', borderRadius: '50%',
                        background: 'var(--accent-emerald)',
                        boxShadow: '0 0 8px rgba(16,185,129,0.5)',
                    }} />
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>System Online</span>
                </div>
            </div>
        </aside>
    );
}
