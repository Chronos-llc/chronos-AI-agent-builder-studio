import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt, JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from e2b import Sandbox  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Sandbox = None


@dataclass
class VirtualComputerSession:
    session_id: str
    agent_id: int
    user_id: int
    sandbox: Any
    created_at: datetime
    last_used_at: datetime
    idle_timeout_seconds: int
    max_runtime_seconds: int


class VirtualComputerManager:
    def __init__(self):
        self._sessions: Dict[str, VirtualComputerSession] = {}
        self._lock = asyncio.Lock()

    def _now(self) -> datetime:
        return datetime.utcnow()

    def _sandbox_api_url(self) -> str:
        host = settings.API_HOST
        if host in {"0.0.0.0", "::"}:
            host = "localhost"
        return f"http://{host}:{settings.API_PORT}"

    def _create_sandbox_token(self, agent_id: int, user_id: int, ttl_minutes: int = 15) -> str:
        expire = self._now() + timedelta(minutes=ttl_minutes)
        payload = {
            "exp": expire,
            "agent_id": agent_id,
            "user_id": user_id,
            "scope": "sandbox_mcp",
            "jti": str(uuid.uuid4())
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def decode_sandbox_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError as exc:
            raise ValueError("Invalid sandbox token") from exc
        if payload.get("scope") != "sandbox_mcp":
            raise ValueError("Invalid sandbox token scope")
        return payload

    def _assert_available(self):
        if not settings.E2B_API_KEY:
            raise RuntimeError("E2B_API_KEY not configured")
        if Sandbox is None:
            raise RuntimeError("E2B SDK is not installed")

    def _cleanup_expired(self):
        now = self._now()
        expired = []
        for session_id, session in self._sessions.items():
            idle_expired = (now - session.last_used_at).total_seconds() > session.idle_timeout_seconds
            runtime_expired = (now - session.created_at).total_seconds() > session.max_runtime_seconds
            if idle_expired or runtime_expired:
                expired.append(session_id)
        for session_id in expired:
            self._close_session(session_id)

    def _close_session(self, session_id: str):
        session = self._sessions.pop(session_id, None)
        if not session:
            return
        sandbox = session.sandbox
        try:
            if hasattr(sandbox, "close"):
                sandbox.close()
            elif hasattr(sandbox, "kill"):
                sandbox.kill()
        except Exception:
            logger.warning("Failed to close sandbox session", exc_info=True)

    def _write_file(self, sandbox: Any, path: str, content: str):
        if hasattr(sandbox, "files") and hasattr(sandbox.files, "write"):
            sandbox.files.write(path, content)
            return
        if hasattr(sandbox, "write_file"):
            sandbox.write_file(path, content)
            return
        raise RuntimeError("E2B sandbox does not support file writing")

    def _run_command(self, sandbox: Any, command: str, timeout: Optional[int] = None):
        if hasattr(sandbox, "commands") and hasattr(sandbox.commands, "run"):
            return sandbox.commands.run(command, timeout=timeout)
        if hasattr(sandbox, "run"):
            return sandbox.run(command)
        raise RuntimeError("E2B sandbox does not support command execution")

    def _set_envs(self, sandbox: Any, envs: Dict[str, str]):
        try:
            if hasattr(sandbox, "envs") and hasattr(sandbox.envs, "set"):
                for key, value in envs.items():
                    sandbox.envs.set(key, value)
                return
            if hasattr(sandbox, "set_env"):
                for key, value in envs.items():
                    sandbox.set_env(key, value)
        except Exception:
            logger.debug("Failed to set sandbox envs", exc_info=True)

    def _prepare_tools(self, sandbox: Any, token: str, api_url: str, server_ids: Optional[list[str]]):

        tools_json = {
            "operations": ["file_operation", "database_query", "web_scraping", "api_request"],
            "server_ids": server_ids or [],
            "api_url": api_url,
        }
        self._write_file(sandbox, "tools.json", json.dumps(tools_json, indent=2))

        helper = f"""import json
import os
import urllib.request

CHRONOS_API_URL = {api_url!r}
CHRONOS_TOKEN = {token!r}

def call_tool(operation_type, payload, server_id=None, group_name=None):
    url = f\"{CHRONOS_API_URL}/api/v1/virtual-computer/mcp-proxy\"
    data = json.dumps({{
        "operation_type": operation_type,
        "payload": payload,
        "server_id": server_id,
        "group_name": group_name
    }}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={{
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHRONOS_TOKEN}"
    }})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))
"""
        self._write_file(sandbox, "chronos_tools.py", helper)

    async def create_session(self, agent_id: int, user_id: int, idle_timeout_seconds: int, max_runtime_seconds: int,
                             server_ids: Optional[list[str]] = None, mcp_enabled: bool = True) -> VirtualComputerSession:
        self._assert_available()
        async with self._lock:
            self._cleanup_expired()

            api_url = self._sandbox_api_url()
            token = self._create_sandbox_token(agent_id, user_id)
            envs = {
                "CHRONOS_API_URL": api_url,
                "CHRONOS_SANDBOX_TOKEN": token,
            }
            try:
                sandbox = Sandbox(api_key=settings.E2B_API_KEY, envs=envs)
            except TypeError:
                sandbox = Sandbox(api_key=settings.E2B_API_KEY)
                self._set_envs(sandbox, envs)
            session_id = str(uuid.uuid4())
            now = self._now()
            session = VirtualComputerSession(
                session_id=session_id,
                agent_id=agent_id,
                user_id=user_id,
                sandbox=sandbox,
                created_at=now,
                last_used_at=now,
                idle_timeout_seconds=idle_timeout_seconds,
                max_runtime_seconds=max_runtime_seconds,
            )
            if mcp_enabled:
                self._prepare_tools(sandbox, token, api_url, server_ids)
            self._sessions[session_id] = session
            return session

    async def execute_python(
        self,
        agent_id: int,
        user_id: int,
        code: str,
        inputs: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        idle_timeout_seconds: int = 300,
        max_runtime_seconds: int = 900,
        server_ids: Optional[list[str]] = None,
        mcp_enabled: bool = True
    ) -> Dict[str, Any]:
        self._assert_available()
        async with self._lock:
            self._cleanup_expired()

            session = None
            if session_id:
                session = self._sessions.get(session_id)

            if session is None:
                session = await self.create_session(
                    agent_id=agent_id,
                    user_id=user_id,
                    idle_timeout_seconds=idle_timeout_seconds,
                    max_runtime_seconds=max_runtime_seconds,
                    server_ids=server_ids,
                    mcp_enabled=mcp_enabled
                )

            session.last_used_at = self._now()

            inputs = inputs or {}
            payload = json.dumps(inputs)
            script = (
                "import json\n"
                f"inputs = json.loads({payload!r})\n"
                + code
                + "\n"
            )
            self._write_file(session.sandbox, "main.py", script)

            start = self._now()
            result = await asyncio.to_thread(self._run_command, session.sandbox, "python main.py", timeout=max_runtime_seconds)
            duration_ms = int((self._now() - start).total_seconds() * 1000)

            stdout = getattr(result, "stdout", "") if result is not None else ""
            stderr = getattr(result, "stderr", "") if result is not None else ""
            exit_code = getattr(result, "exit_code", None) if result is not None else None

            return {
                "session_id": session.session_id,
                "stdout": stdout or "",
                "stderr": stderr or "",
                "exit_code": exit_code,
                "duration_ms": duration_ms
            }

    async def close_session(self, session_id: str):
        async with self._lock:
            self._close_session(session_id)


virtual_computer_manager = VirtualComputerManager()


def get_virtual_computer_manager() -> VirtualComputerManager:
    return virtual_computer_manager
