import { useState } from 'react'
import './index.css'

function App() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)

  const handleTranslate = async () => {
    if (!text.trim()) return
    
    setLoading(true)
    setError(null)
    setCopied(false)
    
    try {
      const response = await fetch('http://localhost:8000/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      
      const data = await response.json()
      
      if (data.success) {
        const dataArray = Array.isArray(data.data) ? data.data : [data.data];
        setResults(dataArray);
      } else {
        setError(data.error)
      }
    } catch (err) {
      setError('Error al conectar con el servidor. ¿Está corriendo FastAPI?')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (!results) return;
    const fullText = results.map(node => node.mist_translation).join(' ');
    navigator.clipboard.writeText(fullText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="app-container">
      <header>
        {/* Volcano SVG */}
        <div className="logo-container">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#111" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
            <path d="M8.5 9L2 21h20L15.5 9"/>
            <path d="M8.5 9C10 10.5 11 11 12 11c1 0 2-.5 3.5-2"/>
            <path d="M12 3v3"/>
            <path d="M16 4l-1 2"/>
            <path d="M8 4l1 2"/>
            <path d="M12 11v4"/>
          </svg>
        </div>
        <h1>MIST-JP/ES</h1>
        <p>Pragmatic Neural Machine Translation</p>
      </header>

      <main className="main-content">
        {/* Left Panel: Input */}
        <section className="manga-panel">
          <h2>Conversación Original</h2>
          <textarea 
            placeholder="Pega aquí la conversación o diálogo en japonés..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button 
            className="translate-btn" 
            onClick={handleTranslate}
            disabled={loading || !text.trim()}
          >
            {loading ? <span className="loading-spinner"></span> : 'Procesar Traducción'}
          </button>
          {error && <p style={{color: '#e60000', fontSize: '1rem', fontWeight: 'bold'}}>{error}</p>}
        </section>

        {/* Right Panel: Output */}
        <section className="manga-panel">
          <h2>
            Traducción Pragmática
            {results && (
              <button className="copy-btn" onClick={handleCopy} title="Copiar al portapapeles">
                {copied ? (
                  <>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    ¡Copiado!
                  </>
                ) : (
                  <>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    Copiar
                  </>
                )}
              </button>
            )}
          </h2>
          
          {results ? (
            <div className="conversation-output">
              {results.map((node, idx) => (
                <div key={idx} className="dialogue-node">
                  <div className="translation-text">
                    {node.mist_translation}
                  </div>
                  <div className="mist-tooltip">
                    <div className="tooltip-stat">
                      <span className="stat-label">Intención</span>
                      <span className="stat-value">
                        {node.intent.label} <span className="stat-pct">({Math.round(node.intent.confidence * 100)}%)</span>
                      </span>
                    </div>
                    <div className="tooltip-divider"></div>
                    <div className="tooltip-stat">
                      <span className="stat-label">Tono</span>
                      <span className="stat-value">
                        {node.tone.label} <span className="stat-pct">({Math.round(node.tone.confidence * 100)}%)</span>
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              Esperando diálogo para analizar...
            </div>
          )}
        </section>
      </main>
      
      <footer>
        made with <span>❤</span> by unmsm
      </footer>
    </div>
  )
}

export default App
