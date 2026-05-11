import { useState, useEffect } from 'react';
import { getAuditLog, getApprovals, approveRequest } from '../api';

const card = { backgroundColor: '#1e293b', borderRadius: 8, padding: 20, border: '1px solid #334155', marginBottom: 16 };
const btn = { backgroundColor: '#6366f1', color: 'white', border: 'none', borderRadius: 6, padding: '6px 14px', cursor: 'pointer', fontSize: 13, fontWeight: 500 };

export default function Governance() {
  const [approvals, setApprovals] = useState([]);
  const [auditEntries, setAuditEntries] = useState([]);
  const [auditStats, setAuditStats] = useState(null);
  const [error, setError] = useState(null);

  const refresh = () => {
    getApprovals().then(d => setApprovals(d.pending || [])).catch(() => {});
    getAuditLog().then(d => {
      setAuditEntries(d.entries || []);
      setAuditStats(d.stats || null);
    }).catch((err) => setError(err.message));
  };

  useEffect(() => { refresh(); }, []);

  const doApprove = async (id) => {
    try {
      await approveRequest(id);
      refresh();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 24 }}>Governance</h1>
      {error && (
        <div style={{ ...card, borderColor: '#f87171' }}>
          <p style={{ color: '#f87171' }}>{error}</p>
        </div>
      )}
      {auditStats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16, marginBottom: 24 }}>
          <div style={card}>
            <div style={{ fontSize: 28, fontWeight: 'bold', color: '#818cf8' }}>{auditStats.total_entries}</div>
            <div style={{ fontSize: 14, color: '#94a3b8' }}>Total Events</div>
          </div>
          <div style={card}>
            <div style={{ fontSize: 28, fontWeight: 'bold', color: '#f87171' }}>{auditStats.blocked_entries}</div>
            <div style={{ fontSize: 14, color: '#94a3b8' }}>Blocked</div>
          </div>
          <div style={card}>
            <div style={{ fontSize: 28, fontWeight: 'bold', color: '#34d399' }}>{(auditStats.block_rate * 100).toFixed(1)}%</div>
            <div style={{ fontSize: 14, color: '#94a3b8' }}>Block Rate</div>
          </div>
        </div>
      )}
      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Pending Approvals</h2>
        {approvals.length === 0 ? (
          <p style={{ color: '#64748b' }}>No pending approvals.</p>
        ) : (
          <div style={{ display: 'grid', gap: 8 }}>
            {approvals.map(a => (
              <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', padding: 12, backgroundColor: '#0f172a', borderRadius: 6 }}>
                <span>{a.description || `Request #${a.id}`}</span>
                <button style={btn} onClick={() => doApprove(a.id)}>Approve</button>
              </div>
            ))}
          </div>
        )}
      </div>
      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Audit Trail</h2>
        {auditEntries.length === 0 ? (
          <p style={{ color: '#64748b' }}>No audit entries yet.</p>
        ) : (
          <div style={{ display: 'grid', gap: 6 }}>
            {auditEntries.map(e => (
              <div key={e.id} style={{ padding: '8px 12px', backgroundColor: '#0f172a', borderRadius: 6, fontSize: 13 }}>
                <span style={{ color: e.allowed ? '#34d399' : '#f87171', fontWeight: 600 }}>{e.allowed ? 'ALLOWED' : 'BLOCKED'}</span>
                {' | '}{e.action}{' | '}{e.timestamp?.slice(0, 19) ?? ''}
                {e.reason ? ` | ${e.reason}` : ''}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
