import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import Dashboard from './pages/Dashboard';
import SourceRegistry from './pages/SourceRegistry';
import DataMonitor from './pages/DataMonitor';
import IntelligenceFeed from './pages/IntelligenceFeed';
import AIQueryConsole from './pages/AIQueryConsole';
import SystemLogs from './pages/SystemLogs';
import KnowledgeGraph from './pages/KnowledgeGraph';
import Settings from './pages/Settings';
import './index.css';

export default function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <div className="main-wrapper">
          <TopNav />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/sources" element={<SourceRegistry />} />
              <Route path="/monitor" element={<DataMonitor />} />
              <Route path="/intelligence" element={<IntelligenceFeed />} />
              <Route path="/query" element={<AIQueryConsole />} />
              <Route path="/logs" element={<SystemLogs />} />
              <Route path="/graph" element={<KnowledgeGraph />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

