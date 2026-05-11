import { useState, useEffect } from 'react';
import { getMemoryStats, searchMemory, ingestMemory } from '../api';

const card = { backgroundColor: '#1e293b', borderRadius: 8, padding: 20, border: '1px solid #334155', marginBottom: 16 };
const input = { backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 6, padding: '8px 12px', color: '#e2e8f0', fontSize: 14, width: '100%', boxSizing: 'border-box' };
const btn = { backgroundColor: '#6366f1', color: 'white', border: 'none', borderRadius: 6, padding: '8px 16px', cursor: 'pointer', fontSize: 14, fontWeight: 500 };
const textarea = { ...input, minHeight: 100, resize: 'vertical', fontFamily: 'inherit' };

export default function Memory() {
  const [stats, setStats] = useState({ collections: [], document_counts: {}, total_documents: 0 });
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [ingestText, setIngestText] = useState('');
  const [ingestStatus, setIngestStatus] = useState('');

  useEffect(() => { getMemoryStats().then(setStats).catch(() => {}); }, []);

  const doSearch = async () => {
    if (!query.trim()) return;
    try {
      const data = await searchMemory(query);
      setResults(data.results || []);
      setSearched(true);
    } catch (err) {
      setResults([]);
      setSearched(true);
    }
  };

  const doIngest = async () => {
    if (!ingestText.trim()) return;
    setIngestStatus('Ingesting...');
    try {
      const data = await ingestMemory(ingestText);
      setIngestStatus(`Ingested ${data.documents_ingested} chunks`);
      setIngestText('');
      const s = await getMemoryStats();
      setStats(s);
    } catch (err) {
      setIngestStatus(`Error: ${err.message}`);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 24 }}>Memory & RAG</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16, marginBottom: 24 }}>
        {stats.collections && stats.collections.length > 0 ? (
          stats.collections.map((name) => (
            <div key={name} style={card}>
              <div style={{ fontSize: 14, color: '#94a3b8' }}>{name}</div>
              <div style={{ fontSize: 28, fontWeight: 'bold', color: '#818cf8' }}>{stats.document_counts?.[name] ?? 0}</div>
              <div style={{ fontSize: 12, color: '#64748b' }}>documents</div>
            </div>
          ))
        ) : (
          <div style={card}>
            <p style={{ color: '#64748b' }}>No collections yet.</p>
          </div>
        )}
        <div style={card}>
          <div style={{ fontSize: 14, color: '#94a3b8' }}>Total</div>
          <div style={{ fontSize: 28, fontWeight: 'bold', color: '#818cf8' }}>{stats.total_documents ?? 0}</div>
          <div style={{ fontSize: 12, color: '#64748b' }}>documents</div>
        </div>
      </div>
      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Ingest Text</h2>
        <textarea style={textarea} placeholder="Paste text to ingest..." value={ingestText} onChange={e => setIngestText(e.target.value)} />
        <div style={{ display: 'flex', gap: 12, marginTop: 8, alignItems: 'center' }}>
          <button style={btn} onClick={doIngest}>Ingest</button>
          {ingestStatus && <span style={{ fontSize: 13, color: '#94a3b8' }}>{ingestStatus}</span>}
        </div>
      </div>
      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 12 }}>Search</h2>
        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1 }}>
            <input style={input} placeholder="Search your documents..." value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === 'Enter' && doSearch()} />
          </div>
          <button style={btn} onClick={doSearch}>Search</button>
        </div>
        {searched && (
          <div style={{ marginTop: 16 }}>
            {results.length === 0 ? (
              <p style={{ color: '#64748b' }}>No results found.</p>
            ) : (
              results.map((r, i) => (
                <div key={i} style={{ padding: 12, backgroundColor: '#0f172a', borderRadius: 6, marginBottom: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ color: '#94a3b8', fontSize: 12 }}>Score: {r.score}</span>
                    <span style={{ color: '#64748b', fontSize: 11 }}>{r.id}</span>
                  </div>
                  <div style={{ fontSize: 14 }}>{r.text?.slice(0, 300)}</div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
