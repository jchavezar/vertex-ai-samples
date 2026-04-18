import { useState } from 'react'

const mockAssets = [
  { asset_id: '1', title: 'Cozy Coffee Shop Morning', category: 'photo', thumb_url: '/abstract_graphic.png', score: 0.95 },
  { asset_id: '2', title: 'Neon Cyberpunk Street', category: 'photo', thumb_url: '/abstract_graphic.png', score: 0.88 },
  { asset_id: '3', title: 'Minimalist Interior', category: 'photo', thumb_url: '/website_template_mockup.png', score: 0.85 },
  { asset_id: '4', title: 'Drone Aerial Path', category: 'video', thumb_url: '/website_template_mockup.png', score: 0.92 },
  { asset_id: '5', title: 'Abstract Liquid Ink', category: 'video', thumb_url: '/abstract_graphic.png', score: 0.78 },
  { asset_id: '6', title: 'Modern UI Design Kit', category: 'graphic', thumb_url: '/abstract_graphic.png', score: 0.91 },
  { asset_id: '7', title: '3D Abstract Rendering', category: '3d', thumb_url: '/website_template_mockup.png', score: 0.87 },
  { asset_id: '8', title: 'Corporate Web Template', category: 'template', thumb_url: '/website_template_mockup.png', score: 0.84 },
]

