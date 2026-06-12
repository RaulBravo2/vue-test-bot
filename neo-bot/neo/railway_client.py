"""Cliente de la API pública (GraphQL) de Railway para gestionar environments de preview.

Se usa para el comando `!neo bajar pr-N` y para la limpieza automática al cerrar un PR.
Doc: https://docs.railway.com/reference/public-api
"""
from __future__ import annotations

import httpx


class RailwayError(RuntimeError):
    pass


class RailwayClient:
    def __init__(self, api_token: str, project_id: str, graphql_url: str) -> None:
        self._token = api_token
        self._project_id = project_id
        self._url = graphql_url

    @property
    def configured(self) -> bool:
        return bool(self._token and self._project_id)

    async def _gql(self, query: str, variables: dict) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self._url,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
                json={"query": query, "variables": variables},
            )
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("errors"):
                raise RailwayError(str(payload["errors"]))
            return payload["data"]

    async def list_environments(self) -> list[dict]:
        query = """
        query environments($projectId: String!) {
          environments(projectId: $projectId) {
            edges { node { id name } }
          }
        }
        """
        data = await self._gql(query, {"projectId": self._project_id})
        return [edge["node"] for edge in data["environments"]["edges"]]

    async def find_pr_environment(self, pr_number: int) -> dict | None:
        """Busca el environment del PR. Railway suele nombrarlos `pr-<N>`; aceptamos
        coincidencia exacta o que el nombre contenga `pr-<N>` (p. ej. `uko-vue-pr-12`)."""
        target = f"pr-{pr_number}"
        envs = await self.list_environments()
        # Coincidencia exacta primero.
        for env in envs:
            if env["name"].lower() == target:
                return env
        # Luego "contiene", evitando falsos positivos tipo pr-1 vs pr-12.
        for env in envs:
            name = env["name"].lower()
            if target in name and not _has_longer_pr_match(name, pr_number):
                return env
        return None

    async def delete_environment(self, environment_id: str) -> bool:
        mutation = """
        mutation environmentDelete($id: String!) {
          environmentDelete(id: $id)
        }
        """
        data = await self._gql(mutation, {"id": environment_id})
        return bool(data.get("environmentDelete"))


def _has_longer_pr_match(name: str, pr_number: int) -> bool:
    """True si `name` parece referir a un PR de número mayor que comparte prefijo,
    p. ej. evita que `pr-1` matchee el environment `pr-12`."""
    import re

    for found in re.findall(r"pr-(\d+)", name):
        if int(found) != pr_number:
            return True
    return False
