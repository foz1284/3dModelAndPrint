const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 8080;
const REQUIRE_APPROVALS = process.env.REQUIRE_APPROVALS !== "false";

const jobs = new Map();

function createJobId() {
  return `job-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function newJob(prompt, config = {}) {
  const id = createJobId();

  return {
    id,
    prompt,
    status: "queued",
    requireApproval: config.requireApproval ?? REQUIRE_APPROVALS,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    summary: "Waiting for the laptop agent to generate the first model.",
    modelUrl: null,
    renderImages: [],
    gcodeUrl: null,
    printJobId: null,
    approvalHistory: [],
    agent: config.agent || null,
    revisions: []
  };
}

app.use(express.json({ limit: "20mb" }));
app.use(express.static(path.join(__dirname, "public")));

app.get("/api/health", (req, res) => {
  res.json({ ok: true, service: "3dModelAndPrint", requireApprovals: REQUIRE_APPROVALS });
});

app.post("/api/jobs", (req, res) => {
  const prompt = (req.body?.prompt || "").trim();

  if (!prompt) {
    return res.status(400).json({ error: "A prompt is required." });
  }

  const job = newJob(prompt, { requireApproval: req.body?.requireApproval ?? REQUIRE_APPROVALS });
  jobs.set(job.id, job);

  res.status(201).json(job);
});

app.get("/api/jobs", (req, res) => {
  const status = req.query.status;
  const allJobs = Array.from(jobs.values()).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const filtered = status ? allJobs.filter((job) => job.status === status) : allJobs;
  res.json(filtered);
});

app.get("/api/jobs/:id", (req, res) => {
  const item = jobs.get(req.params.id);
  if (!item) {
    return res.status(404).json({ error: "Job not found." });
  }
  res.json(item);
});

app.post("/api/jobs/:id/approve", (req, res) => {
  const item = jobs.get(req.params.id);
  if (!item) {
    return res.status(404).json({ error: "Job not found." });
  }

  item.status = "approved";
  item.updatedAt = new Date().toISOString();
  item.summary = "Approved by the user. Ready to export and slice.";
  item.approvalHistory.push({
    type: "approve",
    approvedBy: req.body?.user || "web-user",
    timestamp: item.updatedAt
  });

  res.json(item);
});

app.post("/api/jobs/:id/iterate", (req, res) => {
  const item = jobs.get(req.params.id);
  if (!item) {
    return res.status(404).json({ error: "Job not found." });
  }

  const prompt = (req.body?.prompt || "").trim();
  if (!prompt) {
    return res.status(400).json({ error: "A revision request is required." });
  }

  item.status = "needs_revision";
  item.updatedAt = new Date().toISOString();
  item.revisions.push({ prompt, timestamp: item.updatedAt });
  item.summary = "User requested a revision. The laptop agent will refine the model.";

  res.json(item);
});

app.post("/api/jobs/:id/trigger-print", (req, res) => {
  const item = jobs.get(req.params.id);
  if (!item) {
    return res.status(404).json({ error: "Job not found." });
  }

  item.status = "exporting";
  item.updatedAt = new Date().toISOString();
  item.summary = "Exporting the approved model and preparing the print job.";

  res.json(item);
});

app.get("/api/agent/jobs/next", (req, res) => {
  const statuses = (req.query.status || "queued,needs_revision").split(",");
  const candidates = Array.from(jobs.values())
    .filter((job) => statuses.includes(job.status))
    .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));

  res.json(candidates[0] || null);
});

app.post("/api/agent/jobs/:id/update", (req, res) => {
  const item = jobs.get(req.params.id);
  if (!item) {
    return res.status(404).json({ error: "Job not found." });
  }

  const { status, summary, modelUrl, renderImages, gcodeUrl, printJobId, agent } = req.body || {};

  if (status) item.status = status;
  if (summary) item.summary = summary;
  if (modelUrl) item.modelUrl = modelUrl;
  if (Array.isArray(renderImages)) item.renderImages = renderImages;
  if (gcodeUrl) item.gcodeUrl = gcodeUrl;
  if (printJobId) item.printJobId = printJobId;
  if (agent) item.agent = agent;

  item.updatedAt = new Date().toISOString();

  res.json(item);
});

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
  console.log(`3D print workflow server is running at http://localhost:${PORT}`);
});
