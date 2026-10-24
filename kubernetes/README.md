# Kubernetes (bro_cast)

Everything to run the app on the cluster: namespace, secrets, database with
backups, backend, frontend, ingress. One entry point: `kubectl apply -k .`

Folders follow apply order: `00-namespace`, `01-secrets` (env + generator +
generated manifests), `02-config`, `03-storage`, `04-database`, `05-backend`,
`06-frontend`).

Previous manifests are kept in `kubernetes_old/` (not applied).

## Commands

```bash
# first setup
kubectl apply -f 00-namespace/namespace.yaml
./01-secrets/manage_secrets.py            # add --generate to rotate values first
kubectl apply -k .

# rotate a secret value
# edit 01-secrets/secrets.env, then:
./01-secrets/manage_secrets.py && kubectl apply -k . && \
  kubectl -n broer rollout restart deploy/fastapi-deployment deploy/worker-deployment deploy/cron-worker-deployment

# teardown
kubectl delete -k .
```

## Migrating from the plain-Postgres setup

This tree runs Postgres via CloudNativePG (`brocast-db`, Longhorn-backed).
Applying it creates a NEW, EMPTY database: existing data in the old
`deployment-postgres` PVC is NOT carried over automatically. Migrate first:

```bash
# 1. dump the old database (from any pod/host with psql access)
pg_dump -h <old-postgres-host> -U <user> -Fc brocast_db -f brocast.dump
# 2. apply the new tree, wait for brocast-db to be ready
# 3. restore into the new primary
pg_restore -h brocast-db-rw.broer.svc.cluster.local -U brostgres -d brocast_db brocast.dump
# 4. only then delete the old deployment-postgres + its PVC

## Migrating avatars to S3

Avatars live in S3 (`brocast/avatars/`), not on node storage. One-shot
backfill after the new pods are up, using the staged files from the old
PVC as the source (`/tmp/bro-uploads/avatars`, 215 files):

```bash
NEWPOD=$(kubectl get pods -n broer -l app=fastapi -o jsonpath='{.items[0].metadata.name}')
kubectl cp -n broer /tmp/bro-uploads/avatars/. $NEWPOD:/app/static/uploads/avatars/
kubectl port-forward -n broer svc/fastapi-service 32136:32136 &
curl -X POST http://localhost:32136/api/v1.4/admin/migrate_avatars/<LOG_READ_PASSWORD>
```

The endpoint uploads staged files (preserving custom avatars) and
generates any missing defaults; existing S3 keys are skipped, so
re-running is safe. Afterwards the old `zwaar-brocast-pvc` holds no
needed files anymore (database migrated separately, see above).


