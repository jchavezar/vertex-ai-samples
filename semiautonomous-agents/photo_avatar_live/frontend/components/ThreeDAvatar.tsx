/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */
import { useEffect, useRef, useState, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { useGLTF, OrbitControls, Center } from '@react-three/drei';
import * as THREE from 'three';
import { useLiveAPIContext } from '../contexts/LiveAPIContext';

const AVATAR_URL = 'https://readyplayerme.github.io/visage/male.glb';

function Avatar({ url, volumeRef }: { url: string; volumeRef: React.MutableRefObject<number> }) {
  const { scene } = useGLTF(url);
  const meshesRef = useRef<THREE.Mesh[]>([]);

  useEffect(() => {
    const meshes: THREE.Mesh[] = [];
    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh && (child as THREE.Mesh).morphTargetDictionary) {
        // Ready Player Me has morph targets on Head, Teeth, Eyeballs, etc.
        // We want to animate all of them if they have the target blendshape
        meshes.push(child as THREE.Mesh);
      }
    });
    meshesRef.current = meshes;
    console.log("Found meshes with morph targets:", meshes.map(m => m.name));
  }, [scene]);

  useFrame(() => {
    const volume = volumeRef.current;
    // Map volume (0-1) to jawOpen influence (0-1)
    // Scale volume to make mouth open more easily
    const targetJawOpen = Math.min(volume * 3.0, 1.0);

    meshesRef.current.forEach((mesh) => {
      if (mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
        const dict = mesh.morphTargetDictionary;
        const influences = mesh.morphTargetInfluences;

        // Try different common blendshape names for jaw open
        const jawOpenIdx = dict['jawOpen'] ?? dict['viseme_aa'] ?? dict['mouth_open'];
        
        if (jawOpenIdx !== undefined) {
          // Lerp for smoother animation
          influences[jawOpenIdx] = THREE.MathUtils.lerp(influences[jawOpenIdx], targetJawOpen, 0.3);
        }

        // Simple random blinking
        const blinkLeftIdx = dict['eyeBlinkLeft'] ?? dict['blink_left'];
        const blinkRightIdx = dict['eyeBlinkRight'] ?? dict['blink_right'];
        
        // We can add blink logic here if needed, but keeping it simple for now
      }
    });
  });

  return <primitive object={scene} />;
}

// Preload the model
useGLTF.preload(AVATAR_URL);

export default function ThreeDAvatar() {
  const { volume, connected } = useLiveAPIContext();
  const volRef = useRef(0);

  useEffect(() => {
    volRef.current = volume;
  }, [volume]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', background: '#0c0d12' }}>
      <Suspense fallback={
        <div style={{
          width: '100%', height: '100%',
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          color: 'rgba(255,255,255,0.7)',
          fontFamily: 'sans-serif'
        }}>
          <div style={{ fontSize: 24, marginBottom: 10 }}>Loading 3D Avatar...</div>
          <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.4)' }}>Ready Player Me Integration</div>
        </div>
      }>
        <Canvas
          camera={{ position: [0, 0, 0.5], fov: 45 }}
          style={{ width: '100%', height: '100%' }}
        >
          <ambientLight intensity={1.5} />
          <directionalLight position={[1, 2, 3]} intensity={1.5} />
          <directionalLight position={[-1, 2, -3]} intensity={0.5} />
          <pointLight position={[0, 1, 1]} intensity={0.8} />
          
          <Center position={[0, -0.6, 0]}>
            <Avatar url={AVATAR_URL} volumeRef={volRef} />
          </Center>
          
          <OrbitControls 
            enablePan={false}
            enableZoom={true}
            minDistance={0.2}
            maxDistance={2}
            target={[0, 0, 0]}
          />
        </Canvas>
      </Suspense>

      {/* Waiting overlay when not connected */}
      {!connected && (
        <div style={{
          position: 'absolute', bottom: '15%', left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)',
          padding: '10px 22px', borderRadius: 20, color: 'white',
          fontSize: 13, fontWeight: 500, border: '1px solid rgba(255,255,255,0.15)',
          pointerEvents: 'none', whiteSpace: 'nowrap',
          zIndex: 10
        }}>
          Press ▶ to start talking
        </div>
      )}
    </div>
  );
}
