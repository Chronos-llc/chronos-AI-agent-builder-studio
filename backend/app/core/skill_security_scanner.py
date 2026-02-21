"""Security scanner for uploaded skill files.

Primary scan provider: VirusTotal.
Fallback: local deterministic rules when VT is unavailable or inconclusive.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.models.skills import SkillScanStatus

logger = logging.getLogger(__name__)


LOCAL_SUSPICIOUS_PATTERNS: list[tuple[str, str, int]] = [
    (r"\bos\.system\(", "Uses os.system shell execution", 45),
    (r"\bsubprocess\.(?:Popen|run|call)\(", "Uses subprocess execution", 40),
    (r"\beval\(", "Uses eval()", 55),
    (r"\bexec\(", "Uses exec()", 55),
    (r"\brequests\.(?:post|get|put|delete)\(", "Performs outbound HTTP requests", 20),
    (r"\bsocket\.", "Uses raw socket APIs", 35),
    (r"\bshutil\.rmtree\(", "Deletes filesystem directories", 50),
    (r"\brm\s+-rf\b", "Contains destructive shell pattern", 65),
    (r"\bdel\s+/\w+", "Contains Windows delete command pattern", 55),
    (r"(?:token|secret|api[_-]?key)\s*[:=]", "Contains secret-like instructions", 20),
    (r"\b(base64|b64decode)\(", "Contains encoded payload handling", 25),
]

LOCAL_MALICIOUS_PATTERNS: list[tuple[str, str, int]] = [
    (r"\bPowerShell\b.*-EncodedCommand", "Contains encoded PowerShell command", 85),
    (r"\bcurl\b.*\|\s*(?:bash|sh)\b", "Downloads and executes remote script", 95),
    (r"\bwget\b.*\|\s*(?:bash|sh)\b", "Downloads and executes remote script", 95),
    (r"\b(?:steal|exfiltrat|keylog|credential dump)\b", "Potential data exfiltration intent", 90),
]


@dataclass
class ScanResult:
    status: str
    confidence: int
    summary: str
    report: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "confidence": self.confidence,
            "summary": self.summary,
            "report": self.report,
        }


class SkillSecurityScanner:
    """Scans skill files for potential malicious behavior."""

    def __init__(self) -> None:
        self.virus_total_api_key = getattr(settings, "VIRUSTOTAL_API_KEY", None)
        self.vt_timeout_seconds = max(5, int(getattr(settings, "VIRUSTOTAL_TIMEOUT_SECONDS", 10)))
        self.vt_poll_attempts = max(1, int(getattr(settings, "VIRUSTOTAL_POLL_ATTEMPTS", 5)))
        self.local_suspicious_threshold = int(
            getattr(settings, "SKILL_LOCAL_SUSPICIOUS_THRESHOLD", 40)
        )
        self.local_malicious_threshold = int(
            getattr(settings, "SKILL_LOCAL_MALICIOUS_THRESHOLD", 80)
        )

    def _local_scan(self, content: str) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        score = 0
        lowered = content.lower()

        for pattern, reason, weight in LOCAL_SUSPICIOUS_PATTERNS:
            if re.search(pattern, content, flags=re.IGNORECASE):
                findings.append({"type": "suspicious", "reason": reason, "weight": weight, "pattern": pattern})
                score += weight

        for pattern, reason, weight in LOCAL_MALICIOUS_PATTERNS:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                findings.append({"type": "malicious", "reason": reason, "weight": weight, "pattern": pattern})
                score += weight

        normalized_score = min(score, 100)
        if normalized_score >= self.local_malicious_threshold:
            status = SkillScanStatus.MALICIOUS
        elif normalized_score >= self.local_suspicious_threshold:
            status = SkillScanStatus.SUSPICIOUS
        else:
            status = SkillScanStatus.BENIGN

        summary = "No risky patterns detected by local scanner."
        if findings:
            summary = f"Local scanner detected {len(findings)} risk indicators."

        return {
            "provider": "local_rules",
            "status": status,
            "score": normalized_score,
            "summary": summary,
            "findings": findings,
        }

    async def _virustotal_scan(self, filename: str, content_bytes: bytes) -> dict[str, Any]:
        if not self.virus_total_api_key:
            return {
                "provider": "virustotal",
                "status": "unavailable",
                "reason": "VIRUSTOTAL_API_KEY is not configured",
            }

        headers = {"x-apikey": self.virus_total_api_key}
        timeout = httpx.Timeout(float(self.vt_timeout_seconds), connect=float(self.vt_timeout_seconds))
        files = {"file": (filename, content_bytes, "text/markdown")}

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                upload = await client.post("https://www.virustotal.com/api/v3/files", headers=headers, files=files)
                upload.raise_for_status()
                upload_data = upload.json()
                analysis_id = upload_data.get("data", {}).get("id")

                if not analysis_id:
                    return {
                        "provider": "virustotal",
                        "status": "error",
                        "reason": "VirusTotal response missing analysis id",
                    }

                analysis_payload: dict[str, Any] | None = None
                for _ in range(self.vt_poll_attempts):
                    await asyncio.sleep(1.5)
                    response = await client.get(
                        f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                        headers=headers,
                    )
                    response.raise_for_status()
                    analysis_payload = response.json()
                    analysis_status = analysis_payload.get("data", {}).get("attributes", {}).get("status")
                    if analysis_status == "completed":
                        break

                if not analysis_payload:
                    return {
                        "provider": "virustotal",
                        "status": "error",
                        "reason": "No analysis payload returned",
                    }

                stats = (
                    analysis_payload.get("data", {})
                    .get("attributes", {})
                    .get("stats", {})
                )
                malicious = int(stats.get("malicious", 0) or 0)
                suspicious = int(stats.get("suspicious", 0) or 0)
                harmless = int(stats.get("harmless", 0) or 0)
                undetected = int(stats.get("undetected", 0) or 0)

                if malicious > 0:
                    mapped_status = SkillScanStatus.MALICIOUS
                elif suspicious > 0:
                    mapped_status = SkillScanStatus.SUSPICIOUS
                elif harmless > 0 or undetected > 0:
                    mapped_status = SkillScanStatus.BENIGN
                else:
                    mapped_status = SkillScanStatus.SUSPICIOUS

                return {
                    "provider": "virustotal",
                    "status": mapped_status,
                    "analysis_id": analysis_id,
                    "stats": stats,
                }
        except Exception as exc:  # noqa: BLE001
            logger.warning("VirusTotal scan failed: %s", exc)
            return {
                "provider": "virustotal",
                "status": "error",
                "reason": str(exc),
            }

    async def scan_skill(self, filename: str, raw_content: str) -> ScanResult:
        content_bytes = raw_content.encode("utf-8", errors="ignore")
        sha256 = hashlib.sha256(content_bytes).hexdigest()

        local_report = self._local_scan(raw_content)
        vt_report = await self._virustotal_scan(filename=filename, content_bytes=content_bytes)

        final_status = local_report["status"]
        confidence = int(local_report["score"])

        vt_status = vt_report.get("status")
        if vt_status in {SkillScanStatus.MALICIOUS, SkillScanStatus.SUSPICIOUS, SkillScanStatus.BENIGN}:
            if vt_status == SkillScanStatus.MALICIOUS:
                final_status = SkillScanStatus.MALICIOUS
                confidence = max(confidence, 95)
            elif vt_status == SkillScanStatus.SUSPICIOUS and final_status != SkillScanStatus.MALICIOUS:
                final_status = SkillScanStatus.SUSPICIOUS
                confidence = max(confidence, 70)
            elif vt_status == SkillScanStatus.BENIGN and final_status == SkillScanStatus.BENIGN:
                confidence = max(confidence, 85)

        if final_status == SkillScanStatus.MALICIOUS:
            summary = "Potentially malicious instructions detected. Publishing is blocked."
        elif final_status == SkillScanStatus.SUSPICIOUS:
            summary = "Suspicious patterns found. Requires explicit admin review."
        else:
            summary = "No critical threats detected. Eligible for publishing."

        report = {
            "sha256": sha256,
            "final_status": final_status,
            "local": local_report,
            "virustotal": vt_report,
        }

        return ScanResult(
            status=final_status,
            confidence=confidence,
            summary=summary,
            report=report,
        )


skill_security_scanner = SkillSecurityScanner()
