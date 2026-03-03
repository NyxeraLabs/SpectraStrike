# Sprint 36: Nullable Fields by Model

- Generated at: `2026-03-03T14:33:31.399871+00:00`

## `action_risk_log`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `action_taken` | `TEXT` | `NULL` |
| `integrity_hash` | `TEXT` | `''` |

## `actions`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `asset_id` | `INTEGER` | `` |
| `mitre_technique` | `TEXT` | `` |
| `command` | `TEXT` | `` |
| `result` | `TEXT` | `` |
| `operator` | `TEXT` | `` |
| `timestamp` | `TEXT` | `` |
| `detection` | `TEXT` | `` |
| `integrity_hash` | `TEXT` | `''` |

## `activity_log`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `target_type` | `TEXT` | `` |
| `target_id` | `TEXT` | `` |
| `context_json` | `TEXT` | `` |
| `severity` | `TEXT` | `'info'` |

## `actor_ttps`
| Column | Type | Default |
|---|---|---|
| `frequency` | `TEXT` | `'common'` |
| `last_observed` | `TEXT` | `` |
| `confidence` | `REAL` | `0.5` |
| `evidence` | `TEXT` | `` |

## `anomaly_detections`
| Column | Type | Default |
|---|---|---|
| `severity` | `TEXT` | `'MEDIUM'` |
| `baseline_expectation` | `TEXT` | `` |
| `observed_behavior` | `TEXT` | `` |
| `likelihood_score` | `REAL` | `0.5` |
| `remediation_suggested` | `TEXT` | `` |

## `api_integrations`
| Column | Type | Default |
|---|---|---|
| `api_endpoint` | `TEXT` | `` |
| `api_key_hash` | `TEXT` | `` |
| `enabled` | `INTEGER` | `1` |
| `sync_frequency_minutes` | `INTEGER` | `60` |
| `last_sync` | `TEXT` | `NULL` |

## `assets`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `address` | `TEXT` | `` |
| `os` | `TEXT` | `` |
| `tags` | `TEXT` | `` |
| `first_seen` | `TEXT` | `` |
| `last_seen` | `TEXT` | `` |
| `integrity_hash` | `TEXT` | `''` |

## `audit_certification_reports`
| Column | Type | Default |
|---|---|---|
| `framework` | `TEXT` | `` |
| `total_requirements` | `INTEGER` | `0` |
| `satisfied_requirements` | `INTEGER` | `0` |
| `certification_status` | `TEXT` | `'incomplete'` |

## `audit_log`
| Column | Type | Default |
|---|---|---|
| `target_id` | `TEXT` | `''` |
| `old_value_hash` | `TEXT` | `''` |
| `new_value_hash` | `TEXT` | `''` |

## `audit_verification_chain`
| Column | Type | Default |
|---|---|---|
| `verification_method` | `TEXT` | `` |

## `behavioral_profiles`
| Column | Type | Default |
|---|---|---|
| `avg_execution_time` | `REAL` | `0.0` |
| `avg_detection_likelihood` | `REAL` | `0.5` |
| `success_rate` | `REAL` | `0.0` |
| `variance` | `REAL` | `0.1` |

## `c2_infrastructure`
| Column | Type | Default |
|---|---|---|
| `node_type` | `TEXT` | `'listener'` |
| `exposure_score` | `REAL` | `0.0` |
| `reputation_score` | `REAL` | `0.0` |
| `burn_probability` | `REAL` | `0.0` |
| `burn_level` | `TEXT` | `'fresh'` |
| `should_rotate` | `INTEGER` | `0` |
| `last_rotated` | `TEXT` | `` |
| `notes` | `TEXT` | `''` |

## `campaign_metrics`
| Column | Type | Default |
|---|---|---|
| `total_assets` | `INTEGER` | `0` |
| `compromised_assets` | `INTEGER` | `0` |
| `active_sessions` | `INTEGER` | `0` |
| `active_persistence` | `INTEGER` | `0` |
| `total_commands_executed` | `INTEGER` | `0` |
| `detection_risk_score` | `REAL` | `0.0` |
| `objectives_complete` | `REAL` | `0.0` |
| `evasion_success_pct` | `REAL` | `0.0` |

