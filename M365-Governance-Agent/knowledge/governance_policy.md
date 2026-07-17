# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

# M365 Governance Policy

## Data Access
- Least privilege is required for all service accounts and automation identities.
- Privileged operations must be approved by an admin when targeting identity, mailbox, or tenant-wide controls.

## Incident Response
- High-risk sign-in events must be triaged within 15 minutes.
- A remediation task must be created with owner, severity, and due date.
- User-facing notifications should be sent through approved Teams channels.

## Change Management
- All actions must be logged with actor identity, timestamp, payload, and outcome.
- Sensitive actions require explicit approval before execution.
- Approval records must include reviewer identity and rationale.
