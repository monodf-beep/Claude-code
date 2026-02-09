"""
n8n Workflow Manager — safe workflow operations with backup & human-in-the-loop.

Usage (as a library, called by Claude):
    from n8n_manager import N8NManager
    mgr = N8NManager()
    mgr.list_workflows()
    mgr.backup_workflow("workflow_id")
    mgr.get_workflow("workflow_id")
    mgr.update_workflow("workflow_id", new_data)
    mgr.create_workflow(workflow_data)
    mgr.activate_workflow("workflow_id")
    mgr.deactivate_workflow("workflow_id")
    mgr.delete_workflow("workflow_id")
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from copy import deepcopy

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

# Load .env manually (no dependency on python-dotenv)
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

BASE_URL = os.environ.get("N8N_BASE_URL", "").rstrip("/")
API_KEY = os.environ.get("N8N_API_KEY", "")
BACKUP_DIR = Path(__file__).parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


class N8NManager:
    """Manages n8n workflows with automatic backup and safety checks."""

    def __init__(self, base_url=None, api_key=None):
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.api_key = api_key or API_KEY
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    def _api(self, method, path, data=None):
        """Make an API call to n8n."""
        url = f"{self.base_url}/api/v1{path}"
        resp = requests.request(method, url, headers=self.headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ── Read operations ──────────────────────────────────────────────

    def list_workflows(self):
        """List all workflows (id, name, active, node count)."""
        data = self._api("GET", "/workflows?limit=250")
        workflows = []
        for w in data.get("data", []):
            workflows.append({
                "id": w["id"],
                "name": w["name"],
                "active": w.get("active", False),
                "nodes": len(w.get("nodes", [])),
                "tags": [t["name"] for t in w.get("tags", [])],
                "updatedAt": w.get("updatedAt"),
            })
        return workflows

    def get_workflow(self, workflow_id):
        """Get full workflow definition."""
        return self._api("GET", f"/workflows/{workflow_id}")

    def get_workflow_summary(self, workflow_id):
        """Get a human-readable summary of a workflow."""
        wf = self.get_workflow(workflow_id)
        nodes = wf.get("nodes", [])
        connections = wf.get("connections", {})
        summary = {
            "id": wf["id"],
            "name": wf["name"],
            "active": wf.get("active", False),
            "nodes": [],
            "connection_count": sum(
                len(conns) for targets in connections.values() for conns in targets.values()
            ),
        }
        for node in nodes:
            summary["nodes"].append({
                "name": node.get("name"),
                "type": node.get("type"),
                "position": node.get("position"),
            })
        return summary

    # ── Backup operations ────────────────────────────────────────────

    def backup_workflow(self, workflow_id, label=None):
        """
        Backup a workflow:
        1. Save JSON locally in backups/
        2. Create a clone on n8n with [BACKUP <timestamp>] prefix

        Returns (local_path, cloned_workflow_id).
        """
        wf = self.get_workflow(workflow_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tag = label or timestamp

        # 1. Local JSON backup
        filename = f"{workflow_id}_{tag}.json"
        local_path = BACKUP_DIR / filename
        local_path.write_text(json.dumps(wf, indent=2, ensure_ascii=False))

        # 2. Clone on n8n
        clone = deepcopy(wf)
        clone["name"] = f"[BACKUP {tag}] {wf['name']}"
        # Remove fields that shouldn't be in create payload
        for key in ("id", "createdAt", "updatedAt", "versionId", "homeProject", "sharedWithProjects"):
            clone.pop(key, None)
        clone["active"] = False  # backups are always inactive

        created = self._api("POST", "/workflows", data=clone)
        clone_id = created.get("id")

        return str(local_path), clone_id

    def list_backups(self, workflow_id=None):
        """List local backup files, optionally filtered by workflow_id."""
        backups = sorted(BACKUP_DIR.glob("*.json"))
        if workflow_id:
            backups = [b for b in backups if b.name.startswith(workflow_id)]
        return [str(b) for b in backups]

    def restore_from_local(self, backup_path):
        """Load a workflow from a local backup file (returns dict, does NOT apply it)."""
        return json.loads(Path(backup_path).read_text())

    # ── Write operations (all require human approval) ────────────────

    def update_workflow(self, workflow_id, data):
        """
        Update a workflow. Caller is responsible for:
        1. Calling backup_workflow() first
        2. Getting human approval

        `data` should be the full workflow body to PUT.
        """
        # Remove read-only fields
        payload = deepcopy(data)
        for key in ("id", "createdAt", "updatedAt", "homeProject", "sharedWithProjects"):
            payload.pop(key, None)
        return self._api("PUT", f"/workflows/{workflow_id}", data=payload)

    def create_workflow(self, data):
        """Create a new workflow."""
        payload = deepcopy(data)
        for key in ("id", "createdAt", "updatedAt", "homeProject", "sharedWithProjects"):
            payload.pop(key, None)
        return self._api("POST", "/workflows", data=payload)

    def activate_workflow(self, workflow_id):
        """Activate a workflow."""
        return self._api("PATCH", f"/workflows/{workflow_id}", data={"active": True})

    def deactivate_workflow(self, workflow_id):
        """Deactivate a workflow."""
        return self._api("PATCH", f"/workflows/{workflow_id}", data={"active": False})

    def delete_workflow(self, workflow_id):
        """Delete a workflow. USE WITH CAUTION — backup first!"""
        return self._api("DELETE", f"/workflows/{workflow_id}")

    # ── Execution operations ─────────────────────────────────────────

    def list_executions(self, workflow_id=None, limit=20):
        """List recent executions."""
        params = f"?limit={limit}"
        if workflow_id:
            params += f"&workflowId={workflow_id}"
        return self._api("GET", f"/executions{params}")

    def get_execution(self, execution_id):
        """Get details of a specific execution."""
        return self._api("GET", f"/executions/{execution_id}")


# ── CLI for quick tests ──────────────────────────────────────────────

if __name__ == "__main__":
    mgr = N8NManager()

    if len(sys.argv) < 2:
        print("Usage: python n8n_manager.py <command> [args]")
        print("Commands: list, get <id>, backup <id>, summary <id>, executions [id]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        for w in mgr.list_workflows():
            status = "ACTIVE" if w["active"] else "off"
            print(f"  [{status:6}] {w['id']:20} {w['nodes']:2} nodes  {w['name']}")

    elif cmd == "get" and len(sys.argv) > 2:
        wf = mgr.get_workflow(sys.argv[2])
        print(json.dumps(wf, indent=2, ensure_ascii=False))

    elif cmd == "backup" and len(sys.argv) > 2:
        local, clone_id = mgr.backup_workflow(sys.argv[2])
        print(f"Local backup: {local}")
        print(f"n8n clone ID: {clone_id}")

    elif cmd == "summary" and len(sys.argv) > 2:
        s = mgr.get_workflow_summary(sys.argv[2])
        print(json.dumps(s, indent=2, ensure_ascii=False))

    elif cmd == "executions":
        wf_id = sys.argv[2] if len(sys.argv) > 2 else None
        execs = mgr.list_executions(wf_id)
        for e in execs.get("data", []):
            print(f"  {e['id']}  status={e.get('status','?'):10}  wf={e.get('workflowId','?')}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