function App() {
  const [query, setQuery] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 })
  const [cursorVisible, setCursorVisible] = useState(false)
  const [searchResults, setSearchResults] = useState(mockAssets)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const suggestions = ['UI Design', 'Abstract Graphics', '3D Assets', 'Web Templates']

  const handleSearch = (e: React.FormEvent | React.KeyboardEvent) => {
    e.preventDefault()
    console.log('Searching for:', query)
    setShowSuggestions(false)
    setLoading(true)
    setError(null)
    
    fetch(`http://localhost:8090/api/search?q=${encodeURIComponent(query)}`)
      .then(res => {
        if (!res.ok) throw new Error('Search failed');
        return res.json();
      })
      .then(data => {
        setSearchResults(data.results || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to fetch results from vector search');
        setLoading(false);
      });
  }

  return (
    <div style={{ background: '#f9f5f0', minHeight: '100vh', fontFamily: "'Outfit', sans-serif" }}>

      {/* Premium Header */}
      <header className="header" style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '1rem 3rem', background: 'rgba(255,255,255,0.8)', backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0,0,0,0.05)', position: 'sticky', top: 0, zIndex: 100
      }}>
        <div className="logo" style={{ flex: '0 0 300px', display: 'flex', alignItems: 'center' }}>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280.28 64" style={{ height: '32px' }}>
            <defs>
              <style>{`
                .cls-1 { fill: #191919; }
                .cls-2 { fill: #87e64b; }
              `}</style>
            </defs>
            <g>
              <path className="cls-1" d="M76.34,12.52c9.59,0,18.97,5.65,18.97,18.25,0,1-.05,2.55-.16,3.64-.03.25-.24.44-.49.44h-26.9c.79,4.51,3.94,7.44,8.88,7.44,3.28,0,5.37-1.81,6.5-3.97.14-.27.45-.41.75-.35l10.06,2.19c.31.07.47.4.34.69-2.35,5.33-7.7,10.61-17.73,10.61-13.17,0-20.19-8.59-20.19-19.47s7.3-19.47,19.97-19.47ZM84.07,27.98c-.5-4.29-3.36-6.59-7.52-6.59-5.44,0-7.73,2.79-8.59,6.59h16.11Z"/>
              <path className="cls-1" d="M98.75,49.82V14.16c0-.27.22-.49.49-.49h10.47c.27,0,.49.22.49.49v4.23c2.51-3.94,6.23-5.87,11.02-5.87,7.01,0,13.03,4.8,13.03,15.53v21.77c0,.27-.22.49-.49.49h-10.47c-.27,0-.49-.22-.49-.49v-20.12c0-4.8-2.51-7.44-6.16-7.44-3.94,0-6.44,2.58-6.44,8.45v19.12c0,.27-.22.49-.49.49h-10.47c-.27,0-.49-.22-.49-.49Z"/>
              <path className="cls-1" d="M134.95,13.66h11.1c.22,0,.41.14.47.35l8.34,27.64,8.34-27.64c.06-.21.25-.35.47-.35h11.1c.34,0,.58.34.46.66l-12.77,35.53c-.1.27-.36.46-.65.46h-13.92c-.29,0-.55-.18-.65-.46l-12.77-35.53c-.12-.32.12-.66.46-.66Z"/>
              <path className="cls-1" d="M199.53,49.82v-5.59c-1.79,3.72-5.8,7.23-12.03,7.23-7.23,0-12.6-4.58-12.6-11.02,0-6.8,4.51-11.88,14.39-11.88h5.73c3.15,0,4.01-2.29,3.72-3.79-.43-2.58-2.72-3.94-5.94-3.94-4.07,0-6.53,2.25-6.84,5.34-.03.28-.29.48-.57.44l-9.71-1.62c-.27-.04-.46-.3-.41-.57,1.58-8.45,9.59-11.89,17.81-11.89s17.32,2,17.32,17.18v20.12c0,.27-.22.49-.49.49h-9.9c-.27,0-.49-.22-.49-.49ZM190.87,43.16c4.58,0,7.73-3.44,8.09-7.73h-6.94c-4.22,0-5.73,1.72-5.65,4.08.07,2.51,2.08,3.65,4.51,3.65Z"/>
              <path className="cls-1" d="M212.13,22.33v-8.18c0-.27.22-.49.49-.49h4.09c1.9,0,3.44-1.54,3.44-3.44V3.85c0-.27.22-.49.49-.49h9.32c.27,0,.49.22.49.49v9.81h7.52c.27,0,.49.22.49.49v8.18c0,.27-.22.49-.49.49h-7.52v13.24c0,4.31,3.67,6.07,7.5,4.71.25-.09.52.1.52.37v8.63c0,.32-.21.6-.52.67-.99.23-2.36.44-3.99.44-8.88,0-14.96-3.01-14.96-15.89v-12.17h-6.38c-.27,0-.49-.22-.49-.49Z"/>
              <path className="cls-1" d="M280.28,31.99c0,10.74-7.59,19.47-20.04,19.47s-20.04-8.73-20.04-19.47,7.59-19.47,20.04-19.47,20.04,8.73,20.04,19.47ZM268.82,31.99c0-5.3-2.93-9.73-8.59-9.73s-8.59,4.44-8.59,9.73,2.93,9.73,8.59,9.73,8.59-4.44,8.59-9.73Z"/>
            </g>
            <g>
              <circle className="cls-2" cx="25.56" cy="61.14" r="2.86"/>
              <path className="cls-2" d="M42,41.64l-16.13,1.73c-.3.03-.45-.34-.21-.53l15.78-12.29c1.02-.84,1.68-2.14,1.4-3.54-.28-2.14-2.05-3.54-4.29-3.26l-17.15,2.51c-.3.04-.46-.34-.22-.53l17-12.98c3.35-2.61,3.63-7.73.56-10.71-2.79-2.79-7.27-2.7-10.06.09L1.29,30c-1.02,1.12-1.49,2.61-1.21,4.19.47,2.52,2.98,4.19,5.5,3.73l14.77-3.01c.32-.07.49.36.22.54l-16.38,10.49c-2.05,1.3-2.98,3.63-2.33,5.96.65,3.07,3.73,4.84,6.71,4.1l24.49-6.03c.28-.07.48.25.3.47l-3.82,4.72c-1.02,1.3.65,3.07,2.05,2.05l12.58-10.34c2.24-1.86.75-5.5-2.14-5.22Z"/>
            </g>
          </svg>
        </div>
        
        <nav className="categories-nav" style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.9rem', color: '#666', flex: '1 1 auto', marginLeft: '2rem' }}>
          {['Gen AI', 'Video Templates', 'Stock Video', 'Audio', 'Graphics', 'Design Templates', 'Photos', '3D', 'More'].map((cat, idx) => (
            <span key={idx} className="nav-item" style={{ cursor: 'pointer', transition: 'all 0.15s ease' }}>{cat}</span>
          ))}
        </nav>
        
        <nav className="nav" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', fontSize: '0.95rem', color: '#333' }}>
          <span className="nav-item" style={{ cursor: 'pointer', transition: 'all 0.15s ease' }}>License</span>
          <span className="nav-item" style={{ cursor: 'pointer', transition: 'all 0.15s ease' }}>Enterprise</span>
          <span className="nav-item" style={{ cursor: 'pointer', transition: 'all 0.15s ease' }}>Pricing</span>
          <button className="cta-btn" style={{
            background: '#87E64B', color: '#1A4200', border: 'none', padding: '0.6rem 1.2rem',
            borderRadius: '20px', cursor: 'pointer', fontWeight: 600, 
            transition: 'background-color 0.15s cubic-bezier(0.42, 0, 0.58, 1), box-shadow 0.15s cubic-bezier(0.42, 0, 0.58, 1), color 0.15s cubic-bezier(0.42, 0, 0.58, 1)'
          }}>Get unlimited downloads</button>
          <span className="profile-icon" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
            <svg width="24" height="24" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" fill="#191919"/>
              <circle cx="16" cy="11" r="4" fill="#fff"/>
              <path d="M7 23.5C8.5 20.5 12 18.5 16 18.5C20 18.5 23.5 20.5 25 23.5C23 26.5 20 27.5 16 27.5C12 27.5 9 26.5 7 23.5Z" fill="#fff"/>
            </svg>
          </span>
        </nav>
      </header>

      {/* Main Content Area mirroring Envato */}
      <main className="main-content" style={{ padding: '3rem', maxWidth: '1400px', margin: '0 auto' }}>
         {/* Hero Section with pricing block */}
         <section className="hero" style={{ display: 'flex', gap: '4rem', marginBottom: '4rem', width: '100%' }}>
           <div className="hero-text" style={{ width: '100%' }}>
             <h1 style={{ fontSize: '3.5rem', fontWeight: 700, lineHeight: 1.1, margin: '0 0 1.5rem 0' }}>Unlimited creativity, all in one place</h1>
             <p style={{ fontSize: '1.2rem', color: '#666', margin: 0 }}>Join Envato Elements and download assets as fast as you can click.</p>
             
             <div className="search-container" style={{ marginTop: '2rem', position: 'relative', width: '100%', maxWidth: '100%' }}>
                <div className="search-bar-wrapper" style={{
                  display: 'flex', alignItems: 'center', background: '#fff', borderRadius: '30px',
                  border: '1px solid #ccc', padding: '0.4rem 1rem', width: '100%'
                }}>
                   <div className="category-select" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', paddingRight: '0.8rem', borderRight: '1px solid #ddd', fontSize: '0.9rem', color: '#333', cursor: 'pointer' }}>
                      All Items <span style={{ fontSize: '0.8rem' }}>▼</span>
                   </div>
                   <div className="search-icon" style={{ cursor: 'pointer', color: '#000', padding: '0.5rem', marginLeft: '0.5rem', display: 'flex', alignItems: 'center' }}><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg></div>
                   <input 
                     type="text" 
                     placeholder="Search assets..." 
                     value={query}
                     onChange={(e) => {
                       setQuery(e.target.value)
                       setShowSuggestions(true)
                     }}
                     onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                     onKeyDown={(e) => {
                       if (e.key === 'Enter') {
                         handleSearch(e)
                       }
                     }}
                     style={{ border: 'none', outline: 'none', padding: '0.5rem 1rem', flex: '1', fontSize: '1rem' }}
                   />
                   {query && <div style={{ cursor: 'pointer', color: '#000', padding: '0.5rem', display: 'flex', alignItems: 'center' }} onClick={() => setQuery('')}><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></div>}
                   <div style={{ display: 'flex', gap: '0.5rem', marginLeft: 'auto', paddingRight: '0.5rem', alignItems: 'center' }}>
                      <div style={{ width: '1px', height: '20px', background: '#ddd', marginRight: '0.5rem' }}></div>
                      <span title="Sounds Like" style={{ cursor: 'pointer', padding: '0.3rem', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000' }}><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg></span>
                      <span title="Looks Like" style={{ cursor: 'pointer', padding: '0.3rem', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000' }}><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><circle cx="12" cy="13" r="3"></circle></svg></span>
                   </div>
                </div>
                {showSuggestions && query && (
                  <div className="suggestions-complex" style={{
                    position: 'absolute', top: 'calc(100% + 5px)', left: 0, width: '850px',
                    background: '#fff', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                    border: '1px solid #ccc', overflow: 'hidden', display: 'flex', flexDirection: 'column',
                    zIndex: 1000
                  }}>
                    <div className="dropdown-body" style={{ display: 'flex' }}>
                      <div className="suggestions-list" style={{ flex: '1', borderRight: '1px solid #eee', padding: '1rem 0' }}>
                        {[
                          { text: 'abstract', category: 'Stock Video' },
                          { text: 'abstract background', category: 'Stock Video' },
                          { text: 'abstract', category: 'Graphics' },
                          { text: 'abstract background', category: 'Graphics' },
                          { text: 'abstract', category: '' },
                          { text: 'abstract background', category: '' }
                        ].map((item, idx) => (
                          <div key={idx} className="suggestion-item" onClick={() => setQuery(item.text)} style={{
                            padding: '0.6rem 1.5rem', cursor: 'pointer', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem',
                            transition: 'background 0.2s'
                          }} onMouseOver={(e) => e.currentTarget.style.background = '#f9f9f9'} onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}>
                            <span style={{ color: '#999' }}>🔍</span>
                            <span>
                              <strong>{item.text}</strong>
                              {item.category && <span style={{ color: '#666' }}> in {item.category}</span>}
                            </span>
                          </div>
                        ))}
                      </div>
                      <div className="looks-like-card" style={{ width: '300px', padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', background: '#fafafa' }}>
                         <div style={{ fontSize: '3rem', marginBottom: '1rem', border: '2px dashed #ddd', borderRadius: '8px', padding: '1rem', width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#000' }}><svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg></div>
                         <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1.1rem', fontWeight: 600 }}>Looks Like Search</h4>
                         <p style={{ margin: 0, color: '#666', fontSize: '0.85rem' }}>Click to add image or drag and drop to find similar photos</p>
                      </div>
                    </div>
                       <div className="dropdown-footer" style={{ background: '#fff', padding: '0.8rem 1.5rem', borderTop: '1px solid #eee', fontSize: '0.9rem', color: '#333', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ color: '#000', display: 'flex', alignItems: 'center' }}><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg></span> Got a song in mind? <strong style={{ cursor: 'pointer' }}>Search with 'Sounds Like'</strong>
                       </div>
                  </div>
                )}
              </div>
           </div>
           
           

         </section>

         {/* AI Tools Section */}
         <section className="ai-tools" style={{ marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '1.5rem' }}>Suite of AI tools</h2>
            <div className="horizontal-scroll" style={{ display: 'flex', gap: '1.5rem', overflowX: 'auto', paddingBottom: '1rem' }}>
               {['VideoGen', 'ImageGen', 'VoiceGen', 'CodeGen'].map((tool, idx) => (
                  <div key={idx} style={{
                    flex: '0 0 200px', background: '#fff', padding: '1.5rem',
                    borderRadius: '12px', border: '1px solid #eee', textAlign: 'center', cursor: 'pointer'
                  }}>{tool}</div>
               ))}
            </div>
         </section>

         {/* Categories Grid */}
         <section className="categories-grid" style={{ marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '1.5rem' }}>Search Results</h2>
            {loading && <p>Loading...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <div className="grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
              {searchResults.length > 0 ? (
                searchResults.map((item: any) => (
                  <div key={item.asset_id} className="card" style={{ background: '#fff', borderRadius: '12px', overflow: 'hidden', border: '1px solid #eee', cursor: 'none' }}
                    onMouseMove={(e) => setCursorPos({ x: e.clientX, y: e.clientY })}
                    onMouseEnter={() => setCursorVisible(true)}
                    onMouseLeave={() => setCursorVisible(false)}>
                    <img src={item.thumb_url || '/website_template_mockup.png'} alt={item.title} style={{ width: '100%', height: '200px', objectFit: 'cover' }} />
                    <div className="card-info" style={{ padding: '1.2rem' }}>
                      <h3 style={{ margin: '0 0 0.3rem 0', fontSize: '1.2rem' }}>{item.title}</h3>
                      <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>Score: {item.score}</p>
                    </div>
                  </div>
                ))
              ) : (
                !loading && <p>No results found or type to search.</p>
              )}
            </div>
         </section>
      </main>

      {/* Full Footer */}
      <footer className="footer" style={{ background: '#fff', padding: '3rem', borderTop: '1px solid #eee', marginTop: 'auto' }}>
        <div className="footer-columns" style={{ display: 'flex', justifyContent: 'space-between', gap: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
           <div className="footer-col" style={{ flex: '1' }}>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Discover</h4>
              <p style={{ color: '#666', fontSize: '0.9rem', margin: '0.5rem 0', cursor: 'pointer' }}>Templates</p>
              <p style={{ color: '#666', fontSize: '0.9rem', margin: '0.5rem 0', cursor: 'pointer' }}>Stock Video</p>
           </div>
           <div className="footer-col" style={{ flex: '1' }}>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>License</h4>
              <p style={{ color: '#666', fontSize: '0.9rem', margin: '0.5rem 0', cursor: 'pointer' }}>Terms</p>
              <p style={{ color: '#666', fontSize: '0.9rem', margin: '0.5rem 0', cursor: 'pointer' }}>Types</p>
           </div>
           <div className="footer-col" style={{ flex: '1' }}>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Resources</h4>
              <p style={{ color: '#666', fontSize: '0.9rem', margin: '0.5rem 0', cursor: 'pointer' }}>Blog</p>
              <p style={{ color: '#666', fontSize: '0.9rem', margin: '0.5rem 0', cursor: 'pointer' }}>Help Center</p>
           </div>
        </div>
        <div className="footer-bottom" style={{ textAlign: 'center', marginTop: '3rem', borderTop: '1px solid #eee', paddingTop: '1.5rem', color: '#999', fontSize: '0.85rem' }}>
           <p>&copy; 2026 Sovereign Elements. All rights reserved.</p>
        </div>
      </footer>
      
      {cursorVisible && (
        <div style={{
          position: 'fixed', top: cursorPos.y - 20, left: cursorPos.x - 20,
          width: '40px', height: '40px', borderRadius: '50%', background: '#87E64B',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          pointerEvents: 'none', zIndex: 9999, color: '#000', fontWeight: 'bold',
          fontSize: '1.2rem', transition: 'transform 0.1s ease'
        }}>
          →
        </div>
      )}
    </div>
  )
}

export default App
