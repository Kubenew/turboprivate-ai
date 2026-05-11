import { useState, useEffect } from 'react';
import { getModels, pullModel, quantizeModel } from '../api';

const card = { backgroundColor: '#1e293b', borderRadius: 8, padding: 20, border: '1px solid #334155', marginBottom: 16 };
const btn = { backgroundColor: '#6366f1', color: 'white', border: 'none', borderRadius: 6, padding: '8px 16px', cursor: 'pointer', fontSize: 14, fontWeight: 500 };
const input = { backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 6, padding: '8px 12px', color: '#e2e8f0', fontSize: 14, width: '100%', boxSizing: 'border-box' };

export default function Models() {
  const [models, setModels] = useState([]);
  const [modelName, setModelName] = useState('');
  const [status, setStatus] = useState('');

  const refresh = () => getModels().then(d => setModels(d.models || [])).catch(() => {});

  useEffect(() => { refresh(); }, []);

  const doPull = async () => {
    if (!modelName.trim()) return;
    setStatus(`Pulling ${modelName}...`);
    try {
      const result = await pullModel(modelName);
      setStatus(result.message || `Pulled ${modelName}`);
      setModelName('');
      refresh();
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    }
  };

  const doQuantize = async (name) => {
    setStatus(`Quantizing ${name}...`);
    try {
      const result = await quantizeModel(name);
      setStatus(`Quantized ${name} → ${result.output_path}`);
      refresh();
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 24 }}>Models</h1>
      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Pull New Model</h2>
        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1 }}>
            <input style={input} placeholder="e.g. meta-llama/Llama-3-8B" value={modelName} onChange={e => setModelName(e.target.value)} onKeyDown={e => e.key === 'Enter' && doPull()} />
          </div>
          <button style={btn} onClick={doPull}>Pull</button>
        </div>
        {status && <p style={{ marginTop: 8, fontSize: 13, color: '#94a3b8' }}>{status}</p>}
      </div>
      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Installed Models</h2>
        {models.length === 0 ? (
          <p style={{ color: '#64748b' }}>No models installed. Pull a model to get started.</p>
        ) : (
          <div style={{ display: 'grid', gap: 8 }}>
            {models.map(m => (
              <div key={m} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 12, backgroundColor: '#0f172a', borderRadius: 6 }}>
                <span>{m}</span>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button style={btn} onClick={() => alert(`Serving ${m}...`)}>Serve</button>
                  <button style={{ ...btn, backgroundColor: '#f59e0b' }} onClick={() => doQuantize(m)}>Quantize</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
