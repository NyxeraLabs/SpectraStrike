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
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
)

var (
	ErrInvalidJWSFormat    = errors.New("invalid compact jws format")
	ErrUnsupportedJWSAlg   = errors.New("unsupported jws algorithm")
	ErrMissingHMACSecret   = errors.New("missing hmac secret for HS256")
	ErrSignatureValidation = errors.New("jws signature validation failed")
)

func parseSegment(seg string) ([]byte, error) {
	return base64.RawURLEncoding.DecodeString(seg)
}

func VerifyHS256JWS(compact, hmacSecret string) (map[string]any, error) {
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
	if alg != "HS256" {
		return nil, ErrUnsupportedJWSAlg
	}
	if hmacSecret == "" {
		return nil, ErrMissingHMACSecret
	}

	signingInput := []byte(parts[0] + "." + parts[1])
	mac := hmac.New(sha256.New, []byte(hmacSecret))
	mac.Write(signingInput)
	expected := mac.Sum(nil)
	if !hmac.Equal(expected, signatureRaw) {
		return nil, ErrSignatureValidation
	}

	var payload map[string]any
	if err := json.Unmarshal(payloadRaw, &payload); err != nil {
		return nil, fmt.Errorf("parse payload: %w", err)
	}
	return payload, nil
}
