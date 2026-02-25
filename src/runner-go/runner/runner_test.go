package runner

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"testing"
)

func b64(v []byte) string {
	return base64.RawURLEncoding.EncodeToString(v)
}

func hs256Token(payload map[string]any, secret string) string {
	header := map[string]any{"alg": "HS256", "typ": "JWT"}
	hRaw, _ := json.Marshal(header)
	pRaw, _ := json.Marshal(payload)
	hSeg := b64(hRaw)
	pSeg := b64(pRaw)
	signing := hSeg + "." + pSeg
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(signing))
	sig := b64(mac.Sum(nil))
	return signing + "." + sig
}

func TestVerifyHS256JWSSuccess(t *testing.T) {
	token := hs256Token(map[string]any{"task_id": "task-1"}, "secret")
	payload, err := VerifyHS256JWS(token, "secret")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if payload["task_id"] != "task-1" {
		t.Fatalf("unexpected payload: %#v", payload)
	}
}

func TestVerifyHS256JWSForgedFails(t *testing.T) {
	token := hs256Token(map[string]any{"task_id": "task-1"}, "secret")
	forged := token[:len(token)-1] + "A"
	if _, err := VerifyHS256JWS(forged, "secret"); err == nil {
		t.Fatalf("expected forged signature to fail")
	}
}

func TestResolveAuthorizedDigest(t *testing.T) {
	tools := []ArmoryTool{
		{ToolSHA256: "sha256:abc", Authorized: false},
		{ToolSHA256: "sha256:def", Authorized: true},
	}
	tool, err := ResolveAuthorizedToolDigest(tools, "sha256:def")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if tool.ToolSHA256 != "sha256:def" {
		t.Fatalf("unexpected tool: %#v", tool)
	}
}

func TestMapToCloudEventIncludesStdoutStderr(t *testing.T) {
	manifest := ExecutionManifest{
		TaskContext: TaskContext{TaskID: "task-1", TenantID: "tenant-a"},
		ToolSHA256:  "sha256:def",
		TargetURN:   "urn:target:ip:10.0.0.5",
	}
	result := CommandResult{ExitCode: 2, Stdout: "ok", Stderr: "err"}
	evt := MapToCloudEvent(manifest, result, "a.b.c")
	if evt.SpecVersion != "1.0" {
		t.Fatalf("unexpected specversion: %s", evt.SpecVersion)
	}
	if evt.Data["stdout"] != "ok" || evt.Data["stderr"] != "err" {
		t.Fatalf("unexpected data: %#v", evt.Data)
	}
	if evt.Data["status"] != "failed" {
		t.Fatalf("unexpected status: %#v", evt.Data["status"])
	}
}
