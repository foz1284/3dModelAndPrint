const express = require('express');
const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
require('dotenv').config();

const app = express();
const PORT = Number(process.env.PORT || 8080);
const AGENT_API_KEY = process.env.AGENT_API_KEY || 'dev-local-agent-key';
const DEFAULT_REQUIRE_APPROVALS = process.env.REQUIRE_APPROVALS !== 'false';
const DATA_DIR = path.join(__dirname, 'data');
const DB_PATH = path.join(DATA_DIR, 'jobs.db');

const publicDir = path.join(__dirname, 'public');

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function openDb() {
  ensureDataDir();
  return new sqlite3.Database(DB_PATH);
}

function runSql(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(err) {
      if (err) {
        reject(err);
      } else {
        resolve({ lastID: this.lastID, changes: this.changes });
      }
    });
  });
}

function getSql(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row || null);
    });
  });
}

function allSql(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows || []);
    });
  });
}

async function initializeDb() {
  const db = openDb();
  await runSql(db, `
    CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY,
      prompt TEXT NOT NULL,
      status TEXT NOT NULL,
      require_approval INTEGER NOT NULL,
      approval_mode TEXT NOT NULL,
      summary TEXT,
      model_url TEXT,
      render_images TEXT,
      gcode_url TEXT,
      print_job_id TEXT,
      approved INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      agent TEXT,
      revisions TEXT DEFAULT '[]'
    )
  `);
  db.close();
}

function parseJsonField(value) {
  if (!value) return [];
  try {
    return JSON.parse(value);
  } catch (error) {
    return [];
  }
}

function serializeJsonData(value) {
  return JSON.stringify(value || []);
}

