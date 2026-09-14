# AWS Credits and Cost Controls

## Promotional credit request

The entrant registered for the Build, Ship, Shape: Amazon Developer Hackathon and submitted the official request for **$150 in AWS Promotional Credits** on 2026-09-14.

The request is not guaranteed and may take up to five business days to process. One code is permitted per entrant. Do not record redemption codes, credentials, access keys, or other secrets in this repository.

## Cost principle

Promotional credit is a budget offset, not permission for uncontrolled resource consumption. Additional AWS charges remain the entrant's responsibility.

## Before deploying billable resources

- [ ] Confirm the AWS account being used.
- [ ] Inspect available promotional-credit balance and expiration.
- [ ] Confirm service eligibility for the issued credit.
- [ ] Identify all already-running resources in the account that may consume eligible credit.
- [ ] Establish a project budget/alert strategy where supported.
- [ ] Prefer bounded, explicitly started resources over indefinite deployments.
- [ ] Document expected cost drivers.
- [ ] Never commit AWS credentials or reusable secrets.

## During development

- Review spend regularly.
- Shut down resources that are not required for development, demo, or judging.
- Keep the Alexa+ project distinguishable from other workloads in the same AWS account where practical.
- Record AWS services actually used in `product-feedback.md`.

## After judging

Perform an explicit resource teardown/cost audit. Preserve only resources that have an intentional post-hackathon purpose.
