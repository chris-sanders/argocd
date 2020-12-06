# Example Argocd deployment repository
This repository has manifests for deploying software with Argocd.

## Testing
Some basic testing of the configurations is done by deploying each manifest and verifying the
containers start. The test runs on each push as well as weekly since upstream charts are in use
and updates are being allowed for Minor version updates.

![Build](https://github.com/chris-sanders/argocd/workflows/Deploy/badge.svg)
