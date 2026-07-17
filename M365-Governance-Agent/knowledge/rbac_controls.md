# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

# RBAC and Security Controls

## Roles
- Viewer: can ask governance questions only.
- Operator: can ask questions and execute non-sensitive actions.
- Admin: can execute all actions and approve/reject sensitive requests.

## Authentication
- API requests require an API key header.
- User identity and role are passed in trusted headers from upstream gateway or app service auth.

## Approval Policy
- Any action that simulates Graph identity control changes is considered sensitive.
- Sensitive actions are created in pending state and require admin approval.
