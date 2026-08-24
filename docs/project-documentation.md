# Field Content - Self-Service CI Development Platform

## Purpose

Enable Red Hat employees to develop Catalog Items (CIs) for RHDP using GitOps patterns without deep AgnosticD knowledge.

## How It Works

1. Developer creates a Helm chart in their own Git repository
2. Developer provides the repo URL to the "field assets" CI in RHDP
3. The `ocp4_workload_field_content` role creates an ArgoCD Application pointing to their repo
4. ArgoCD deploys the content, using sync waves for ordering
5. ConfigMaps with `demo.redhat.com/userinfo` label pass data back to AgnosticD

## Hybrid Deployment Model

All deployments are Helm charts. Developers can include:
- **Helm templates**: Standard K8s manifests
- **Ansible Jobs**: ansible-runner Jobs for complex orchestration

Use ArgoCD sync waves to control execution order.

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `roles/ocp4_workload_field_content/` | Main workload role |
| `examples/` | Working examples (helm, ansible) |
| `docs/` | Developer guides and architecture diagrams |

## Variable Naming

All AgnosticD workload variables use `ocp4_workload_` prefix:
- ✅ `ocp4_workload_field_content_gitops_repo_url`
- ❌ `field_content_gitops_repo_url`

## RHDP Integration

- **Health monitoring**: Label resources with `demo.redhat.com/application`
- **Data flow**: Create ConfigMaps with `demo.redhat.com/userinfo` label

---
*Last Updated: 2025-01-19*
