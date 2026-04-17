import React from 'react';

// Lesson 1: Protocol Overview Diagram
export function ProtocolOverviewDiagram() {
  return (
    <svg
      viewBox="0 0 800 400"
      className="diagram"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="protocolGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#f59e0b', stopOpacity: 0.2 }} />
          <stop offset="100%" style={{ stopColor: '#f59e0b', stopOpacity: 0.05 }} />
        </linearGradient>
        <linearGradient id="agentGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#6366f1', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#6366f1', stopOpacity: 0.1 }} />
        </linearGradient>
      </defs>

      {/* Title */}
      <text x="400" y="30" textAnchor="middle" fill="#e2e8f0" fontSize="20" fontWeight="600">
        N Agents, 1 Standard Protocol
      </text>

      {/* A2A Protocol Layer */}
      <rect
        x="50"
        y="160"
        width="700"
        height="80"
        rx="8"
        fill="url(#protocolGradient)"
        stroke="#f59e0b"
        strokeWidth="2"
      />
      <text x="400" y="195" textAnchor="middle" fill="#f59e0b" fontSize="16" fontWeight="600">
        A2A Protocol Layer
      </text>
      <text x="400" y="218" textAnchor="middle" fill="#94a3b8" fontSize="13">
        Standard interface for discovery, tasks, SSE, and orchestration
      </text>

      {/* Agents */}
      {[
        { x: 100, label: 'Agent A', color: '#6366f1' },
        { x: 250, label: 'Agent B', color: '#8b5cf6' },
        { x: 400, label: 'Agent C', color: '#6366f1' },
        { x: 550, label: 'Agent D', color: '#8b5cf6' },
        { x: 700, label: 'Agent E', color: '#6366f1' },
      ].map((agent, i) => (
        <g key={i}>
          {/* Agent box */}
          <rect
            x={agent.x - 40}
            y="60"
            width="80"
            height="60"
            rx="8"
            fill="url(#agentGradient)"
            stroke={agent.color}
            strokeWidth="2"
          />
          <text
            x={agent.x}
            y="95"
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="14"
            fontWeight="500"
          >
            {agent.label}
          </text>

          {/* Connection to protocol */}
          <line
            x1={agent.x}
            y1="120"
            x2={agent.x}
            y2="160"
            stroke="#22c55e"
            strokeWidth="2"
            strokeDasharray="4 4"
          />
          <circle cx={agent.x} cy="160" r="4" fill="#22c55e" />
        </g>
      ))}

      {/* Bottom agents */}
      {[
        { x: 175, label: 'Agent F', color: '#6366f1' },
        { x: 325, label: 'Agent G', color: '#8b5cf6' },
        { x: 475, label: 'Agent H', color: '#6366f1' },
        { x: 625, label: 'Agent I', color: '#8b5cf6' },
      ].map((agent, i) => (
        <g key={`bottom-${i}`}>
          {/* Agent box */}
          <rect
            x={agent.x - 40}
            y="300"
            width="80"
            height="60"
            rx="8"
            fill="url(#agentGradient)"
            stroke={agent.color}
            strokeWidth="2"
          />
          <text
            x={agent.x}
            y="335"
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="14"
            fontWeight="500"
          >
            {agent.label}
          </text>

          {/* Connection to protocol */}
          <line
            x1={agent.x}
            y1="300"
            x2={agent.x}
            y2="240"
            stroke="#22c55e"
            strokeWidth="2"
            strokeDasharray="4 4"
          />
          <circle cx={agent.x} cy="240" r="4" fill="#22c55e" />
        </g>
      ))}

      {/* Legend */}
      <text x="50" y="385" fill="#94a3b8" fontSize="12">
        vs. N×N custom integrations without a standard
      </text>
    </svg>
  );
}

