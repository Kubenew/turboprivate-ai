import { useState } from 'react';

const card = { backgroundColor: '#1e293b', borderRadius: 8, padding: 20, border: '1px solid #334155', marginBottom: 16 };
const input = { backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 6, padding: '8px 12px', color: '#e2e8f0', fontSize: 14, width: '100%', boxSizing: 'border-box', marginBottom: 12 };
const label = { display: 'block', fontSize: 14, color: '#94a3b8', marginBottom: 4 };
const btn = { backgroundColor: '#6366f1', color: 'white', border: 'none', borderRadius: 6, padding: '8px 16px', cursor: 'pointer', fontSize: 14, fontWeight: 500 };
const toggle = (on) => ({
  width: 44, height: 24, borderRadius: 12, cursor: 'pointer', border: 'none',
  backgroundColor: on ? '#6366f1' : '#475569', position: 'relative', transition: '0.2s',
});

export default function Settings() {
  const [config, setConfig] = useState({
    inference_backend: 'auto',
    gpu_type: 'auto',
    safety_enabled: true,
    pre_flight: true,
    post_flight: true,
    memory_enabled: true,
    auth_provider: 'jwt',
    cluster_name: 'turbo-cluster',
    provider: 'bare-metal',
  });

  const update = (key, value) => setConfig(prev => ({ ...prev, [key]: value }));

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 24 }}>Settings</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 16 }}>
        <div style={card}>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Inference</h2>
          <label style={label}>Backend</label>
          <select style={input} value={config.inference_backend} onChange={e => update('inference_backend', e.target.value)}>
            <option value="auto">Auto-detect</option>
            <option value="vllm">vLLM (GPU)</option>
            <option value="llamacpp">llama.cpp (CPU)</option>
          </select>
          <label style={label}>GPU Type</label>
          <select style={input} value={config.gpu_type} onChange={e => update('gpu_type', e.target.value)}>
            <option value="auto">Auto</option>
            <option value="consumer">Consumer (RTX 3090/4090)</option>
            <option value="cloud">Cloud (A100/H100)</option>
            <option value="cpu">CPU only</option>
          </select>
        </div>
        <div style={card}>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Safety</h2>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span>Safety Gates</span>
            <button style={toggle(config.safety_enabled)} onClick={() => update('safety_enabled', !config.safety_enabled)}>
              <div style={{ width: 20, height: 20, borderRadius: 10, backgroundColor: 'white', position: 'absolute', top: 2, left: config.safety_enabled ? 22 : 2, transition: '0.2s' }} />
            </button>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span>Pre-Flight</span>
            <button style={toggle(config.pre_flight)} onClick={() => update('pre_flight', !config.pre_flight)}>
              <div style={{ width: 20, height: 20, borderRadius: 10, backgroundColor: 'white', position: 'absolute', top: 2, left: config.pre_flight ? 22 : 2, transition: '0.2s' }} />
            </button>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Post-Flight</span>
            <button style={toggle(config.post_flight)} onClick={() => update('post_flight', !config.post_flight)}>
              <div style={{ width: 20, height: 20, borderRadius: 10, backgroundColor: 'white', position: 'absolute', top: 2, left: config.post_flight ? 22 : 2, transition: '0.2s' }} />
            </button>
          </div>
        </div>
        <div style={card}>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Infrastructure</h2>
          <label style={label}>Cluster Name</label>
          <input style={input} value={config.cluster_name} onChange={e => update('cluster_name', e.target.value)} />
          <label style={label}>Provider</label>
          <select style={input} value={config.provider} onChange={e => update('provider', e.target.value)}>
            <option value="bare-metal">Bare Metal</option>
            <option value="proxmox">Proxmox</option>
            <option value="morpheus">Morpheus</option>
          </select>
        </div>
      </div>
      <div style={{ marginTop: 24 }}>
        <button style={{ ...btn, padding: '12px 32px', fontSize: 16 }} onClick={() => alert('Configuration saved!')}>Save Configuration</button>
      </div>
    </div>
  );
}