## `campaign_objectives`
| Column | Type | Default |
|---|---|---|
| `description` | `TEXT` | `` |
| `priority` | `INTEGER` | `1` |
| `created_by` | `INTEGER` | `` |

## `campaign_phase_history`
| Column | Type | Default |
|---|---|---|
| `integrity_hash` | `TEXT` | `''` |

## `campaign_reports`
| Column | Type | Default |
|---|---|---|
| `format` | `TEXT` | `'pdf'` |
| `file_path` | `TEXT` | `` |
| `file_hash` | `TEXT` | `` |
| `status` | `TEXT` | `'draft'` |
| `executive_summary` | `TEXT` | `` |
| `technical_summary` | `TEXT` | `` |
| `distribution_list` | `TEXT` | `` |
| `updated_at` | `TEXT` | `NULL` |

## `campaign_team_assignments`
| Column | Type | Default |
|---|---|---|
| `assigned_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |
| `access_level` | `TEXT` | `'read_write'` |

## `campaigns`
| Column | Type | Default |
|---|---|---|
| `created_by` | `INTEGER` | `` |
| `status` | `TEXT` | `'active'` |
| `integrity_hash` | `TEXT` | `''` |

## `capability_assessment`
| Column | Type | Default |
|---|---|---|
| `difficulty_score` | `REAL` | `5.0` |
| `success_rate` | `REAL` | `0.0` |
| `defender_maturity_required` | `TEXT` | `` |
| `alternative_techniques` | `TEXT` | `` |
| `effectiveness_trend` | `TEXT` | `'stable'` |

## `capability_timeline`
| Column | Type | Default |
|---|---|---|
| `detection_likelihood` | `REAL` | `0.5` |
| `remediation_difficulty` | `REAL` | `5.0` |
| `notes` | `TEXT` | `` |

## `client_reports`
| Column | Type | Default |
|---|---|---|
| `filter_rules` | `TEXT` | `` |
| `include_exec_summary` | `INTEGER` | `1` |
| `include_risk_dashboard` | `INTEGER` | `1` |
| `include_metrics` | `INTEGER` | `1` |
| `branding_logo_url` | `TEXT` | `` |
| `footer_text` | `TEXT` | `` |
| `status` | `TEXT` | `'draft'` |
| `file_path` | `TEXT` | `` |
| `file_hash` | `TEXT` | `` |

## `cognition_state_cache`
| Column | Type | Default |
|---|---|---|
| `detection_pressure` | `REAL` | `0.0` |
| `pressure_state` | `TEXT` | `'LOW'` |
| `infra_burn` | `TEXT` | `'fresh'` |
| `confidence_score` | `REAL` | `0.0` |
| `updated_by` | `INTEGER` | `` |

## `collaboration_sessions`
| Column | Type | Default |
|---|---|---|
| `created_by` | `INTEGER` | `` |
| `status` | `TEXT` | `'active'` |
| `max_operators` | `INTEGER` | `5` |
| `sync_version` | `INTEGER` | `0` |
| `last_sync` | `TEXT` | `NULL` |

## `collaborative_changes`
| Column | Type | Default |
|---|---|---|
| `operator_id` | `INTEGER` | `` |
| `entity_id` | `INTEGER` | `` |
| `operation` | `TEXT` | `` |
| `old_value_hash` | `TEXT` | `` |
| `new_value_hash` | `TEXT` | `` |
| `conflict_detected` | `INTEGER` | `0` |
| `resolved_by` | `TEXT` | `NULL` |

## `command_execution_ledger`
| Column | Type | Default |
|---|---|---|
| `session_id` | `INTEGER` | `NULL` |
| `asset_id` | `INTEGER` | `` |
| `shell_type` | `TEXT` | `` |
| `output` | `TEXT` | `NULL` |
| `mitre_technique` | `TEXT` | `` |
| `success` | `INTEGER` | `1` |
| `return_code` | `INTEGER` | `NULL` |
| `detection_likelihood` | `TEXT` | `'MEDIUM'` |
| `created_by` | `INTEGER` | `` |
| `integrity_hash` | `TEXT` | `''` |

## `compliance_attestations`
| Column | Type | Default |
|---|---|---|
| `total_requirements` | `INTEGER` | `0` |
| `satisfied_requirements` | `INTEGER` | `0` |
| `satisfaction_percent` | `REAL` | `0.0` |
| `attestation_text` | `TEXT` | `` |
| `digital_signature` | `TEXT` | `` |
| `signed_at` | `TEXT` | `` |

## `compliance_frameworks`
| Column | Type | Default |
|---|---|---|
| `description` | `TEXT` | `` |
| `requirements_count` | `INTEGER` | `0` |
| `enabled` | `INTEGER` | `1` |

## `compliance_mappings`
| Column | Type | Default |
|---|---|---|
| `requirement_description` | `TEXT` | `` |
| `evidence_provided` | `TEXT` | `` |
| `status` | `TEXT` | `'pending'` |
| `last_verified` | `TEXT` | `NULL` |

## `compliance_report_mappings`
| Column | Type | Default |
|---|---|---|
| `finding_id` | `INTEGER` | `` |
| `requirement_name` | `TEXT` | `` |
| `finding_evidence_link` | `TEXT` | `` |
| `compliance_status` | `TEXT` | `'pending'` |
| `mapped_by` | `TEXT` | `` |
| `verified` | `INTEGER` | `0` |

## `coordination_logs`
| Column | Type | Default |
|---|---|---|
| `message` | `TEXT` | `` |
| `status` | `TEXT` | `'pending'` |
| `created_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |
| `resolved_at` | `TIMESTAMP` | `` |

