import { Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Models from './pages/Models';
import Safety from './pages/Safety';
import Governance from './pages/Governance';
import Memory from './pages/Memory';
import Settings from './pages/Settings';

function Layout({ children }) {
  const linkClass = ({ isActive }) =>
    `px-3 py-2 rounded text-sm font-medium ${isActive ? 'bg-indigo-700 text-white' : 'text-indigo-200 hover:bg-indigo-600'}`;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#e2e8f0' }}>
      <nav style={{ backgroundColor: '#1e293b', borderBottom: '1px solid #334155', padding: '0 24px', display: 'flex', alignItems: 'center', height: 56 }}>
        <div style={{ fontWeight: 'bold', fontSize: 18, color: '#818cf8', marginRight: 32 }}>TurboPrivate AI</div>
        <div style={{ display: 'flex', gap: 8 }}>
          <NavLink to="/" end className={linkClass}>Dashboard</NavLink>
          <NavLink to="/models" className={linkClass}>Models</NavLink>
          <NavLink to="/safety" className={linkClass}>Safety</NavLink>
          <NavLink to="/governance" className={linkClass}>Governance</NavLink>
          <NavLink to="/memory" className={linkClass}>Memory</NavLink>
          <NavLink to="/settings" className={linkClass}>Settings</NavLink>
        </div>
      </nav>
      <main style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/models" element={<Models />} />
        <Route path="/safety" element={<Safety />} />
        <Route path="/governance" element={<Governance />} />
        <Route path="/memory" element={<Memory />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}
