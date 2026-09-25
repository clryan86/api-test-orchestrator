# Security Policy

The platform sends outbound requests defined by test suites. Production deployments should configure `ALLOWED_HOSTS` and should not expose the execution API to untrusted users without authentication and authorization.

Future secret support should use secret references backed by a vault rather than storing credentials in test-suite JSON.
