# Frontend

[<- Back to Main README](../README.md) | [Architecture](../docs/architecture.md) | [Backend](../backend/README.md)

> **React 19 frontend with Aurora theme and SQL query explorer**

## Architecture

```
frontend/
├── src/
│   ├── App.tsx          # Main application component
│   ├── main.tsx         # React entry point
│   └── index.css        # Aurora theme styles
├── public/
│   └── favicon.svg      # Aurora logo
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration with API proxy
├── tsconfig.json        # TypeScript config
└── package.json         # Dependencies
```

## Files

| File | Description |
|------|-------------|
| [`src/App.tsx`](src/App.tsx) | Main React component with all views |
| [`src/index.css`](src/index.css) | Aurora theme CSS (purple/teal gradients) |
| [`vite.config.ts`](vite.config.ts) | Vite dev server with `/api` proxy to backend |

## Aurora Theme

The UI uses a distinctive purple/teal gradient design system:

| Color | CSS Variable | Hex | Usage |
|-------|--------------|-----|-------|
| Purple | `--aurora-purple` | `#a855f7` | Primary accent |
| Violet | `--aurora-violet` | `#8b5cf6` | Secondary accent |
| Teal | `--aurora-teal` | `#14b8a6` | Success states |
| Cyan | `--aurora-cyan` | `#06b6d4` | Links |
| Pink | `--aurora-pink` | `#ec4899` | Warnings |

Source: [`src/index.css#L1-L20`](src/index.css#L1-L20)

## Key Features

### Document Upload

Source: [`src/App.tsx#L88-L94`](src/App.tsx#L88-L94)

- Drag-and-drop zone with visual feedback
- Processing overlay with step-by-step progress
- Support for PDF, PNG, JPEG

### Results Dashboard

Four tabs for exploring processed documents:

| Tab | Description | Source |
|-----|-------------|--------|
| **Data** | Table view of extracted entities | [`src/App.tsx#L508-L530`](src/App.tsx#L508-L530) |
| **Pages** | Annotated page images with bounding boxes | [`src/App.tsx#L533-L545`](src/App.tsx#L533-L545) |
| **Traces** | ADK agent execution logs | [`src/App.tsx#L547-L566`](src/App.tsx#L547-L566) |
| **SQL** | Interactive SQL query explorer | [`src/App.tsx#L568-L630`](src/App.tsx#L568-L630) |

### SQL Query Tab

Source: [`src/App.tsx#L568-L630`](src/App.tsx#L568-L630)

- Monospace code editor
- Pre-built example queries
- Results table with row count
- Error display for invalid queries

### Chat Interface

Source: [`src/App.tsx#L640-L680`](src/App.tsx#L640-L680)

- Markdown rendering with ReactMarkdown
- Citation rendering (e.g., `[1]`, `[2]`)
- Model selector for Gemini variants

## State Management

Key React state variables:

| State | Type | Purpose |
|-------|------|---------|
| `view` | `'upload' \| 'dashboard'` | Current app view |
| `activeTab` | `'data' \| 'images' \| 'traces' \| 'sql'` | Active results tab |
| `pipelineData` | `PipelineEntity[]` | Extracted document chunks |
| `sqlQuery` | `string` | Current SQL query |
| `sqlResult` | `SqlResult \| null` | SQL query results |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| React | 19.x | UI framework |
| Framer Motion | 11.x | Animations |
| Lucide React | 0.468+ | Icons |
| React Markdown | 9.x | Markdown rendering |
| Vite | 6.x | Build tool |

## Configuration

### API Proxy

Source: [`vite.config.ts`](vite.config.ts)

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8002',
      changeOrigin: true,
    },
  },
}
```

## Running

### Development

```bash
cd frontend
npm install
npm run dev
# Opens on http://localhost:5173
```

### Production Build

```bash
npm run build
# Output in dist/
```

## Styling Guide

### Adding New Components

1. Use CSS variables from `:root` in `index.css`
2. Follow BEM-like naming: `.component-name`, `.component-name-element`
3. Use `var(--gradient-aurora)` for primary buttons
4. Use `var(--bg-elevated)` for cards

### Example

```css
.my-component {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
}

.my-component:hover {
  border-color: var(--aurora-purple);
}
```

## Related Documentation

- [Main README](../README.md) - Project overview
- [Backend](../backend/README.md) - API implementation
- [Architecture](../docs/architecture.md) - Full system design
- [Getting Started](../docs/getting-started.md) - Setup guide
- [Troubleshooting](../docs/troubleshooting.md) - Common issues
