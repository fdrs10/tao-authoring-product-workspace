# Repository Bootstrap / First Kinchi Run

## 1. Create remote repository
Recommended name: `tao-authoring-product-workspace`. Create it in the company GitHub/GitLab organisation as a private repository. Do not create a second product/runtime repository for this app.

## 2. Seed it from this package
```bash
unzip TAO_Authoring_KINCHI_REPOSITORY_HANDOFF_v1.0.zip
cd tao-authoring-product-workspace
git init
git checkout -b main
git add .
git commit -m "baseline: import Authoring product workspace handoff"
git remote add origin <COMPANY_REPOSITORY_URL>
git push -u origin main
```

## 3. Protect the baseline
```bash
git tag -a functional-baseline-v38.6 -m "Functional reference before multi-user reimplementation"
git push origin functional-baseline-v38.6
```

## 4. Branch for application implementation
```bash
git checkout -b feat/cloud-multiuser-foundation
```

## 5. First implementation order
1. Import/validate canonical data.
2. Create PostgreSQL schema + migrations.
3. Create backend API and health endpoint.
4. Split frontend from legacy HTML without redesign.
5. Implement Sources and universal capability modal.
6. Implement Ideation/Cross-analysis/Product Backlog + Admission.
7. Recover Roadmap behaviours.
8. Implement Migration Path/customer intervals.
9. Automated regression tests.
10. Containerize and deploy to dev Cloud Run + dev Cloud SQL.

No Cloud deployment until data import tests and first-render/browser smoke tests pass.