## `credential_state`
| Column | Type | Default |
|---|---|---|
| `status` | `TEXT` | `'untested'` |
| `last_verified` | `TEXT` | `NULL` |
| `last_host` | `TEXT` | `NULL` |
| `failure_count` | `INTEGER` | `0` |
| `success_count` | `INTEGER` | `0` |
| `detection_risk` | `REAL` | `0.0` |
| `burned_at` | `TEXT` | `NULL` |
| `integrity_hash` | `TEXT` | `''` |

## `credentials`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `asset_id` | `INTEGER` | `` |
| `source` | `TEXT` | `` |
| `captured_by` | `INTEGER` | `` |
| `captured_at` | `TEXT` | `` |
| `integrity_hash` | `TEXT` | `''` |

## `data_sharing_policies`
| Column | Type | Default |
|---|---|---|
| `access_level` | `TEXT` | `'read_only'` |
| `requires_approval` | `INTEGER` | `1` |
| `created_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |

## `defense_prediction`
| Column | Type | Default |
|---|---|---|
| `confidence_score` | `REAL` | `0.5` |
| `affected_techniques` | `TEXT` | `` |
| `mitigation_strategy` | `TEXT` | `` |

## `detection_events`
| Column | Type | Default |
|---|---|---|
| `asset_id` | `INTEGER` | `` |
| `source` | `TEXT` | `` |
| `confidence` | `REAL` | `0.5` |
| `blue_team_aware` | `INTEGER` | `0` |
| `response` | `TEXT` | `NULL` |
| `evasion_action` | `TEXT` | `NULL` |
| `mitigated` | `INTEGER` | `0` |
| `integrity_hash` | `TEXT` | `''` |

## `detection_pressure_history`
| Column | Type | Default |
|---|---|---|
| `total_pressure` | `REAL` | `0.0` |
| `pressure_state` | `TEXT` | `'LOW'` |
| `recent_alerts` | `INTEGER` | `0` |
| `repetition_penalty` | `REAL` | `0.0` |
| `failed_actions` | `INTEGER` | `0` |
| `pressure_trend` | `TEXT` | `'stable'` |

## `engagement_reports`
| Column | Type | Default |
|---|---|---|
| `total_duration_hours` | `REAL` | `0.0` |
| `total_assets_targeted` | `INTEGER` | `0` |
| `assets_compromised` | `INTEGER` | `0` |
| `credentials_obtained` | `INTEGER` | `0` |
| `persistence_mechanisms` | `INTEGER` | `0` |
| `total_detection_events` | `INTEGER` | `0` |
| `detection_evasion_success_rate` | `REAL` | `0.0` |
| `objectives_achieved` | `INTEGER` | `0` |
| `techniques_executed` | `INTEGER` | `` |
| `report_summary` | `TEXT` | `` |
| `recommendations` | `TEXT` | `` |

## `enrichment_data`
| Column | Type | Default |
|---|---|---|
| `source` | `TEXT` | `` |
| `confidence` | `REAL` | `0.5` |
| `expires_at` | `TEXT` | `` |

## `evasion_assessment`
| Column | Type | Default |
|---|---|---|
| `detection_event_id` | `INTEGER` | `` |
| `likely_detection_confidence` | `REAL` | `0.5` |
| `recommended_action` | `TEXT` | `` |
| `executed_evasion` | `TEXT` | `NULL` |
| `result` | `TEXT` | `NULL` |

## `evidence_items`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `finding_id` | `INTEGER` | `` |
| `description` | `TEXT` | `` |
| `collected_by` | `INTEGER` | `` |
| `collection_method` | `TEXT` | `` |
| `source_host` | `TEXT` | `` |
| `technique_id` | `TEXT` | `` |
| `approval_status` | `TEXT` | `'pending'` |
| `approved_by` | `INTEGER` | `` |
| `approval_timestamp` | `TEXT` | `''` |
| `immutable` | `INTEGER` | `1` |

## `evidence_manifest_entries`
| Column | Type | Default |
|---|---|---|
| `evidence_id` | `INTEGER` | `` |
| `collection_method` | `TEXT` | `` |
| `collected_by` | `TEXT` | `` |
| `size_bytes` | `INTEGER` | `0` |
| `chain_of_custody` | `TEXT` | `` |

## `evidence_manifests`
| Column | Type | Default |
|---|---|---|
| `evidence_count` | `INTEGER` | `0` |
| `total_size_bytes` | `INTEGER` | `0` |
| `verified` | `INTEGER` | `0` |
| `verified_at` | `TEXT` | `NULL` |

## `finding_summaries`
| Column | Type | Default |
|---|---|---|
| `impact_assessment` | `TEXT` | `` |
| `remediation_steps` | `TEXT` | `` |
| `priority_level` | `TEXT` | `'MEDIUM'` |
| `cvss_31_vector` | `TEXT` | `` |
| `cvss_31_score` | `REAL` | `0.0` |
| `severity_rating` | `TEXT` | `` |
| `affected_assets` | `TEXT` | `` |
| `evidence_links` | `TEXT` | `` |
| `updated_at` | `TEXT` | `NULL` |

## `findings`
| Column | Type | Default |
|---|---|---|
| `description` | `TEXT` | `` |
| `cvss_score` | `REAL` | `0.0` |
| `mitre_id` | `TEXT` | `''` |
| `tactic_id` | `TEXT` | `''` |
| `status` | `TEXT` | `'Open'` |
| `evidence` | `TEXT` | `''` |
| `remediation` | `TEXT` | `''` |
| `project_id` | `TEXT` | `'DEFAULT'` |
| `cvss_vector` | `TEXT` | `''` |
| `evidence_hash` | `TEXT` | `''` |
| `created_by` | `INTEGER` | `NULL` |
| `last_modified_by` | `INTEGER` | `NULL` |
| `assigned_to` | `INTEGER` | `NULL` |
| `visibility` | `TEXT` | `'group'` |
| `tags` | `TEXT` | `''` |
| `approval_status` | `TEXT` | `'pending'` |
| `approved_by` | `INTEGER` | `NULL` |
| `approval_timestamp` | `TEXT` | `''` |

## `groups`
| Column | Type | Default |
|---|---|---|
| `description` | `TEXT` | `''` |

## `immutable_audit_log`
| Column | Type | Default |
|---|---|---|
| `previous_hash` | `TEXT` | `` |
| `signature` | `TEXT` | `` |
| `verified` | `INTEGER` | `0` |

## `indicators_of_compromise`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `source_feed_id` | `INTEGER` | `` |
| `threat_level` | `TEXT` | `'MEDIUM'` |
| `threat_actor_id` | `INTEGER` | `` |
| `last_seen` | `TEXT` | `` |
| `matched_count` | `INTEGER` | `0` |
| `confidence` | `REAL` | `0.5` |
| `classification` | `TEXT` | `'UNKNOWN'` |

## `intel_indicators`
| Column | Type | Default |
|---|---|---|
| `feed_id` | `INTEGER` | `` |
| `threat_level` | `TEXT` | `'MEDIUM'` |
| `matched_at` | `TEXT` | `` |
| `correlation` | `TEXT` | `` |

## `intelligence_archive`
| Column | Type | Default |
|---|---|---|
| `actor_id` | `INTEGER` | `` |
| `campaign_id` | `INTEGER` | `` |
| `tags` | `TEXT` | `` |
| `classification` | `TEXT` | `'UNCLASSIFIED'` |
| `source` | `TEXT` | `` |
| `archived_by` | `INTEGER` | `` |

## `legal_acceptances`
| Column | Type | Default |
|---|---|---|
| `user_id` | `INTEGER` | `` |
| `ip_address` | `TEXT` | `''` |

## `loot`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `asset_id` | `INTEGER` | `` |
| `path` | `TEXT` | `` |
| `description` | `TEXT` | `` |
| `classification` | `TEXT` | `` |
| `hash` | `TEXT` | `` |
| `stored_at` | `TEXT` | `` |
| `integrity_hash` | `TEXT` | `''` |

## `meta`
| Column | Type | Default |
|---|---|---|
| `value` | `TEXT` | `` |

## `objective_progress`
| Column | Type | Default |
|---|---|---|
| `finding_id` | `TEXT` | `NULL` |
| `progress_pct` | `REAL` | `0.0` |
| `status` | `TEXT` | `'in_progress'` |
| `completed_at` | `TEXT` | `NULL` |
| `completed_by` | `TEXT` | `NULL` |
| `evidence` | `TEXT` | `` |
| `notes` | `TEXT` | `''` |

## `operation_phases`
| Column | Type | Default |
|---|---|---|
| `exited_at` | `TEXT` | `NULL` |
| `entered_by` | `INTEGER` | `` |
| `notes` | `TEXT` | `''` |

## `operator_performance`
| Column | Type | Default |
|---|---|---|
| `findings_created` | `INTEGER` | `0` |
| `findings_approved` | `INTEGER` | `0` |
| `approval_rate` | `REAL` | `0.0` |
| `average_cvss_score` | `REAL` | `0.0` |
| `total_operations` | `INTEGER` | `0` |
| `success_rate` | `REAL` | `0.0` |
| `effectiveness_score` | `REAL` | `0.0` |
| `calculated_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |

