import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import {
  Bounds,
  Environment,
  OrbitControls,
} from "@react-three/drei";

import TelloModel from "./TelloModel";

export default function DroneScene() {
  return (
    <Canvas
      camera={{
        position: [0, 1, 5],
        fov: 45,
      }}
      style={{
        width: "100%",
        height: "100%",
        background: "transparent",
      }}
    >
      <ambientLight intensity={2} />
      <directionalLight position={[5, 5, 5]} intensity={3} />

      <Suspense fallback={null}>
        <Bounds fit clip observe margin={1.5}>
          <TelloModel />
        </Bounds>

        <Environment preset="city" />
      </Suspense>

      <OrbitControls
        enablePan={false}
        enableZoom
      />
    </Canvas>
  );
}