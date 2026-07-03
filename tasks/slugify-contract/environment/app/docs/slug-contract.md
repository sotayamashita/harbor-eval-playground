# Slug contract

`slugify(text)` converts user-facing text into a URL-safe slug.

## Rules

1. Convert ASCII letters to lowercase.
2. Treat spaces, underscores, and repeated hyphens as separators.
3. Remove non-ASCII characters.
4. Collapse repeated separators into one hyphen.
5. Trim separators from the start and end.
6. If the normalized result is empty, return `untitled`.

## Examples

| Input | Output |
| --- | --- |
| `Hello World` | `hello-world` |
| `  A__B  ` | `a-b` |
| `日本語 Test` | `test` |
| `foo---bar` | `foo-bar` |
| `!!!` | `untitled` |
