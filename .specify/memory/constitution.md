<!--
╔════════════════════════════════════════════════════════════════════════════╗
║                    SYNC IMPACT REPORT - CONSTITUTION UPDATE                ║
╚════════════════════════════════════════════════════════════════════════════╝

VERSION CHANGE: 0.0.0 → 1.0.0
DATE: 2025-11-04
REASON: Initial constitution creation from template (MAJOR version)

╔════════════════════════════════════════════════════════════════════════════╗
║ CHANGES SUMMARY                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

ADDITIONS:
- Initial constitution creation from template
- Established 5 core principles for Spec Kit development
- Added Quality & Testing Standards section
- Added Development Workflow section
- Defined governance rules and versioning policy

PRINCIPLES DEFINED:
1. Specification-First Development
   - Specs before code, technology-agnostic requirements
   - Executable contracts between stakeholders and developers

2. AI-Agent Agnostic Design
   - Multi-agent compatibility required in all templates
   - No vendor lock-in, generic guidance over agent-specific references

3. Iterative Refinement Over One-Shot Generation
   - Structured multi-phase process: specify → clarify → plan → tasks → implement
   - Each phase validates previous phase output

4. Template-Driven Consistency
   - Standardized templates for all artifacts
   - Mandatory/optional section definitions enforced

5. Independent Testability
   - User stories must be independently testable
   - Incremental delivery and parallel development support

╔════════════════════════════════════════════════════════════════════════════╗
║ TEMPLATE CONSISTENCY VALIDATION                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ .specify/templates/plan-template.md
   - Constitution Check section aligns with principles
   - Complexity Tracking table supports governance compliance
   - Project structure options support multiple architectures

✅ .specify/templates/spec-template.md
   - User story prioritization aligns with Independent Testability principle
   - Requirements clarity aligns with Quality & Testing Standards
   - Success criteria guidelines enforce technology-agnostic approach

✅ .specify/templates/tasks-template.md
   - Task organization by user story supports Independent Testability
   - Parallel execution markers support efficient workflow
   - Phase dependencies clearly defined for incremental delivery

✅ templates/commands/constitution.md
   - Uses generic guidance with no agent-specific references
   - Properly documents template structure and validation requirements

✅ templates/commands/specify.md
   - Uses generic guidance with no agent-specific references
   - Implements quality validation gates aligned with principles

✅ templates/commands/plan.md
   - Uses __AGENT__ placeholder and detection scripts
   - Generic workflow applicable to all supported agents

✅ README.md
   - Already references /speckit.constitution command
   - Documents constitution as foundational governance artifact
   - Includes constitution in development workflow steps

✅ spec-driven.md
   - Extensive discussion of constitutional principles
   - Explains enforcement through templates and gates
   - Documents constitutional evolution process

✅ docs/ directory
   - No constitution-specific content requiring updates
   - Quickstart and installation docs remain valid

╔════════════════════════════════════════════════════════════════════════════╗
║ FOLLOW-UP ACTIONS                                                          ║
╚════════════════════════════════════════════════════════════════════════════╝

DEFERRED ITEMS:
- None (ratification date set to today as this is initial creation)

RECOMMENDED NEXT STEPS:
1. Review constitution with project maintainers (@localden, @jflam)
2. Consider if ratification date should be backdated to project inception
3. No template updates required - all artifacts already aligned

╔════════════════════════════════════════════════════════════════════════════╗
║ VALIDATION CHECKLIST                                                       ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ No unexplained bracket tokens remaining
✅ Version line matches report (1.0.0)
✅ Dates in ISO format (YYYY-MM-DD)
✅ Principles are declarative and testable
✅ All dependent templates validated for consistency
✅ No agent-specific references in generic templates
✅ Governance rules clearly defined
✅ Amendment process documented

-->

# Spec Kit Constitution

## Core Principles

### I. Specification-First Development

Every feature MUST begin with a clear, technology-agnostic specification before any implementation. Specifications define the **what** and **why**, never the **how**. Implementations are validated against specs, not the reverse.

**Rationale**: Specs serve as executable contracts between stakeholders and developers. They enable parallel exploration of multiple implementations, provide clear acceptance criteria, and ensure features solve the right problems before code is written.

### II. AI-Agent Agnostic Design

All templates, commands, and workflows MUST be compatible with multiple AI coding assistants. Agent-specific references are forbidden in shared templates; use generic guidance instead. Each supported agent receives equivalent capability through agent-specific command files.

**Rationale**: Developers use diverse AI tools based on preference, organizational constraints, and capabilities. Spec Kit must serve all users equally, preventing vendor lock-in and ensuring the methodology transcends any single AI platform.

