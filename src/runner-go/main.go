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

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"spectrastrike/runner-go/runner"
)

func loadManifest(path string) (runner.ExecutionManifest, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return runner.ExecutionManifest{}, err
	}
	var manifest runner.ExecutionManifest
	if err := json.Unmarshal(content, &manifest); err != nil {
		return runner.ExecutionManifest{}, err
	}
	return manifest, nil
}

func main() {
	manifestPath := flag.String("manifest", "", "Path to ExecutionManifest JSON")
	manifestJWS := flag.String("manifest-jws", "", "Compact JWS for manifest")
	hmacSecret := flag.String("hmac-secret", "", "HMAC secret for HS256 verification")
	armoryRegistry := flag.String("armory-registry", ".spectrastrike/armory/registry.json", "Path to armory registry JSON")
	dryRun := flag.Bool("dry-run", true, "Do not execute docker command; emit synthetic output")
	flag.Parse()

	if *manifestPath == "" || *manifestJWS == "" {
		fmt.Fprintln(os.Stderr, "manifest and manifest-jws are required")
		os.Exit(2)
	}

	manifest, err := loadManifest(*manifestPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "load manifest: %v\n", err)
		os.Exit(2)
	}
	if _, err := runner.VerifyHS256JWS(*manifestJWS, *hmacSecret); err != nil {
		fmt.Fprintf(os.Stderr, "verify jws: %v\n", err)
		os.Exit(3)
	}

	tools, err := runner.LoadArmoryRegistry(*armoryRegistry)
	if err != nil {
		fmt.Fprintf(os.Stderr, "load armory registry: %v\n", err)
		os.Exit(4)
	}
	tool, err := runner.ResolveAuthorizedToolDigest(tools, manifest.ToolSHA256)
	if err != nil {
		fmt.Fprintf(os.Stderr, "resolve digest: %v\n", err)
		os.Exit(5)
	}

	command := runner.BuildSandboxCommand(tool, manifest)
	result := runner.CommandResult{ExitCode: 0, Stdout: "dry-run", Stderr: ""}
	if !*dryRun {
		result, err = runner.ExecuteCommand(command)
		if err != nil {
			fmt.Fprintf(os.Stderr, "execute command: %v\n", err)
			os.Exit(6)
		}
	}

	event := runner.MapToCloudEvent(manifest, result, *manifestJWS)
	serialized, err := json.Marshal(event)
	if err != nil {
		fmt.Fprintf(os.Stderr, "encode event: %v\n", err)
		os.Exit(7)
	}
	fmt.Println(string(serialized))
}
