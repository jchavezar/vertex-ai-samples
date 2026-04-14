import React, { useState, useRef, useEffect, useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Upload,
  FileText,
  MessageSquare,
  Database,
  GitBranch,
  Clock,
  Image as ImageIcon,
  Search,
  Trash2,
  Send,
  Loader2,
  Network,
  BarChart3,
  Trophy,
} from 'lucide-react'

interface Document {
  document_name: string
  parent_count: number
  child_count: number
}

interface ParentSegment {
  parent_id: string
  document_name: string
  page_number: number
  heading: string | null
  agent_name: string | null
  content: string
}

interface ChildChunk {
  chunk_id: string
  parent_id: string
  content: string
  page_number: number
  entity_type: string
}

interface Trace {
  agent_name: string
  page_number: number
  start_time: string
  end_time: string
  duration_seconds: number
  sections_extracted: number
}

interface QueryTrace {
  step: string
  description: string
  duration_ms: number
  details: string
}

interface SimpleResult {
  source_num: number
  chunk_id: string
  content: string
  document_name: string
  page_number: number
  similarity: number
}

interface RetrievalResult {
  source_num: number
  parent_id: string
  parent_content: string
  matched_child: string
  agent_name: string | null
  heading: string | null
  similarity: number
  document_name: string
  page_number: number
  related_agents: string[]
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  retrieval?: RetrievalResult[]
}

interface GroundedSpan {
  text: string
  is_grounded: boolean
  source_id: string | null
  confidence: number
}

interface Scores {
  faithfulness: number
  groundedness: number
  completeness: number
  answer_relevance: number
  context_precision: number
  total: number
}

interface Grounding {
  grounded_percentage: number
  ungrounded_percentage: number
  grounded_spans: GroundedSpan[]
  hallucination_count: number
  hallucination_examples: string[]
}

interface EvaluationResult {
  query: string
  hierarchical: {
    answer: string
    context_chars: number
    sources: number
    latency_ms: number
    scores?: Scores
    grounding?: Grounding
    reasoning?: string
  }
  simple: {
    answer: string
    context_chars: number
    sources: number
    latency_ms: number
    scores?: Scores
    grounding?: Grounding
    reasoning?: string
  }
  evaluation: {
    a_score: number
    b_score: number
    winner: 'A' | 'B' | 'TIE'
    winner_label: string
    reason: string
  }
  total_latency_ms: number
}

interface PipelineData {
  parents: ParentSegment[]
  children: ChildChunk[]
  traces: Trace[]
  annotated_images: string[]
  relationships: [string, string, string][]
}

interface GraphNode {
  id: string
  label: string
  documents: string[]
  x: number
  y: number
  connections: string[]
}

interface GraphEdge {
  source: string
  target: string
  type: string
}

type Tab = 'hierarchy' | 'graph' | 'data' | 'images' | 'traces' | 'retrieval'

// Agent color palette
const AGENT_COLORS: Record<string, string> = {
  orchestrator: '#a855f7',
  auth_agent: '#06b6d4',
  payment_gateway: '#22c55e',
  risk_engine: '#f97316',
  billing_agent: '#eab308',
  refund_handler: '#ec4899',
  notification_agent: '#8b5cf6',
  data_pipeline: '#14b8a6',
  monitoring_agent: '#ef4444',
}

// Document color mapping
const DOC_COLORS: Record<string, string> = {
  system_architecture: '#a855f7',
  operations_manual: '#22c55e',
  troubleshooting_guide: '#ef4444',
}

