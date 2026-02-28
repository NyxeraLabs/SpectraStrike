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
	"crypto/x509"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	"strings"
)

var (
	ErrInvalidJWSFormat    = errors.New("invalid compact jws format")
	ErrUnsupportedJWSAlg   = errors.New("unsupported jws algorithm")
	ErrMissingVerifyKey    = errors.New("missing Ed25519 verify key")
	ErrInvalidVerifyKey    = errors.New("invalid Ed25519 verify key")
	ErrSignatureValidation = errors.New("jws signature validation failed")
)

func parseSegment(seg string) ([]byte, error) {
	return base64.RawURLEncoding.DecodeString(seg)
}

func VerifyEdDSAJWS(compact, publicKeyPEM string) (map[string]any, error) {
	parts := strings.Split(compact, ".")
	if len(parts) != 3 {
		return nil, ErrInvalidJWSFormat
	}
	headerRaw, err := parseSegment(parts[0])
	if err != nil {
		return nil, fmt.Errorf("decode header: %w", err)
	}
	payloadRaw, err := parseSegment(parts[1])
	if err != nil {
		return nil, fmt.Errorf("decode payload: %w", err)
	}
	signatureRaw, err := parseSegment(parts[2])
	if err != nil {
		return nil, fmt.Errorf("decode signature: %w", err)
	}

	var header map[string]any
	if err := json.Unmarshal(headerRaw, &header); err != nil {
		return nil, fmt.Errorf("parse header: %w", err)
	}
	alg, _ := header["alg"].(string)
	if alg != "EdDSA" {
		return nil, ErrUnsupportedJWSAlg
	}
	if publicKeyPEM == "" {
		return nil, ErrMissingVerifyKey
	}

	signingInput := []byte(parts[0] + "." + parts[1])
	block, _ := pem.Decode([]byte(publicKeyPEM))
	if block == nil {
		return nil, ErrInvalidVerifyKey
	}
	parsed, err := x509.ParsePKIXPublicKey(block.Bytes)
	if err != nil {
		return nil, ErrInvalidVerifyKey
	}
	publicKey, ok := parsed.(ed25519.PublicKey)
	if !ok {
		return nil, ErrInvalidVerifyKey
	}
	if !ed25519.Verify(publicKey, signingInput, signatureRaw) {
		return nil, ErrSignatureValidation
	}

	var payload map[string]any
	if err := json.Unmarshal(payloadRaw, &payload); err != nil {
		return nil, fmt.Errorf("parse payload: %w", err)
	}
	return payload, nil
}
