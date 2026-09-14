# 90-Day DevSecOps Roadmap

## Phase 1 — Foundations (Days 1–14)

### Week 1: Linux + networking
Learn files/directories, permissions, processes, services, logs, SSH, IP addresses, ports, DNS, TCP/UDP, HTTP/HTTPS and basic troubleshooting.

### Week 2: Git + scripting
Learn commits, branches, pull requests, environment variables, Bash fundamentals and small Python automation scripts.

## Phase 2 — Cloud (Days 15–35)

Learn the cloud mental model first, then AWS hands-on:
- regions and availability zones
- IAM users, roles and policies
- EC2
- S3
- VPC
- public/private subnets
- route tables
- internet gateways
- security groups
- load balancers
- CloudWatch
- Secrets Manager / Parameter Store concepts

Target architecture to understand:

```text
User
  |
DNS
  |
Load Balancer
  |
Application / Container
  |
Database or S3
```

## Phase 3 — Containers + CI/CD (Days 36–50)

Learn Docker images, containers, Dockerfiles, registries, ports, volumes and environment variables. Then create a GitHub Actions pipeline that tests and builds an application automatically.

## Phase 4 — Infrastructure as Code (Days 51–62)

Learn Terraform providers, resources, variables, outputs, state, plan/apply/destroy and modules. Recreate a small AWS environment from code.

## Phase 5 — Security (Days 63–76)

Learn least privilege, secrets management, vulnerability management, OWASP concepts, cloud misconfiguration, logging, threat modeling and incident fundamentals.

## Phase 6 — DevSecOps (Days 77–84)

Add security into the development pipeline:

```text
Code
  -> tests
  -> secret scan
  -> SAST
  -> dependency scan
  -> IaC scan
  -> Docker build
  -> container scan
  -> deploy
  -> monitor
```

Learn tools/concepts such as CodeQL/Semgrep-style SAST, Dependabot/SCA, Gitleaks-style secret detection, Trivy-style container scanning and Checkov/tfsec-style IaC scanning.

## Phase 7 — Portfolio Project (Days 85–90)

Build one small application and secure its complete delivery path.

Required deliverables:
- application source
- Dockerfile
- tests
- Terraform
- AWS architecture diagram
- CI/CD workflow
- SAST
- dependency scanning
- secret scanning
- IaC scanning
- container scanning
- security findings and remediation notes
- threat model
- final README explaining the architecture

## Graduation test

You should be able to explain, without notes:

1. What happens after entering a URL in a browser?
2. How does a packet reach an application running in AWS?
3. What is IAM and why are roles preferable to hard-coded credentials?
4. What problem does Docker solve?
5. What does CI/CD automate?
6. What does Terraform state represent?
7. What are SAST, DAST and SCA?
8. How could secrets leak into a repository?
9. How would you investigate a suspicious cloud workload?
10. Where should security controls exist in a software delivery lifecycle?
