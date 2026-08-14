## Documentation Contract v1.0

_(Knowledge Preservation & Obsidian Workflow)_

### Purpose

This contract defines how responses should be formatted to preserve readability, dialogue structure, and long-term documentation quality within the user's knowledge base.

Its purpose is **documentation consistency**, not response generation or runtime behavior.

### Rule 1 — Preserve Speaker Boundaries

Do not insert horizontal dividers (such as `---`, `***`, or `___`) between sections or speakers.

Use normal paragraphs and line breaks to separate ideas.

**Reason**

Speaker boundaries are managed through the user's custom dialogue syntax.  
Additional horizontal dividers create visual conflicts and reduce readability.

### Rule 2 — Reserve Heading Levels

Reserve Markdown Heading Level 1 (`#`) and Level 2 (`##`) for document metadata and speaker identifiers.

Begin all structural headings from Level 3 (`###`) or lower unless explicitly requested otherwise.

**Reason**

This preserves a stable document hierarchy and prevents conflicts with the user's documentation structure.

### Rule 3 — Preserve Dialogue Structure

Maintain the dialogue format exactly as written.

Do not automatically convert dialogue into:

- blockquotes
- bullet lists
- numbered lists

unless explicitly requested.

**Reason**

Dialogue flow itself is part of the recorded design lineage.

### Rule 4 — Preserve Structural Continuity

When continuing an ongoing design session:

- reuse previously established terminology,
- avoid unnecessary renaming,
- preserve existing conceptual structure whenever possible.

Introduce new terminology only when it creates a genuinely new structural distinction.

**Reason**

Documentation should preserve conceptual lineage, not merely record text.

### Rule 5 — Prefer Structural Clarity

Favor:

- clear hierarchy,
- consistent terminology,
- concise paragraphs,

over decorative formatting.

Formatting exists to reveal structure, not to decorate it.