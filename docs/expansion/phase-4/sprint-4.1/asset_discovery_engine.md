# Sprint 44: Asset Discovery Engine

## AssetInventory core model
Implemented `AssetInventory` with typed fields for:
- identity: `asset_id`, `tenant_id`, `asset_type`, `name`
- addressing/context: `fqdn`, `ip_address`, `asn`
- cloud scope: `cloud_provider`, `cloud_account_id`
- governance: `owner_tag`, `criticality`
- lineage: `source`, `discovered_at`, `metadata`

## Discovery modules
- `domain_discovery(...)`
  - ingests discovered FQDNs under root domain.
- `subdomain_bruteforce(...)`
  - generates candidate subdomains from wordlist.
- `ingest_ip_range(...)`
  - normalizes CIDR and ingests host addresses (bounded by `max_hosts`).
- `ingest_certificate_transparency(...)`
  - ingests `common_name`/`SAN` domain entries and issuer metadata.

## ASN lookup integration
- `asn_lookup(ip_address=...)`:
  - private IPs map to RFC6996 private ASN `64512`
  - public IPs map deterministically for stable analytics behavior.
- Cloud metadata ingestion automatically applies ASN when IP is present.

## DNS record normalization
- `normalize_dns_record(record)` canonicalizes:
  - `type` => uppercase
  - `name` => lowercase FQDN without trailing dot
  - `value` => lowercase scalar without trailing dot
  - `ttl` => non-negative integer with safe fallback

## Cloud metadata ingestion
- `ingest_cloud_metadata_aws(...)`
- `ingest_cloud_metadata_azure(...)`
- `ingest_cloud_metadata_gcp(...)`

Each function maps provider-specific metadata into unified `AssetInventory` rows.

## Ownership + criticality
- `tag_asset_owner(asset_id, owner_tag)` assigns ownership context.
- `classify_asset_criticality(asset_id)` computes `low|medium|high|critical` using:
  - asset type
  - service-name sensitivity signals
  - ownership role weighting

## Deduplication behavior
- Dedup key combines tenant + normalized fqdn/ip/name.
- Duplicate observations across discovery, brute-force, and CT ingestion are merged, not duplicated.

## Validation
- Unit tests verify:
  - cross-source asset deduplication
  - DNS normalization behavior
  - cloud ingestion + ASN + owner tagging + criticality classification
