import { useState } from 'react';
import RoleCard from './RoleCard';

export default function Result({ data, onReset }) {
  const [expandedRoles, setExpandedRoles] = useState(false);

  if (!data) return null;

  // Debug: Log the entire result data to verify API response structure
  console.log('=== FULL RESULT DATA ===');
  console.log('Complete response:', data);
  console.log('=== DATA STRUCTURE ===');
  console.log('detected_skills:', data.detected_skills);
  console.log('analysis_summary:', data.analysis_summary);
  console.log('analysis_summary.best_match_role:', data?.analysis_summary?.best_match_role);
  console.log('top_3_recommended_roles:', data.top_3_recommended_roles);
  if (data.top_3_recommended_roles?.[0]) {
    console.log('First recommended role:', data.top_3_recommended_roles[0]);
  }
  console.log('=== END DEBUG ===');
  
  // Map backend response to frontend structure with safety checks
  const detected_skills = data.detected_skills || [];
  const common_missing_skills = data.common_missing_skills || [];
  
  // Extract best match from analysis_summary with detailed logging
  const analysisData = data.analysis_summary || {};
  console.log('Extracted analysis_summary:', analysisData);
  
  const bestMatchPercentage = analysisData.best_match_percentage || 0;
  const bestMatchRoleData = analysisData.best_match_role || null;
  
  console.log('bestMatchPercentage:', bestMatchPercentage);
  console.log('bestMatchRoleData:', bestMatchRoleData);
  
  // Get all recommended roles
  const allRecommendedRoles = data.top_3_recommended_roles || [];
  console.log('allRecommendedRoles:', allRecommendedRoles);
  
  // Determine the best role with fallback logic
  // Use best_match_role if available, otherwise use first recommended role
  const bestRoleData = bestMatchRoleData || allRecommendedRoles?.[0];
  
  console.log('Final bestRoleData to use:', bestRoleData);
  console.log('bestRoleData.role:', bestRoleData?.role);
  console.log('bestRoleData.role_name:', bestRoleData?.role_name);
  
  // Build top_role object if we have best role data
  const top_role = bestRoleData
    ? {
        name: bestRoleData?.role || bestRoleData?.role_name || 'No role data available',
        description: bestRoleData?.description || bestRoleData?.role_description || '',
        required_skills: bestRoleData?.required_skills || [],
        match_percentage: bestMatchPercentage || bestRoleData?.match_percentage || 0,
      }
    : null;

  console.log('Final top_role object:', top_role);

  // ===== FIX: ROBUST DUPLICATE PREVENTION =====
  // Helper: normalize role names (handle case, spacing, and field variations)
  const normalize = (str) => (typeof str === 'string' ? str.toLowerCase().trim() : '');
  
  // Get the best role's normalized name for comparison
  const topRoleName = normalize(top_role?.name);

  // Filter out the best role from recommended roles
  // Uses normalized name comparison to handle:
  // - Case differences: "Data Scientist" vs "data scientist"
  // - Extra spaces: "Data  Scientist" vs "Data Scientist"
  // - Field inconsistencies: .role vs .role_name
  const filteredRoles = topRoleName
    ? allRecommendedRoles.filter((role) => {
        const roleName = normalize(role?.role || role?.role_name);
        return roleName !== topRoleName;
      })
    : allRecommendedRoles;

  // Apply expand/collapse logic
  const displayedRoles = expandedRoles
    ? filteredRoles
    : filteredRoles.slice(0, 5);

  return (
    <div className="fade-in">
      {/* Results Header */}
      <div className="results-header">
        <h2>Analysis Complete!</h2>
        <p>Here's your personalized career analysis based on your resume</p>
        <button onClick={onReset} className="btn-secondary" style={{ marginTop: '1rem', maxWidth: '300px' }}>
          ← Upload Another Resume
        </button>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-box slide-up">
          <div className="stat-number">{detected_skills.length}</div>
          <div className="stat-label">Skills Detected</div>
        </div>
        <div className="stat-box slide-up">
          <div className="stat-number">
            {bestMatchPercentage > 0 ? `${bestMatchPercentage.toFixed(2)}%` : 'N/A'}
          </div>
          <div className="stat-label">Top Match Score</div>
          <div className="small-progress">
            <div className="small-progress-bar">
              <div className="small-progress-fill" style={{ width: `${bestMatchPercentage}%` }} />
            </div>
          </div>
        </div>
        <div className="stat-box slide-up">
          <div className="stat-number">{common_missing_skills.length}</div>
          <div className="stat-label">Skills to Learn</div>
        </div>
      </div>

      {/* Top Role */}
      {top_role && top_role.name && top_role.name !== 'No role data available' ? (
        <div className="card">
          <h3>Your Best Career Match: {top_role.name}</h3>
          <p style={{ marginBottom: '1rem', color: '#666' }}>
            {bestMatchRoleData 
              ? 'Based on your resume, this role is your perfect fit'
              : 'Based on your skills, this is a great match for you'}
          </p>
          <RoleCard
            role={{
              name: top_role.name,
              description: top_role.description,
              topSkills: top_role.required_skills,
            }}
            matchPercentage={top_role.match_percentage.toFixed(2)}
            isTopRole={true}
          />
        </div>
      ) : (
        <div className="card">
          <h3>Your Best Career Match</h3>
          {allRecommendedRoles.length > 0 ? (
            <>
              <p style={{ marginBottom: '1rem', color: '#666' }}>Based on your skills analysis</p>
              <RoleCard
                role={{
                  name: allRecommendedRoles[0]?.role || 'Top Career Option',
                  description: allRecommendedRoles[0]?.description || '',
                  topSkills: allRecommendedRoles[0]?.required_skills || [],
                }}
                matchPercentage={(allRecommendedRoles[0]?.match_percentage || 0).toFixed(2)}
                isTopRole={true}
              />
            </>
          ) : (
            <div className="info-message">
              ℹ️ No clear best match found. Explore the recommended roles below to find your ideal fit.
            </div>
          )}
        </div>
      )}

      {/* AI Career Insights */}
      {data.ai_insights && (
        <div className="card ai-insights">
          <h3>Career Insights</h3>

          <div className="insight-block">
            <h4>Why this role suits you</h4>
            <p>{data.ai_insights.explanation}</p>
          </div>

          {data.ai_insights.recommendations && data.ai_insights.recommendations.length > 0 && (
            <div className="insight-block">
              <h4>How to improve</h4>
              <ul>
                {data.ai_insights.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Detected Skills */}
      {detected_skills.length > 0 && (
        <div className="card">
          <h3> Your Skills ({detected_skills.length})</h3>
          <div className="tags">
            {detected_skills.map((skill, i) => (
              <span key={i} className="tag">✓ {skill}</span>
            ))}
          </div>
        </div>
      )}

      {/* All Roles */}
      {allRecommendedRoles.length > 0 && (
        <div className="card">
          <h3>💼 Other Career Options ({filteredRoles.length} roles)</h3>
          <p style={{ marginBottom: '1.5rem', color: '#666' }}>Explore more career paths that match your profile</p>

          <div className="role-list">
            {displayedRoles.map((role, i) => (
              <RoleCard
                key={i}
                role={{
                  name: role?.role || role?.role_name || 'No role data available',
                  description: role?.description || role?.role_description || '',
                  topSkills: role?.required_skills || [],
                }}
                matchPercentage={(role?.match_percentage || 0).toFixed(2)}
              />
            ))}
          </div>

          {filteredRoles.length > 5 && (
            <button
              onClick={() => setExpandedRoles(!expandedRoles)}
              className="btn-secondary"
              style={{ marginTop: '1.5rem' }}
            >
              {expandedRoles ? '⬆ Show Less' : `⬇ Show All ${filteredRoles.length} Roles`}
            </button>
          )}
        </div>
      )}

      {/* Missing Skills */}
      {common_missing_skills.length > 0 && (
        <div className="card">
          <h3> Skills to Learn ({common_missing_skills.length})</h3>
          <p style={{ marginBottom: '1rem', color: '#666' }}>Focus on these skills to advance to your ideal role</p>
          <div className="tags">
            {common_missing_skills.slice(0, 20).map((skill, i) => (
              <span key={i} className="tag missing">→ {skill}</span>
            ))}
            {common_missing_skills.length > 20 && (
              <span style={{ color: '#666', fontSize: '0.9rem' }}>
                +{common_missing_skills.length - 20} more skills
              </span>
            )}
          </div>
        </div>
      )}

      {/* Action Steps */}
      <div className="card" style={{ background: '#f8faff', borderTop: '4px solid #4a90e2' }}>
        <h3> Next Steps</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginTop: '1.5rem' }}>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4a90e2', marginBottom: '0.5rem' }}>1</div>
            <strong>Learn Key Skills</strong>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>Focus on the top skills in your target role</p>
          </div>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4a90e2', marginBottom: '0.5rem' }}>2</div>
            <strong>Build Projects</strong>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>Create portfolio pieces with these skills</p>
          </div>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4a90e2', marginBottom: '0.5rem' }}>3</div>
            <strong>Apply & Interview</strong>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>Target companies looking for these roles</p>
          </div>
        </div>
      </div>
    </div>
  );
}
