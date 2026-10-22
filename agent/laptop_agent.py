* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: #08111f;
  color: #e8f1ff;
  font-family: Arial, Helvetica, sans-serif;
}

button,
input,
textarea {
  font: inherit;
}

.app-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px 48px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #7dd3fc;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h1, h2, h3, p {
  margin-top: 0;
}

.layout {
  display: grid;
  grid-template-columns: minmax(300px, 380px) 1fr;
  gap: 24px;
}

.panel {
  background: rgba(15, 23, 42, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 12px 30px rgba(8, 17, 31, 0.35);
}

textarea {
  width: 100%;
  min-height: 160px;
  resize: vertical;
  border: 1px solid #334155;
  background: #0f172a;
  color: #e5eefb;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

button {
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #38bdf8, #2563eb);
  color: white;
  font-weight: 700;
  cursor: pointer;
  padding: 10px 16px;
}

button.secondary {
  background: #1e293b;
  border: 1px solid #334155;
}

.toggle-wrap {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

#jobs {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.job-card {
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 16px;
  background: rgba(2, 6, 23, 0.75);
  padding: 16px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.job-id {
  color: #7dd3fc;
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.status-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(96, 165, 250, 0.45);
  background: rgba(37, 99, 235, 0.15);
  color: #bfdbfe;
  font-size: 11px;
  text-transform: uppercase;
}

.job-prompt,
.job-summary,
.empty,
.muted {
  color: #dbeafe;
}

.render-area {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin: 16px 0;
}

.preview-image {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.links {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.links a {
  color: #7dd3fc;
  text-decoration: none;
}

@media (max-width: 800px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