function generateId() {
  return `job-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function requireAgentKey(req, res, next) {
  const key = req.header('x-agent-key');
  const expected = AGENT_API_KEY;

  if (!expected) {
    return next();
  }

  if (!key || key !== expected) {
    return res.status(401).json({ error: 'Missing or invalid agent key.' });
  }

  return next();
}

async function getJobs() {
  const db = openDb();
  const rows = await allSql(db, 'SELECT * FROM jobs ORDER BY created_at DESC');
  db.close();

  return rows.map((row) => ({
    id: row.id,
    prompt: row.prompt,
    status: row.status,
    requireApproval: Boolean(row.require_approval),
    mode: row.approval_mode,
    summary: row.summary,
    modelUrl: row.model_url,
    renderImages: parseJsonField(row.render_images),
    gcodeUrl: row.gcode_url,
    printJobId: row.print_job_id,
    approved: Boolean(row.approved),
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    agent: row.agent,
    revisions: parseJsonField(row.revisions),
    approvalHistory: []
  }));
}

async function getJobById(id) {
  const db = openDb();
  const row = await getSql(db, 'SELECT * FROM jobs WHERE id = ?', [id]);
  db.close();

  if (!row) return null;

  return {
    id: row.id,
    prompt: row.prompt,
    status: row.status,
    requireApproval: Boolean(row.require_approval),
    mode: row.approval_mode,
    summary: row.summary,
    modelUrl: row.model_url,
    renderImages: parseJsonField(row.render_images),
    gcodeUrl: row.gcode_url,
    printJobId: row.print_job_id,
    approved: Boolean(row.approved),
    createdAt: row.created_at,
    updatedAt: row.updated_at,
    agent: row.agent,
    revisions: parseJsonField(row.revisions),
    approvalHistory: []
  };
}

async function createJobRecord(prompt, opts = {}) {
  const now = new Date().toISOString();
  const requireApproval = typeof opts.requireApproval === 'boolean' ? opts.requireApproval : DEFAULT_REQUIRE_APPROVALS;
  const mode = opts.mode || (requireApproval ? 'approval' : 'one-shot');
  const id = generateId();

  const db = openDb();
  await runSql(db, `
    INSERT INTO jobs (
      id, prompt, status, require_approval, approval_mode, summary,
      model_url, render_images, gcode_url, print_job_id, approved,
      created_at, updated_at, agent, revisions
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `, [
    id,
    prompt,
    'queued',
    requireApproval ? 1 : 0,
    mode,
    'Queued for the laptop agent.',
    null,
    '[]',
    null,
    null,
    0,
    now,
    now,
    null,
    '[]'
  ]);
  db.close();

  return getJobById(id);
}

async function saveJobUpdate(id, payload) {
  const existing = await getJobById(id);
  if (!existing) return null;

  const next = {
    ...existing,
    ...payload,
    updatedAt: new Date().toISOString(),
    renderImages: Array.isArray(payload.renderImages) ? payload.renderImages : existing.renderImages,
    revisions: Array.isArray(payload.revisions) ? payload.revisions : existing.revisions
  };

  const db = openDb();
  await runSql(db, `
    UPDATE jobs SET
      status = ?,
      require_approval = ?,
      approval_mode = ?,
      summary = ?,
      model_url = ?,
      render_images = ?,
      gcode_url = ?,
      print_job_id = ?,
      approved = ?,
      updated_at = ?,
      agent = ?,
      revisions = ?
    WHERE id = ?
  `, [
    next.status,
    next.requireApproval ? 1 : 0,
    next.mode || (next.requireApproval ? 'approval' : 'one-shot'),
    next.summary,
    next.modelUrl || null,
    serializeJsonData(next.renderImages),
    next.gcodeUrl || null,
    next.printJobId || null,
    next.approved ? 1 : 0,
    next.updatedAt,
    next.agent || null,
    serializeJsonData(next.revisions),
    id
  ]);
  db.close();

  return getJobById(id);
}

app.use(express.json({ limit: '20mb' }));
app.use(express.static(publicDir));

app.get('/api/health', (req, res) => {
  res.json({
    ok: true,
    service: '3dModelAndPrint',
    requireApprovals: DEFAULT_REQUIRE_APPROVALS,
    apiKeyConfigured: Boolean(AGENT_API_KEY),
    timestamp: new Date().toISOString()
  });
});

app.get('/api/jobs', async (req, res) => {
  const jobs = await getJobs();
  res.json(jobs);
});

app.post('/api/jobs', async (req, res) => {
  const prompt = String(req.body?.prompt || '').trim();
  if (!prompt) {
    return res.status(400).json({ error: 'A prompt is required.' });
  }

  const requireApproval = typeof req.body?.requireApproval === 'boolean'
    ? req.body.requireApproval
    : (req.body?.approvalMode === 'one-shot' ? false : DEFAULT_REQUIRE_APPROVALS);

  const job = await createJobRecord(prompt, {
    requireApproval,
    mode: req.body?.approvalMode || (requireApproval ? 'approval' : 'one-shot')
  });

  res.status(201).json(job);
});

app.get('/api/jobs/:id', async (req, res) => {
  const job = await getJobById(req.params.id);
  if (!job) {
    return res.status(404).json({ error: 'Job not found.' });
  }
  res.json(job);
});

app.post('/api/jobs/:id/approve', async (req, res) => {
  const existing = await getJobById(req.params.id);
  if (!existing) {
    return res.status(404).json({ error: 'Job not found.' });
  }

  const updated = await saveJobUpdate(req.params.id, {
    status: 'approved',
    approved: true,
    requireApproval: false,
    mode: 'approval',
    summary: 'Approved by the user. Ready to export and slice.'
  });

  res.json(updated);
});

app.post('/api/jobs/:id/iterate', async (req, res) => {
  const existing = await getJobById(req.params.id);
  if (!existing) {
    return res.status(404).json({ error: 'Job not found.' });
  }

  const prompt = String(req.body?.prompt || '').trim();
  if (!prompt) {
    return res.status(400).json({ error: 'A revision request is required.' });
  }

  const revisions = Array.isArray(existing.revisions) ? existing.revisions : [];
  revisions.push({ prompt, createdAt: new Date().toISOString() });

  const updated = await saveJobUpdate(req.params.id, {
    status: 'needs_revision',
    summary: 'User requested a revision. The laptop agent will revise the design.',
    revisions
  });

  res.json(updated);
});

app.post('/api/jobs/:id/trigger-print', async (req, res) => {
  const existing = await getJobById(req.params.id);
  if (!existing) {
    return res.status(404).json({ error: 'Job not found.' });
  }

  const updated = await saveJobUpdate(req.params.id, {
    status: 'exporting',
    summary: 'Approved model is being exported and sliced for printing.'
  });

  res.json(updated);
});

app.get('/api/agent/jobs/next', requireAgentKey, async (req, res) => {
  const statuses = (req.query.status || 'queued,needs_revision').split(',').map((value) => value.trim()).filter(Boolean);
  const jobs = await getJobs();
  const next = jobs.find((job) => statuses.includes(job.status));
  res.json(next || null);
});

app.post('/api/agent/jobs/:id/update', requireAgentKey, async (req, res) => {
  const existing = await getJobById(req.params.id);
  if (!existing) {
    return res.status(404).json({ error: 'Job not found.' });
  }

  const payload = req.body || {};
  const next = {
    ...existing,
    status: payload.status || existing.status,
    summary: payload.summary || existing.summary,
    modelUrl: payload.modelUrl || existing.modelUrl,
    renderImages: Array.isArray(payload.renderImages) ? payload.renderImages : existing.renderImages,
    gcodeUrl: payload.gcodeUrl || existing.gcodeUrl,
    printJobId: payload.printJobId || existing.printJobId,
    requireApproval: typeof payload.requireApproval === 'boolean' ? payload.requireApproval : existing.requireApproval,
    mode: payload.mode || existing.mode,
    agent: payload.agent || existing.agent,
    approved: typeof payload.approved === 'boolean' ? payload.approved : existing.approved
  };

  const updated = await saveJobUpdate(req.params.id, next);
  res.json(updated);
});

app.get('*', (req, res) => {
  res.sendFile(path.join(publicDir, 'index.html'));
});

initializeDb().then(() => {
  app.listen(PORT, () => {
    console.log(`3D Model & Print server running on http://localhost:${PORT}`);
  });
}).catch((error) => {
  console.error('Failed to initialize DB:', error);
  process.exit(1);
});