// Lesson 3: Task Lifecycle Diagram
export function TaskLifecycleDiagram() {
  return (
    <svg
      viewBox="0 0 800 450"
      className="diagram"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="submittedGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#3b82f6', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#3b82f6', stopOpacity: 0.1 }} />
        </linearGradient>
        <linearGradient id="workingGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#f59e0b', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#f59e0b', stopOpacity: 0.1 }} />
        </linearGradient>
        <linearGradient id="inputGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#8b5cf6', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#8b5cf6', stopOpacity: 0.1 }} />
        </linearGradient>
        <linearGradient id="completedGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#22c55e', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#22c55e', stopOpacity: 0.1 }} />
        </linearGradient>
        <linearGradient id="failedGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#ef4444', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#ef4444', stopOpacity: 0.1 }} />
        </linearGradient>
      </defs>

      {/* Title */}
      <text x="400" y="30" textAnchor="middle" fill="#e2e8f0" fontSize="20" fontWeight="600">
        Task Lifecycle State Machine
      </text>

      {/* Submitted */}
      <g>
        <rect
          x="50"
          y="100"
          width="120"
          height="70"
          rx="8"
          fill="url(#submittedGrad)"
          stroke="#3b82f6"
          strokeWidth="2"
        />
        <text x="110" y="130" textAnchor="middle" fill="#3b82f6" fontSize="15" fontWeight="600">
          submitted
        </text>
        <text x="110" y="150" textAnchor="middle" fill="#94a3b8" fontSize="11">
          Task created
        </text>
      </g>

      {/* Arrow to working */}
      <path
        d="M 170 135 L 230 135"
        stroke="#94a3b8"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
      />
      <text x="200" y="125" textAnchor="middle" fill="#94a3b8" fontSize="11">
        start
      </text>

      {/* Working */}
      <g>
        <rect
          x="230"
          y="100"
          width="120"
          height="70"
          rx="8"
          fill="url(#workingGrad)"
          stroke="#f59e0b"
          strokeWidth="2"
        />
        <text x="290" y="130" textAnchor="middle" fill="#f59e0b" fontSize="15" fontWeight="600">
          working
        </text>
        <text x="290" y="150" textAnchor="middle" fill="#94a3b8" fontSize="11">
          Processing
        </text>
      </g>

      {/* Arrow to input-required */}
      <path
        d="M 290 170 L 290 250"
        stroke="#94a3b8"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
      />
      <text x="310" y="210" fill="#94a3b8" fontSize="11">
        needs input
      </text>

      {/* Input-required */}
      <g>
        <rect
          x="230"
          y="250"
          width="120"
          height="70"
          rx="8"
          fill="url(#inputGrad)"
          stroke="#8b5cf6"
          strokeWidth="2"
        />
        <text x="290" y="275" textAnchor="middle" fill="#8b5cf6" fontSize="14" fontWeight="600">
          input-required
        </text>
        <text x="290" y="295" textAnchor="middle" fill="#94a3b8" fontSize="11">
          Waiting for user
        </text>
      </g>

      {/* Arrow back to working */}
      <path
        d="M 230 285 L 200 285 L 200 135 L 230 135"
        stroke="#94a3b8"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
        strokeDasharray="4 4"
      />
      <text x="180" y="210" fill="#94a3b8" fontSize="11" textAnchor="end">
        resume
      </text>

      {/* Arrow to completed */}
      <path
        d="M 350 135 L 450 135"
        stroke="#94a3b8"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
      />
      <text x="400" y="125" textAnchor="middle" fill="#94a3b8" fontSize="11">
        done
      </text>

      {/* Completed */}
      <g>
        <rect
          x="450"
          y="100"
          width="120"
          height="70"
          rx="8"
          fill="url(#completedGrad)"
          stroke="#22c55e"
          strokeWidth="2"
        />
        <text x="510" y="130" textAnchor="middle" fill="#22c55e" fontSize="15" fontWeight="600">
          completed
        </text>
        <text x="510" y="150" textAnchor="middle" fill="#94a3b8" fontSize="11">
          Success
        </text>
      </g>

      {/* Arrow to failed */}
      <path
        d="M 290 100 L 290 50 L 510 50 L 510 250"
        stroke="#94a3b8"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
        strokeDasharray="4 4"
      />
      <text x="400" y="40" textAnchor="middle" fill="#94a3b8" fontSize="11">
        error
      </text>

      {/* Failed */}
      <g>
        <rect
          x="450"
          y="250"
          width="120"
          height="70"
          rx="8"
          fill="url(#failedGrad)"
          stroke="#ef4444"
          strokeWidth="2"
        />
        <text x="510" y="280" textAnchor="middle" fill="#ef4444" fontSize="15" fontWeight="600">
          failed
        </text>
        <text x="510" y="300" textAnchor="middle" fill="#94a3b8" fontSize="11">
          Terminal
        </text>
      </g>

      {/* Arrow to canceled */}
      <path
        d="M 110 100 L 110 50 L 710 50 L 710 285"
        stroke="#94a3b8"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
        strokeDasharray="4 4"
      />
      <text x="410" y="65" textAnchor="middle" fill="#94a3b8" fontSize="11">
        cancel anytime
      </text>

      {/* Canceled */}
      <g>
        <rect
          x="630"
          y="250"
          width="120"
          height="70"
          rx="8"
          fill="url(#failedGrad)"
          stroke="#ef4444"
          strokeWidth="2"
        />
        <text x="690" y="280" textAnchor="middle" fill="#ef4444" fontSize="15" fontWeight="600">
          canceled
        </text>
        <text x="690" y="300" textAnchor="middle" fill="#94a3b8" fontSize="11">
          Terminal
        </text>
      </g>

      {/* Arrowhead marker */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon points="0 0, 10 3, 0 6" fill="#94a3b8" />
        </marker>
      </defs>

      {/* Legend */}
      <text x="50" y="380" fill="#94a3b8" fontSize="12">
        Active states: submitted, working, input-required
      </text>
      <text x="50" y="400" fill="#94a3b8" fontSize="12">
        Terminal states: completed, failed, canceled
      </text>
    </svg>
  );
}

// Lesson 5: SSE Flow Diagram
export function SSEFlowDiagram() {
  return (
    <svg
      viewBox="0 0 800 500"
      className="diagram"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="clientGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#6366f1', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#6366f1', stopOpacity: 0.1 }} />
        </linearGradient>
        <linearGradient id="agentGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#8b5cf6', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#8b5cf6', stopOpacity: 0.1 }} />
        </linearGradient>
      </defs>

      {/* Title */}
      <text x="400" y="30" textAnchor="middle" fill="#e2e8f0" fontSize="20" fontWeight="600">
        Server-Sent Events (SSE) Flow
      </text>

      {/* Swimlanes */}
      <g>
        {/* Client lane */}
        <rect x="100" y="70" width="150" height="400" rx="8" fill="url(#clientGrad)" stroke="#6366f1" strokeWidth="2" />
        <text x="175" y="95" textAnchor="middle" fill="#6366f1" fontSize="16" fontWeight="600">
          Client
        </text>

        {/* Agent lane */}
        <rect x="550" y="70" width="150" height="400" rx="8" fill="url(#agentGrad2)" stroke="#8b5cf6" strokeWidth="2" />
        <text x="625" y="95" textAnchor="middle" fill="#8b5cf6" fontSize="16" fontWeight="600">
          Agent
        </text>
      </g>

      {/* Timeline */}
      <line x1="175" y1="120" x2="175" y2="450" stroke="#94a3b8" strokeWidth="2" strokeDasharray="4 4" />
      <line x1="625" y1="120" x2="625" y2="450" stroke="#94a3b8" strokeWidth="2" strokeDasharray="4 4" />

      {/* 1. POST Request */}
      <g>
        <path
          d="M 175 140 L 625 160"
          stroke="#22c55e"
          strokeWidth="3"
          fill="none"
          markerEnd="url(#arrowGreen)"
        />
        <rect x="280" y="130" width="240" height="40" rx="4" fill="#111827" stroke="#22c55e" strokeWidth="1" />
        <text x="400" y="147" textAnchor="middle" fill="#22c55e" fontSize="13" fontWeight="600">
          POST /tasks
        </text>
        <text x="400" y="162" textAnchor="middle" fill="#94a3b8" fontSize="11">
          {'{ "text": "...", "accept": "text/event-stream" }'}
        </text>
      </g>

      {/* 2. SSE Connection opened */}
      <g>
        <path
          d="M 625 190 L 175 210"
          stroke="#f59e0b"
          strokeWidth="3"
          fill="none"
          markerEnd="url(#arrowAmber)"
        />
        <rect x="280" y="185" width="240" height="30" rx="4" fill="#111827" stroke="#f59e0b" strokeWidth="1" />
        <text x="400" y="205" textAnchor="middle" fill="#f59e0b" fontSize="12">
          200 OK (text/event-stream)
        </text>
      </g>

      {/* 3. Status update: working */}
      <g>
        <path
          d="M 625 240 L 175 260"
          stroke="#f59e0b"
          strokeWidth="2"
          fill="none"
          markerEnd="url(#arrowAmber)"
          strokeDasharray="4 4"
        />
        <rect x="280" y="235" width="240" height="30" rx="4" fill="#111827" stroke="#f59e0b" strokeWidth="1" />
        <text x="400" y="255" textAnchor="middle" fill="#f59e0b" fontSize="12">
          event: status-update (working)
        </text>
      </g>

      {/* 4. Artifact chunk 1 */}
      <g>
        <path
          d="M 625 290 L 175 310"
          stroke="#8b5cf6"
          strokeWidth="2"
          fill="none"
          markerEnd="url(#arrowPurple)"
          strokeDasharray="4 4"
        />
        <rect x="280" y="285" width="240" height="30" rx="4" fill="#111827" stroke="#8b5cf6" strokeWidth="1" />
        <text x="400" y="305" textAnchor="middle" fill="#8b5cf6" fontSize="12">
          event: artifact-update (chunk 1)
        </text>
      </g>

      {/* 5. Artifact chunk 2 */}
      <g>
        <path
          d="M 625 340 L 175 360"
          stroke="#8b5cf6"
          strokeWidth="2"
          fill="none"
          markerEnd="url(#arrowPurple)"
          strokeDasharray="4 4"
        />
        <rect x="280" y="335" width="240" height="30" rx="4" fill="#111827" stroke="#8b5cf6" strokeWidth="1" />
        <text x="400" y="355" textAnchor="middle" fill="#8b5cf6" fontSize="12">
          event: artifact-update (chunk 2)
        </text>
      </g>

      {/* 6. Status update: completed */}
      <g>
        <path
          d="M 625 390 L 175 410"
          stroke="#22c55e"
          strokeWidth="3"
          fill="none"
          markerEnd="url(#arrowGreen)"
        />
        <rect x="280" y="385" width="240" height="30" rx="4" fill="#111827" stroke="#22c55e" strokeWidth="1" />
        <text x="400" y="405" textAnchor="middle" fill="#22c55e" fontSize="12" fontWeight="600">
          event: status-update (completed)
        </text>
      </g>

      {/* 7. Connection closed */}
      <g>
        <circle cx="175" cy="440" r="5" fill="#ef4444" />
        <circle cx="625" cy="440" r="5" fill="#ef4444" />
        <text x="400" y="460" textAnchor="middle" fill="#ef4444" fontSize="12">
          Connection closed
        </text>
      </g>

      {/* Arrow markers */}
      <defs>
        <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#22c55e" />
        </marker>
        <marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#f59e0b" />
        </marker>
        <marker id="arrowPurple" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#8b5cf6" />
        </marker>
      </defs>
    </svg>
  );
}

// Lesson 2: Agent Card Diagram
export function AgentCardDiagram() {
  return (
    <svg
      viewBox="0 0 800 450"
      className="diagram"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#6366f1', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#6366f1', stopOpacity: 0.1 }} />
        </linearGradient>
        <linearGradient id="fieldGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#22c55e', stopOpacity: 0.2 }} />
          <stop offset="100%" style={{ stopColor: '#22c55e', stopOpacity: 0.05 }} />
        </linearGradient>
      </defs>

      {/* Title */}
      <text x="400" y="30" textAnchor="middle" fill="#e2e8f0" fontSize="20" fontWeight="600">
        Agent Discovery Flow
      </text>

      {/* Client */}
      <g>
        <rect x="50" y="100" width="100" height="60" rx="8" fill="url(#cardGrad)" stroke="#6366f1" strokeWidth="2" />
        <text x="100" y="135" textAnchor="middle" fill="#e2e8f0" fontSize="14" fontWeight="500">
          Client
        </text>
      </g>

      {/* Arrow to endpoint */}
      <path
        d="M 150 130 L 240 130"
        stroke="#94a3b8"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowGray)"
      />
      <text x="195" y="120" textAnchor="middle" fill="#94a3b8" fontSize="11">
        GET
      </text>

      {/* Endpoint */}
      <g>
        <rect x="240" y="90" width="200" height="80" rx="8" fill="#111827" stroke="#f59e0b" strokeWidth="2" />
        <text x="340" y="120" textAnchor="middle" fill="#f59e0b" fontSize="13" fontWeight="600">
          /.well-known/
        </text>
        <text x="340" y="140" textAnchor="middle" fill="#f59e0b" fontSize="13" fontWeight="600">
          agent-card.json
        </text>
      </g>

      {/* Arrow to card */}
      <path
        d="M 440 130 L 530 130"
        stroke="#94a3b8"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowGray)"
      />
      <text x="485" y="120" textAnchor="middle" fill="#94a3b8" fontSize="11">
        200 OK
      </text>

      {/* Agent Card */}
      <g>
        <rect x="530" y="80" width="220" height="100" rx="8" fill="url(#cardGrad)" stroke="#6366f1" strokeWidth="2" />
        <text x="640" y="110" textAnchor="middle" fill="#6366f1" fontSize="15" fontWeight="600">
          Agent Card JSON
        </text>
        <text x="640" y="135" textAnchor="middle" fill="#94a3b8" fontSize="11">
          name, description,
        </text>
        <text x="640" y="153" textAnchor="middle" fill="#94a3b8" fontSize="11">
          skills, capabilities, auth
        </text>
      </g>

      {/* Expanding lines to fields */}
      <g>
        {/* Name */}
        <path d="M 640 180 L 640 210 L 150 210 L 150 240" stroke="#22c55e" strokeWidth="2" fill="none" />
        <rect x="80" y="240" width="140" height="50" rx="6" fill="url(#fieldGrad)" stroke="#22c55e" strokeWidth="1.5" />
        <text x="150" y="262" textAnchor="middle" fill="#22c55e" fontSize="13" fontWeight="600">
          name
        </text>
        <text x="150" y="280" textAnchor="middle" fill="#94a3b8" fontSize="10">
          "Data Analyzer"
        </text>

        {/* Skills */}
        <path d="M 640 180 L 640 210 L 320 210 L 320 240" stroke="#22c55e" strokeWidth="2" fill="none" />
        <rect x="250" y="240" width="140" height="50" rx="6" fill="url(#fieldGrad)" stroke="#22c55e" strokeWidth="1.5" />
        <text x="320" y="262" textAnchor="middle" fill="#22c55e" fontSize="13" fontWeight="600">
          skills
        </text>
        <text x="320" y="280" textAnchor="middle" fill="#94a3b8" fontSize="10">
          ["analyze", "report"]
        </text>

        {/* Capabilities */}
        <path d="M 640 180 L 640 210 L 490 210 L 490 240" stroke="#22c55e" strokeWidth="2" fill="none" />
        <rect x="420" y="240" width="140" height="50" rx="6" fill="url(#fieldGrad)" stroke="#22c55e" strokeWidth="1.5" />
        <text x="490" y="262" textAnchor="middle" fill="#22c55e" fontSize="13" fontWeight="600">
          capabilities
        </text>
        <text x="490" y="280" textAnchor="middle" fill="#94a3b8" fontSize="10">
          streaming, async
        </text>

        {/* Authentication */}
        <path d="M 640 180 L 640 210 L 660 210 L 660 240" stroke="#22c55e" strokeWidth="2" fill="none" />
        <rect x="590" y="240" width="140" height="50" rx="6" fill="url(#fieldGrad)" stroke="#22c55e" strokeWidth="1.5" />
        <text x="660" y="262" textAnchor="middle" fill="#22c55e" fontSize="13" fontWeight="600">
          authentication
        </text>
        <text x="660" y="280" textAnchor="middle" fill="#94a3b8" fontSize="10">
          bearer, api-key
        </text>
      </g>

      {/* Description */}
      <g>
        <text x="400" y="340" textAnchor="middle" fill="#94a3b8" fontSize="12">
          Clients discover agent capabilities before interaction
        </text>
        <text x="400" y="360" textAnchor="middle" fill="#94a3b8" fontSize="12">
          Enables dynamic routing and orchestration
        </text>
      </g>

      {/* Arrow marker */}
      <defs>
        <marker id="arrowGray" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#94a3b8" />
        </marker>
      </defs>
    </svg>
  );
}

