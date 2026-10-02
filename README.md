# Network Compliance Lab

Containerlab test networks for developing and benchmarking a multi-vendor
network audit engine: inventory, configuration hardening, reachability,
cryptography and post-quantum readiness, mapped to ISM controls.

## Requirements
- Linux host (OrbStack Ubuntu machine on Apple Silicon)
- Docker and containerlab
- Nokia SR Linux image: ghcr.io/nokia/srlinux

## Labs
| Lab | Status | Description |
|-----|--------|-------------|
| `labs/dev` | Working | 2 SR Linux nodes and 1 Linux host |
| `labs/small-office` | Planned | 5-node small office with seeded faults |
| `labs/multi-site` | Planned | 25-node multi-site business |

## Run a lab
```bash
cd labs/dev
sudo containerlab deploy -t dev-topology.clab.yml
sudo containerlab inspect -t dev-topology.clab.yml
sudo containerlab destroy -t dev-topology.clab.yml --cleanup
```

## Repository layout
- `labs/` – one folder per topology, each with its own configs
- `ansible/` – inventory, variables and playbooks
- `collector/` – discovery and collection code
- `rules/` – compliance and crypto rules mapped to ISM controls
- `answer-keys/` – seeded-fault catalogues used for scoring
- `scripts/` – helper scripts
- `docs/` – notes, diagrams and sample reports

Lab credentials are defaults for local testing only. Never use real client data here.
