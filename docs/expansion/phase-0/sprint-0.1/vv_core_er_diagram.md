# Sprint 36: vv_core ER Diagram (Mermaid)

- Generated at: `2026-03-03T14:33:31.399871+00:00`

```mermaid
flowchart LR
    action_risk_log["action_risk_log"]
    actions["actions"]
    activity_log["activity_log"]
    actor_ttps["actor_ttps"]
    anomaly_detections["anomaly_detections"]
    api_integrations["api_integrations"]
    assets["assets"]
    audit_certification_reports["audit_certification_reports"]
    audit_log["audit_log"]
    audit_verification_chain["audit_verification_chain"]
    behavioral_profiles["behavioral_profiles"]
    c2_infrastructure["c2_infrastructure"]
    campaign_metrics["campaign_metrics"]
    campaign_objectives["campaign_objectives"]
    campaign_phase_history["campaign_phase_history"]
    campaign_reports["campaign_reports"]
    campaign_team_assignments["campaign_team_assignments"]
    campaigns["campaigns"]
    capability_assessment["capability_assessment"]
    capability_timeline["capability_timeline"]
    client_reports["client_reports"]
    cognition_state_cache["cognition_state_cache"]
    collaboration_sessions["collaboration_sessions"]
    collaborative_changes["collaborative_changes"]
    command_execution_ledger["command_execution_ledger"]
    compliance_attestations["compliance_attestations"]
    compliance_frameworks["compliance_frameworks"]
    compliance_mappings["compliance_mappings"]
    compliance_report_mappings["compliance_report_mappings"]
    coordination_logs["coordination_logs"]
    credential_state["credential_state"]
    credentials["credentials"]
    data_sharing_policies["data_sharing_policies"]
    defense_prediction["defense_prediction"]
    detection_events["detection_events"]
    detection_pressure_history["detection_pressure_history"]
    engagement_reports["engagement_reports"]
    enrichment_data["enrichment_data"]
    evasion_assessment["evasion_assessment"]
    evidence_items["evidence_items"]
    evidence_manifest_entries["evidence_manifest_entries"]
    evidence_manifests["evidence_manifests"]
    finding_summaries["finding_summaries"]
    findings["findings"]
    groups["groups"]
    immutable_audit_log["immutable_audit_log"]
    indicators_of_compromise["indicators_of_compromise"]
    intel_indicators["intel_indicators"]
    intelligence_archive["intelligence_archive"]
    legal_acceptances["legal_acceptances"]
    loot["loot"]
    meta["meta"]
    objective_progress["objective_progress"]
    operation_phases["operation_phases"]
    operator_performance["operator_performance"]
    operator_presence["operator_presence"]
    operator_tempo_metrics["operator_tempo_metrics"]
    opsec_rules["opsec_rules"]
    persistence_registry["persistence_registry"]
    persistence_verification_log["persistence_verification_log"]
    projects["projects"]
    purge_operations["purge_operations"]
    re_authentication_log["re_authentication_log"]
    real_time_alerts["real_time_alerts"]
    recommendation_history["recommendation_history"]
    relations["relations"]
    relationships["relationships"]
    remediation_actions["remediation_actions"]
    remediation_impact["remediation_impact"]
    replay_events["replay_events"]
    report_history["report_history"]
    report_schedules["report_schedules"]
    report_templates["report_templates"]
    report_versions["report_versions"]
    retention_policies["retention_policies"]
    risk_scores["risk_scores"]
    scheduled_tasks["scheduled_tasks"]
    secure_deletion_log["secure_deletion_log"]
    sensitive_field_audit["sensitive_field_audit"]
    session_lifecycle["session_lifecycle"]
    session_management["session_management"]
    sessions["sessions"]
    sessions_ops["sessions_ops"]
    target_lock_diffs["target_lock_diffs"]
    target_locks["target_locks"]
    task_execution_log["task_execution_log"]
    task_templates["task_templates"]
    team_intelligence_pools["team_intelligence_pools"]
    team_members["team_members"]
    team_metrics["team_metrics"]
    team_permissions["team_permissions"]
    team_roles["team_roles"]
    teams["teams"]
    technique_patterns["technique_patterns"]
    threat_actors["threat_actors"]
    threat_correlations["threat_correlations"]
    threat_feeds["threat_feeds"]
    threat_intelligence_feeds["threat_intelligence_feeds"]
    tlp_classifications["tlp_classifications"]
    ttp_execution_metrics["ttp_execution_metrics"]
    user_capabilities["user_capabilities"]
    users["users"]
    webhook_delivery_log["webhook_delivery_log"]
    webhook_subscriptions["webhook_subscriptions"]
    action_risk_log --> campaigns: campaign_id -> id
    actions --> assets: asset_id -> id
    actions --> campaigns: campaign_id -> id
    activity_log --> campaigns: campaign_id -> id
    actor_ttps --> threat_actors: actor_id -> id
    anomaly_detections --> campaigns: campaign_id -> id
    api_integrations --> campaigns: campaign_id -> id
    assets --> campaigns: campaign_id -> id
    audit_certification_reports --> campaigns: campaign_id -> id
    audit_verification_chain --> immutable_audit_log: audit_log_id -> id
    behavioral_profiles --> campaigns: campaign_id -> id
    c2_infrastructure --> campaigns: campaign_id -> id
    campaign_metrics --> campaigns: campaign_id -> id
    campaign_objectives --> campaigns: campaign_id -> id
    campaign_objectives --> users: created_by -> id
    campaign_phase_history --> campaigns: campaign_id -> id
    campaign_reports --> campaigns: campaign_id -> id
    campaign_team_assignments --> campaigns: campaign_id -> id
    campaign_team_assignments --> teams: team_id -> id
    campaigns --> users: created_by -> id
    capability_assessment --> campaigns: campaign_id -> id
    capability_timeline --> capability_assessment: capability_id -> id
    client_reports --> campaigns: campaign_id -> id
    cognition_state_cache --> campaigns: campaign_id -> id
    cognition_state_cache --> users: updated_by -> id
    collaboration_sessions --> campaigns: campaign_id -> id
    collaboration_sessions --> users: created_by -> id
    collaborative_changes --> collaboration_sessions: collab_session_id -> id
    collaborative_changes --> users: operator_id -> id
    command_execution_ledger --> assets: asset_id -> id
    command_execution_ledger --> campaigns: campaign_id -> id
    command_execution_ledger --> users: created_by -> id
    compliance_attestations --> campaigns: campaign_id -> id
    compliance_mappings --> campaigns: campaign_id -> id
    compliance_mappings --> compliance_frameworks: framework_id -> id
    compliance_report_mappings --> campaigns: campaign_id -> id
    compliance_report_mappings --> findings: finding_id -> id
    coordination_logs --> teams: source_team_id -> id
    coordination_logs --> teams: target_team_id -> id
    credential_state --> credentials: credential_id -> id
    credentials --> assets: asset_id -> id
    credentials --> campaigns: campaign_id -> id
    credentials --> users: captured_by -> id
    data_sharing_policies --> teams: source_team_id -> id
    data_sharing_policies --> teams: target_team_id -> id
    defense_prediction --> campaigns: campaign_id -> id
    detection_events --> assets: asset_id -> id
    detection_events --> campaigns: campaign_id -> id
    detection_pressure_history --> campaigns: campaign_id -> id
    engagement_reports --> campaigns: campaign_id -> id
    enrichment_data --> indicators_of_compromise: ioc_id -> id
    evasion_assessment --> campaigns: campaign_id -> id
    evasion_assessment --> detection_events: detection_event_id -> id
    evidence_items --> campaigns: campaign_id -> id
    evidence_items --> findings: finding_id -> id
    evidence_items --> users: approved_by -> id
    evidence_items --> users: collected_by -> id
    evidence_manifest_entries --> evidence_items: evidence_id -> id
    evidence_manifest_entries --> evidence_manifests: manifest_id -> id
    evidence_manifests --> campaigns: campaign_id -> id
    finding_summaries --> findings: finding_id -> id
    indicators_of_compromise --> campaigns: campaign_id -> id
    indicators_of_compromise --> threat_actors: threat_actor_id -> id
    indicators_of_compromise --> threat_feeds: source_feed_id -> id
    intel_indicators --> campaigns: campaign_id -> id
    intel_indicators --> threat_intelligence_feeds: feed_id -> id
    intelligence_archive --> campaigns: campaign_id -> id
    intelligence_archive --> threat_actors: actor_id -> id
    intelligence_archive --> users: archived_by -> id
    loot --> assets: asset_id -> id
    loot --> campaigns: campaign_id -> id
    objective_progress --> campaign_objectives: objective_id -> id
    operation_phases --> campaigns: campaign_id -> id
    operation_phases --> users: entered_by -> id
    operator_performance --> teams: team_id -> id
    operator_performance --> users: user_id -> id
    operator_presence --> collaboration_sessions: collab_session_id -> id
    operator_presence --> users: operator_id -> id
    operator_tempo_metrics --> campaigns: campaign_id -> id
    operator_tempo_metrics --> users: operator_id -> id
    opsec_rules --> users: created_by -> id
    persistence_registry --> assets: asset_id -> id
    persistence_registry --> campaigns: campaign_id -> id
    persistence_verification_log --> persistence_registry: persistence_id -> id
    projects --> groups: group_id -> id
    purge_operations --> retention_policies: policy_id -> id
    re_authentication_log --> users: user_id -> id
    real_time_alerts --> campaigns: campaign_id -> id
    recommendation_history --> campaigns: campaign_id -> id
    recommendation_history --> users: created_by -> id
    relations --> campaigns: campaign_id -> id
    relationships --> campaigns: campaign_id -> id
    relationships --> users: created_by -> id
    remediation_actions --> assets: asset_id -> id
    remediation_actions --> campaigns: campaign_id -> id
    remediation_impact --> remediation_actions: remediation_id -> id
    replay_events --> campaigns: campaign_id -> id
    report_history --> report_schedules: report_schedule_id -> id
    report_schedules --> campaigns: campaign_id -> id
    report_versions --> campaign_reports: report_id -> id
    risk_scores --> campaigns: campaign_id -> id
    risk_scores --> findings: finding_id -> id
    scheduled_tasks --> campaigns: campaign_id -> id
    scheduled_tasks --> task_templates: task_template_id -> id
    scheduled_tasks --> users: created_by -> id
    sensitive_field_audit --> users: accessed_by -> id
    session_lifecycle --> assets: asset_id -> id
    session_lifecycle --> campaigns: campaign_id -> id
    session_management --> users: user_id -> id
    sessions --> users: user_id -> id
    sessions_ops --> assets: asset_id -> id
    sessions_ops --> campaigns: campaign_id -> id
    target_lock_diffs --> target_locks: lock_id -> id
    target_lock_diffs --> users: reviewed_by -> id
    target_locks --> campaigns: campaign_id -> id
    target_locks --> users: operator_id -> id
    task_execution_log --> scheduled_tasks: scheduled_task_id -> id
    task_templates --> campaigns: campaign_id -> id
    task_templates --> users: created_by -> id
    team_intelligence_pools --> teams: team_id -> id
    team_members --> teams: team_id -> id
    team_members --> users: user_id -> id
    team_metrics --> teams: team_id -> id
    team_permissions --> teams: team_id -> id
    team_permissions --> users: user_id -> id
    team_roles --> teams: team_id -> id
    teams --> users: lead_operator_id -> id
    technique_patterns --> campaigns: campaign_id -> id
    threat_actors --> users: created_by -> id
    threat_correlations --> campaigns: campaign_id -> id
    threat_correlations --> users: correlated_by -> id
    threat_feeds --> users: created_by -> id
    tlp_classifications --> users: created_by -> id
    ttp_execution_metrics --> campaigns: campaign_id -> id
    user_capabilities --> users: user_id -> id
    users --> groups: group_id -> id
    webhook_delivery_log --> webhook_subscriptions: webhook_id -> id
    webhook_subscriptions --> campaigns: campaign_id -> id
```
