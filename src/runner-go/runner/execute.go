package runner

import (
	"bytes"
	"fmt"
	"os/exec"
)

func BuildSandboxCommand(tool ArmoryTool, manifest ExecutionManifest) []string {
	return []string{
		"docker",
		"run",
		"--rm",
		"--read-only",
		"--cap-drop=ALL",
		"--runtime=runsc",
		"--security-opt=apparmor=spectrastrike-default",
		"--network=none",
		"-e", "SPECTRA_TASK_ID=" + manifest.TaskContext.TaskID,
		"-e", "SPECTRA_TARGET_URN=" + manifest.TargetURN,
		tool.ImageRef,
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
