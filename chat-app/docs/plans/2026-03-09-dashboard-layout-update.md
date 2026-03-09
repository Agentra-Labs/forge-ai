# Dashboard Layout Update Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Adjust the dashboard workspace layout to better mirror the reference workflow UI, while keeping the existing Forge colors, typography, and theme.

**Architecture:** Introduce a simple dashboard shell structure that arranges the main chat panel and a right-hand sidebar in a responsive flex row, reusing existing components and state. All behavior (chat creation, uploads, research mode selection) stays the same; we only change layout and add a lightweight sidebar component for contextual steps.

**Tech Stack:** Nuxt 4, Vue 3 (`<script setup lang="ts">`), Tailwind CSS 4, daisyUI.

---

### Task 1: Create a dashboard sidebar component

**Files:**
- Create: `chat-app/app/components/DashboardSidebar.vue`

**Step 1:** Scaffold the component with `<script setup lang="ts">` and a minimal `props` interface that accepts the current research mode (string) and an optional title.

**Step 2:** In the template, render:
- A header row with a small uppercase label (e.g. "Steps") and a subtle pill showing the active mode.
- A simple vertical list of three static steps: "Wide Scan", "Paper Reading", "Deep Analysis", styled using existing Tailwind/daisyUI tokens (`bg-base-*`, `text-base-content/*`, rounded cards).

**Step 3:** Ensure the component is visually neutral and reuses existing theme colors without introducing new custom colors.

### Task 2: Reshape the dashboard layout to add the sidebar

**Files:**
- Modify: `chat-app/app/pages/dashboard.vue`

**Step 1:** Keep `DashboardNavbar` as-is at the top of the page.

**Step 2:** Wrap the current central prompt content in a flex row container that:
- Uses `flex`, `gap-*`, and responsive classes so that on large screens it shows two columns, and on small screens it gracefully stacks.
- Assigns the left area (`flex-[2]` or `lg:basis-2/3`) to the existing chat/prompt card and quick prompts.
- Assigns the right area (`flex-[1]` or `lg:basis-1/3`) to the new `DashboardSidebar` component.

**Step 3:** Move only container-level markup; do not change the logic for `createChat`, file upload, or the textarea bindings.

### Task 3: Wire research mode into the sidebar

**Files:**
- Modify: `chat-app/app/pages/dashboard.vue`
- Modify (if needed): `chat-app/app/components/DashboardSidebar.vue`

**Step 1:** Pass `mode.value` from `useResearchMode()` into `DashboardSidebar` as a prop, mapping it to a human-readable label (e.g. "Deep Research" / "Wide Research") for display.

**Step 2:** Optionally highlight one of the sidebar steps depending on the current mode in a subtle way (e.g. slightly stronger border on "Deep Analysis" when in deep mode); keep styling consistent with existing tokens.

### Task 4: Verify layout and responsiveness

**Files:**
- View only: `chat-app/app/pages/dashboard.vue`, `chat-app/app/components/DashboardSidebar.vue`

**Step 1:** Run the Nuxt dev server and open `/dashboard`.

**Step 2:** Check that:
- On desktop widths, the page shows a central chat panel and a right sidebar similar in structure to the reference screenshot.
- On tablet/mobile widths, the sidebar stacks below the chat panel without clipping or overflow.
- All buttons, file upload controls, and quick prompts remain fully functional.

**Step 3:** Adjust spacing classes (padding, margin, gap) as needed to keep the layout balanced without altering theme colors.

### Task 5: Run lint and type checks

**Files:**
- N/A (commands only)

**Step 1:** From `chat-app/`, run:

```bash
pnpm lint
pnpm typecheck
```

**Step 2:** If any lint or type errors reference the new files or imports, fix those by adjusting imports, props, or template structure.

