import { useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

function App() {
  const [code, setCode] = useState('')
  const [filename, setFilename] = useState('code.py')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)

  const submitReview = async () => {
    if (!code.trim()) return
    setLoading(true)
    setReport(null)
    setError(null)

    try {
      // Submit review
      const res = await axios.post(`${API}/review`, { code, filename })
      const jobId = res.data.job_id

      // Poll for result
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
          setError('Review failed. Try again.')
          setLoading(false)
        }
      }, 2000)
    } catch (e) {
      setError('API error. Is server running?')
      setLoading(false)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-400 bg-red-900/30 border-red-800'
      case 'high': return 'text-orange-400 bg-orange-900/30 border-orange-800'
      case 'medium': return 'text-yellow-400 bg-yellow-900/30 border-yellow-800'
      case 'low': return 'text-blue-400 bg-blue-900/30 border-blue-800'
      default: return 'text-gray-400 bg-gray-900/30 border-gray-800'
    }
  }

  return (
    <div style={{minHeight: '100vh', background: '#0f172a', color: '#e2e8f0', fontFamily: 'monospace'}}>
      
      {/* Header */}
      <div style={{background: '#1e293b', borderBottom: '1px solid #334155', padding: '16px 32px', display: 'flex', alignItems: 'center', gap: '12px'}}>
        <div style={{width: '32px', height: '32px', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px'}}>🔍</div>
        <div>
          <h1 style={{fontSize: '18px', fontWeight: 'bold', color: '#f1f5f9'}}>CodeReview AI</h1>
          <p style={{fontSize: '11px', color: '#64748b'}}>Multi-agent code review with intelligent LLM routing</p>
        </div>
        <div style={{marginLeft: 'auto', display: 'flex', gap: '8px'}}>
          <span style={{padding: '4px 10px', background: '#10b981', borderRadius: '999px', fontSize: '11px', color: 'white'}}>● API Connected</span>
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0', height: 'calc(100vh - 65px)'}}>
        
        {/* Left Panel - Code Input */}
        <div style={{borderRight: '1px solid #334155', display: 'flex', flexDirection: 'column'}}>
          <div style={{padding: '16px', borderBottom: '1px solid #334155', display: 'flex', alignItems: 'center', gap: '12px'}}>
            <span style={{fontSize: '13px', color: '#94a3b8'}}>📝 Code Input</span>
            <input
              value={filename}
              onChange={e => setFilename(e.target.value)}
              style={{marginLeft: 'auto', padding: '4px 8px', background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', color: '#94a3b8', fontSize: '12px', width: '120px'}}
            />
          </div>
          <textarea
            value={code}
            onChange={e => setCode(e.target.value)}
            placeholder="Paste your Python, JavaScript, or Java code here..."
            style={{flex: 1, padding: '16px', background: '#0f172a', color: '#e2e8f0', border: 'none', outline: 'none', resize: 'none', fontSize: '13px', lineHeight: '1.6', fontFamily: 'monospace'}}
          />
          <div style={{padding: '16px', borderTop: '1px solid #334155'}}>
            <button
              onClick={submitReview}
              disabled={loading || !code.trim()}
              style={{width: '100%', padding: '12px', background: loading ? '#334155' : 'linear-gradient(135deg, #3b82f6, #8b5cf6)', color: 'white', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: 'bold', cursor: loading ? 'not-allowed' : 'pointer'}}
            >
              {loading ? '⏳ Reviewing...' : '🚀 Review Code'}
            </button>
          </div>
        </div>

        {/* Right Panel - Results */}
        <div style={{overflowY: 'auto', display: 'flex', flexDirection: 'column'}}>
          {!report && !loading && (
            <div style={{flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '12px', color: '#475569'}}>
              <div style={{fontSize: '48px'}}>🤖</div>
              <p style={{fontSize: '14px'}}>Paste code and click Review</p>
              <p style={{fontSize: '12px'}}>7 AI agents will analyze your code</p>
            </div>
          )}

          {loading && (
            <div style={{flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px'}}>
              <div style={{fontSize: '32px'}}>⚡</div>
              <p style={{color: '#3b82f6', fontSize: '14px'}}>Running agent pipeline...</p>
              <div style={{display: 'flex', flexDirection: 'column', gap: '8px', width: '250px'}}>
                {['Parser Agent', 'Router Agent', 'Bug Detector', 'Security Scanner', 'Fix Suggester', 'Explainer', 'Report Generator'].map((agent, i) => (
                  <div key={i} style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#64748b'}}>
                    <span>→</span><span>{agent}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {report && (
            <div style={{padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px'}}>
              
              {/* Summary */}
              <div style={{background: '#1e293b', borderRadius: '8px', padding: '16px', border: '1px solid #334155'}}>
                <h3 style={{fontSize: '13px', color: '#94a3b8', marginBottom: '12px'}}>📊 Review Summary</h3>
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px'}}>
                  {[
                    {label: 'Bugs', value: report.summary.total_bugs, color: '#ef4444'},
                    {label: 'Security', value: report.summary.total_security_issues, color: '#f97316'},
                    {label: 'Fixes', value: report.summary.total_fixes, color: '#10b981'},
                    {label: 'Time', value: `${report.summary.review_time_seconds}s`, color: '#3b82f6'},
                  ].map((stat, i) => (
                    <div key={i} style={{background: '#0f172a', borderRadius: '6px', padding: '10px', textAlign: 'center'}}>
                      <div style={{fontSize: '20px', fontWeight: 'bold', color: stat.color}}>{stat.value}</div>
                      <div style={{fontSize: '11px', color: '#64748b'}}>{stat.label}</div>
                    </div>
                  ))}
                </div>
                <div style={{marginTop: '8px', display: 'flex', gap: '8px', fontSize: '11px'}}>
                  <span style={{color: '#64748b'}}>Model:</span>
                  <span style={{color: '#3b82f6'}}>{report.summary.model_used}</span>
                  <span style={{color: '#64748b', marginLeft: '8px'}}>Language:</span>
                  <span style={{color: '#10b981'}}>{report.summary.language}</span>
                  <span style={{color: '#64748b', marginLeft: '8px'}}>Severity:</span>
                  <span style={{color: '#f97316'}}>{report.summary.severity}</span>
                </div>
              </div>

              {/* Bugs */}
              {report.bugs.length > 0 && (
                <div>
                  <h3 style={{fontSize: '13px', color: '#94a3b8', marginBottom: '8px'}}>🐛 Bugs Found ({report.bugs.length})</h3>
                  {report.bugs.map((bug, i) => (
                    <div key={i} style={{background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', padding: '12px', marginBottom: '8px', borderLeft: `3px solid ${bug.severity === 'critical' ? '#ef4444' : bug.severity === 'high' ? '#f97316' : '#eab308'}`}}>
                      <div style={{display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '4px'}}>
                        <span style={{fontSize: '11px', color: '#64748b'}}>Line {bug.line}</span>
                        <span style={{fontSize: '10px', padding: '2px 6px', borderRadius: '4px', background: bug.severity === 'critical' ? '#450a0a' : '#431407', color: bug.severity === 'critical' ? '#ef4444' : '#f97316'}}>{bug.severity?.toUpperCase()}</span>
                        <span style={{fontSize: '10px', color: '#64748b'}}>{bug.category}</span>
                      </div>
                      <p style={{fontSize: '12px', color: '#e2e8f0', marginBottom: '4px'}}>{bug.description}</p>
                      <p style={{fontSize: '11px', color: '#10b981'}}>Fix: {bug.fix}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Security */}
              {report.security_issues.length > 0 && (
                <div>
                  <h3 style={{fontSize: '13px', color: '#94a3b8', marginBottom: '8px'}}>🔒 Security Issues ({report.security_issues.length})</h3>
                  {report.security_issues.map((issue, i) => (
                    <div key={i} style={{background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', padding: '12px', marginBottom: '8px', borderLeft: '3px solid #ef4444'}}>
                      <div style={{display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '4px'}}>
                        <span style={{fontSize: '11px', color: '#64748b'}}>Line {issue.line}</span>
                        <span style={{fontSize: '10px', padding: '2px 6px', borderRadius: '4px', background: '#450a0a', color: '#ef4444'}}>{issue.severity?.toUpperCase()}</span>
                        <span style={{fontSize: '10px', color: '#f97316'}}>{issue.vulnerability}</span>
                      </div>
                      <p style={{fontSize: '12px', color: '#e2e8f0', marginBottom: '4px'}}>{issue.description}</p>
                      <p style={{fontSize: '11px', color: '#10b981'}}>Fix: {issue.fix}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Fixes */}
              {report.fixes.length > 0 && (
                <div>
                  <h3 style={{fontSize: '13px', color: '#94a3b8', marginBottom: '8px'}}>🔧 Suggested Fixes ({report.fixes.length})</h3>
                  {report.fixes.map((fix, i) => (
                    <div key={i} style={{background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', padding: '12px', marginBottom: '8px'}}>
                      <div style={{fontSize: '11px', color: '#64748b', marginBottom: '6px'}}>Line {fix.line} — {fix.principle}</div>
                      <div style={{background: '#450a0a', borderRadius: '4px', padding: '6px', marginBottom: '4px', fontSize: '11px', color: '#fca5a5', fontFamily: 'monospace'}}>- {fix.original}</div>
                      <div style={{background: '#052e16', borderRadius: '4px', padding: '6px', fontSize: '11px', color: '#86efac', fontFamily: 'monospace'}}>+ {fix.fixed}</div>
                      {fix.explanation && <p style={{fontSize: '11px', color: '#94a3b8', marginTop: '6px'}}>{fix.explanation}</p>}
                    </div>
                  ))}
                </div>
              )}

            </div>
          )}

          {error && (
            <div style={{padding: '16px'}}>
              <div style={{background: '#450a0a', border: '1px solid #ef4444', borderRadius: '8px', padding: '12px', color: '#ef4444', fontSize: '13px'}}>{error}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App