## `operator_presence`
| Column | Type | Default |
|---|---|---|
| `cursor_position` | `TEXT` | `` |
| `viewing_asset` | `INTEGER` | `NULL` |

## `operator_tempo_metrics`
| Column | Type | Default |
|---|---|---|
| `operator_id` | `INTEGER` | `` |
| `actions_per_hour` | `REAL` | `0.0` |
| `action_intensity` | `TEXT` | `'normal'` |
| `spike_detected` | `INTEGER` | `0` |
| `suggested_slow_window` | `TEXT` | `''` |
| `staging_recommendation` | `TEXT` | `''` |

## `opsec_rules`
| Column | Type | Default |
|---|---|---|
| `created_by` | `INTEGER` | `` |
| `active` | `INTEGER` | `1` |

## `persistence_registry`
| Column | Type | Default |
|---|---|---|
| `asset_id` | `INTEGER` | `` |
| `status` | `TEXT` | `'active'` |
| `last_verified` | `TEXT` | `NULL` |
| `verification_result` | `TEXT` | `NULL` |
| `cleanup_required` | `INTEGER` | `0` |
| `redundancy_group` | `TEXT` | `` |
| `backup_persistence_id` | `INTEGER` | `NULL` |
| `integrity_hash` | `TEXT` | `''` |

