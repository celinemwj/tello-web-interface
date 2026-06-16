import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import WelcomePage from "./pages/WelcomePage.jsx";
import CommandPage from "./pages/CommandPage.jsx";
import MonitoringPage from "./pages/MonitoringPage.jsx";

import { PipelineProvider } from "./context/PipelineContext.jsx";


export default function App() {
  return (
    <PipelineProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<WelcomePage />} />

          <Route
            path="/command"
            element={<CommandPage />}
          />

          <Route
            path="/monitoring"
            element={<MonitoringPage />}
          />

          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />
        </Routes>
      </BrowserRouter>
    </PipelineProvider>
  );
}