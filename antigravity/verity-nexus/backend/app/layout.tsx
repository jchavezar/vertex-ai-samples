import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="dashboard">
          <header className="header">
            VERITY NEXUS ENGINE | Forensic & Regulatory AI
          </header>
          <aside className="sidebar">
            <h3>Investigation Hub</h3>
            <ul>
              <li>Active Audits</li>
              <li>Tax Compliance</li>
              <li>Orchestration Logs</li>
            </ul>
          </aside>
          <main className="main-content">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
