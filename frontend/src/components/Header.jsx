export default function Header() {
  return (
    <header className="header-component glass">
      <div className="header-inner container" style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "70px"
      }}>

        <div className="logo-section" style={{
          display: "flex",
          alignItems: "center",
          gap: "10px"
        }}>
          <div className="logo-icon">🚀</div>

          <h1 className="header-title gradient-text" style={{
            fontSize: "1.4rem",
            fontWeight: "600"
          }}>
            AI Career Mentor
          </h1>
        </div>

      </div>
    </header>
  );
}