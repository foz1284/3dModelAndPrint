* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  background: #0b1220;
  color: #e5eefb;
}

button,
textarea,
input {
  font: inherit;
}

.app-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px 48px;
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
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #74c0fc;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

.layout {
  display: grid;
  grid-template-columns: minmax(300px, 380px) minmax(0, 1fr);
  gap: 24px;
}

.panel {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 10px 35px rgba(15, 23, 42, 0.2);
}

label {
  display: block;
  margin-bottom: 8px;
  color: #c6d2e5;
}

textarea {
  width: 100%;
  min-height: 160px;
  resize: vertical;
  border-radius: 12px;
  border: 1px solid #334155;
  background: #0f172a;
  color: white;
  padding: 12px;
  margin-bottom: 16px;
}

button {
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #38bdf8, #2563eb);
  color: white;
  cursor: pointer;
  font-weight: 600;
}

button.secondary {
  background: #1e293b;
  border: 1px solid #334155;
}

.toggle-wrap {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #dbeafe;
}

#jobs {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.job-card {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  padding: 16px;
}

.job-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.job-id {
  display: inline-block;
  color: #7dd3fc;
  font-size: 12px;
  margin-bottom: 4px;
  letter-spacing: 0.06em;
}

.status-badge {
  display: inline-flex;
  border-radius: 999px;
  padding: 6px 10px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(96, 165, 250, 0.4);
  color: #bfdbfe;
  font-size: 12px;
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
  margin-top: 16px;
  margin-bottom: 16px;
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

.model-link {
  display: inline-block;
  color: #7dd3fc;
  text-decoration: none;
  margin-right: 12px;
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
