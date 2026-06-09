import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Center, useGLTF } from "@react-three/drei";

export default function TelloModel() {
  const groupRef = useRef();
  const { scene } = useGLTF("/assets/models/tello/scene.gltf");

  useFrame((state, delta) => {
    if (!groupRef.current) return;

    groupRef.current.position.y =
      Math.sin(state.clock.elapsedTime * 0.8) * 0.08;

    groupRef.current.rotation.y += delta * 0.05;
  });

  return (
    <group ref={groupRef}>
      <Center>
        <primitive
          object={scene}
          scale={0.7}
          rotation={[0.08, -0.4, 0]}
        />
      </Center>
    </group>
  );
}

useGLTF.preload("/assets/models/tello/scene.gltf");