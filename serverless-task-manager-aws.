
# Serverless Task Management Application — AWS

A serverless, authenticated task management app built to practice AWS Solutions Architect concepts: managed identity, API-layer authorization, event-driven decoupling, and least-privilege access control.

## Architecture

```
Users → CloudFront → S3 (static frontend)
Users → Cognito (auth) → API Gateway (JWT authorizer) → Lambda → DynamoDB
                                                            ↓
                                                     SNS → Email notification
```

**Flow:** A user signs up and signs in through Amazon Cognito. The frontend (hosted on S3, served through CloudFront) sends API requests with a Cognito-issued JWT in the Authorization header. API Gateway validates that token *before* invoking Lambda — unauthenticated or expired requests never reach application code. Lambda reads/writes DynamoDB, scoping every query to the authenticated user's own partition, and publishes an SNS notification on task creation.

## Tech stack

- **Amazon Cognito** — user sign-up/sign-in, JWT issuance
- **Amazon API Gateway (HTTP API)** — request routing, JWT authorizer
- **AWS Lambda (Python)** — `createTask` and `listTasks` functions
- **Amazon DynamoDB** — on-demand table, partitioned by user ID
- **Amazon SNS** — decoupled email notification on new task creation
- **Amazon S3 + CloudFront** — static frontend hosting via Origin Access Control
- **AWS IAM** — least-privilege execution role scoped to specific table/topic ARNs

## Key design decisions

- **No credentials in application code.** Lambda never sees a password or session token — Cognito and the API Gateway JWT authorizer handle the entire authentication boundary.
- **Per-user data isolation via partition key.** Each DynamoDB item is keyed by the user's Cognito `sub`, so one user's tasks are structurally inaccessible to another without any extra access-control logic.
- **Least-privilege IAM.** The Lambda execution role grants only `PutItem`/`GetItem`/`Query`/`DeleteItem` on the specific table ARN and `Publish` on the specific SNS topic ARN — not broad managed policies.
- **Decoupled notifications.** Lambda publishes to SNS without any knowledge of who (or what) is subscribed, which is the core pattern behind loosely-coupled, event-driven architectures.

## Contents

- `createTask.py` / `listTasks.py` — Lambda function code
- `iam-policy.json` — scoped IAM policy for the Lambda execution role
- `frontend/index.html` — static frontend using Cognito Hosted UI
- `/screenshots` — sign-in flow, task creation, email notification, CloudWatch logs

## What I learned

Building this alongside a more traditional EC2/ALB/RDS project (see [link to your other repo]) gave me hands-on comparison between server-based and serverless architecture patterns — when each makes sense, and how authentication, scaling, and cost models differ between them.