## `persistence_verification_log`
| Column | Type | Default |
|---|---|---|
| `evidence` | `TEXT` | `` |
| `remediation_needed` | `INTEGER` | `0` |

## `projects`
| Column | Type | Default |
|---|---|---|
| `description` | `TEXT` | `''` |
| `group_id` | `INTEGER` | `` |
| `archived` | `INTEGER` | `0` |

## `purge_operations`
| Column | Type | Default |
|---|---|---|
| `policy_id` | `INTEGER` | `` |
| `records_deleted` | `INTEGER` | `0` |
| `records_archived` | `INTEGER` | `0` |
| `completion_status` | `TEXT` | `'pending'` |

## `re_authentication_log`
| Column | Type | Default |
|---|---|---|
| `reason` | `TEXT` | `` |
| `success` | `INTEGER` | `1` |
| `method` | `TEXT` | `'PASSPHRASE'` |

## `real_time_alerts`
| Column | Type | Default |
|---|---|---|
| `severity` | `TEXT` | `'INFO'` |
| `related_asset` | `INTEGER` | `` |
| `acknowledged` | `INTEGER` | `0` |
| `acknowledged_by` | `TEXT` | `NULL` |

## `recommendation_history`
| Column | Type | Default |
|---|---|---|
| `technique` | `TEXT` | `''` |
| `target_asset` | `TEXT` | `''` |
| `score` | `REAL` | `0.0` |
| `stealth` | `REAL` | `0.0` |
| `value` | `REAL` | `0.0` |
| `risk` | `REAL` | `0.0` |
| `confidence` | `REAL` | `0.0` |
| `explanation` | `TEXT` | `''` |
| `safer_alternative` | `TEXT` | `''` |
| `created_by` | `INTEGER` | `` |

