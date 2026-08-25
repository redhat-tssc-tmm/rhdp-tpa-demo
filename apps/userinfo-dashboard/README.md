# UserInfo Dashboard

A lightweight Flask web app that reads Kubernetes ConfigMaps labeled with `demo.redhat.com/userinfo` and renders them as a formatted instructions page. It appears in the OpenShift Console application launcher under a configurable category (default: "Demo Platform" / "Instructions") via a `ConsoleLink` CR.

## How It Works

At container startup, the app queries the Kubernetes API for all ConfigMaps with the label `demo.redhat.com/userinfo` in its namespace. The data is cached in memory — a pod restart picks up any changes to ConfigMaps.

The app is deployed with a ServiceAccount that has read-only access to ConfigMaps in its namespace.

## ConfigMap Format

Each ConfigMap with the label `demo.redhat.com/userinfo: ""` becomes a section on the page.

### Required

- **`demo_title`** — section heading, displayed as a bold title bar spanning the full width

### Optional (top-level)

| Key | Description |
|-----|-------------|
| `order` | Numeric sort order. ConfigMaps with `order` are displayed first (ascending). Those without are sorted alphabetically by ConfigMap name. |
| `demo_url` | Displayed as a clickable link, full width, directly below the title |
| `access_instructions` | Descriptive text, full width, below the URL |

### Optional (field pairs)

Fields are displayed as label/value rows in a 20%/80% two-column layout. The numeric suffix determines the order within the section.

| Key | Description |
|-----|-------------|
| `label_N` | Left column — the field label (e.g., "Username") |
| `content_N` | Right column — the field value (e.g., "admin") |
| `content_url_N` | If present, renders an additional row below `content_N` with a clickable link (opens in a new tab) |

Where `N` is a number (1, 2, 3, ...) that determines the display order.

### Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-userinfo
  labels:
    demo.redhat.com/userinfo: ""
data:
  order: "1"
  demo_title: "My Application"
  demo_url: "https://my-app.apps.cluster.example.com"
  access_instructions: "Log in with the credentials below."
  label_1: "Username"
  content_1: "admin"
  label_2: "Password"
  content_2: "changeme"
  label_3: "Documentation"
  content_3: "Full documentation is available here"
  content_url_3: "https://docs.example.com"
```

This renders as:

```
┌──────────────────────────────────────────────────┐
│ My Application                                    │
├──────────────────────────────────────────────────┤
│ https://my-app.apps.cluster.example.com           │
│ Log in with the credentials below.                │
│ Username          │ admin                         │
│ Password          │ changeme                      │
│ Documentation     │ Full documentation is ...     │
│                   │ https://docs.example.com  ↗   │
└──────────────────────────────────────────────────┘
```

## OpenShift Console Integration

The Helm component deploys a `ConsoleLink` CR that adds an entry to the OpenShift Console application launcher (the grid icon in the top-right corner). The category, link text, and icon are configurable via Helm values:

```yaml
components:
  userinfoDashboard:
    consoleLink:
      section: "Demo Platform"       # category in the launcher menu
      text: "Instructions"           # link text
      iconUrl: ""                    # defaults to the app's own /static/demo-icon.png
```

## Building

```bash
podman build -t quay.io/tssc_demos/rhdp-userinfo:latest -f Containerfile .
podman push quay.io/tssc_demos/rhdp-userinfo:latest
```

## Configuration

The app reads the `NAMESPACE` environment variable to know which namespace to query for ConfigMaps. In the Helm deployment, this is set automatically from the pod's own namespace via the downward API.
