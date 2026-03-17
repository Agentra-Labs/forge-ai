import type { ResearchMode } from '#shared/types/research'
import { consumeSseMessages, flushSseMessages, normalizeBackendMessage } from '#shared/utils/backend'

interface ResearchStep {
  name: string
  status: 'running' | 'completed' | 'failed'
  content: string
}

interface UseResearchOptions {
  onStep?: (step: ResearchStep) => void
  onComplete?: (content: string) => void
  onError?: (error: string) => void
}

export function useResearch(options: UseResearchOptions = {}) {
  const isRunning = ref(false)
  const error = ref<string | null>(null)
  const steps = ref<ResearchStep[]>([])
  const content = ref('')
  const currentStep = ref('')
  const abortController = ref<AbortController | null>(null)
  let activeRunId = 0

  function upsertStep(name: string, status: ResearchStep['status'], stepContent = '') {
    const existing = steps.value.find(step => step.name === name)
    if (existing) {
      existing.status = status
      if (stepContent) {
        existing.content = stepContent
      }
      return existing
    }

    const nextStep = { name, status, content: stepContent }
    steps.value.push(nextStep)
    return nextStep
  }

  function handleNormalizedMessage(message: ReturnType<typeof normalizeBackendMessage>) {
    if (message.error) {
      error.value = message.error
      options.onError?.(message.error)
      return
    }

    if (message.done) {
      options.onComplete?.(content.value)
      return
    }

    if (message.content) {
      content.value += message.content
    }
  }

  async function run(params: {
    goal: string
    mode?: ResearchMode
    primary_url?: string
    secondary_url?: string
    seed_arxiv_id?: string
    keywords?: string[]
    workflow?: string
  }) {
    stop()

    const runId = ++activeRunId
    isRunning.value = true
    error.value = null
    steps.value = []
    content.value = ''
    currentStep.value = ''
    abortController.value = new AbortController()

    try {
      const { csrf, headerName } = useCsrf()

      const response = await fetch('/api/research/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          [headerName]: csrf,
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({
          goal: params.goal,
          mode: params.mode || 'deep',
          primary_url: params.primary_url,
          secondary_url: params.secondary_url,
          seed_arxiv_id: params.seed_arxiv_id,
          keywords: params.keywords,
          workflow: params.workflow
        }),
        signal: abortController.value.signal
      })

      if (!response.ok) {
        throw new Error(await response.text())
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response stream available')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          break
        }

        if (runId !== activeRunId) {
          return
        }

        const parsed = consumeSseMessages(buffer, decoder.decode(value, { stream: true }))
        buffer = parsed.buffer

        for (const message of parsed.messages) {
          handleNormalizedMessage(normalizeBackendMessage(message))
        }
      }

      for (const message of flushSseMessages(buffer)) {
        handleNormalizedMessage(normalizeBackendMessage(message))
      }

      if (runId === activeRunId) {
        options.onComplete?.(content.value)
      }
    } catch (err) {
      if ((err as Error)?.name === 'AbortError') {
        return
      }

      const message = err instanceof Error ? err.message : 'Research request failed'
      const runningStep = [...steps.value].reverse().find(step => step.status === 'running')
      if (runningStep) {
        runningStep.status = 'failed'
      }
      error.value = message
      options.onError?.(message)
    } finally {
      if (runId === activeRunId) {
        isRunning.value = false
        abortController.value = null
      }
    }
  }

  function stop() {
    abortController.value?.abort()
    abortController.value = null
    isRunning.value = false
  }

  function reset() {
    stop()
    error.value = null
    steps.value = []
    content.value = ''
    currentStep.value = ''
  }

  return {
    run,
    stop,
    reset,
    isRunning: readonly(isRunning),
    error: readonly(error),
    steps: readonly(steps),
    content: readonly(content),
    currentStep: readonly(currentStep)
  }
}