## `relations`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `src_type` | `TEXT` | `` |
| `src_id` | `INTEGER` | `` |
| `rel_type` | `TEXT` | `` |
| `dst_type` | `TEXT` | `` |
| `dst_id` | `INTEGER` | `` |
| `integrity_hash` | `TEXT` | `''` |
| `confidence` | `REAL` | `1.0` |
| `evidence_id` | `INTEGER` | `NULL` |

## `relationships`
| Column | Type | Default |
|---|---|---|
| `confidence` | `REAL` | `1.0` |
| `evidence_id` | `TEXT` | `NULL` |
| `created_by` | `INTEGER` | `` |
| `integrity_hash` | `TEXT` | `''` |

## `remediation_actions`
| Column | Type | Default |
|---|---|---|
| `asset_id` | `INTEGER` | `` |
| `status` | `TEXT` | `'in_progress'` |
| `effectiveness` | `REAL` | `0.0` |
| `blocked_techniques` | `TEXT` | `` |
| `evidence` | `TEXT` | `` |

## `remediation_impact`
| Column | Type | Default |
|---|---|---|
| `affected_persistence_mechanisms` | `INTEGER` | `0` |
| `affected_sessions` | `INTEGER` | `0` |
| `affected_access_paths` | `INTEGER` | `0` |
| `impact_score` | `REAL` | `0.0` |

## `replay_events`
| Column | Type | Default |
|---|---|---|
| `operator` | `TEXT` | `'SYSTEM'` |
| `asset_id` | `INTEGER` | `` |
| `technique` | `TEXT` | `''` |
| `success` | `INTEGER` | `1` |
| `summary` | `TEXT` | `''` |
| `details_json` | `TEXT` | `''` |

## `report_history`
| Column | Type | Default |
|---|---|---|
| `file_path` | `TEXT` | `` |
| `file_size` | `INTEGER` | `0` |
| `generation_status` | `TEXT` | `'success'` |
| `error_message` | `TEXT` | `NULL` |
| `recipients` | `TEXT` | `` |

## `report_schedules`
| Column | Type | Default |
|---|---|---|
| `last_generated` | `TEXT` | `NULL` |
| `email_recipients` | `TEXT` | `` |
| `enabled` | `INTEGER` | `1` |

## `report_templates`
| Column | Type | Default |
|---|---|---|
| `format` | `TEXT` | `'jinja2'` |
| `description` | `TEXT` | `` |

## `report_versions`
| Column | Type | Default |
|---|---|---|
| `version_number` | `INTEGER` | `1` |
| `changes` | `TEXT` | `` |
| `approved_by` | `TEXT` | `` |
| `approved_at` | `TEXT` | `` |
| `distribution_count` | `INTEGER` | `0` |

## `retention_policies`
| Column | Type | Default |
|---|---|---|
| `retention_days` | `INTEGER` | `90` |
| `action_on_expiry` | `TEXT` | `'archive'` |
| `enabled` | `INTEGER` | `1` |

