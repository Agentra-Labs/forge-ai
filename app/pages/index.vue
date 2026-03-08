<script setup lang="ts">
definePageMeta({
  layout: false
})

const { loggedIn, openInPopup } = useUserSession()

const modeCards = [
  {
    title: 'Deep Research',
    label: 'Focused analysis',
    description: 'Follow the strongest papers, compare methodology quality, and converge on a defensible recommendation.',
    icon: 'lucide:scan-search'
  },
  {
    title: 'Wide Research',
    label: 'Landscape mapping',
    description: 'Survey papers, labs, and solution families quickly before deciding where to go deep.',
    icon: 'lucide:network'
  }
]

const workflow = [
  {
    step: '01',
    title: 'Start with the real question',
    description: 'Bring in a product decision, architecture bet, or research target.'
  },
  {
    step: '02',
    title: 'Pick the research mode',
    description: 'Use wide mode for coverage or deep mode for evidence-led synthesis and tradeoff analysis.'
  },
  {
    step: '03',
    title: 'Move from evidence to action',
    description: 'Turn the result into implementation priorities, clearer bets, and next experiments.'
  }
]

const signals = [
  'Research-mode switching',
  'Paper-grounded answers',
  'Threaded workspace memory',
  'Evidence and tradeoff synthesis'
]

const outputRows = [
  { label: 'Question', value: 'Which planning architectures are holding up best for browser agents?' },
  { label: 'Mode', value: 'Deep Research' },
  { label: 'Coverage', value: 'Papers, methods, benchmarks, tradeoffs' },
  { label: 'Result', value: 'Clear recommendation with an evidence trail' }
]
</script>

