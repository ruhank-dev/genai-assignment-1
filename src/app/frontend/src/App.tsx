import { Navigate, Route, Routes } from "react-router-dom";
import Shell from "./components/layout/Shell";
import FaceToSketch from "./pages/FaceToSketch";
import HardRoutedRestoration from "./pages/HardRoutedRestoration";
import SoftMoERestoration from "./pages/SoftMoERestoration";
import UniversalRestoration from "./pages/UniversalRestoration";

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<Navigate to="/universal" replace />} />
        <Route path="/universal" element={<UniversalRestoration />} />
        <Route path="/hard-routed" element={<HardRoutedRestoration />} />
        <Route path="/soft-moe" element={<SoftMoERestoration />} />
        <Route path="/face-to-sketch" element={<FaceToSketch />} />
        <Route path="*" element={<Navigate to="/universal" replace />} />
      </Routes>
    </Shell>
  );
}
