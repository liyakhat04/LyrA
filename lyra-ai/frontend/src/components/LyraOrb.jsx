import { OrbitControls, Points, PointMaterial } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const stateProfile = {
  idle: { scale: 1, glow: "#72a8ff", speed: 0.4 },
  listening: { scale: 1.12, glow: "#67e8f9", speed: 1.2 },
  thinking: { scale: 1.05, glow: "#a78bfa", speed: 1.8 },
  speaking: { scale: 1.15, glow: "#22d3ee", speed: 2.3 },
  error: { scale: 0.95, glow: "#f43f5e", speed: 3.5 }
};

function CoreSphere({ state }) {
  const meshRef = useRef();
  const profile = stateProfile[state] || stateProfile.idle;

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const pulse = 1 + Math.sin(t * profile.speed) * 0.04;
    meshRef.current.scale.setScalar(profile.scale * pulse);
    meshRef.current.rotation.y += 0.005 * profile.speed;
    meshRef.current.rotation.x += 0.002 * profile.speed;
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 64, 64]} />
      <meshPhysicalMaterial color={profile.glow} roughness={0.1} transmission={0.6} thickness={1.3} />
    </mesh>
  );
}

function EnergyField({ state }) {
  const points = useMemo(() => {
    const arr = new Float32Array(1200);
    for (let i = 0; i < arr.length; i++) arr[i] = THREE.MathUtils.randFloatSpread(8);
    return arr;
  }, []);
  const ref = useRef();
  useFrame(() => {
    if (!ref.current) return;
    ref.current.rotation.y += state === "thinking" ? 0.01 : 0.003;
  });

  return (
    <Points ref={ref} positions={points} stride={3}>
      <PointMaterial transparent color="#67e8f9" size={0.03} sizeAttenuation depthWrite={false} />
    </Points>
  );
}

export default function LyraOrb({ state }) {
  return (
    <Canvas camera={{ position: [0, 0, 4.5], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[3, 3, 3]} intensity={2.2} />
      <CoreSphere state={state} />
      <EnergyField state={state} />
      <OrbitControls enablePan={false} enableZoom={false} />
    </Canvas>
  );
}
