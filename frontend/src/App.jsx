import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import ReportPage from './pages/ReportPage';
import DiffPage from './pages/DiffPage';
import './index.css';

function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand">
        <div>
          <div className="logo">⟁ ZeroGate</div>
          <div className="subtitle">Autonomous Security Graph</div>
        </div>
      </NavLink>
      <div className="navbar-links">
        <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''} end>
          Upload
        </NavLink>
        <NavLink to="/report" className={({ isActive }) => isActive ? 'active' : ''}>
          Report
        </NavLink>
      </div>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/report/:projectId" element={<ReportPage />} />
        <Route path="/diff/:projectId/:findingId" element={<DiffPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
