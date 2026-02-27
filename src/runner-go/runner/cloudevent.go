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
	"crypto/rand"
	"encoding/hex"
)

func randID() string {
	buf := make([]byte, 16)
	if _, err := rand.Read(buf); err != nil {
		return "runner-event-fallback"
	}
	return hex.EncodeToString(buf)
}

func MapToCloudEvent(manifest ExecutionManifest, result CommandResult, manifestJWS string) CloudEvent {
	status := "success"
	if result.ExitCode != 0 {
		status = "failed"
	}
	return CloudEvent{
		ID:          randID(),
		SpecVersion: "1.0",
		Source:      "urn:spectrastrike:runner:go",
		Type:        "com.nyxeralabs.spectrastrike.runner.execution.v1",
		Subject:     manifest.TaskContext.TaskID,
		Time:        nowISO8601(),
		Data: map[string]any{
			"task_id":      manifest.TaskContext.TaskID,
			"tenant_id":    manifest.TaskContext.TenantID,
			"tool_sha256":  manifest.ToolSHA256,
			"target_urn":   manifest.TargetURN,
			"status":       status,
			"exit_code":    result.ExitCode,
			"stdout":       result.Stdout,
			"stderr":       result.Stderr,
			"manifest_jws": manifestJWS,
		},
	}
}
