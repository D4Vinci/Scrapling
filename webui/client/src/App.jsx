import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import NewJob from "./pages/NewJob.jsx";
import History from "./pages/History.jsx";
import JobDetail from "./pages/JobDetail.jsx";
import McpManager from "./pages/McpManager.jsx";

export default function App() {
  return (
    <div className="app">
      <nav className="nav">
        <span className="brand">
          <span className="brand-dot" />
          Scrapling
        </span>
        <div className="nav-links">
          <NavLink to="/" end>
            New job
          </NavLink>
          <NavLink to="/history">History</NavLink>
          <NavLink to="/mcp">MCP server</NavLink>
        </div>
      </nav>
      <main className="content">
        <Routes>
          <Route path="/" element={<NewJob />} />
          <Route path="/history" element={<History />} />
          <Route path="/jobs/:id" element={<JobDetail />} />
          <Route path="/mcp" element={<McpManager />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