### III. Iterative Refinement Over One-Shot Generation

Feature development follows a structured multi-phase process: specify → clarify → plan → tasks → implement. Each phase refines and validates the previous phase's output. One-shot prompts-to-code are explicitly rejected.

**Rationale**: Complex software requires deliberate planning and validation at multiple stages. Rushing to implementation without clarification and planning leads to rework, scope creep, and misaligned solutions. Each refinement gate catches issues early when they're cheapest to fix.

### IV. Template-Driven Consistency

All artifacts (specs, plans, tasks, checklists) MUST follow standardized templates. Templates define mandatory sections, optional sections, and formatting conventions. Deviations require explicit justification and constitutional amendment.

**Rationale**: Consistency enables predictability. When all specs follow the same structure, reviewers know where to find critical information, AI agents can reliably parse requirements, and teams can build muscle memory around the process.

### V. Independent Testability

Every user story, feature, and task MUST be independently testable without requiring other incomplete components. Stories are prioritized and organized to support incremental delivery. Each story delivers standalone value as a Minimum Viable Product (MVP).

**Rationale**: Independent testability enables parallel development, early user feedback, and risk reduction. Teams can validate critical features first, pivot based on learnings, and deliver value incrementally rather than waiting for complete implementations.

## Quality & Testing Standards

### Requirement Clarity

- All requirements MUST be testable, unambiguous, and measurable
- Success criteria MUST be technology-agnostic and user-focused
- [NEEDS CLARIFICATION] markers limited to maximum 3 per specification
- Reasonable defaults MUST be documented in Assumptions section

### Validation Gates

- Specifications validated against quality checklists before planning
- Implementation plans validated against constitutional principles
- Task breakdowns validated for dependency management and parallelization opportunities
- Each validation gate MUST pass before proceeding to next phase

### Testing Philosophy

- Tests are optional but encouraged based on feature criticality
- When included, tests MUST be written before implementation (TDD)
- Contract tests validate external interfaces and API contracts
- Integration tests validate user journeys and cross-component behavior
- Unit tests validate individual component logic

## Development Workflow

### Phase Execution Order

1. **Constitution** (`/speckit.constitution`) - Establish governing principles
2. **Specify** (`/speckit.specify`) - Define user needs and requirements
3. **Clarify** (`/speckit.clarify`) - Optional: Resolve ambiguities through structured questioning
4. **Plan** (`/speckit.plan`) - Define technical approach and architecture
5. **Analyze** (`/speckit.analyze`) - Optional: Cross-artifact consistency validation
6. **Tasks** (`/speckit.tasks`) - Break down into actionable task list
7. **Implement** (`/speckit.implement`) - Execute implementation following task order

### Branching & Organization

- Each feature creates a numbered branch: `###-short-name` (e.g., `001-user-auth`)
- Branch numbers determined by checking remote branches, local branches, and specs directories
- Feature artifacts stored in `specs/###-short-name/` directory
- Constitutional principles stored in `.specify/memory/constitution.md`

### Documentation Requirements

- All artifacts MUST use Markdown format
- File paths MUST be absolute or clearly relative to documented root
- Commands MUST include both bash and PowerShell script variants
- Agent-specific guidance MUST be isolated to agent-specific files (e.g., `.claude/`, `.gemini/`)

## Governance

This constitution supersedes all other development practices and guidelines within Spec Kit projects. All specifications, plans, implementations, and pull requests MUST comply with these principles.

### Amendment Process

1. Proposed amendments documented with clear rationale and impact analysis
2. Changes require approval from project maintainers
3. Version increment follows semantic versioning:
   - **MAJOR**: Backward-incompatible governance/principle removals or redefinitions
   - **MINOR**: New principle/section added or materially expanded guidance
   - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements
4. All dependent templates and documentation updated to reflect amendments
5. Sync Impact Report generated listing all affected artifacts

### Compliance Review

- All PRs/reviews verify compliance with constitutional principles
- Violations require explicit justification or spec/plan updates
- Complexity additions (e.g., new dependencies, patterns) documented in Complexity Tracking tables
- Constitution validation performed before planning phase (Constitution Check section)

### Runtime Guidance

For agent-specific runtime development guidance during implementation, consult the appropriate agent guidance file (e.g., `.claude/rules/specify-rules.md`, `.gemini/commands/specify-rules.toml`) which translates these constitutional principles into actionable agent instructions.

**Version**: 1.0.0 | **Ratified**: 2025-11-04 | **Last Amended**: 2025-11-04
