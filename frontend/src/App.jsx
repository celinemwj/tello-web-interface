import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import WelcomePage from "./pages/WelcomePage";


function TemporaryPage({ title }) {
  return (
    <div style={{ padding: 40 }}>
      <h1>{title}</h1>
      <p>This page will be implemented later.</p>
    </div>
  );
}


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WelcomePage />} />

        <Route
          path="/command"
          element={<TemporaryPage title="AI Command" />}
        />

        <Route
          path="/monitoring"
          element={<TemporaryPage title="Monitoring" />}
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}