<template>
  <div class="min-h-screen bg-transparent text-base-content">
    <header class="sticky top-0 z-30 border-b border-base-300/60 bg-base-100/65 backdrop-blur-2xl">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <NuxtLink to="/" class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10 text-primary shadow-sm">
            <Logo class="h-5 w-auto" />
          </div>
          <div>
            <p class="text-[11px] uppercase tracking-[0.28em] text-base-content/45">Forge</p>
            <p class="text-sm font-semibold">Research Agent</p>
          </div>
        </NuxtLink>

        <div class="flex items-center gap-2">
          <button
            v-if="!loggedIn"
            class="btn btn-ghost btn-sm rounded-full px-4"
            @click="openInPopup('/auth/github')"
          >
            Sign in
          </button>
          <NuxtLink to="/dashboard" class="btn btn-primary btn-sm rounded-full px-4">
            Open Dashboard
          </NuxtLink>
        </div>
      </div>
    </header>

    <main>
      <section class="relative overflow-hidden px-4 pb-16 pt-14 sm:px-6 lg:px-8 lg:pb-24 lg:pt-20">
        <div class="pointer-events-none absolute inset-0">
          <div class="absolute inset-0 opacity-40" style="background-image: linear-gradient(to right, color-mix(in oklab, oklch(var(--bc)) 10%, transparent) 1px, transparent 1px), linear-gradient(to bottom, color-mix(in oklab, oklch(var(--bc)) 10%, transparent) 1px, transparent 1px); background-size: 48px 48px;" />
          <div class="absolute left-[12%] top-12 h-72 w-72 rounded-full bg-primary/14 blur-3xl" />
          <div class="absolute right-[10%] top-24 h-80 w-80 rounded-full bg-info/10 blur-3xl" />
          <div class="absolute bottom-0 left-1/2 h-64 w-[42rem] -translate-x-1/2 rounded-full bg-secondary/8 blur-3xl" />
        </div>

        <div class="relative mx-auto grid max-w-7xl gap-10 lg:grid-cols-[minmax(0,1.1fr)_26rem] lg:items-center">
          <div class="space-y-8">
            <div class="inline-flex items-center gap-2 rounded-full border border-base-300/70 bg-base-100/58 px-3 py-1.5 text-xs text-base-content/60">
              <Icon name="lucide:sparkles" class="h-3.5 w-3.5 text-primary" />
              Research-grade AI workflow for Forge
            </div>

            <div class="space-y-5">
              <h1 class="max-w-5xl text-5xl font-semibold leading-[0.95] tracking-[-0.055em] sm:text-6xl lg:text-7xl">
                Research that resolves into product decisions.
              </h1>
              <p class="max-w-2xl text-base leading-7 text-base-content/64 sm:text-lg">
                Forge turns paper search, synthesis, and tradeoff analysis into one workspace for engineering and product teams.
              </p>
            </div>

            <div class="flex flex-wrap items-center gap-3">
              <NuxtLink to="/dashboard" class="btn btn-primary rounded-full px-5">
                Open Workspace
              </NuxtLink>
              <button
                v-if="!loggedIn"
                class="btn btn-outline rounded-full px-5"
                @click="openInPopup('/auth/github')"
              >
                Sign in with GitHub
              </button>
            </div>

            <div class="flex flex-wrap gap-2">
              <span
                v-for="signal in signals"
                :key="signal"
                class="rounded-full border border-base-300/70 bg-base-100/48 px-3 py-1.5 text-xs text-base-content/60"
              >
                {{ signal }}
              </span>
            </div>
          </div>

          <div class="rounded-[2rem] border border-base-300/70 bg-base-100/54 p-4 shadow-2xl shadow-neutral/10 backdrop-blur-2xl">
            <div class="rounded-[1.6rem] border border-base-300/70 bg-base-200/72 p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-[11px] uppercase tracking-[0.28em] text-base-content/45">Live System</p>
                  <p class="mt-1 text-sm font-medium">Research output shape</p>
                </div>
                <div class="rounded-full border border-base-300/70 bg-base-100/70 px-3 py-1 text-xs text-base-content/58">
                  Forge vNext
                </div>
              </div>

              <div class="mt-4 space-y-2">
                <div
                  v-for="row in outputRows"
                  :key="row.label"
                  class="flex items-start justify-between gap-4 rounded-[1.1rem] border border-base-300/65 bg-base-100/72 px-3 py-3"
                >
                  <span class="text-xs uppercase tracking-[0.18em] text-base-content/45">{{ row.label }}</span>
                  <span class="max-w-[15rem] text-right text-sm text-base-content/80">{{ row.value }}</span>
                </div>
              </div>

              <div class="mt-4 rounded-[1.25rem] border border-primary/18 bg-primary/8 p-4">
                <div class="flex items-start gap-3">
                  <div class="mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl bg-primary/12 text-primary">
                    <Icon name="lucide:file-search-2" class="h-4 w-4" />
                  </div>
                  <div>
                    <p class="text-sm font-medium">Evidence-first output</p>
                    <p class="mt-1 text-sm leading-6 text-base-content/62">
                      Outputs are framed around comparison, uncertainty, tradeoffs, and next steps.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="px-4 pb-10 sm:px-6 lg:px-8">
        <div class="mx-auto grid max-w-7xl gap-4 lg:grid-cols-2">
          <div
            v-for="card in modeCards"
            :key="card.title"
            class="rounded-[1.75rem] border border-base-300/70 bg-base-100/52 p-5 shadow-xl shadow-neutral/5 backdrop-blur-xl"
          >
            <div class="flex items-start gap-4">
              <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-base-200/85">
                <Icon :name="card.icon" class="h-5 w-5 text-primary" />
              </div>
              <div>
                <p class="text-[11px] uppercase tracking-[0.28em] text-base-content/45">{{ card.label }}</p>
                <h2 class="mt-2 text-2xl font-semibold tracking-[-0.03em]">{{ card.title }}</h2>
                <p class="mt-2 max-w-xl text-sm leading-6 text-base-content/62">{{ card.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="px-4 pb-20 pt-6 sm:px-6 lg:px-8">
        <div class="mx-auto max-w-7xl rounded-[2rem] border border-base-300/70 bg-base-100/48 p-5 shadow-2xl shadow-neutral/5 backdrop-blur-2xl sm:p-6 lg:p-8">
          <div class="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p class="text-[11px] uppercase tracking-[0.28em] text-base-content/45">Workflow</p>
              <h2 class="mt-2 text-3xl font-semibold tracking-[-0.04em]">
                From open question to clear direction.
              </h2>
            </div>
            <NuxtLink to="/dashboard" class="btn btn-ghost rounded-full px-4">
              Go to workspace
            </NuxtLink>
          </div>

          <div class="grid gap-4 lg:grid-cols-3">
            <div
              v-for="item in workflow"
              :key="item.step"
              class="rounded-[1.5rem] border border-base-300/70 bg-base-100/72 p-5"
            >
              <p class="text-[11px] uppercase tracking-[0.28em] text-primary/80">{{ item.step }}</p>
              <h3 class="mt-3 text-xl font-semibold tracking-[-0.03em]">{{ item.title }}</h3>
              <p class="mt-2 text-sm leading-6 text-base-content/62">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
