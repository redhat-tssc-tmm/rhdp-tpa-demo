# Trusted Profile Analyzer - RHDP Deployment

Deploys [Red Hat Trusted Profile Analyzer](https://docs.redhat.com/en/documentation/red_hat_trusted_profile_analyzer) and all required components on OpenShift using an ArgoCD app-of-apps pattern.

## Provisioning via RHDP

This repository is designed to be deployed through the [Field Content CI](https://catalog.demo.redhat.com/catalog/all?item=babylon-catalog-prod%2Fpublished.ocp-field-asset.prod) catalog item on Red Hat Demo Platform.

When ordering, fill in the provisioning form as follows:

| Field | Value |
|-------|-------|
| **Existing Gitops Repo?** | Checked |
| **GitOps Repo** | `https://github.com/redhat-tssc-tmm/rhdp-tpa-demo.git` |
| **GitOps Revision** | `main` |
| **GitOps Path** | `.` |

> **Important:** The GitOps Path must be set to `.` (a single dot). Leaving it empty will cause the ArgoCD Application to fail with an `InvalidSpecError` because ArgoCD requires an explicit path value.

## Components

| Component | Status | Description |
|-----------|--------|-------------|
| PostgreSQL | Deployed | Database backend for TPA (RHEL 10 / PostgreSQL 18) |

## Repository Structure

```
rhdp-tpa-demo/
├── Chart.yaml                  # App-of-apps root chart
├── values.yaml                 # Global configuration
├── templates/
│   └── applications.yaml       # Generates ArgoCD Application CRs
├── components/
│   └── postgresql/             # PostgreSQL database
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/          # Secret, PVC, ConfigMap, Deployment, Service
├── examples/                   # Reference: field-content template examples
└── roles/                      # Reference: AgnosticD workload role
```

## Configuration

All settings are in `values.yaml`. Key values:

```yaml
fieldContentName: tpa                        # Prefix for child ArgoCD Application names
tpaNamespace: trusted-profile-analyzer       # Target namespace for all TPA components
```

Component-specific settings (credentials, storage, tuning, resources) are under `components.<name>` in `values.yaml`.

## Local Testing

```bash
helm lint .
helm template tpa .
helm template tpa . --set tpaNamespace=my-namespace
```
