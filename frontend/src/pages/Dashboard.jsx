import { useState, useEffect } from 'react';
import { getHealth, getDashboard } from '../api';

const card = { backgroundColor: '#1e293b', borderRadius: 8, padding: 20, border: '1px solid #334155' };
const stat = { fontSize: 32, fontWeight: 'bold', color: '#818cf8' };
const label = { fontSize: 14, color: '#94a3b8', marginTop: 4 };

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ status: 'unknown' }));
    getDashboard().then(setMetrics).catch((err) => setError(err.message));
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 24 }}>Dashboard</h1>
      {error && (
        <div style={{ ...card, marginBottom: 16, borderColor: '#f87171' }}>
          <p style={{ color: '#f87171' }}>Could not load metrics: {error}</p>
        </div>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 24 }}>
        <div style={card}>
          <div style={stat}>{metrics?.requests ?? 0}</div>
          <div style={label}>Total Requests</div>
        </div>
        <div style={card}>
          <div style={stat}>{metrics?.tokens ?? 0}</div>
          <div style={label}>Tokens Generated</div>
        </div>
        <div style={card}>
          <div style={stat}>{metrics?.latency_p50 != null ? `${metrics.latency_p50}ms` : '-'}</div>
          <div style={label}>P50 Latency</div>
        </div>
        <div style={card}>
          <div style={stat}>{metrics?.latency_p99 != null ? `${metrics.latency_p99}ms` : '-'}</div>
          <div style={label}>P99 Latency</div>
        </div>
        <div style={card}>
          <div style={{ ...stat, color: health?.status === 'ok' ? '#34d399' : '#f87171' }}>
            {health?.status ?? '?'}
          </div>
          <div style={label}>API Health</div>
        </div>
      </div>
      <div style={{ ...card, marginBottom: 16 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Model Performance</h2>
        {metrics?.models && metrics.models.length > 0 ? (
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {metrics.models.map((m, i) => (
              <div key={i} style={{ padding: 12, backgroundColor: '#0f172a', borderRadius: 6, minWidth: 150 }}>
                <div style={{ fontSize: 14, fontWeight: 600 }}>{m.name}</div>
                <div style={{ fontSize: 12, color: '#94a3b8' }}>{m.requests} req / {m.latency}ms</div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#64748b' }}>No data yet. Start serving a model to see metrics.</p>
        )}
      </div>
    </div>
  );
}