// Lesson 7: Orchestration Diagram
export function OrchestrationDiagram() {
  return (
    <svg
      viewBox="0 0 800 500"
      className="diagram"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="orchestratorGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#f59e0b', stopOpacity: 0.4 }} />
          <stop offset="100%" style={{ stopColor: '#f59e0b', stopOpacity: 0.1 }} />
        </linearGradient>
        <linearGradient id="specialistGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#6366f1', stopOpacity: 0.3 }} />
          <stop offset="100%" style={{ stopColor: '#6366f1', stopOpacity: 0.1 }} />
        </linearGradient>
        <radialGradient id="glowGrad">
          <stop offset="0%" style={{ stopColor: '#f59e0b', stopOpacity: 0.4 }} />
          <stop offset="100%" style={{ stopColor: '#f59e0b', stopOpacity: 0 }} />
        </radialGradient>
      </defs>

      {/* Title */}
      <text x="400" y="30" textAnchor="middle" fill="#e2e8f0" fontSize="20" fontWeight="600">
        Orchestration Pattern: Fan-Out / Fan-In
      </text>

      {/* Orchestrator glow */}
      <circle cx="400" cy="250" r="80" fill="url(#glowGrad)" />

      {/* Orchestrator */}
      <g>
        <rect
          x="320"
          y="200"
          width="160"
          height="100"
          rx="12"
          fill="url(#orchestratorGrad)"
          stroke="#f59e0b"
          strokeWidth="3"
        />
        <text x="400" y="240" textAnchor="middle" fill="#f59e0b" fontSize="16" fontWeight="600">
          Orchestrator
        </text>
        <text x="400" y="260" textAnchor="middle" fill="#94a3b8" fontSize="12">
          Coordinates
        </text>
        <text x="400" y="280" textAnchor="middle" fill="#94a3b8" fontSize="12">
          multiple agents
        </text>
      </g>

      {/* User request */}
      <g>
        <rect x="320" y="80" width="160" height="50" rx="8" fill="#111827" stroke="#22c55e" strokeWidth="2" />
        <text x="400" y="110" textAnchor="middle" fill="#22c55e" fontSize="13" fontWeight="500">
          Complex User Request
        </text>
      </g>
      <path d="M 400 130 L 400 200" stroke="#22c55e" strokeWidth="2" markerEnd="url(#arrowGreen2)" />

      {/* Specialist Agents */}
      {[
        { x: 100, y: 380, label: 'Data\nAgent', skill: 'fetch data', color: '#6366f1' },
        { x: 250, y: 420, label: 'Analysis\nAgent', skill: 'analyze', color: '#8b5cf6' },
        { x: 400, y: 450, label: 'Image\nAgent', skill: 'generate', color: '#6366f1' },
        { x: 550, y: 420, label: 'Report\nAgent', skill: 'format', color: '#8b5cf6' },
        { x: 700, y: 380, label: 'Email\nAgent', skill: 'send', color: '#6366f1' },
      ].map((agent, i) => (
        <g key={i}>
          {/* Agent box */}
          <rect
            x={agent.x - 50}
            y={agent.y - 35}
            width="100"
            height="70"
            rx="8"
            fill="url(#specialistGrad)"
            stroke={agent.color}
            strokeWidth="2"
          />
          <text
            x={agent.x}
            y={agent.y - 10}
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="13"
            fontWeight="500"
          >
            {agent.label.split('\n')[0]}
          </text>
          <text
            x={agent.x}
            y={agent.y + 5}
            textAnchor="middle"
            fill="#e2e8f0"
            fontSize="13"
            fontWeight="500"
          >
            {agent.label.split('\n')[1]}
          </text>
          <text
            x={agent.x}
            y={agent.y + 22}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="10"
          >
            {agent.skill}
          </text>

          {/* Fan-out line from orchestrator */}
          <path
            d={`M 400 300 L ${agent.x} ${agent.y - 35}`}
            stroke="#f59e0b"
            strokeWidth="2"
            fill="none"
            markerEnd="url(#arrowAmber2)"
          />

          {/* Fan-in line to orchestrator */}
          <path
            d={`M ${agent.x} ${agent.y - 35} L 400 300`}
            stroke="#22c55e"
            strokeWidth="2"
            fill="none"
            strokeDasharray="4 4"
          />
        </g>
      ))}

      {/* Labels */}
      <g>
        <text x="220" y="330" fill="#f59e0b" fontSize="12" fontWeight="500">
          Fan-out: Discover & Delegate
        </text>
        <text x="500" y="330" fill="#22c55e" fontSize="12" fontWeight="500">
          Fan-in: Aggregate Results
        </text>
      </g>

      {/* Arrow markers */}
      <defs>
        <marker id="arrowGreen2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#22c55e" />
        </marker>
        <marker id="arrowAmber2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#f59e0b" />
        </marker>
      </defs>
    </svg>
  );
}
