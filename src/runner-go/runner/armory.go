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
	"encoding/json"
	"errors"
	"fmt"
	"os"
)

var ErrAuthorizedDigestNotFound = errors.New("authorized digest not found")

func LoadArmoryRegistry(path string) ([]ArmoryTool, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read registry: %w", err)
	}
	var tools []ArmoryTool
	if err := json.Unmarshal(content, &tools); err != nil {
		return nil, fmt.Errorf("parse registry: %w", err)
	}
	return tools, nil
}

func ResolveAuthorizedToolDigest(tools []ArmoryTool, digest string) (ArmoryTool, error) {
	for _, tool := range tools {
		if tool.ToolSHA256 == digest && tool.Authorized {
			return tool, nil
		}
	}
	return ArmoryTool{}, ErrAuthorizedDigestNotFound
}
