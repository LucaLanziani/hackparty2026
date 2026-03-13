---
description: "Use when writing frontend code: React components, pages, hooks, styles, routing, or UI. Covers Vite 6, React 19, TypeScript, Tailwind CSS v4, ShadCN UI, and React Router v7 conventions."
applyTo: "frontend/**"
---

# Frontend Guidelines

## Stack

- **Vite 6** — build tool; `@/` path alias maps to `src/`
- **React 19** — functional components only, hooks-based state
- **TypeScript** — strict mode enabled; always type props and return values
- **Tailwind CSS v4** — utility-first styling via `@import "tailwindcss"` (not v3 directives)
- **ShadCN UI** — pre-built accessible components in `src/components/ui/`
- **React Router v7** — file: `src/App.tsx` owns route definitions

## File Organization

```
src/
├── components/    # Shared, reusable components
│   └── ui/        # ShadCN UI components (do not hand-edit)
├── pages/         # One file per route (e.g., Home.tsx, About.tsx)
├── hooks/         # Custom hooks (use* naming convention)
└── lib/           # Pure utilities and helpers
```

## Component Conventions

- Use named exports (`export function MyComponent`)
- Co-locate component-specific logic (types, helpers) in the same file unless broadly reused
- Prefer ShadCN UI components over custom equivalents (Button, Input, Card, etc.)
- Apply Tailwind classes inline; avoid custom CSS unless unavoidable

## Tailwind CSS v4

- Import: `@import "tailwindcss"` in `src/index.css` — never use `@tailwind base/components/utilities`
- No `tailwind.config.*` file needed — v4 auto-detects content
- Use standard utility classes; custom values via CSS variables in `index.css`

## Routing

To add a new page:
1. Create component in `src/pages/`
2. Add `<Route>` in `src/App.tsx`
3. Update `src/components/Navigation.tsx` if it needs a nav link

## TypeScript

- Use `@/` imports (e.g., `import { Button } from "@/components/ui/button"`)
- **Always run `pnpm typecheck` after making any change** — treat type errors as blocking
- Prefer `interface` for object shapes, `type` for unions/aliases

## API Calls

- Base URL: `import.meta.env.VITE_API_URL` (fallback: `http://localhost:5000/api`)
- Put fetch logic in custom hooks under `src/hooks/` or utility functions in `src/lib/api.ts`
- Handle loading and error states explicitly

## Checks Before Committing

```bash
pnpm typecheck   # must pass — no type errors
pnpm lint        # must pass — no lint errors
pnpm build       # verify production build succeeds
```
