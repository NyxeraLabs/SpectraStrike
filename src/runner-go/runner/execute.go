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
	"bytes"
	"fmt"
	"os/exec"
	"regexp"
)

func vmID(taskID string) string {
	normalized := regexp.MustCompile(`[^a-zA-Z0-9-]`).ReplaceAllString(taskID, "-")
	if normalized == "" {
		return "task"
	}
	if len(normalized) > 63 {
		return normalized[:63]
	}
	return normalized
}

func BuildSandboxCommand(tool ArmoryTool, manifest ExecutionManifest) []string {
	toolPrefix := tool.ToolSHA256
	if len(toolPrefix) > 16 {
		toolPrefix = toolPrefix[:16]
	}
	// Firecracker microVM simulation is the standard local launch contract.
	return []string{
		"echo",
		fmt.Sprintf("firecracker_simulated:%s:%s", vmID(manifest.TaskContext.TaskID), toolPrefix),
	}
}

func ExecuteCommand(command []string) (CommandResult, error) {
	if len(command) == 0 {
		return CommandResult{}, fmt.Errorf("empty command")
	}
	cmd := exec.Command(command[0], command[1:]...)
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	cmd.Stdout = stdout
	cmd.Stderr = stderr
	err := cmd.Run()
	result := CommandResult{Stdout: stdout.String(), Stderr: stderr.String()}
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			result.ExitCode = exitErr.ExitCode()
			return result, nil
		}
		return CommandResult{}, err
	}
	result.ExitCode = 0
	return result, nil
}
