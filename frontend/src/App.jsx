import { useState } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const API = 'http://localhost:8000'

export default function App() {
  const [page, setPage] = useState('Landing')
  const [code, setCode] = useState('')
  const [filename, setFilename] = useState('code.py')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [routeMode, setRouteMode] = useState('Auto')
  const [dragOver, setDragOver] = useState(false)

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setFilename(file.name)
    const reader = new FileReader()
    reader.onload = (event) => setCode(event.target.result)
    reader.readAsText(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (!file) return
    setFilename(file.name)
    const reader = new FileReader()
    reader.onload = (event) => setCode(event.target.result)
    reader.readAsText(file)
  }

  const submitReview = async () => {
    if (!code.trim()) return
    setLoading(true)
    setReport(null)
    setError(null)
    setPage('Demo')

    try {
      const res = await axios.post(`${API}/review`, { code, filename })
      const jobId = res.data.job_id
      let attempts = 0
      const poll = setInterval(async () => {
        attempts++
        const result = await axios.get(`${API}/review/${jobId}`)
        if (result.data.status === 'completed') {
          clearInterval(poll)
          setReport(result.data.report)
          setLoading(false)
        } else if (result.data.status === 'failed' || attempts > 30) {
          clearInterval(poll)
          setError('Review failed.')
          setLoading(false)
        }
      }, 2000)
    } catch (e) {
      setError('API error. Is server running?')
      setLoading(false)
    }
  }

  const benchmarkData = [
    { name: 'Bug Detection F1', value: 88 },
    { name: 'Security Recall', value: 92 },
    { name: 'Router Accuracy', value: 95 },
    { name: 'Test Coverage', value: 78 },
  ]

  const latencyData = [
    { name: 'Without Router', latency: 28 },
    { name: 'With Router', latency: 11 },
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#0d1117', color: '#c9d1d9', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>

      {/* ── NAVBAR ── */}
      <nav style={{ background: '#161b22', borderBottom: '1px solid #30363d', padding: '0 32px', display: 'flex', alignItems: 'center', height: '60px', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginRight: '40px' }}>
          <div style={{ width: '32px', height: '32px', background: 'linear-gradient(135deg, #58a6ff, #bc8cff)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px' }}>🔍</div>
          <span style={{ fontWeight: 700, fontSize: '15px', color: '#f0f6fc', letterSpacing: '-0.3px' }}>CODEREVIEW AI</span>
        </div>
        <div style={{ display: 'flex', gap: '4px', flex: 1 }}>
          {['Landing', 'Demo', 'Benchmarks', 'Architecture', 'About'].map(p => (
            <button key={p} onClick={() => setPage(p)}
              style={{ padding: '6px 14px', background: page === p ? '#21262d' : 'transparent', border: 'none', borderRadius: '6px', color: page === p ? '#58a6ff' : '#8b949e', cursor: 'pointer', fontSize: '14px', fontWeight: page === p ? 600 : 400 }}>
              {p}
            </button>
          ))}
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: '#3fb950' }}>● Live</span>
          <a href="https://github.com/Mumtaj-77/CodeReview-AI" target="_blank" style={{ padding: '6px 16px', background: '#238636', border: '1px solid #2ea043', borderRadius: '6px', color: 'white', fontSize: '13px', fontWeight: 600, textDecoration: 'none' }}>GitHub</a>
        </div>
      </nav>

      {/* ── LANDING PAGE ── */}
      {page === 'Landing' && (
        <div>
          <div style={{ padding: '80px 64px 60px', maxWidth: '1200px', margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '60px', alignItems: 'center' }}>
            <div>
              <div style={{ display: 'inline-block', padding: '4px 12px', background: '#1f2937', border: '1px solid #374151', borderRadius: '999px', fontSize: '12px', color: '#58a6ff', marginBottom: '20px' }}>
                🤖 Multi-Agent AI System
              </div>
              <h1 style={{ fontSize: '48px', fontWeight: 800, lineHeight: 1.1, marginBottom: '20px', color: '#f0f6fc' }}>
                Smarter <span style={{ color: '#58a6ff' }}>Code Review</span><br />
                Through Agent <span style={{ color: '#bc8cff' }}>Intelligence</span>
              </h1>
              <p style={{ fontSize: '16px', color: '#8b949e', lineHeight: 1.7, marginBottom: '32px' }}>
                A 7-agent pipeline that routes each code review to the most efficient model, maximizing bug detection while minimizing latency.
              </p>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button onClick={() => setPage('Demo')}
                  style={{ padding: '12px 24px', background: 'linear-gradient(135deg, #58a6ff, #bc8cff)', border: 'none', borderRadius: '8px', color: 'white', fontSize: '15px', fontWeight: 600, cursor: 'pointer' }}>
                  Try the Demo →
                </button>
                <button onClick={() => setPage('Benchmarks')}
                  style={{ padding: '12px 24px', background: 'transparent', border: '1px solid #30363d', borderRadius: '8px', color: '#c9d1d9', fontSize: '15px', cursor: 'pointer' }}>
                  View Benchmarks
                </button>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {[
                { value: '88%', label: 'Bug Detection F1', color: '#58a6ff' },
                { value: '7', label: 'AI Agents', color: '#bc8cff' },
                { value: '11s', label: 'Avg Review Time', color: '#3fb950' },
                { value: '0₹', label: 'Inference Cost', color: '#f78166' },
              ].map((s, i) => (
                <div key={i} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '12px', padding: '24px', textAlign: 'center' }}>
                  <div style={{ fontSize: '36px', fontWeight: 800, color: s.color, marginBottom: '4px' }}>{s.value}</div>
                  <div style={{ fontSize: '13px', color: '#8b949e' }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ padding: '0 64px 60px', maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '48px' }}>
              {[
                { icon: '🧠', title: 'Hybrid Intelligence', desc: 'Router dynamically selects fast or powerful model for each code file' },
                { icon: '🎯', title: 'High Accuracy', desc: '88% F1 score on bug detection with fine-tuned CodeBERT classifier' },
                { icon: '⚡', title: 'Efficient Routing', desc: 'Simple bugs → fast model. Complex bugs → powerful model' },
                { icon: '🔒', title: 'Security Aware', desc: '10 vulnerability patterns detected automatically via regex + LLM' },
              ].map((f, i) => (
                <div key={i} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '12px', padding: '20px' }}>
                  <div style={{ fontSize: '24px', marginBottom: '10px' }}>{f.icon}</div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#f0f6fc', marginBottom: '6px' }}>{f.title}</div>
                  <div style={{ fontSize: '12px', color: '#8b949e', lineHeight: 1.5 }}>{f.desc}</div>
                </div>
              ))}
            </div>

            <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '12px', padding: '32px' }}>
              <div style={{ fontSize: '13px', color: '#8b949e', marginBottom: '20px' }}>How It Works</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflowX: 'auto' }}>
                {['Code Input', 'Parser', 'CodeBERT Router', 'Bug Detector', 'Security Scanner', 'Fix Suggester', 'Explainer', 'Report'].map((step, i, arr) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                    <div style={{ background: i === 2 ? 'linear-gradient(135deg, #58a6ff22, #bc8cff22)' : '#21262d', border: `1px solid ${i === 2 ? '#58a6ff' : '#30363d'}`, borderRadius: '8px', padding: '10px 14px', fontSize: '12px', color: i === 2 ? '#58a6ff' : '#c9d1d9', textAlign: 'center', minWidth: '80px' }}>
                      {step}
                    </div>
                    {i < arr.length - 1 && <span style={{ color: '#30363d', fontSize: '18px' }}>→</span>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── DEMO PAGE ── */}
      {page === 'Demo' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', height: 'calc(100vh - 60px)' }}>

          {/* Left — Problem */}
          <div style={{ borderRight: '1px solid #30363d', display: 'flex', flexDirection: 'column' }}>

            {/* Header */}
            <div style={{ padding: '12px 16px', borderBottom: '1px solid #30363d', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '16px' }}>🐛</span>
              <span style={{ fontSize: '14px', fontWeight: 600, color: '#f0f6fc' }}>Problem</span>
              <span style={{ fontSize: '12px', color: '#8b949e' }}>Paste code or upload file.</span>
              <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px', alignItems: 'center' }}>
                <label style={{ padding: '5px 12px', background: '#21262d', border: '1px solid #30363d', borderRadius: '6px', color: '#8b949e', fontSize: '12px', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                  📁 Upload File
                  <input
                    type="file"
                    accept=".py,.js,.java,.ts,.cpp,.cs,.go,.rb,.php"
                    style={{ display: 'none' }}
                    onChange={handleFileUpload}
                  />
                </label>
                <input value={filename} onChange={e => setFilename(e.target.value)}
                  style={{ padding: '4px 10px', background: '#21262d', border: '1px solid #30363d', borderRadius: '6px', color: '#8b949e', fontSize: '12px', width: '100px' }} />
              </div>
            </div>

            {/* Drag & Drop + Textarea */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              style={{ flex: 1, position: 'relative', border: dragOver ? '2px dashed #58a6ff' : 'none' }}
            >
              {dragOver && (
                <div style={{ position: 'absolute', inset: 0, background: '#58a6ff11', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10, pointerEvents: 'none' }}>
                  <div style={{ fontSize: '24px', color: '#58a6ff' }}>📁 Drop file here</div>
                </div>
              )}
              <textarea
                value={code}
                onChange={e => setCode(e.target.value)}
                placeholder="Paste your Python, JavaScript, TypeScript, Java, C++, C#, Go, Ruby, or PHP code here...&#10;&#10;Or drag & drop a file anywhere on this panel."
                style={{ width: '100%', height: '100%', padding: '20px', background: '#0d1117', color: '#c9d1d9', border: 'none', outline: 'none', resize: 'none', fontSize: '13px', lineHeight: '1.7', fontFamily: '"Fira Code", "Cascadia Code", monospace', boxSizing: 'border-box' }}
              />
            </div>

            {/* Footer */}
            <div style={{ padding: '10px 16px', borderTop: '1px solid #30363d', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: '#8b949e' }}>{code.length} / 5000</span>
              {filename && <span style={{ fontSize: '11px', color: '#3fb950', background: '#3fb95020', padding: '2px 8px', borderRadius: '4px' }}>📄 {filename}</span>}
              <div style={{ display: 'flex', gap: '4px', marginLeft: 'auto' }}>
                {['Auto', 'Fast', 'Powerful'].map(m => (
                  <button key={m} onClick={() => setRouteMode(m)}
                    style={{ padding: '5px 12px', background: routeMode === m ? '#1f6feb' : '#21262d', border: `1px solid ${routeMode === m ? '#388bfd' : '#30363d'}`, borderRadius: '6px', color: routeMode === m ? 'white' : '#8b949e', fontSize: '12px', cursor: 'pointer' }}>
                    {m === 'Auto' ? '⚡ Auto' : m === 'Fast' ? '🚀 Fast' : '💪 Powerful'}
                  </button>
                ))}
              </div>
            </div>

            {/* Review Button */}
            <div style={{ padding: '12px 16px', borderTop: '1px solid #30363d' }}>
              <button onClick={submitReview} disabled={loading || !code.trim()}
                style={{ width: '100%', padding: '11px', background: loading ? '#21262d' : 'linear-gradient(135deg, #1f6feb, #8957e5)', border: 'none', borderRadius: '8px', color: 'white', fontSize: '14px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                {loading ? '⏳ Reviewing...' : '▶ Review Code'}
                {!loading && <span style={{ fontSize: '11px', opacity: 0.7 }}>⌘ Enter</span>}
              </button>
            </div>
          </div>

          {/* Right — Results */}
          <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid #30363d', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '16px' }}>🤖</span>
              <span style={{ fontSize: '14px', fontWeight: 600, color: '#f0f6fc' }}>Review Results</span>
              {report && <button onClick={() => { setReport(null); setCode(''); setFilename('code.py') }} style={{ marginLeft: 'auto', padding: '4px 10px', background: 'transparent', border: '1px solid #30363d', borderRadius: '6px', color: '#8b949e', fontSize: '12px', cursor: 'pointer' }}>Clear</button>}
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
              {!report && !loading && (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '12px', color: '#484f58' }}>
                  <div style={{ fontSize: '48px' }}>🤖</div>
                  <p style={{ fontSize: '14px' }}>Paste code or upload a file</p>
                  <p style={{ fontSize: '12px' }}>Supports: Python, JS, TS, Java, C++, C#, Go, Ruby, PHP</p>
                  <p style={{ fontSize: '12px' }}>7 AI agents will analyze your code</p>
                </div>
              )}

              {loading && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <p style={{ color: '#58a6ff', fontSize: '13px', marginBottom: '8px' }}>⚡ Running agent pipeline...</p>
                  {['Parser Agent', 'CodeBERT Router', 'Bug Detector', 'Security Scanner', 'Fix Suggester', 'Explainer', 'Report Generator'].map((a, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 12px', background: '#161b22', borderRadius: '6px', border: '1px solid #30363d', fontSize: '13px', color: '#8b949e' }}>
                      <span style={{ color: '#3fb950' }}>→</span> {a}
                    </div>
                  ))}
                </div>
              )}

              {report && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
                    {[
                      { label: 'Route Taken', value: report.summary.model_used?.split('/')[1] || 'compound', color: '#3fb950' },
                      { label: 'Latency', value: `⚡ ${report.summary.review_time_seconds}s`, color: '#f0f6fc' },
                      { label: 'Bugs Found', value: `🐛 ${report.summary.total_bugs}`, color: '#f85149' },
                      { label: 'Security', value: `🔒 ${report.summary.total_security_issues}`, color: '#f78166' },
                    ].map((s, i) => (
                      <div key={i} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: s.color }}>{s.value}</div>
                        <div style={{ fontSize: '10px', color: '#484f58', marginTop: '2px' }}>{s.label}</div>
                      </div>
                    ))}
                  </div>

                  {report.bugs.length > 0 && (
                    <div>
                      <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '8px', fontWeight: 600 }}>🐛 BUGS ({report.bugs.length})</div>
                      {report.bugs.map((bug, i) => (
                        <div key={i} style={{ background: '#161b22', border: '1px solid #30363d', borderLeft: `3px solid ${bug.severity === 'critical' ? '#f85149' : bug.severity === 'high' ? '#f78166' : '#d29922'}`, borderRadius: '6px', padding: '12px', marginBottom: '6px' }}>
                          <div style={{ display: 'flex', gap: '6px', alignItems: 'center', marginBottom: '4px' }}>
                            <span style={{ fontSize: '10px', color: '#484f58' }}>Line {bug.line}</span>
                            <span style={{ fontSize: '10px', padding: '1px 6px', borderRadius: '4px', background: bug.severity === 'critical' ? '#f8514920' : '#d2992220', color: bug.severity === 'critical' ? '#f85149' : '#d29922', fontWeight: 600 }}>{bug.severity?.toUpperCase()}</span>
                            <span style={{ fontSize: '10px', color: '#484f58' }}>{bug.category}</span>
                          </div>
                          <p style={{ fontSize: '12px', color: '#c9d1d9', marginBottom: '4px' }}>{bug.description}</p>
                          <p style={{ fontSize: '11px', color: '#3fb950' }}>→ {bug.fix}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {report.security_issues.length > 0 && (
                    <div>
                      <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '8px', fontWeight: 600 }}>🔒 SECURITY ({report.security_issues.length})</div>
                      {report.security_issues.map((issue, i) => (
                        <div key={i} style={{ background: '#161b22', border: '1px solid #30363d', borderLeft: '3px solid #f85149', borderRadius: '6px', padding: '12px', marginBottom: '6px' }}>
                          <div style={{ display: 'flex', gap: '6px', alignItems: 'center', marginBottom: '4px' }}>
                            <span style={{ fontSize: '10px', color: '#484f58' }}>Line {issue.line}</span>
                            <span style={{ fontSize: '10px', padding: '1px 6px', borderRadius: '4px', background: '#f8514920', color: '#f85149', fontWeight: 600 }}>{issue.severity?.toUpperCase()}</span>
                            <span style={{ fontSize: '10px', color: '#f78166' }}>{issue.vulnerability}</span>
                          </div>
                          <p style={{ fontSize: '12px', color: '#c9d1d9', marginBottom: '4px' }}>{issue.description}</p>
                          <p style={{ fontSize: '11px', color: '#3fb950' }}>→ {issue.fix}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {report.fixes?.length > 0 && (
                    <div>
                      <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '8px', fontWeight: 600 }}>🔧 FIXES ({report.fixes.length})</div>
                      {report.fixes.map((fix, i) => (
                        <div key={i} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '6px', padding: '12px', marginBottom: '6px' }}>
                          <div style={{ fontSize: '10px', color: '#484f58', marginBottom: '6px' }}>Line {fix.line} — {fix.principle}</div>
                          <div style={{ background: '#3d0000', borderRadius: '4px', padding: '6px', marginBottom: '4px', fontSize: '11px', color: '#ffa198', fontFamily: 'monospace' }}>- {fix.original}</div>
                          <div style={{ background: '#003d00', borderRadius: '4px', padding: '6px', fontSize: '11px', color: '#7ee787', fontFamily: 'monospace' }}>+ {fix.fixed}</div>
                          {fix.explanation && <p style={{ fontSize: '11px', color: '#94a3b8', marginTop: '6px' }}>{fix.explanation}</p>}
                        </div>
                      ))}
                    </div>
                  )}

                  <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '6px' }}>
                    <div style={{ padding: '10px 14px', fontSize: '12px', color: '#8b949e', display: 'flex', justifyContent: 'space-between' }}>
                      <span>Raw Response</span><span>▼</span>
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div style={{ background: '#450a0a', border: '1px solid #ef4444', borderRadius: '8px', padding: '12px', color: '#ef4444', fontSize: '13px' }}>{error}</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── BENCHMARKS PAGE ── */}
      {page === 'Benchmarks' && (
        <div style={{ padding: '40px 48px', maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#f0f6fc', marginBottom: '4px' }}>Benchmarks Overview</h2>
          <p style={{ color: '#8b949e', fontSize: '14px', marginBottom: '32px' }}>Comprehensive evaluation across accuracy, latency, and agent performance.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
            <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '12px', padding: '24px' }}>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#f0f6fc', marginBottom: '4px' }}>Bug Detection F1 Score</div>
              <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '16px' }}>Per severity class performance</div>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={benchmarkData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#8b949e' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#8b949e' }} domain={[0, 100]} />
                  <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '6px' }} />
                  <Bar dataKey="value" fill="#58a6ff" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '12px', padding: '24px' }}>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#f0f6fc', marginBottom: '4px' }}>Average Latency (seconds)</div>
              <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '16px' }}>Router reduces latency significantly</div>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={latencyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#8b949e' }} />
                  <YAxis tick={{ fontSize: 10, fill: '#8b949e' }} />
                  <Tooltip contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '6px' }} />
                  <Bar dataKey="latency" fill="#bc8cff" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            {[
              { label: 'Bug Detection F1', value: '0.88', sub: 'Weighted average across classes', color: '#58a6ff' },
              { label: 'Security Recall', value: '92%', sub: 'Critical vulnerabilities caught', color: '#f78166' },
              { label: 'Router Accuracy', value: '95%', sub: 'Correct model selection rate', color: '#3fb950' },
              { label: 'Avg Review Time', value: '11.38s', sub: 'End-to-end pipeline latency', color: '#bc8cff' },
            ].map((m, i) => (
              <div key={i} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '12px', padding: '24px' }}>
                <div style={{ fontSize: '36px', fontWeight: 800, color: m.color, marginBottom: '4px' }}>{m.value}</div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#f0f6fc', marginBottom: '4px' }}>{m.label}</div>
                <div style={{ fontSize: '12px', color: '#8b949e' }}>{m.sub}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '24px', padding: '16px 20px', background: '#161b22', border: '1px solid #30363d', borderRadius: '8px', display: 'flex', gap: '24px', fontSize: '12px', color: '#8b949e' }}>
            <span>🤖 Model: CodeBERT (fine-tuned)</span>
            <span>📊 Dataset: 788 labeled samples</span>
            <span>🌡️ Temperature: 0.1</span>
            <span>⚡ Router: groq/compound-mini</span>
          </div>
        </div>
      )}

      {/* ── ARCHITECTURE PAGE ── */}
      {page === 'Architecture' && (
        <div style={{ padding: '40px 48px', maxWidth: '900px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#f0f6fc', marginBottom: '4px' }}>Architecture</h2>
          <p style={{ color: '#8b949e', fontSize: '14px', marginBottom: '32px' }}>7-agent LangGraph pipeline with intelligent routing.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[
              { step: '01', name: 'Parser Agent', desc: 'AST parsing via Python ast module. Extracts functions, classes, imports, complexity score.', color: '#58a6ff' },
              { step: '02', name: 'CodeBERT Router', desc: 'Fine-tuned microsoft/codebert-base classifier. Routes LOW severity → fast model, HIGH → powerful model.', color: '#bc8cff' },
              { step: '03', name: 'Bug Detector Agent', desc: 'LLM-powered bug detection. Finds null pointers, logic errors, undefined variables, type issues.', color: '#f85149' },
              { step: '04', name: 'Security Scanner Agent', desc: 'Dual-layer: regex patterns (10 vulnerability types) + LLM deep scan. SQL injection, hardcoded secrets, weak crypto.', color: '#f78166' },
              { step: '05', name: 'Fix Suggester Agent', desc: 'Generates exact line-level replacement code in diff format. Includes principle violated (SOLID/DRY/Security).', color: '#3fb950' },
              { step: '06', name: 'Explainer Agent', desc: 'Explains each bug and fix to junior developers. Educational, encouraging, max 3 sentences.', color: '#d29922' },
              { step: '07', name: 'Report Generator', desc: 'Aggregates all agent outputs into structured JSON report with summary metrics.', color: '#58a6ff' },
            ].map((a, i) => (
              <div key={i} style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '10px', padding: '20px', display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                <div style={{ fontSize: '24px', fontWeight: 800, color: a.color, minWidth: '40px' }}>{a.step}</div>
                <div>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: '#f0f6fc', marginBottom: '4px' }}>{a.name}</div>
                  <div style={{ fontSize: '13px', color: '#8b949e', lineHeight: 1.6 }}>{a.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── ABOUT PAGE ── */}
      {page === 'About' && (
        <div style={{ padding: '40px 48px', maxWidth: '700px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#f0f6fc', marginBottom: '16px' }}>About</h2>
          <div style={{ background: '#161b22', border: '1px solid #30363d', borderRadius: '12px', padding: '28px', lineHeight: 1.8, color: '#8b949e', fontSize: '14px' }}>
            <p style={{ marginBottom: '16px', color: '#c9d1d9' }}>CodeReview AI is a multi-agent code review system built as a final year project by <strong style={{ color: '#58a6ff' }}>Mumtaj Shaikh</strong>, B.Tech CSE student at D.Y. Patil International University, Pune.</p>
            <p style={{ marginBottom: '16px' }}>The system uses 7 specialized AI agents orchestrated via LangGraph to automatically detect bugs, security vulnerabilities, and style issues in Python, JavaScript, TypeScript, Java, C++, C#, Go, Ruby, and PHP code.</p>
            <p style={{ marginBottom: '16px' }}>Core innovation: intelligent routing using a fine-tuned CodeBERT classifier that routes simple bugs to a fast LLM and complex bugs to a powerful LLM — minimizing latency while maintaining accuracy.</p>
            <div style={{ marginTop: '24px', padding: '16px', background: '#21262d', borderRadius: '8px', fontSize: '13px' }}>
              <div style={{ color: '#f0f6fc', fontWeight: 600, marginBottom: '8px' }}>Tech Stack</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {['Python', 'FastAPI', 'LangGraph', 'CodeBERT', 'Groq API', 'PostgreSQL', 'Redis', 'React', 'Docker', 'W&B'].map(t => (
                  <span key={t} style={{ padding: '3px 10px', background: '#161b22', border: '1px solid #30363d', borderRadius: '999px', fontSize: '12px', color: '#58a6ff' }}>{t}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}