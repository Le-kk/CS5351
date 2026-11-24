# Requirements package location

The six files originally uploaded at the repository root now live together under `docs/req/`:

- [requirements.yaml](requirements.yaml): proposed machine-readable PRD/registry.
- [req-schema.json](req-schema.json): registry schema.
- [validate.py](validate.py): existing validator.
- [requirement-source-notes.md](requirement-source-notes.md), [negative-fixtures.md](negative-fixtures.md) and [change-log.md](change-log.md): Member A's supporting records.

All six moved files are byte-identical to their previous versions. This is a layout correction, not adoption of the registry or an amendment to its requirements. It remains `proposed_for_adoption`, now with **36 active entries and 3 withdrawn IDs** at `schema_version: 1.2.0` (the later revisions added `REQ-TA-INV-014` and `REQ-TA-GOV-004`, and the schema made `enforced_components` required). The existing selected requirements and proposals are retained in this directory.

## Run the existing validator

From the repository root, with PyYAML and jsonschema installed in the chosen Python environment:

```text
python3 docs/req/validate.py
```

By default the validator reads `docs/req/requirements.yaml` and `docs/req/req-schema.json`. Its actual interface accepts a **positional** registry path, or the `--registry` flag, plus an optional `--schema`:

```text
python3 docs/req/validate.py /path/to/temporary-registry.yaml
python3 docs/req/validate.py --registry /path/to/registry.yaml --schema /path/to/schema.json
```

It exits non-zero on a missing file, YAML/schema parse failure, or cross-record violation; a valid registry exits 0. The baseline passed and a controlled invalid-priority copy failed for the expected schema reason; see [relocation verification](../reviews/evidence/requirements-relocation-2026-11-24.json). This check used the existing Ubuntu system Python; it does not establish that every virtual environment or CI job has the dependencies.

## Remaining limitations

Moving the files resolves the original layout/command failure in I24 01, and the current validator accepts both a positional path and `--registry`/`--schema` (the earlier '`--registry` unsupported' note is superseded by the current interface). It does not resolve adoption verification, semantic adoption of the registry, remaining validator-rule hardening, or schema-gate installation. These remain the separately recorded A/C/E follow-ups in the [integration review](../reviews/project-integration-review-2026-11-24.md). The original six files, including their historical examples and claims, were deliberately preserved unchanged.

Current architecture reading paths point here. The historical integration review retains its original findings and now links to the exact reviewed root-layout revision. Authentic AI transcripts and retained measurement evidence are not rewritten by this relocation.
