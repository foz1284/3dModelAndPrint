# 3D Model & Print

This project is an AI-assisted 3D printing workflow. It lets a user request a 3D print design from a web app, have a laptop-side agent generate a CAD model, review the result, approve or revise it, and then export/slice and submit it for printing.

The app supports two modes:
- Approval mode (default): user reviews each design before printing.
- One-shot mode: set `REQUIRE_APPROVALS=false` to skip approval after the model is generated.

## What you need before setup

Install these tools on your machine:
- Node.js 20+
- Python 3.11+
- Git
- Optional but recommended for real CAD/slicing:
  - FreeCAD (`freecadcmd`)
  - PrusaSlicer (`prusaslicer`)
- Azure CLI if you want to deploy to Azure

## 1) Clone the repo

```bash
git clone https://github.com/foz1284/3dModelAndPrint.git
cd 3dModelAndPrint
```

## 2) Install Node dependencies

```bash
npm install
```

This installs the web server dependencies used by the Express app.

## 3) Install Python dependencies for the laptop agent

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r agent/requirements.txt
```

## 4) Create your environment file

Copy the sample file and edit the values.

```bash
cp .env.example .env
```

Open `.env` and set values like this:

```env
PORT=8080
REQUIRE_APPROVALS=true
AGENT_API_KEY=change-this-to-a-secret-long-random-string
BASE_URL=http://localhost:8080
AGENT_ID=laptop-agent
WORKSPACE=./workspace
PRUSA_CONNECT_API_KEY=
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER=artifacts
```

Important notes:
- `AGENT_API_KEY` must match the key used by the laptop agent.
- Use a long random secret in real deployments.
- Leave `PRUSA_CONNECT_API_KEY` blank if you are not yet connected to Prusa Connect.
- Leave Azure values blank until you configure Azure Blob Storage.

## 5) Start the web app

Run the app from the repo root:

```bash
npm start
```

The app should start at:

```text
http://localhost:8080
```

You can test the app by opening the URL in a browser. It will show a simple interface for creating design requests.

## 6) Start the laptop agent

In a second terminal, run:

```bash
source .venv/bin/activate
BASE_URL=http://localhost:8080 AGENT_API_KEY=change-this-to-a-secret-long-random-string python3 agent/laptop_agent.py
```

This runs the laptop automation service, which:
- polls the web app for new jobs
- creates a model from the prompt
- posts render previews back to the app
- waits for approval or runs one-shot processing
- exports STL/G-code if approved
- submits a print job when configured

## 7) Use the app

1. Open http://localhost:8080
2. Enter a design brief, for example:
   - "A phone stand with cable routing and a rounded base"
   - "A custom wall hook with a hidden screw mount"
   - "A minimalist desk organizer with slots"
3. Click Submit request.
4. The laptop agent will pick it up and start the workflow.
5. Review generated previews on the site.
6. Use the approval controls to:
   - approve the model
   - request a revision
   - trigger print export
7. If one-shot mode is enabled, approval is skipped automatically.

## 8) Switch to one-shot mode

Set this in your `.env` file:

```env
REQUIRE_APPROVALS=false
```

Then restart the web app. The workflow will skip the approval step and proceed directly from generation to export.

## 9) Real CAD + slicer setup

If you install FreeCAD and PrusaSlicer locally, the laptop agent will call them automatically using CLI commands like:

```bash
freecadcmd -c /path/to/generate_model.py
prusaslicer /path/to/model.stl --output /path/to/output.gcode
```

If they are not installed, the app falls back to placeholder STL/G-code files so the workflow still runs for local testing.

## 10) Azure deployment setup

The repo is structured to be deployable to Azure App Service. Follow these steps.

### Step A: Create a resource group

```bash
az group create --name rg-3dmodelandprint --location eastus
```

### Step B: Create a storage account for artifacts

```bash
az storage account create \
  --name <storageaccountname> \
  --resource-group rg-3dmodelandprint \
  --location eastus \
  --sku Standard_LRS
```

Choose a globally unique storage account name. Keep it lowercase and no spaces.

### Step C: Create the web app

```bash
az webapp up \
  --name <app-name> \
  --resource-group rg-3dmodelandprint \
  --runtime "NODE|20-lts" \
  --location eastus
```

### Step D: Get the storage connection string

```bash
az storage account show-connection-string \
  --name <storageaccountname> \
  --resource-group rg-3dmodelandprint
```

Copy the connection string value.

### Step E: Configure app settings in Azure

```bash
az webapp config appsettings set \
  --name <app-name> \
  --resource-group rg-3dmodelandprint \
  --settings \
    PORT=8080 \
    REQUIRE_APPROVALS=true \
    AGENT_API_KEY='<your-long-secret>' \
    AZURE_STORAGE_CONNECTION_STRING='<your-storage-connection-string>' \
    AZURE_STORAGE_CONTAINER=artifacts
```

### Step F: Deploy the app

From the repo root:

```bash
az webapp deploy \
  --resource-group rg-3dmodelandprint \
  --name <app-name> \
  --src-path . \
  --type zip
```

Then open the default Azure URL for the web app.

## 11) Production architecture recommendations

For a production deployment, the project is designed to evolve in this direction:

- Azure App Service hosts the web app
- Azure Blob Storage stores STL, G-code, and preview images
- SQLite is fine for local/dev use; Azure PostgreSQL is recommended for production
- Laptop agent runs on a trusted machine inside your local network or secured VM
- Use HTTPS and an API key or signed token between the app and the laptop agent
- Use Azure Key Vault for secrets like `AGENT_API_KEY`, `PRUSA_CONNECT_API_KEY`, and Azure connection strings

## 12) Best next upgrades for a real deployment

Recommended next steps:
1. Replace SQLite with Azure PostgreSQL or Azure SQL
2. Add user login and job ownership
3. Add Azure Key Vault secret handling
4. Add real CAD generation service integration
5. Add real Prusa Connect API integration
6. Add artifact uploads to Blob Storage for STL and G-code
7. Add queueing with Azure Service Bus for scalable job handling

## 13) Project structure

- `server.js` – main web backend and job API
- `public/` – web UI assets
- `agent/laptop_agent.py` – laptop-side automation worker
- `.env.example` – environment template
- `infra/main.bicep` – Azure infrastructure starter template
- `data/` – SQLite database saved locally

## Troubleshooting

### App does not start

Check:
- Node is installed
- dependencies are installed with `npm install`
- `.env` exists and has valid values

### Laptop agent does not connect

Check:
- `BASE_URL` points to the running web app
- `AGENT_API_KEY` matches the server value
- the web app is running and not failing startup

### No CAD output

This usually means FreeCAD is not installed. The app falls back to placeholder STL output. Install FreeCAD and rerun the worker to generate real models.

### No slicer output

Install PrusaSlicer or configure your real slicer path. Without it, the system generates a placeholder G-code file for testing.

## Summary

This project gives you the core workflow for:
- request capture
- local model generation
- user review/approval
- export and slicing
- print submission
- Azure deployment readiness

It is ready to extend into a true production AI-to-print system with the tooling and architecture already in place.
