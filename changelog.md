# Changelog

| Date | Type | Change |
|------|------|--------|
| 2026-08-26 | Fix | **TPA Service port reverts to 80 after cluster restart.** After a cluster restart, ArgoCD re-syncs the TPA Helm chart before the OpenShift Route API is fully registered. The chart uses `$.Capabilities.APIVersions.Has "route.openshift.io/v1/Route"` to detect OpenShift — when this check fails during early sync, the Service renders with port 80 (non-OpenShift mode) instead of port 443 (OpenShift TLS mode), breaking the RHDA backend's internal `https://server:443` connection. Fixed by explicitly setting `openshift.enabled: true` in the TPA server `valuesObject` in `templates/applications.yaml`, removing the dependency on runtime API detection. |
