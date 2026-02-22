"""Sprint 9 QA tests for Metasploit exploit execution and telemetry delivery."""

from __future__ import annotations

from typing import Any

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.metasploit import ExploitRequest, MetasploitConfig, MetasploitWrapper


class QAStubTransport:
    """Deterministic transport for QA exploit/session scenarios."""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, list[Any], MetasploitConfig]] = []

    def __call__(self, method: str, params: list[Any], config: MetasploitConfig) -> dict[str, Any]:
        self.calls.append((method, params, config))
        if not self._responses:
            raise AssertionError("no queued QA transport response")
        return self._responses.pop(0)


def test_qa_validate_exploit_runs_metasploit() -> None:
    transport = QAStubTransport(
        [
            {"result": "success", "token": "qa-token"},
            {"name": "unix/ftp/vsftpd_234_backdoor", "rank": "excellent"},
            {"job_id": 88, "uuid": "msf-uuid-88"},
            {"11": {"type": "shell"}},
            {"data": "id\nuid=0(root) gid=0(root) groups=0(root)"},
        ]
    )
    wrapper = MetasploitWrapper(transport=transport)

    result = wrapper.execute_exploit(
        ExploitRequest(
            module_type="exploit",
            module_name="unix/ftp/vsftpd_234_backdoor",
            target_host="10.10.50.15",
            target_port=21,
            payload="cmd/unix/interact",
            options={"SSL": False},
        )
    )

    assert result.status == "success"
    assert result.job_id == "88"
    assert result.uuid == "msf-uuid-88"
    assert len(result.sessions) == 1
    assert result.sessions[0].session_type == "shell"
    assert "uid=0(root)" in result.sessions[0].output

    methods = [call[0] for call in transport.calls]
    assert methods == [
        "auth.login",
        "module.info",
        "module.execute",
        "session.list",
        "session.shell_read",
    ]


def test_qa_check_telemetry_delivery_metasploit() -> None:
    transport = QAStubTransport(
        [
            {"result": "success", "token": "qa-token"},
            {"name": "multi/handler", "rank": "good"},
            {"job_id": 9, "uuid": "qa-9"},
            {"4": {"type": "meterpreter"}},
            {"data": "meterpreter > sysinfo"},
        ]
    )
    wrapper = MetasploitWrapper(transport=transport)
    telemetry = TelemetryIngestionPipeline(batch_size=1)

    result = wrapper.execute_exploit(
        ExploitRequest(
            module_type="exploit",
            module_name="multi/handler",
            target_host="10.10.50.99",
            payload="windows/meterpreter/reverse_tcp",
        )
    )
    event = wrapper.send_to_orchestrator(result=result, telemetry=telemetry, actor="qa-bot")
    flushed = telemetry.flush_ready()

    assert event.event_type == "metasploit_exploit_completed"
    assert event.actor == "qa-bot"
    assert event.attributes["target_host"] == "10.10.50.99"
    assert event.attributes["session_count"] == 1
    assert len(flushed) == 1
    assert flushed[0].event_type == "metasploit_exploit_completed"
    assert flushed[0].attributes["module_name"] == "multi/handler"