## `risk_scores`
| Column | Type | Default |
|---|---|---|
| `finding_id` | `INTEGER` | `` |
| `risk_level` | `TEXT` | `'MEDIUM'` |
| `threat_score` | `REAL` | `5.0` |
| `likelihood_score` | `REAL` | `5.0` |
| `impact_score` | `REAL` | `5.0` |
| `final_score` | `REAL` | `5.0` |
| `trend` | `TEXT` | `'stable'` |

## `scheduled_tasks`
| Column | Type | Default |
|---|---|---|
| `task_template_id` | `INTEGER` | `` |
| `trigger_condition` | `TEXT` | `` |
| `priority` | `INTEGER` | `1` |
| `max_retries` | `INTEGER` | `3` |
| `status` | `TEXT` | `'pending'` |
| `created_by` | `INTEGER` | `` |

## `secure_deletion_log`
| Column | Type | Default |
|---|---|---|
| `record_count` | `INTEGER` | `` |
| `deletion_method` | `TEXT` | `'multi-pass-overwrite'` |
| `verification_hash` | `TEXT` | `` |
| `verified` | `INTEGER` | `0` |

## `sensitive_field_audit`
| Column | Type | Default |
|---|---|---|
| `accessed_by` | `INTEGER` | `` |
| `tlp_level` | `TEXT` | `` |
| `ip_address` | `TEXT` | `` |
| `session_id` | `TEXT` | `` |

## `session_lifecycle`
| Column | Type | Default |
|---|---|---|
| `asset_id` | `INTEGER` | `` |
| `closed_at` | `TEXT` | `NULL` |
| `detected_at` | `TEXT` | `NULL` |
| `is_active` | `INTEGER` | `1` |
| `activation_count` | `INTEGER` | `1` |
| `revived_at` | `TEXT` | `NULL` |
| `persistence_mechanism` | `TEXT` | `` |
| `backup_session_id` | `INTEGER` | `NULL` |
| `integrity_hash` | `TEXT` | `''` |

## `session_management`
| Column | Type | Default |
|---|---|---|
| `timeout_minutes` | `INTEGER` | `120` |
| `ip_address` | `TEXT` | `` |
| `user_agent` | `TEXT` | `` |
| `is_active` | `INTEGER` | `1` |
| `closed_at` | `TEXT` | `NULL` |

## `sessions`
- None

## `sessions_ops`
| Column | Type | Default |
|---|---|---|
| `campaign_id` | `INTEGER` | `` |
| `asset_id` | `INTEGER` | `` |
| `session_type` | `TEXT` | `` |
| `user` | `TEXT` | `` |
| `pid` | `INTEGER` | `` |
| `tunnel` | `TEXT` | `` |
| `status` | `TEXT` | `` |
| `opened_at` | `TEXT` | `` |
| `closed_at` | `TEXT` | `` |
| `integrity_hash` | `TEXT` | `''` |

## `target_lock_diffs`
| Column | Type | Default |
|---|---|---|
| `lock_id` | `INTEGER` | `` |
| `reviewed_by` | `INTEGER` | `` |
| `reviewed_at` | `TEXT` | `NULL` |
| `approved` | `INTEGER` | `0` |

## `target_locks`
| Column | Type | Default |
|---|---|---|
| `context_json` | `TEXT` | `''` |

## `task_execution_log`
| Column | Type | Default |
|---|---|---|
| `execution_end` | `TEXT` | `` |
| `result` | `TEXT` | `` |
| `error_message` | `TEXT` | `NULL` |
| `output_log` | `TEXT` | `` |

## `task_templates`
| Column | Type | Default |
|---|---|---|
| `description` | `TEXT` | `` |
| `created_by` | `INTEGER` | `` |
| `enabled` | `INTEGER` | `1` |

## `team_intelligence_pools`
| Column | Type | Default |
|---|---|---|
| `description` | `TEXT` | `` |
| `intelligence_items` | `TEXT` | `` |
| `is_shared` | `INTEGER` | `0` |
| `created_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |

## `team_members`
| Column | Type | Default |
|---|---|---|
| `team_role` | `TEXT` | `'member'` |
| `joined_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |

