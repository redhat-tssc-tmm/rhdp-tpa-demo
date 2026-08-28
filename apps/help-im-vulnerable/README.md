# Demo: help-im-vulnerable Spring Boot App

## Context

We need a deliberately vulnerable Spring Boot application for TPA demo purposes. When its SBOM is uploaded to TPA, the system should show vulnerabilities **with Lightwell remediation** — the `x_RHLW-*` advisories in the dataset provide backport fix versions (`*.rhlw-*`) for specific package base versions. The app uses the exact base versions these advisories target, so TPA shows a clear "upgrade to X.rhlw-00001" remediation path.

## RHLW Advisory → Dependency Mapping

The 11 RHLW advisories in the demo dataset specify these exact purls and base versions:

| RHLW Advisory | Package (purl) | Base Version to Use | Fix Available |
|---|---|---|---|
| x_RHLW-CVE-2022-40152-6.0.3 | `pkg:maven/com.fasterxml.woodstox/woodstox-core` | **6.0.3** | 6.0.3.rhlw-00001 |
| x_RHLW-CVE-2022-45688-20220320 | `pkg:maven/org.json/json` | **20220320** | 20220320.0.0.rhlw-00003 |
| x_RHLW-CVE-2023-5072-20220320 | `pkg:maven/org.json/json` | **20220320** | 20220320.0.0.rhlw-00003 |
| x_RHLW-CVE-2023-20860-5.3.18 | `pkg:maven/org.springframework/spring-webmvc` | **5.3.18** | 5.3.18.rhlw-00010 |
| x_RHLW-CVE-2023-20861-5.3.18 | `pkg:maven/org.springframework/spring-expression` | **5.3.18** | 5.3.18.rhlw-00010 |
| x_RHLW-CVE-2023-20863-5.3.18 | `pkg:maven/org.springframework/spring-expression` | **5.3.18** | 5.3.18.rhlw-00010 |
| x_RHLW-CVE-2023-51074-2.8.0 | `pkg:maven/com.jayway.jsonpath/json-path` | **2.8.0** | 2.8.0.rhlw-00001 |
| x_RHLW-CVE-2024-38808-5.3.18 | `pkg:maven/org.springframework/spring-expression` | **5.3.18** | 5.3.18.rhlw-00010 |
| x_RHLW-CVE-2024-38816-5.3.18 | `pkg:maven/org.springframework/spring-webmvc` | **5.3.18** | 5.3.18.rhlw-00010 |
| x_RHLW-CVE-2025-41249-5.3.18 | `pkg:maven/org.springframework/spring-core` | **5.3.18** | 5.3.18.rhlw-00010 |

### Key constraint: Spring Framework 5.3.18

Six RHLW advisories target Spring Framework **5.3.18** (spring-core, spring-expression, spring-webmvc). We pin Spring Framework to exactly **5.3.18**, which means using **Spring Boot 2.6.6** (the release that ships with Spring 5.3.18).

## Dependency Plan

