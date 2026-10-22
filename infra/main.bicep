# 3D Model & Print

A workflow for AI-assisted generation of 3D-printable objects, with approval gates and laptop-side automation for FreeCAD + PrusaSlicer.

## What this project does

- Accepts a design request from a web UI
- Queues the request for a local laptop agent
- Runs CAD generation via FreeCAD when installed
- Produces preview renders for user review
- Allows approval, revision, or one-shot execution
- Exports STL/G-code and submits to Prusa Connect when configured
- Persists workflow state in SQLite for local and lightweight deployment
- Supports Azure-ready deployment patterns with Blob Storage and App Service

## Local development

1. Install dependencies:
   npm install
2. Start the web app:
   npm start
3. Run the laptop worker:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r agent/requirements.txt
   BASE_URL=http://localhost:8080 AGENT_API_KEY=dev-local-agent-key python3 agent/laptop_agent.py
4. Open the app at http://localhost:8080

## Security model

- The web app expects an `X-Agent-Key` header from the laptop agent.
- `AGENT_API_KEY` should be a long random secret in production.
- For a real deployment, run the web app behind HTTPS and keep the agent key out of source control.

## Azure deployment steps

### 1) Create the Azure resources

```bash
az group create --name rg-3dmodelandprint --location eastus
az storage account create \
  --name <storage-account-name> \
  --resource-group rg-3dmodelandprint \
  --location eastus \
  --sku Standard_LRS
az webapp up \
  --name <app-name> \
  --resource-group rg-3dmodelandprint \
  --runtime "NODE|20-lts" \
  --location eastus
```

### 2) Configure application settings

```bash
az webapp config appsettings set \
  --name <app-name> \
  --resource-group rg-3dmodelandprint \
  --settings \
    PORT=8080 \
    REQUIRE_APPROVALS=true \
    AGENT_API_KEY='<your-long-secret>' \
    AZURE_STORAGE_CONNECTION_STRING='<connection-string>' \
    AZURE_STORAGE_CONTAINER=artifacts
```

### 3) Deploy the repo

```bash
az webapp deploy --resource-group rg-3dmodelandprint --name <app-name> --src-path . --type zip
```

### 4) Optional database upgrade

For production scale, replace SQLite with Azure Database for PostgreSQL or Azure SQL. The application model is already structured for a single-job table and artifact URLs, so it can be moved to a relational database without changing the core workflow.

## Production architecture

- Azure App Service hosts the web UI and API.
- SQLite is used for local/dev simplicity; Azure PostgreSQL is the recommended production database.
- Azure Blob Storage stores STL, G-code, and preview files.
- The laptop agent runs on a trusted machine and polls for new jobs via a signed secret header.
- The laptop agent uploads local artifacts to Blob Storage when the Azure connection string is configured.
- FreeCAD and PrusaSlicer are invoked locally on the laptop using CLI commands.

## Real CAD and slicer integration

Example commands:

```bash
freecadcmd -c /path/to/generate_model.py
prusaslicer /path/to/model.stl --output /path/to/output.gcode
```

Use these commands in a real job runner or a local script. The project is structured to allow the laptop worker to call the tool chain securely and then post URLs back to the app.

## Folder layout

- `server.js` — web API and job state
- `public/` — front-end UI
- `agent/laptop_agent.py` — laptop automation worker
- `data/` — SQLite database and persisted state
- `infra/` — Azure deployment templates

## Next recommended production steps

1. Replace SQLite with Azure PostgreSQL or SQL Database.
2. Add file upload endpoints and signed artifact URLs.
3. Add user authentication and job ownership.
4. Add a stronger AI-to-CAD generator and a real CAD script generator.
5. Integrate Prusa Connect API using OAuth or API keys.
6. Add queueing with Azure Service Bus for more resilient workloads.

## Notes

This version intentionally keeps the CAD and slicer flows real-command-based but compatible with a fallback local placeholder. That makes it safe for development while giving you the path to production integration.
