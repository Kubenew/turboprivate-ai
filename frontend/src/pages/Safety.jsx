import { useState, useEffect } from 'react';
import { getSafetyStatus, safetyCheck, getAuditLog } from '../api';

const card = { backgroundColor: '#1e293b', borderRadius: 8, padding: 20, border: '1px solid #334155', marginBottom: 16 };
const badge = (active) => ({
  display: 'inline-block', padding: '4px 12px', borderRadius: 12, fontSize: 12, fontWeight: 600,
  backgroundColor: active ? '#065f46' : '#7f1d1d', color: active ? '#6ee7b7' : '#fca5a5',
});
const input = { backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 6, padding: '8px 12px', color: '#e2e8f0', fontSize: 14, width: '100%', boxSizing: 'border-box' };
const btn = { backgroundColor: '#6366f1', color: 'white', border: 'none', borderRadius: 6, padding: '8px 16px', cursor: 'pointer', fontSize: 14, fontWeight: 500 };
const textarea = { ...input, minHeight: 80, resize: 'vertical', fontFamily: 'inherit' };

export default function Safety() {
  const [status, setStatus] = useState(null);
  const [testPrompt, setTestPrompt] = useState('');
  const [testResponse, setTestResponse] = useState('');
  const [checkResult, setCheckResult] = useState(null);
  const [auditStats, setAuditStats] = useState(null);

  useEffect(() => {
    getSafetyStatus().then(setStatus).catch(() => {});
    getAuditLog().then(d => setAuditStats(d.stats || {})).catch(() => {});
  }, []);

  const runCheck = async () => {
    if (!testPrompt && !testResponse) return;
    try {
      const result = await safetyCheck(testPrompt, testResponse);
      setCheckResult(result);
    } catch (err) {
      setCheckResult({ error: err.message });
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 24 }}>Safety</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 24 }}>
        <div style={card}>
          <div style={{ fontSize: 14, color: '#94a3b8' }}>Pre-Flight Verifiers</div>
          <div style={{ marginTop: 8, fontSize: 28, fontWeight: 'bold', color: '#818cf8' }}>{status?.pre_flight_count ?? 0}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: 14, color: '#94a3b8' }}>Post-Flight Verifiers</div>
          <div style={{ marginTop: 8, fontSize: 28, fontWeight: 'bold', color: '#818cf8' }}>{status?.post_flight_count ?? 0}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: 14, color: '#94a3b8' }}>Audit Total</div>
          <div style={{ marginTop: 8, fontSize: 28, fontWeight: 'bold', color: '#818cf8' }}>{auditStats?.total_entries ?? 0}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: 14, color: '#94a3b8' }}>Block Rate</div>
          <div style={{ marginTop: 8, fontSize: 28, fontWeight: 'bold', color: '#f87171' }}>{auditStats?.block_rate != null ? `${(auditStats.block_rate * 100).toFixed(1)}%` : '-'}</div>
        </div>
      </div>
      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Active Verifiers</h2>
        {status?.pre_flight ? (
          <div>
            <div style={{ fontSize: 14, color: '#94a3b8', marginBottom: 8 }}>Pre-Flight</div>
            {status.pre_flight.map(v => (
              <div key={v} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#0f172a', borderRadius: 6, marginBottom: 4 }}>
                <span>{v}</span><span style={{ color: '#34d399' }}>Active</span>
              </div>
            ))}
          </div>
        ) : null}
        {status?.post_flight ? (
          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 14, color: '#94a3b8', marginBottom: 8 }}>Post-Flight</div>
            {status.post_flight.map(v => (
              <div key={v} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#0f172a', borderRadius: 6, marginBottom: 4 }}>
                <span>{v}</span><span style={{ color: '#34d399' }}>Active</span>
              </div>
            ))}
          </div>
        ) : null}
      </div>
      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Test Safety Check</h2>
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 4 }}>Prompt</div>
          <textarea style={textarea} placeholder="Enter a prompt to test..." value={testPrompt} onChange={e => setTestPrompt(e.target.value)} />
        </div>
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 4 }}>Response (optional)</div>
          <textarea style={textarea} placeholder="Enter a response to test..." value={testResponse} onChange={e => setTestResponse(e.target.value)} />
        </div>
        <button style={btn} onClick={runCheck}>Run Check</button>
        {checkResult && (
          <div style={{ marginTop: 12, padding: 12, backgroundColor: '#0f172a', borderRadius: 6 }}>
            <pre style={{ fontSize: 12, color: '#94a3b8', whiteSpace: 'pre-wrap' }}>{JSON.stringify(checkResult, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