## `team_metrics`
| Column | Type | Default |
|---|---|---|
| `total_findings` | `INTEGER` | `0` |
| `critical_findings` | `INTEGER` | `0` |
| `approved_findings` | `INTEGER` | `0` |
| `average_approval_time_hours` | `REAL` | `0.0` |
| `total_campaigns` | `INTEGER` | `0` |
| `active_campaigns` | `INTEGER` | `0` |
| `calculated_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |

## `team_permissions`
| Column | Type | Default |
|---|---|---|
| `resource_type` | `TEXT` | `` |
| `granted_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |

## `team_roles`
| Column | Type | Default |
|---|---|---|
| `permissions` | `TEXT` | `` |
| `created_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |

## `teams`
| Column | Type | Default |
|---|---|---|
| `description` | `TEXT` | `` |
| `budget_usd` | `REAL` | `0.0` |
| `status` | `TEXT` | `'active'` |
| `created_at` | `TIMESTAMP` | `CURRENT_TIMESTAMP` |

## `technique_patterns`
| Column | Type | Default |
|---|---|---|
| `asset_type` | `TEXT` | `'unknown'` |
| `executions` | `INTEGER` | `0` |
| `successes` | `INTEGER` | `0` |
| `failures` | `INTEGER` | `0` |
| `avg_time_to_compromise` | `REAL` | `0.0` |
| `confidence` | `REAL` | `0.5` |

## `threat_actors`
| Column | Type | Default |
|---|---|---|
| `aliases` | `TEXT` | `` |
| `origin_country` | `TEXT` | `` |
| `organization` | `TEXT` | `` |
| `known_targets` | `TEXT` | `` |
| `first_seen` | `TEXT` | `` |
| `last_seen` | `TEXT` | `` |
| `attribution_confidence` | `REAL` | `0.5` |
| `description` | `TEXT` | `` |
| `created_by` | `INTEGER` | `` |

## `threat_correlations`
| Column | Type | Default |
|---|---|---|
| `source_id` | `INTEGER` | `` |
| `target_id` | `INTEGER` | `` |
| `confidence` | `REAL` | `0.5` |
| `evidence` | `TEXT` | `` |
| `correlated_by` | `INTEGER` | `` |

## `threat_feeds`
| Column | Type | Default |
|---|---|---|
| `feed_url` | `TEXT` | `` |
| `api_key_hash` | `TEXT` | `` |
| `last_updated` | `TEXT` | `` |
| `last_error` | `TEXT` | `` |
| `status` | `TEXT` | `'active'` |
| `description` | `TEXT` | `` |
| `created_by` | `INTEGER` | `` |
| `feed_icon` | `TEXT` | `'🔗'` |

## `threat_intelligence_feeds`
| Column | Type | Default |
|---|---|---|
| `feed_url` | `TEXT` | `` |
| `last_updated` | `TEXT` | `` |
| `status` | `TEXT` | `'active'` |
| `description` | `TEXT` | `` |

## `tlp_classifications`
| Column | Type | Default |
|---|---|---|
| `encrypted` | `INTEGER` | `1` |
| `encryption_algorithm` | `TEXT` | `'AES-256-GCM'` |
| `iv_hash` | `TEXT` | `` |
| `created_by` | `INTEGER` | `` |

## `ttp_execution_metrics`
| Column | Type | Default |
|---|---|---|
| `times_executed` | `INTEGER` | `1` |
| `success_rate` | `REAL` | `1.0` |
| `avg_detection_likelihood` | `REAL` | `0.5` |
| `effectiveness_score` | `REAL` | `0.0` |
| `last_executed` | `TEXT` | `` |

## `user_capabilities`
- None

## `users`
| Column | Type | Default |
|---|---|---|
| `group_id` | `INTEGER` | `` |
| `last_login` | `TEXT` | `''` |

## `webhook_delivery_log`
| Column | Type | Default |
|---|---|---|
| `payload_hash` | `TEXT` | `` |
| `http_status` | `INTEGER` | `` |
| `retry_count` | `INTEGER` | `0` |
| `delivered` | `INTEGER` | `0` |

## `webhook_subscriptions`
| Column | Type | Default |
|---|---|---|
| `secret_key` | `TEXT` | `` |
| `active` | `INTEGER` | `1` |
| `last_triggered` | `TEXT` | `NULL` |

