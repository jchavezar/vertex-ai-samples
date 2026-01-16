import React from 'react';

const SummaryPanel = ({ ticker, externalData }) => {
  return (
    <div className="card profile-card">
      <div className="section-title">Profile</div>
      <div className="profile-content">
        <p className="profile-desc">
          {externalData?.summary || "FactSet Research Systems Inc. is a global financial digital platform and enterprise solutions provider."}
        </p>

        <div className="profile-details">
          <div className="detail-row">
            <span className="label">Sector</span>
            <span className="value">{externalData?.sector || "Software and Consulting"}</span>
          </div>
          <div className="detail-row">
            <span className="label">Industry</span>
            <span className="value">{externalData?.industry || "Professional Content Providers"}</span>
          </div>
          <div className="detail-row">
            <span className="label">Exchange</span>
            <span className="value">NYSE</span>
          </div>
        </div>

        <div className="value-bridge">
          <div className="section-title" style={{ marginTop: 24 }}>Value Bridge</div>
          <div className="bridge-list">
            <div className="bridge-item bold"><span>Market Cap (M)</span> <span>{externalData?.marketCap ? (externalData.marketCap / 1e6).toFixed(2) : "11,015.51"}</span></div>
            <div className="bridge-item"><span>Currency</span> <span>{externalData?.currency || "USD"}</span></div>
          </div>
        </div>
      </div>

      <style jsx="true">{`
        .profile-card {
          min-height: 400px;
          display: flex;
          flex-direction: column;
        }
        .profile-desc {
          font-size: 11px;
          color: var(--text-secondary);
          line-height: 1.4;
          margin-bottom: 20px;
        }
        .profile-details {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .detail-row {
          display: grid;
          grid-template-columns: 100px 1fr;
          font-size: 11px;
        }
        .label {
          color: var(--text-muted);
        }
        .value {
          color: var(--text-primary);
          font-weight: 500;
        }
        .bridge-list {
          margin-top: 12px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .bridge-item {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          padding: 4px 0;
          border-bottom: 1px dotted var(--border-light);
        }
      `}</style>
    </div >
  );
};

export default SummaryPanel;
