from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

SUPABASE_REST_URL = os.getenv("SUPABASE_REST_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class SupabaseRestError(RuntimeError):
    pass


class SupabaseClient:
    def __init__(self) -> None:
        if not SUPABASE_REST_URL or not SUPABASE_ANON_KEY:
            raise SupabaseRestError(
                "Missing SUPABASE_REST_URL or SUPABASE_ANON_KEY in backend/.env"
            )

        self.base_url = SUPABASE_REST_URL
        self.headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
        }

    def select(self, table: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
        return self._request("GET", table, params=params)

    def insert(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        rows = self._request(
            "POST",
            table,
            json=payload,
            headers={"Prefer": "return=representation"},
        )
        return rows[0] if rows else {}

    def update(
        self,
        table: str,
        column: str,
        value: str | int,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        rows = self._request(
            "PATCH",
            table,
            params={column: f"eq.{value}"},
            json=payload,
            headers={"Prefer": "return=representation"},
        )
        return rows[0] if rows else {}

    def delete(self, table: str, column: str, value: str | int) -> list[dict[str, Any]]:
        return self._request(
            "DELETE",
            table,
            params={column: f"eq.{value}"},
            headers={"Prefer": "return=representation"},
        )

    def _request(
        self,
        method: str,
        table: str,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        request_headers = {**self.headers, **(headers or {})}
        url = f"{self.base_url}/{quote(table)}"

        response = requests.request(
            method,
            url,
            params=params,
            json=json,
            headers=request_headers,
            timeout=30,
        )

        if response.status_code >= 400:
            raise SupabaseRestError(f"Supabase error {response.status_code}: {response.text}")

        if not response.text:
            return []

        return response.json()


supabase = SupabaseClient()
