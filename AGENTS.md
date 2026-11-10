# AGENTS.md

## Project Overview

This repository is the participant starter kit for "Think Fast: Local Decision Models", the proximata track at proximata Hackathon '26 (13–14 November 2026, Vienna). It holds the case brief (`CASE.md`), the decision API contract (`docs/decision-api.md`) and a dependency-free Python package (`thinkfast/`) with the dev-suite generator, the evaluation runner, a baseline bridge and a messy-dataset generator. Everything here is public and MIT-licensed: never commit hidden-suite data, its generator seeds or answer keys. Before making changes, read the README, project documentation, and nearby code to understand the intended workflow, architecture, and conventions.

## Working Principles

- Prefer the repository's existing patterns, naming, and tools over introducing new conventions.
- Keep changes focused on the user's request; avoid opportunistic refactors unless they are necessary for correctness or maintainability.
- Preserve behavior unless the task explicitly asks for a behavior change.
- Treat the working tree as shared: do not revert or overwrite changes you did not make.
- When requirements are ambiguous, ask the user rather than inventing assumptions.
- Never invent factual inputs, evidence, metrics, people, or results.

## Project Structure

- Keep the project structure easy to scan and document the purpose of important top-level folders.
- Separate source code, tests, documentation, configuration, generated artifacts, and local data/cache files where possible.
- Put reusable implementation logic in the project's source package or shared module area.
- Keep one-off, workflow-specific, experiment-specific, or notebook-specific logic close to the workflow that uses it.
- Do not move code into shared `src` modules just because it is convenient; shared code should be generic, reusable, and stable enough to import from multiple places.

## Setup and Dependencies

- Use modern package managers (e.g. uv or bun) and environment tooling and similar to ones that are already present in the repository, if any.
- Update lockfiles when dependency changes require it.
- Do not add new dependencies when the standard library or existing project dependencies are sufficient.
- When there are vetted and battle-tested well-maintained open source options to import from, use those instead of inventing new code.
- Get user permission before installing software. Prefer verified package-manager sources and do not pipe remote scripts directly to a shell.
- Document required setup commands in the README or another visible project document.

## Code Quality

- Use your skills whenever applicable.
- Before opening a PR, run thorough code quality checks with available tools.
- Prefer clear, direct code over clever abstractions.
- Add abstractions only when they remove real duplication or clarify a stable boundary.
- Keep functions small enough to understand, with names that describe intent.
- Use structured APIs and parsers for structured data instead of fragile string manipulation.
- Add comments only where they explain non-obvious reasoning, constraints, or trade-offs.

## Tests and Validation

- Run the narrowest relevant checks after a change, then broader checks when the change affects shared behavior.
- Add or update tests when changing behavior, fixing a bug, or touching shared logic.
- If tests cannot be run, state what was not run and why.
- Clear all notebook outputs before committing.

## Data, Secrets, and Generated Files

- Do not commit secrets, credentials, local environment files, or private tokens.
- Do not commit large data files, caches, build outputs, or generated artifacts unless the project explicitly tracks them.
- Keep generated files in documented locations and make regeneration steps clear.
- Avoid changing source data or persisted outputs unless the task explicitly requires it.
- Explain data transmission and get approval before sending private, unpublished, personal, or secret-bearing content to a new external service.

## Documentation

- Never write hard paths into docs as they might be public facing -- always use relative repo-scope paths.
- Keep documentation aligned with code behavior, file names, commands, and data contracts.
- Update README or reference docs when changing workflow order, public interfaces, configuration, or generated outputs.
- Preserve historical notes unless the task is specifically to revise them.

## Git and Collaboration

- Use Conventional Commits with short, imperative summaries, while respecting stricter existing project conventions.
- Before committing, review the full diff and avoid including unrelated files.
- Use topic branches with descriptive names and make meaningfully-sized commits.

## External Actions

- Treat the user's task request as authorization for routine, in-scope external edits.
- Get confirmation before destructive, costly, production, account-level, or irreversible external actions.
