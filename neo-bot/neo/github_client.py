"""Cliente de GitHub para Neo, autenticado como la GitHub App neo-bot.

Genera un JWT a partir del App ID + private key, lo canjea por un installation access token
(cacheado ~1h) y con eso dispara workflows y consulta PRs. No usa el GITHUB_TOKEN del runner:
así los PRs quedan a nombre de la App y la protección de rama impide que Neo los mergee.
"""
from __future__ import annotations

import time

import httpx
import jwt

API = "https://api.github.com"


class GitHubClient:
    def __init__(self, app_id: str, private_key: str, installation_id: str) -> None:
        self._app_id = app_id
        self._private_key = private_key
        self._installation_id = installation_id
        self._token: str | None = None
        self._token_exp: float = 0.0

    def _app_jwt(self) -> str:
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 9 * 60, "iss": self._app_id}
        return jwt.encode(payload, self._private_key, algorithm="RS256")

    async def _installation_token(self, client: httpx.AsyncClient) -> str:
        # Reutiliza el token mientras le queden > 5 min de vida.
        if self._token and time.time() < self._token_exp - 300:
            return self._token
        resp = await client.post(
            f"{API}/app/installations/{self._installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {self._app_jwt()}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["token"]
        # expires_at viene en ISO; por simplicidad asumimos validez de ~1h.
        self._token_exp = time.time() + 3600
        return self._token

    async def _headers(self, client: httpx.AsyncClient) -> dict[str, str]:
        token = await self._installation_token(client)
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def dispatch_workflow(
        self,
        repo: str,
        workflow_file: str,
        ref: str,
        inputs: dict[str, str],
    ) -> None:
        """Dispara el workflow Neo vía workflow_dispatch. GitHub responde 204 sin cuerpo."""
        async with httpx.AsyncClient(timeout=30) as client:
            headers = await self._headers(client)
            resp = await client.post(
                f"{API}/repos/{repo}/actions/workflows/{workflow_file}/dispatches",
                headers=headers,
                json={"ref": ref, "inputs": inputs},
            )
            resp.raise_for_status()

    async def latest_run_url(self, repo: str, workflow_file: str) -> str | None:
        """Mejor esfuerzo: devuelve la URL de la corrida más reciente del workflow."""
        async with httpx.AsyncClient(timeout=30) as client:
            headers = await self._headers(client)
            resp = await client.get(
                f"{API}/repos/{repo}/actions/workflows/{workflow_file}/runs",
                headers=headers,
                params={"event": "workflow_dispatch", "per_page": 1},
            )
            if resp.status_code != 200:
                return None
            runs = resp.json().get("workflow_runs", [])
            return runs[0]["html_url"] if runs else None

    async def get_pull_request(self, repo: str, number: int) -> dict | None:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = await self._headers(client)
            resp = await client.get(f"{API}/repos/{repo}/pulls/{number}", headers=headers)
            if resp.status_code != 200:
                return None
            return resp.json()

    async def comment_issue(self, repo: str, number: int, body: str) -> None:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = await self._headers(client)
            await client.post(
                f"{API}/repos/{repo}/issues/{number}/comments",
                headers=headers,
                json={"body": body},
            )
