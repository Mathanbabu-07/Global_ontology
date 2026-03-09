import { useLocation } from 'react-router-dom';
import { HiOutlineBell, HiOutlineSearch } from 'react-icons/hi';

const pageTitles = {
    '/': 'Dashboard',
    '/sources': 'Source Registry',
    '/monitor': 'Data Monitor',
    '/query': 'AI Query Console',
    '/logs': 'System Logs',
    '/settings': 'Settings',
};

export default function TopNav() {
    const location = useLocation();
    const title = pageTitles[location.pathname] || 'Dashboard';

    return (
        <header className="topnav">
            <div className="topnav-left">
                <h2 className="topnav-title">{title}</h2>
                <span className="topnav-breadcrumb">/ Global Ontology Engine</span>
            </div>

            <div className="topnav-right">
                <div className="topnav-status">
                    <span className="status-dot" />
                    <span>All Systems Active</span>
                </div>

                <button className="topnav-icon-btn" title="Search">
                    <HiOutlineSearch />
                </button>
                <button className="topnav-icon-btn" title="Notifications">
                    <HiOutlineBell />
                </button>

                <div className="topnav-avatar" title="User">OP</div>
            </div>
        </header>
    );
}
