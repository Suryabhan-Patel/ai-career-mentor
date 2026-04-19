export default function RoleCard({ role, matchPercentage, isTopRole = false }) {
  // Ensure matchPercentage is a number
  const percentage = typeof matchPercentage === 'string' 
    ? parseFloat(matchPercentage) 
    : matchPercentage;

  const getRecommendation = (pct) => {
    if (pct >= 80) return ' Excellent match! This role aligns perfectly with your skills.';
    if (pct >= 60) return ' Good fit! You have most of the required skills.';
    if (pct >= 40) return ' Potential match. Consider developing additional skills.';
    return 'Consider building relevant skills in this area.';
  };

  return (
    <div className={`role-card premium-card ${isTopRole ? ' top-match' : ''}`}>
      <div className="role-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <div className="role-name">{role.name}</div>
            {isTopRole && <span className="role-badge"> Top Match</span>}
          </div>
          {role.description && (
            <p style={{ fontSize: '0.9rem', color: '#666', margin: '0' }}>{role.description}</p>
          )}
        </div>
      </div>

      {/* Match Percentage */}
      <div className="match-section">
        <div className="match-label">
          <span>Match Score</span>
          <span className="match-percentage">{typeof matchPercentage === 'string' ? matchPercentage : `${percentage.toFixed(2)}%`}</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Recommendation */}
      <p style={{ fontSize: '0.9rem', color: '#555', margin: '1rem 0 0 0', fontWeight: '500' }}>
        {getRecommendation(percentage)}
      </p>

      {/* Skills */}
      {role.topSkills && role.topSkills.length > 0 && (
        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e0e0e0' }}>
          <p style={{ fontSize: '0.85rem', fontWeight: '600', color: '#333', marginBottom: '0.5rem' }}>
            Required Skills:
          </p>
          <div className="tags">
            {role.topSkills.slice(0, 5).map((skill, i) => (
              <span key={i} className="tag">{skill}</span>
            ))}
            {role.topSkills.length > 5 && (
              <span style={{ fontSize: '0.9rem', color: '#666' }}>
                +{role.topSkills.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
