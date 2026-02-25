package runner

import "time"

type TaskContext struct {
	TaskID     string `json:"task_id"`
	TenantID   string `json:"tenant_id"`
	OperatorID string `json:"operator_id"`
	Source     string `json:"source"`
	Action     string `json:"action"`
}

type ExecutionManifest struct {
	TaskContext     TaskContext    `json:"task_context"`
	TargetURN       string         `json:"target_urn"`
	ToolSHA256      string         `json:"tool_sha256"`
	Nonce           string         `json:"nonce"`
	Parameters      map[string]any `json:"parameters"`
	IssuedAt        string         `json:"issued_at"`
	ManifestVersion string         `json:"manifest_version"`
}

type ArmoryTool struct {
	ToolName             string            `json:"tool_name"`
	ImageRef             string            `json:"image_ref"`
	ToolSHA256           string            `json:"tool_sha256"`
	SBOMFormat           string            `json:"sbom_format"`
	SBOMDigest           string            `json:"sbom_digest"`
	VulnerabilitySummary map[string]int    `json:"vulnerability_summary"`
	SignatureBundle      map[string]string `json:"signature_bundle"`
	Authorized           bool              `json:"authorized"`
}

type CloudEvent struct {
	ID          string         `json:"id"`
	SpecVersion string         `json:"specversion"`
	Source      string         `json:"source"`
	Type        string         `json:"type"`
	Subject     string         `json:"subject"`
	Time        string         `json:"time"`
	Data        map[string]any `json:"data"`
}

type CommandResult struct {
	ExitCode int
	Stdout   string
	Stderr   string
}

func nowISO8601() string {
	return time.Now().UTC().Format(time.RFC3339)
}