| Dependency | Pinned Version | RHLW CVEs | Other CVEs |
|---|---|---|---|
| Spring Boot (parent) | **2.6.7** | | CVE-2025-22235, CVE-2026-40973 |
| spring-webmvc (transitive 5.3.18) | via Boot 2.6.6 | CVE-2023-20860, CVE-2024-38816 | |
| spring-expression (transitive 5.3.18) | via Boot 2.6.6 | CVE-2023-20861, CVE-2023-20863, CVE-2024-38808 | |
| spring-core (transitive 5.3.18) | via Boot 2.6.6 | CVE-2025-41249 | |
| spring-security (via starter) | 5.6.2 (Boot 2.6.6 default) | | CVE-2024-22257, CVE-2024-38821, CVE-2026-22732, CVE-2026-22746 |
| woodstox-core | **6.0.3** | CVE-2022-40152 | |
| org.json:json | **20220320** | CVE-2022-45688, CVE-2023-5072 | |
| json-path | **2.8.0** | CVE-2023-51074 | |
| snakeyaml | 1.29 (Boot 2.6.6 default) | | CVE-2022-1471 |
| logback-classic | 1.2.11 (Boot 2.6.6 default) | | CVE-2023-6378 |
| jackson-databind | 2.13.2 (Boot 2.6.6 default) | | CVE-2022-42003 |
| commons-fileupload | 1.4 | | CVE-2023-24998 |
| commons-io | 2.11.0 | | CVE-2024-47554 |
| httpclient | 4.5.12 | | CVE-2020-13956 |
| json-smart | 2.4.8 | | CVE-2023-1370, CVE-2024-57699 |
| junit (test) | 4.13 | | CVE-2020-15250 |
| h2 | 2.1.214 | | CVE-2022-45868 |
| plexus-utils | 3.5.0 | | CVE-2025-67030 |

**Coverage: all 27 CVEs, including all 11 RHLW advisories with Lightwell remediation.**

## App Structure

```
apps/help-im-vulnerable/
├── pom.xml                                          # Spring Boot 2.6.6 parent, pinned deps
├── Containerfile                                    # Multi-stage: Maven build + UBI runtime
├── src/main/java/com/redhat/tpa/vulnerable/
│   ├── HelpImVulnerableApplication.java             # @SpringBootApplication
│   ├── HelloController.java                         # Exercises all vulnerable deps
│   └── SecurityConfig.java                          # Minimal Spring Security config
└── src/main/resources/
    └── application.properties
```

## UI / Landing Page

The app serves a self-contained HTML landing page at `/` that explains its purpose and shows live status:

- **Header:** "Help, I'm Vulnerable!" with a subtitle explaining it's an intentionally vulnerable demo app for TPA
- **Description:** Brief paragraph explaining that this app bundles known-vulnerable dependencies so TPA can demonstrate vulnerability detection and Lightwell remediation
- **Dependency table** (rendered server-side) with columns:
  - Library name
  - Version used
  - CVE(s) triggered
  - Lightwell fix available (yes/no + version)
  - Status: a green checkmark confirming the library loaded successfully at runtime
- **Footer:** links to TPA and a note about not deploying this to production

The page is a single `@GetMapping("/")` returning HTML with inline CSS (PatternFly-inspired). No templates, no static resources, just a string built in the controller. A separate `/api/status` endpoint returns the same data as JSON.

## HelloController Design

Each library is exercised in a `checkLibrary()` method called at startup/request time:
- SnakeYAML: `new Yaml().dump(...)` 
- Jackson: `new ObjectMapper().writeValueAsString(...)`
- HttpClient: `HttpClients.createDefault()`
- json-smart: `JSONValue.parse(...)`
- org.json: `new JSONObject(...)`
- json-path: `JsonPath.read(...)`
- Woodstox: `WstxInputFactory` reference
- Commons IO: `IOUtils.toString(...)`
- Commons FileUpload: `DiskFileItemFactory` reference
- H2: `org.h2.Driver` class reference
- plexus-utils: `StringUtils.trim(...)`

Results are collected into a list of status entries that feed both the HTML table and the JSON endpoint.

## Verification

1. `cd apps/help-im-vulnerable && mvn clean package` — confirms compilation
2. `podman build -f Containerfile -t help-im-vulnerable .` — builds container
3. Generate SBOM: 
   - if running locally (no container registry), export a tar first
   - `podman save help-im-vulnerable -o /tmp/help-im-vulnerable.tar`
   - `syft /tmp/help-im-vulnerable.tar -o cyclonedx-json@1.6 --source-name "Help-Im-Vulnerable" --source-version "1.0.0" > sbom.json`
4. Upload to TPA and verify:
   - All 11 RHLW advisories match with Lightwell remediation versions
   - Additional CVE advisories match the remaining deps
