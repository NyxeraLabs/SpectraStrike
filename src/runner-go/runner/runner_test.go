// Copyright (c) 2026 NyxeraLabs
// Author: Jose Maria Micoli
// Licensed under BSL 1.1
// Change Date: 2033-02-22 -> Apache-2.0
//
// You may:
// Study
// Modify
// Use for internal security testing
//
// You may NOT:
// Offer as a commercial service
// Sell derived competing products

package runner

import (
	"crypto/ed25519"
	"crypto/rand"
	"crypto/x509"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"testing"
)

func b64(v []byte) string {
	return base64.RawURLEncoding.EncodeToString(v)
}

func eddsaToken(payload map[string]any, privateKey ed25519.PrivateKey) string {
	header := map[string]any{"alg": "EdDSA", "typ": "JWT"}
	hRaw, _ := json.Marshal(header)
	pRaw, _ := json.Marshal(payload)
	hSeg := b64(hRaw)
	pSeg := b64(pRaw)
	signing := hSeg + "." + pSeg
	sigRaw := ed25519.Sign(privateKey, []byte(signing))
	sig := b64(sigRaw)
	return signing + "." + sig
}

func TestVerifyEdDSAJWSSuccess(t *testing.T) {
	publicKey, privateKey, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		t.Fatalf("failed to generate keypair: %v", err)
	}
	pubRaw, err := x509.MarshalPKIXPublicKey(publicKey)
	if err != nil {
		t.Fatalf("failed to marshal pubkey: %v", err)
	}
	pubPEM := pem.EncodeToMemory(&pem.Block{Type: "PUBLIC KEY", Bytes: pubRaw})
	token := eddsaToken(map[string]any{"task_id": "task-1"}, privateKey)
	payload, err := VerifyEdDSAJWS(token, string(pubPEM))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if payload["task_id"] != "task-1" {
		t.Fatalf("unexpected payload: %#v", payload)
	}
}

func TestVerifyEdDSAJWSForgedFails(t *testing.T) {
	publicKey, privateKey, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		t.Fatalf("failed to generate keypair: %v", err)
	}
	pubRaw, err := x509.MarshalPKIXPublicKey(publicKey)
	if err != nil {
		t.Fatalf("failed to marshal pubkey: %v", err)
	}
	pubPEM := pem.EncodeToMemory(&pem.Block{Type: "PUBLIC KEY", Bytes: pubRaw})
	token := eddsaToken(map[string]any{"task_id": "task-1"}, privateKey)
	forged := token[:len(token)-1] + "A"
	if _, err := VerifyEdDSAJWS(forged, string(pubPEM)); err == nil {
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

func TestBuildSandboxCommandUsesFirecrackerSimulation(t *testing.T) {
	tool := ArmoryTool{ToolSHA256: "sha256:abcdef0123456789abcdef", ImageRef: "ignored"}
	manifest := ExecutionManifest{
		TaskContext: TaskContext{TaskID: "task-1"},
		TargetURN:   "urn:target:ip:10.0.0.5",
	}
	command := BuildSandboxCommand(tool, manifest)
	if command[0] != "echo" {
		t.Fatalf("expected firecracker simulation command, got: %#v", command)
	}
	if len(command) < 2 || command[1] == "" {
		t.Fatalf("expected simulation payload in command")
	}
}