function App() {
  const [view, setView] = useState<'upload' | 'dashboard'>('upload')
  const [documents, setDocuments] = useState<Document[]>([])
  const [activeTab, setActiveTab] = useState<Tab>('hierarchy')
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const [pipelineData, setPipelineData] = useState<PipelineData | null>(null)
  const [retrievalResults, setRetrievalResults] = useState<RetrievalResult[]>([])
  const [queryTraces, setQueryTraces] = useState<QueryTrace[]>([])
  const [simpleResults, setSimpleResults] = useState<SimpleResult[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [hoveredEdge, setHoveredEdge] = useState<string | null>(null)
  const [graphData, setGraphData] = useState<{ agents: Array<{agent_name: string, document_name: string}>, relationships: Array<[string, string, string]> } | null>(null)
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null)
  const [evaluating, setEvaluating] = useState(false)
  const [lastQuery, setLastQuery] = useState('')

  const fileInputRef = useRef<HTMLInputElement>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Create ADK session on app load (pre-warm for faster first query)
  const createSession = async () => {
    try {
      const res = await fetch('/api/session', { method: 'POST' })
      const data = await res.json()
      if (data.session_id) {
        setSessionId(data.session_id)
        console.log('[ADK] Session created:', data.session_id)
      }
    } catch (err) {
      console.error('Failed to create session:', err)
    }
  }

  useEffect(() => {
    fetchDocuments()
    fetchGraphData()
    createSession()  // Pre-create ADK session on app load
  }, [])

  const fetchGraphData = async () => {
    try {
      const res = await fetch('/api/graph')
      const data = await res.json()
      setGraphData(data)
    } catch (err) {
      console.error('Failed to fetch graph data:', err)
    }
  }

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/documents')
      const data = await res.json()
      setDocuments(data.documents || [])
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    }
  }

  // Extract agents and relationships from API graph data
  const { graphNodes, graphEdges } = useMemo(() => {
    if (!graphData) return { graphNodes: [], graphEdges: [] }

    const agentMap = new Map<string, { documents: Set<string>; connections: Set<string> }>()
    const edges: GraphEdge[] = []

    // Extract agents from API data
    graphData.agents.forEach((agent) => {
      if (agent.agent_name) {
        const agentKey = agent.agent_name.toLowerCase().replace(/\s+/g, '_')
        if (!agentMap.has(agentKey)) {
          agentMap.set(agentKey, { documents: new Set(), connections: new Set() })
        }
        agentMap.get(agentKey)!.documents.add(agent.document_name)
      }
    })

    // Add relationships from API data
    graphData.relationships.forEach(([source, target, type]) => {
      const sourceKey = source.toLowerCase().replace(/\s+/g, '_')
      const targetKey = target.toLowerCase().replace(/\s+/g, '_')

      // Ensure both agents exist in the map
      if (!agentMap.has(sourceKey)) {
        agentMap.set(sourceKey, { documents: new Set(), connections: new Set() })
      }
      if (!agentMap.has(targetKey)) {
        agentMap.set(targetKey, { documents: new Set(), connections: new Set() })
      }

      agentMap.get(sourceKey)!.connections.add(targetKey)
      edges.push({ source: sourceKey, target: targetKey, type })
    })

    // Predefined layout for better visualization
    const agentPositions: Record<string, { x: number; y: number }> = {
      orchestrator: { x: 400, y: 80 },
      auth_agent: { x: 200, y: 180 },
      payment_gateway: { x: 600, y: 180 },
      risk_engine: { x: 300, y: 280 },
      billing_agent: { x: 500, y: 280 },
      refund_handler: { x: 200, y: 380 },
      notification_agent: { x: 400, y: 380 },
      data_pipeline: { x: 600, y: 380 },
      monitoring_agent: { x: 400, y: 480 },
    }

    const nodes: GraphNode[] = Array.from(agentMap.entries()).map(([id, data]) => ({
      id,
      label: id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      documents: Array.from(data.documents),
      x: agentPositions[id]?.x || Math.random() * 600 + 100,
      y: agentPositions[id]?.y || Math.random() * 400 + 50,
      connections: Array.from(data.connections),
    }))

    return { graphNodes: nodes, graphEdges: edges }
  }, [graphData])

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return

    setLoading(true)
    const formData = new FormData()
    for (const file of files) {
      formData.append('files', file)
    }
    formData.append('session_id', sessionId)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()

      setSessionId(data.session_id)
      if (data.pipeline_data) {
        setPipelineData(data.pipeline_data)
      }
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response },
      ])
      setView('dashboard')
      fetchDocuments()
    } catch (err) {
      console.error('Upload failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEvaluate = async () => {
    if (!lastQuery || evaluating) return

    setEvaluating(true)
    setEvaluationResult(null)

    try {
      const formData = new FormData()
      formData.append('query', lastQuery)

      const res = await fetch('/api/evaluate', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) throw new Error(`Server error: ${res.status}`)

      const data = await res.json()
      setEvaluationResult(data)
    } catch (err) {
      console.error('Evaluation failed:', err)
    } finally {
      setEvaluating(false)
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setLastQuery(userMessage)  // Store for evaluation
    setEvaluationResult(null)  // Clear previous evaluation
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    const formData = new FormData()
    formData.append('message', userMessage)
    formData.append('session_id', sessionId)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`)
      }

      const data = await res.json()

      if (data.session_id) {
        setSessionId(data.session_id)
      }
      if (data.retrieval_results) {
        setRetrievalResults(data.retrieval_results)
      }
      if (data.query_traces) {
        setQueryTraces(data.query_traces)
      }
      if (data.simple_results) {
        setSimpleResults(data.simple_results)
      }
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response || 'No response received',
          retrieval: data.retrieval_results,
        },
      ])
    } catch (err) {
      console.error('Chat failed:', err)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${err instanceof Error ? err.message : 'Failed to get response'}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleLoadDocument = async (docName: string) => {
    setLoading(true)
    setSessionId('') // Reset session for new document
    setMessages([])  // Clear previous messages
    try {
      const res = await fetch(`/api/documents/${encodeURIComponent(docName)}/data`)
      const data = await res.json()

      setPipelineData({
        parents: data.parents || [],
        children: data.children || [],
        traces: [],
        annotated_images: [],
        relationships: [],
      })
      setView('dashboard')
    } catch (err) {
      console.error('Failed to load document:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDocument = async (docName: string) => {
    if (!confirm(`Delete ${docName} and all its data?`)) return

    try {
      await fetch(`/api/documents/${encodeURIComponent(docName)}`, {
        method: 'DELETE',
      })
      fetchDocuments()
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  const renderCitations = (text: React.ReactNode): React.ReactNode => {
    // Handle non-string children (React elements)
    if (typeof text !== 'string') {
      if (Array.isArray(text)) {
        return text.map((item, i) => <span key={i}>{renderCitations(item)}</span>)
      }
      return text
    }

    const parts = text.split(/(\[\d+\])/)
    return parts.map((part, i) => {
      const match = part.match(/\[(\d+)\]/)
      if (match) {
        return (
          <span
            key={i}
            className="citation"
            onClick={() => setActiveTab('retrieval')}
          >
            {match[1]}
          </span>
        )
      }
      return <span key={i}>{part}</span>
    })
  }

  const getNodeColor = (node: GraphNode) => {
    return AGENT_COLORS[node.id] || '#6b7280'
  }

  const isNodeHighlighted = (nodeId: string) => {
    if (!selectedAgent) return true
    if (nodeId === selectedAgent) return true
    const selectedNode = graphNodes.find((n) => n.id === selectedAgent)
    if (selectedNode?.connections.includes(nodeId)) return true
    const connectedToSelected = graphNodes.find(
      (n) => n.id === nodeId && n.connections.includes(selectedAgent)
    )
    return !!connectedToSelected
  }

  const isEdgeHighlighted = (edge: GraphEdge) => {
    if (!selectedAgent) return true
    return edge.source === selectedAgent || edge.target === selectedAgent
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <GitBranch size={24} />
          <h1>Hierarchical RAG</h1>
        </div>

        <button
          onClick={async () => {
            setView('upload')
            setPipelineData(null)
            setMessages([])
            setRetrievalResults([])
            setQueryTraces([])
            setSimpleResults([])
            setSelectedAgent(null)
            // Create new ADK session
            await createSession()
          }}
          style={{
            width: '100%',
            padding: '12px',
            marginBottom: '16px',
            background: 'linear-gradient(135deg, var(--aurora-purple), var(--aurora-violet))',
            border: 'none',
            borderRadius: '8px',
            color: 'white',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          + New Session
        </button>

        <div className="doc-list">
          <h3 style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
            INDEXED DOCUMENTS
          </h3>
          {documents.length === 0 ? (
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              No documents indexed yet
            </p>
          ) : (
            documents.map((doc) => (
              <div key={doc.document_name} className="doc-item">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div onClick={() => handleLoadDocument(doc.document_name)} style={{ flex: 1 }}>
                    <h3>{doc.document_name}</h3>
                    <p>
                      {doc.parent_count} parents, {doc.child_count} children
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteDocument(doc.document_name)
                    }}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--aurora-pink)',
                      cursor: 'pointer',
                      padding: '4px',
                    }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <AnimatePresence mode="wait">
          {view === 'upload' ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="upload-zone"
            >
              <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                <h1 style={{ fontSize: '32px', marginBottom: '12px' }}>
                  Parent-Child RAG Pipeline
                </h1>
                <p style={{ color: 'var(--text-secondary)', maxWidth: '600px' }}>
                  Upload documents to extract hierarchical segments. Children are embedded for
                  precision search, parents provide full context to the LLM.
                </p>
              </div>

              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => handleFileUpload(e.target.files)}
                accept=".pdf"
                multiple
                style={{ display: 'none' }}
              />

              <div
                className={`upload-dropzone ${dragOver ? 'dragover' : ''}`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => {
                  e.preventDefault()
                  setDragOver(true)
                }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault()
                  setDragOver(false)
                  handleFileUpload(e.dataTransfer.files)
                }}
              >
                {loading ? (
                  <>
                    <Loader2 size={48} className="upload-icon" style={{ animation: 'spin 1s linear infinite' }} />
                    <h2>Processing Document...</h2>
                    <p>Extracting sections, generating embeddings, building hierarchy</p>
                  </>
                ) : (
                  <>
                    <Upload size={48} className="upload-icon" />
                    <h2>Drop PDF files here</h2>
                    <p>or click to browse</p>
                  </>
                )}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="dashboard"
            >
              {/* Results Panel */}
              <div className="results-panel">
                <div className="tabs">
                  <button
                    className={`tab ${activeTab === 'hierarchy' ? 'active' : ''}`}
                    onClick={() => setActiveTab('hierarchy')}
                  >
                    <GitBranch size={14} style={{ marginRight: '6px' }} />
                    Hierarchy
                  </button>
                  <button
                    className={`tab ${activeTab === 'graph' ? 'active' : ''}`}
                    onClick={() => setActiveTab('graph')}
                  >
                    <Network size={14} style={{ marginRight: '6px' }} />
                    Graph
                  </button>
                  <button
                    className={`tab ${activeTab === 'data' ? 'active' : ''}`}
                    onClick={() => setActiveTab('data')}
                  >
                    <Database size={14} style={{ marginRight: '6px' }} />
                    Data
                  </button>
                  <button
                    className={`tab ${activeTab === 'images' ? 'active' : ''}`}
                    onClick={() => setActiveTab('images')}
                  >
                    <ImageIcon size={14} style={{ marginRight: '6px' }} />
                    Pages
                  </button>
                  <button
                    className={`tab ${activeTab === 'traces' ? 'active' : ''}`}
                    onClick={() => setActiveTab('traces')}
                  >
                    <Clock size={14} style={{ marginRight: '6px' }} />
                    Traces
                  </button>
                  <button
                    className={`tab ${activeTab === 'retrieval' ? 'active' : ''}`}
                    onClick={() => setActiveTab('retrieval')}
                  >
                    <Search size={14} style={{ marginRight: '6px' }} />
                    Retrieval
                  </button>
                </div>

                <div className="tab-content">
                  {activeTab === 'hierarchy' && pipelineData && (
                    <div className="hierarchy-view">
                      {pipelineData.parents.length === 0 ? (
                        <div className="empty-state">
                          <GitBranch size={48} />
                          <h3>No hierarchy data</h3>
                          <p>Upload a document to see parent-child structure</p>
                        </div>
                      ) : (
                        pipelineData.parents.map((parent) => {
                          const children = pipelineData.children.filter(
                            (c) => c.parent_id === parent.parent_id
                          )
                          return (
                            <div key={parent.parent_id} className="parent-segment">
                              <div className="parent-header">
                                <span className="parent-badge">PARENT</span>
                                <h3>{parent.heading || parent.parent_id}</h3>
                                {parent.agent_name && (
                                  <span
                                    className="agent-tag"
                                    style={{
                                      backgroundColor:
                                        AGENT_COLORS[parent.agent_name.toLowerCase().replace(/\s+/g, '_')] ||
                                        'var(--aurora-cyan)',
                                    }}
                                  >
                                    {parent.agent_name}
                                  </span>
                                )}
                              </div>
                              <div className="parent-content">
                                {parent.content}
                              </div>
                              {children.length > 0 && (
                                <div className="children-section">
                                  <div className="children-label">
                                    {children.length} Child Chunk{children.length > 1 ? 's' : ''}
                                  </div>
                                  {children.map((child) => (
                                    <div key={child.chunk_id} className="child-chunk">
                                      <strong>{child.chunk_id}</strong>: {child.content.slice(0, 150)}...
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          )
                        })
                      )}
                    </div>
                  )}

                  {activeTab === 'graph' && (
                    <div className="graph-view">
                      {graphNodes.length === 0 ? (
                        <div className="empty-state">
                          <Network size={48} />
                          <h3>No relationship data</h3>
                          <p>Upload documents with agent relationships to see the graph</p>
                        </div>
                      ) : (
                        <>
                          {/* Legend */}
                          <div className="graph-legend">
                            <h4>Document Sources</h4>
                            <div className="legend-items">
                              {Object.entries(DOC_COLORS).map(([doc, color]) => (
                                <div key={doc} className="legend-item">
                                  <span
                                    className="legend-color"
                                    style={{ backgroundColor: color }}
                                  />
                                  <span>{doc.replace(/_/g, ' ')}</span>
                                </div>
                              ))}
                            </div>
                            <h4 style={{ marginTop: '16px' }}>Agents</h4>
                            <div className="legend-items">
                              {Object.entries(AGENT_COLORS).map(([agent, color]) => (
                                <div
                                  key={agent}
                                  className={`legend-item clickable ${selectedAgent === agent ? 'selected' : ''}`}
                                  onClick={() =>
                                    setSelectedAgent(selectedAgent === agent ? null : agent)
                                  }
                                >
                                  <span
                                    className="legend-color"
                                    style={{ backgroundColor: color }}
                                  />
                                  <span>{agent.replace(/_/g, ' ')}</span>
                                </div>
                              ))}
                            </div>
                            {selectedAgent && (
                              <button
                                className="clear-selection"
                                onClick={() => setSelectedAgent(null)}
                              >
                                Clear Selection
                              </button>
                            )}
                          </div>

                          {/* Graph SVG */}
                          <svg className="graph-svg" viewBox="0 0 800 550">
                            <defs>
                              <marker
                                id="arrowhead"
                                markerWidth="10"
                                markerHeight="7"
                                refX="9"
                                refY="3.5"
                                orient="auto"
                              >
                                <polygon points="0 0, 10 3.5, 0 7" fill="var(--text-secondary)" />
                              </marker>
                              <marker
                                id="arrowhead-highlighted"
                                markerWidth="10"
                                markerHeight="7"
                                refX="9"
                                refY="3.5"
                                orient="auto"
                              >
                                <polygon points="0 0, 10 3.5, 0 7" fill="var(--aurora-cyan)" />
                              </marker>
                              <filter id="glow">
                                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                                <feMerge>
                                  <feMergeNode in="coloredBlur" />
                                  <feMergeNode in="SourceGraphic" />
                                </feMerge>
                              </filter>
                            </defs>

                            {/* Edges */}
                            {graphEdges.map((edge, idx) => {
                              const source = graphNodes.find((n) => n.id === edge.source)
                              const target = graphNodes.find((n) => n.id === edge.target)
                              if (!source || !target) return null

                              const highlighted = isEdgeHighlighted(edge)
                              const edgeId = `${edge.source}-${edge.target}`

                              // Calculate curve for multiple edges
                              const dx = target.x - source.x
                              const dy = target.y - source.y
                              const midX = (source.x + target.x) / 2
                              const midY = (source.y + target.y) / 2
                              const offset = 20
                              const perpX = -dy / Math.sqrt(dx * dx + dy * dy) * offset
                              const perpY = dx / Math.sqrt(dx * dx + dy * dy) * offset

                              return (
                                <g key={idx}>
                                  <path
                                    d={`M ${source.x} ${source.y} Q ${midX + perpX} ${midY + perpY} ${target.x} ${target.y}`}
                                    fill="none"
                                    stroke={
                                      highlighted
                                        ? hoveredEdge === edgeId
                                          ? 'var(--aurora-cyan)'
                                          : 'var(--text-secondary)'
                                        : 'var(--border-subtle)'
                                    }
                                    strokeWidth={highlighted ? 2 : 1}
                                    strokeDasharray={edge.type === 'depends_on' ? '5,5' : undefined}
                                    markerEnd={
                                      highlighted
                                        ? hoveredEdge === edgeId
                                          ? 'url(#arrowhead-highlighted)'
                                          : 'url(#arrowhead)'
                                        : undefined
                                    }
                                    opacity={highlighted ? 1 : 0.2}
                                    onMouseEnter={() => setHoveredEdge(edgeId)}
                                    onMouseLeave={() => setHoveredEdge(null)}
                                    style={{ cursor: 'pointer' }}
                                  />
                                  {hoveredEdge === edgeId && (
                                    <text
                                      x={midX + perpX}
                                      y={midY + perpY - 10}
                                      fill="var(--aurora-cyan)"
                                      fontSize="11"
                                      textAnchor="middle"
                                    >
                                      {edge.type}
                                    </text>
                                  )}
                                </g>
                              )
                            })}

                            {/* Nodes */}
                            {graphNodes.map((node) => {
                              const highlighted = isNodeHighlighted(node.id)
                              const isSelected = selectedAgent === node.id

                              return (
                                <g
                                  key={node.id}
                                  transform={`translate(${node.x}, ${node.y})`}
                                  onClick={() =>
                                    setSelectedAgent(selectedAgent === node.id ? null : node.id)
                                  }
                                  style={{ cursor: 'pointer' }}
                                  opacity={highlighted ? 1 : 0.3}
                                  filter={isSelected ? 'url(#glow)' : undefined}
                                >
                                  {/* Document indicator rings */}
                                  {node.documents.map((doc, docIdx) => {
                                    const docKey = doc.replace('.pdf', '').toLowerCase()
                                    const radius = 28 + docIdx * 6
                                    return (
                                      <circle
                                        key={doc}
                                        r={radius}
                                        fill="none"
                                        stroke={DOC_COLORS[docKey] || '#6b7280'}
                                        strokeWidth={3}
                                        strokeDasharray={docIdx > 0 ? '8,4' : undefined}
                                        opacity={0.6}
                                      />
                                    )
                                  })}

                                  {/* Main node */}
                                  <circle
                                    r={22}
                                    fill={getNodeColor(node)}
                                    stroke={isSelected ? '#fff' : 'transparent'}
                                    strokeWidth={3}
                                  />

                                  {/* Node label */}
                                  <text
                                    y={45}
                                    fill="var(--text-primary)"
                                    fontSize="11"
                                    fontWeight="500"
                                    textAnchor="middle"
                                  >
                                    {node.label}
                                  </text>

                                  {/* Connection count badge */}
                                  <circle cx={16} cy={-16} r={10} fill="var(--bg-card)" stroke={getNodeColor(node)} strokeWidth={2} />
                                  <text x={16} y={-12} fill="var(--text-primary)" fontSize="10" textAnchor="middle">
                                    {node.connections.length}
                                  </text>
                                </g>
                              )
                            })}
                          </svg>

                          {/* Selected agent details */}
                          {selectedAgent && (
                            <div className="agent-details">
                              <h3>
                                <span
                                  className="agent-color-dot"
                                  style={{ backgroundColor: AGENT_COLORS[selectedAgent] }}
                                />
                                {selectedAgent.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                              </h3>
                              <div className="agent-connections">
                                <h4>Connects To:</h4>
                                <div className="connection-tags">
                                  {graphNodes
                                    .find((n) => n.id === selectedAgent)
                                    ?.connections.map((conn) => (
                                      <span
                                        key={conn}
                                        className="connection-tag"
                                        style={{ borderColor: AGENT_COLORS[conn] }}
                                        onClick={() => setSelectedAgent(conn)}
                                      >
                                        {conn.replace(/_/g, ' ')}
                                      </span>
                                    ))}
                                </div>
                                <h4>Connected From:</h4>
                                <div className="connection-tags">
                                  {graphNodes
                                    .filter((n) => n.connections.includes(selectedAgent))
                                    .map((n) => (
                                      <span
                                        key={n.id}
                                        className="connection-tag"
                                        style={{ borderColor: AGENT_COLORS[n.id] }}
                                        onClick={() => setSelectedAgent(n.id)}
                                      >
                                        {n.label}
                                      </span>
                                    ))}
                                </div>
                              </div>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  )}

                  {activeTab === 'data' && pipelineData && (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Chunk ID</th>
                          <th>Parent ID</th>
                          <th>Page</th>
                          <th>Type</th>
                          <th>Content</th>
                        </tr>
                      </thead>
                      <tbody>
                        {pipelineData.children.map((child) => (
                          <tr key={child.chunk_id}>
                            <td>{child.chunk_id}</td>
                            <td>{child.parent_id}</td>
                            <td>{child.page_number}</td>
                            <td>{child.entity_type}</td>
                            <td>{child.content.slice(0, 100)}...</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}

                  {activeTab === 'images' && pipelineData && (
                    <div className="image-gallery">
                      {pipelineData.annotated_images.length === 0 ? (
                        <div className="empty-state">
                          <ImageIcon size={48} />
                          <h3>No annotated images</h3>
                          <p>Annotated pages are only available immediately after upload.</p>
                          <p style={{ fontSize: '12px', marginTop: '8px', color: 'var(--text-secondary)' }}>
                            Re-upload the document to see bounding box visualizations.
                          </p>
                        </div>
                      ) : (
                        pipelineData.annotated_images.map((img, idx) => (
                          <div key={idx} className="image-card">
                            <img src={img} alt={`Page ${idx + 1}`} />
                            <div className="image-card-footer">Page {idx + 1}</div>
                          </div>
                        ))
                      )}
                    </div>
                  )}

                  {activeTab === 'traces' && (
                    <div>
                      {/* Query traces */}
                      {queryTraces.length > 0 && (
                        <div style={{ marginBottom: '24px' }}>
                          <h3 style={{ fontSize: '14px', color: 'var(--aurora-cyan)', marginBottom: '16px' }}>
                            Query Retrieval Flow
                          </h3>
                          {queryTraces.map((trace, idx) => (
                            <div key={idx} className="trace-item" style={{
                              borderLeft: trace.step === 'Total' ? '3px solid var(--aurora-purple)' : '3px solid var(--aurora-cyan)',
                              background: trace.step === 'Total' ? 'rgba(168, 85, 247, 0.1)' : 'var(--bg-card)',
                            }}>
                              <div className="trace-page" style={{ minWidth: '40px' }}>{idx + 1}</div>
                              <div className="trace-info" style={{ flex: 1 }}>
                                <h4 style={{ color: trace.step === 'Total' ? 'var(--aurora-purple)' : 'var(--text-primary)' }}>
                                  {trace.step}
                                </h4>
                                <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{trace.description}</p>
                                <p style={{ fontSize: '11px', color: 'var(--aurora-teal)', marginTop: '4px' }}>{trace.details}</p>
                              </div>
                              <div className="trace-stats">
                                <div className="trace-duration">{trace.duration_ms}ms</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Document processing traces */}
                      {pipelineData && pipelineData.traces.length > 0 && (
                        <div>
                          <h3 style={{ fontSize: '14px', color: 'var(--aurora-pink)', marginBottom: '16px' }}>
                            Document Processing Traces
                          </h3>
                          {pipelineData.traces.map((trace, idx) => (
                            <div key={idx} className="trace-item">
                              <div className="trace-page">{trace.page_number}</div>
                              <div className="trace-info">
                                <h4>{trace.agent_name}</h4>
                                <p>Started: {new Date(trace.start_time).toLocaleTimeString()}</p>
                              </div>
                              <div className="trace-stats">
                                <div className="trace-duration">{trace.duration_seconds.toFixed(2)}s</div>
                                <div className="trace-count">{trace.sections_extracted} sections</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Empty state */}
                      {queryTraces.length === 0 && (!pipelineData || pipelineData.traces.length === 0) && (
                        <div className="empty-state">
                          <Clock size={48} />
                          <h3>No trace data</h3>
                          <p>Ask a question to see retrieval traces, or upload a document to see processing traces</p>
                        </div>
                      )}
                    </div>
                  )}

                  {activeTab === 'retrieval' && (
                    <div>
                      {retrievalResults.length === 0 && simpleResults.length === 0 ? (
                        <div className="empty-state">
                          <Search size={48} />
                          <h3>No retrieval results</h3>
                          <p>Ask a question to see the comparison between hierarchical and simple RAG</p>
                        </div>
                      ) : (
                        <>
                        {/* Evaluation Section */}
                        <div style={{
                          marginBottom: '20px',
                          padding: '16px',
                          background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(20, 184, 166, 0.1))',
                          borderRadius: '12px',
                          border: '1px solid var(--border-subtle)',
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <BarChart3 size={18} style={{ color: 'var(--aurora-purple)' }} />
                              <h3 style={{ fontSize: '14px', margin: 0 }}>LLM-as-Judge Evaluation</h3>
                            </div>
                            <button
                              onClick={handleEvaluate}
                              disabled={evaluating || !lastQuery}
                              style={{
                                padding: '8px 16px',
                                background: evaluating ? 'var(--bg-card)' : 'linear-gradient(135deg, var(--aurora-purple), var(--aurora-violet))',
                                border: 'none',
                                borderRadius: '6px',
                                color: 'white',
                                fontWeight: 600,
                                cursor: evaluating ? 'not-allowed' : 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                fontSize: '13px',
                              }}
                            >
                              {evaluating ? (
                                <>
                                  <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                                  Evaluating...
                                </>
                              ) : (
                                <>
                                  <Trophy size={14} />
                                  Compare Answers
                                </>
                              )}
                            </button>
                          </div>

                          {evaluationResult && (
                            <div style={{ marginTop: '16px' }}>
                              {/* Total Score Bars */}
                              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                <div>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                    <span style={{ fontSize: '12px', color: 'var(--aurora-purple)' }}>Hierarchical RAG</span>
                                    <span style={{ fontSize: '12px', fontWeight: 600 }}>{evaluationResult.evaluation.a_score}/30</span>
                                  </div>
                                  <div style={{ height: '8px', background: 'var(--bg-card)', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{
                                      height: '100%',
                                      width: `${(evaluationResult.evaluation.a_score / 30) * 100}%`,
                                      background: 'linear-gradient(90deg, var(--aurora-purple), var(--aurora-violet))',
                                      borderRadius: '4px',
                                    }} />
                                  </div>
                                </div>
                                <div>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                    <span style={{ fontSize: '12px', color: 'var(--aurora-teal)' }}>Simple RAG</span>
                                    <span style={{ fontSize: '12px', fontWeight: 600 }}>{evaluationResult.evaluation.b_score}/30</span>
                                  </div>
                                  <div style={{ height: '8px', background: 'var(--bg-card)', borderRadius: '4px', overflow: 'hidden' }}>
                                    <div style={{
                                      height: '100%',
                                      width: `${(evaluationResult.evaluation.b_score / 30) * 100}%`,
                                      background: 'linear-gradient(90deg, var(--aurora-teal), var(--aurora-cyan))',
                                      borderRadius: '4px',
                                    }} />
                                  </div>
                                </div>
                              </div>

                              {/* Deep Evaluation Scores Table */}
                              {evaluationResult.hierarchical.scores && evaluationResult.simple.scores && (
                                <div style={{ marginBottom: '16px', background: 'var(--bg-card)', borderRadius: '8px', padding: '12px' }}>
                                  <h4 style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                    Detailed Scores (0-5)
                                  </h4>
                                  <table style={{ width: '100%', fontSize: '11px', borderCollapse: 'collapse' }}>
                                    <thead>
                                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                        <th style={{ textAlign: 'left', padding: '6px 4px', color: 'var(--text-secondary)' }}>Dimension</th>
                                        <th style={{ textAlign: 'center', padding: '6px 4px', color: 'var(--aurora-purple)' }}>Hierarchical</th>
                                        <th style={{ textAlign: 'center', padding: '6px 4px', color: 'var(--aurora-teal)' }}>Simple</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {[
                                        { key: 'faithfulness', label: 'Faithfulness', desc: 'Claims supported by context' },
                                        { key: 'groundedness', label: 'Groundedness', desc: 'Citations accuracy' },
                                        { key: 'completeness', label: 'Completeness', desc: 'Coverage of relevant info' },
                                        { key: 'answer_relevance', label: 'Relevance', desc: 'Addresses the query' },
                                      ].map(({ key, label, desc }) => (
                                        <tr key={key} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                          <td style={{ padding: '6px 4px' }}>
                                            <div style={{ fontWeight: 500 }}>{label}</div>
                                            <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>{desc}</div>
                                          </td>
                                          <td style={{ textAlign: 'center', padding: '6px 4px' }}>
                                            <span style={{
                                              display: 'inline-block',
                                              padding: '2px 8px',
                                              borderRadius: '4px',
                                              background: `rgba(168, 85, 247, ${(evaluationResult.hierarchical.scores as any)[key] / 5 * 0.3})`,
                                              fontWeight: 600,
                                            }}>
                                              {(evaluationResult.hierarchical.scores as any)[key]}
                                            </span>
                                          </td>
                                          <td style={{ textAlign: 'center', padding: '6px 4px' }}>
                                            <span style={{
                                              display: 'inline-block',
                                              padding: '2px 8px',
                                              borderRadius: '4px',
                                              background: `rgba(20, 184, 166, ${(evaluationResult.simple.scores as any)[key] / 5 * 0.3})`,
                                              fontWeight: 600,
                                            }}>
                                              {(evaluationResult.simple.scores as any)[key]}
                                            </span>
                                          </td>
                                        </tr>
                                      ))}
                                      <tr>
                                        <td style={{ padding: '6px 4px' }}>
                                          <div style={{ fontWeight: 500 }}>Context Precision</div>
                                          <div style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>% chunks actually useful</div>
                                        </td>
                                        <td style={{ textAlign: 'center', padding: '6px 4px', fontWeight: 600 }}>
                                          {((evaluationResult.hierarchical.scores?.context_precision || 0) * 100).toFixed(0)}%
                                        </td>
                                        <td style={{ textAlign: 'center', padding: '6px 4px', fontWeight: 600 }}>
                                          {((evaluationResult.simple.scores?.context_precision || 0) * 100).toFixed(0)}%
                                        </td>
                                      </tr>
                                    </tbody>
                                  </table>
                                </div>
                              )}

                              {/* Grounding Analysis */}
                              {evaluationResult.hierarchical.grounding && evaluationResult.simple.grounding && (
                                <div style={{ marginBottom: '16px', background: 'var(--bg-card)', borderRadius: '8px', padding: '12px' }}>
                                  <h4 style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                    Grounding Analysis
                                  </h4>
                                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                    {/* Hierarchical Grounding */}
                                    <div>
                                      <div style={{ fontSize: '11px', color: 'var(--aurora-purple)', marginBottom: '6px' }}>Hierarchical</div>
                                      <div style={{ display: 'flex', gap: '4px', height: '20px', borderRadius: '4px', overflow: 'hidden', marginBottom: '6px' }}>
                                        <div style={{
                                          width: `${evaluationResult.hierarchical.grounding.grounded_percentage}%`,
                                          background: '#22c55e',
                                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                                          fontSize: '10px', fontWeight: 600, color: 'white',
                                        }}>
                                          {evaluationResult.hierarchical.grounding.grounded_percentage > 15 && `${evaluationResult.hierarchical.grounding.grounded_percentage.toFixed(0)}%`}
                                        </div>
                                        <div style={{
                                          width: `${evaluationResult.hierarchical.grounding.ungrounded_percentage}%`,
                                          background: '#ef4444',
                                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                                          fontSize: '10px', fontWeight: 600, color: 'white',
                                        }}>
                                          {evaluationResult.hierarchical.grounding.ungrounded_percentage > 15 && `${evaluationResult.hierarchical.grounding.ungrounded_percentage.toFixed(0)}%`}
                                        </div>
                                      </div>
                                      <div style={{ fontSize: '10px', display: 'flex', gap: '12px' }}>
                                        <span><span style={{ color: '#22c55e' }}>●</span> Grounded</span>
                                        <span><span style={{ color: '#ef4444' }}>●</span> Ungrounded</span>
                                        {evaluationResult.hierarchical.grounding.hallucination_count > 0 && (
                                          <span style={{ color: '#ef4444' }}>⚠ {evaluationResult.hierarchical.grounding.hallucination_count} hallucinations</span>
                                        )}
                                      </div>
                                    </div>
                                    {/* Simple Grounding */}
                                    <div>
                                      <div style={{ fontSize: '11px', color: 'var(--aurora-teal)', marginBottom: '6px' }}>Simple</div>
                                      <div style={{ display: 'flex', gap: '4px', height: '20px', borderRadius: '4px', overflow: 'hidden', marginBottom: '6px' }}>
                                        <div style={{
                                          width: `${evaluationResult.simple.grounding.grounded_percentage}%`,
                                          background: '#22c55e',
                                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                                          fontSize: '10px', fontWeight: 600, color: 'white',
                                        }}>
                                          {evaluationResult.simple.grounding.grounded_percentage > 15 && `${evaluationResult.simple.grounding.grounded_percentage.toFixed(0)}%`}
                                        </div>
                                        <div style={{
                                          width: `${evaluationResult.simple.grounding.ungrounded_percentage}%`,
                                          background: '#ef4444',
                                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                                          fontSize: '10px', fontWeight: 600, color: 'white',
                                        }}>
                                          {evaluationResult.simple.grounding.ungrounded_percentage > 15 && `${evaluationResult.simple.grounding.ungrounded_percentage.toFixed(0)}%`}
                                        </div>
                                      </div>
                                      <div style={{ fontSize: '10px', display: 'flex', gap: '12px' }}>
                                        <span><span style={{ color: '#22c55e' }}>●</span> Grounded</span>
                                        <span><span style={{ color: '#ef4444' }}>●</span> Ungrounded</span>
                                        {evaluationResult.simple.grounding.hallucination_count > 0 && (
                                          <span style={{ color: '#ef4444' }}>⚠ {evaluationResult.simple.grounding.hallucination_count} hallucinations</span>
                                        )}
                                      </div>
                                    </div>
                                  </div>

                                  {/* Hallucination Examples */}
                                  {(evaluationResult.hierarchical.grounding.hallucination_examples?.length > 0 ||
                                    evaluationResult.simple.grounding.hallucination_examples?.length > 0) && (
                                    <div style={{ marginTop: '12px', padding: '8px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '6px', borderLeft: '3px solid #ef4444' }}>
                                      <div style={{ fontSize: '11px', fontWeight: 600, color: '#ef4444', marginBottom: '6px' }}>
                                        ⚠ Potential Hallucinations Detected
                                      </div>
                                      <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '10px', color: 'var(--text-secondary)' }}>
                                        {evaluationResult.hierarchical.grounding.hallucination_examples?.slice(0, 2).map((ex, i) => (
                                          <li key={`h-${i}`} style={{ marginBottom: '4px' }}><span style={{ color: 'var(--aurora-purple)' }}>[H]</span> {ex}</li>
                                        ))}
                                        {evaluationResult.simple.grounding.hallucination_examples?.slice(0, 2).map((ex, i) => (
                                          <li key={`s-${i}`} style={{ marginBottom: '4px' }}><span style={{ color: 'var(--aurora-teal)' }}>[S]</span> {ex}</li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              )}

                              {/* Winner */}
                              <div style={{
                                padding: '12px',
                                background: evaluationResult.evaluation.winner === 'A'
                                  ? 'rgba(168, 85, 247, 0.2)'
                                  : evaluationResult.evaluation.winner === 'B'
                                  ? 'rgba(20, 184, 166, 0.2)'
                                  : 'rgba(107, 114, 128, 0.2)',
                                borderRadius: '8px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                              }}>
                                <Trophy size={16} style={{
                                  color: evaluationResult.evaluation.winner === 'A'
                                    ? 'var(--aurora-purple)'
                                    : evaluationResult.evaluation.winner === 'B'
                                    ? 'var(--aurora-teal)'
                                    : 'var(--text-secondary)'
                                }} />
                                <div>
                                  <div style={{ fontWeight: 600, fontSize: '13px' }}>
                                    Winner: {evaluationResult.evaluation.winner_label}
                                  </div>
                                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                    {evaluationResult.evaluation.reason}
                                  </div>
                                </div>
                              </div>

                              {/* Stats */}
                              <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(3, 1fr)',
                                gap: '12px',
                                marginTop: '12px',
                                fontSize: '11px',
                                color: 'var(--text-secondary)',
                              }}>
                                <div style={{ textAlign: 'center', padding: '8px', background: 'var(--bg-card)', borderRadius: '6px' }}>
                                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                    {evaluationResult.hierarchical.context_chars.toLocaleString()}
                                  </div>
                                  <div>Hierarchical chars</div>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px', background: 'var(--bg-card)', borderRadius: '6px' }}>
                                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                    {evaluationResult.simple.context_chars.toLocaleString()}
                                  </div>
                                  <div>Simple chars</div>
                                </div>
                                <div style={{ textAlign: 'center', padding: '8px', background: 'var(--bg-card)', borderRadius: '6px' }}>
                                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                                    {(evaluationResult.total_latency_ms / 1000).toFixed(1)}s
                                  </div>
                                  <div>Eval time</div>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                          {/* Hierarchical RAG Column */}
                          <div>
                            <h3 style={{
                              fontSize: '14px',
                              color: 'var(--aurora-purple)',
                              marginBottom: '16px',
                              padding: '12px',
                              background: 'rgba(168, 85, 247, 0.1)',
                              borderRadius: '8px',
                              borderLeft: '3px solid var(--aurora-purple)',
                            }}>
                              Hierarchical RAG (Parent-Child)
                              <span style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                Search children → Get parent context → Expand related agents
                              </span>
                            </h3>
                            {retrievalResults.map((result) => (
                              <div key={result.parent_id} className="retrieval-card" style={{ marginBottom: '12px' }}>
                                <div className="retrieval-header">
                                  <div className="retrieval-source">
                                    <span className="source-badge">{result.source_num}</span>
                                    <span>{result.document_name}</span>
                                  </div>
                                  <span className="similarity-score">
                                    {(result.similarity * 100).toFixed(1)}%
                                  </span>
                                </div>
                                <div className="retrieval-body">
                                  <div className="retrieval-meta">
                                    <span><FileText size={14} /> Page {result.page_number}</span>
                                    {result.agent_name && <span><GitBranch size={14} /> {result.agent_name}</span>}
                                  </div>
                                  <div className="matched-child">
                                    <div className="matched-child-label">Matched Child:</div>
                                    {result.matched_child.slice(0, 150)}...
                                  </div>
                                  <div className="parent-context">
                                    <div className="parent-context-label">Parent Context (to LLM):</div>
                                    {result.parent_content}
                                  </div>
                                  {result.related_agents.length > 0 && (
                                    <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--aurora-cyan)' }}>
                                      + Expanded: {result.related_agents.join(', ')}
                                    </div>
                                  )}
                                </div>
                              </div>
                            ))}
                            <div style={{
                              padding: '12px',
                              background: 'var(--bg-card)',
                              borderRadius: '8px',
                              fontSize: '12px',
                              color: 'var(--aurora-purple)',
                            }}>
                              Total context: ~{retrievalResults.reduce((acc, r) => acc + r.parent_content.length, 0).toLocaleString()} chars
                            </div>
                          </div>

                          {/* Simple RAG Column */}
                          <div>
                            <h3 style={{
                              fontSize: '14px',
                              color: 'var(--aurora-teal)',
                              marginBottom: '16px',
                              padding: '12px',
                              background: 'rgba(20, 184, 166, 0.1)',
                              borderRadius: '8px',
                              borderLeft: '3px solid var(--aurora-teal)',
                            }}>
                              Simple RAG (Flat Chunks)
                              <span style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                Direct vector search → Return matched chunk only
                              </span>
                            </h3>
                            {simpleResults.map((result) => (
                              <div key={result.chunk_id} className="retrieval-card" style={{ marginBottom: '12px', borderColor: 'var(--aurora-teal)' }}>
                                <div className="retrieval-header">
                                  <div className="retrieval-source">
                                    <span className="source-badge" style={{ background: 'var(--aurora-teal)' }}>{result.source_num}</span>
                                    <span>{result.document_name}</span>
                                  </div>
                                  <span className="similarity-score">
                                    {(result.similarity * 100).toFixed(1)}%
                                  </span>
                                </div>
                                <div className="retrieval-body">
                                  <div className="retrieval-meta">
                                    <span><FileText size={14} /> Page {result.page_number}</span>
                                  </div>
                                  <div style={{ fontSize: '13px', lineHeight: '1.5', color: 'var(--text-secondary)' }}>
                                    {result.content}
                                  </div>
                                  <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--aurora-pink)' }}>
                                    No parent context, no expansion
                                  </div>
                                </div>
                              </div>
                            ))}
                            <div style={{
                              padding: '12px',
                              background: 'var(--bg-card)',
                              borderRadius: '8px',
                              fontSize: '12px',
                              color: 'var(--aurora-teal)',
                            }}>
                              Total context: ~{simpleResults.reduce((acc, r) => acc + r.content.length, 0).toLocaleString()} chars
                            </div>
                          </div>
                        </div>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Chat Panel */}
              <div className="chat-panel">
                <div className="chat-header">
                  <MessageSquare size={16} style={{ marginRight: '8px' }} />
                  Chat
                </div>

                <div className="chat-messages">
                  {messages.length === 0 ? (
                    <div className="empty-state">
                      <MessageSquare size={32} />
                      <p>Ask a question about the indexed documents</p>
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div key={idx} className={`message ${msg.role}`}>
                        <div className="markdown-content">
                          {msg.role === 'assistant' ? (
                            <ReactMarkdown
                              components={{
                                p: ({ children }) => <p>{renderCitations(children)}</p>,
                                li: ({ children }) => <li>{renderCitations(children)}</li>,
                                strong: ({ children }) => <strong>{renderCitations(children)}</strong>,
                              }}
                            >
                              {msg.content}
                            </ReactMarkdown>
                          ) : (
                            <p>{msg.content}</p>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                  {loading && (
                    <div className="loading">
                      <div className="spinner" />
                      <p>Searching children, fetching parents...</p>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                <div className="chat-input">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSendMessage()
                      }
                    }}
                    placeholder="Ask a question..."
                    rows={1}
                  />
                  <button onClick={handleSendMessage} disabled={loading || !inputMessage.trim()}>
                    <Send size={18} />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
