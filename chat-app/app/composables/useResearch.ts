/**
 * Composable for running research queries against the Agno backend.
 *
 * Handles SSE streaming, reactive state management, and error handling.
 * Vue components consume: `const { run, steps, content, isRunning } = useResearch()`
 */

import type { ResearchMode } from '#shared/types/research'

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
    const currentStep = ref<string>('')
    const abortController = ref<AbortController | null>(null)

    async function run(params: {
        goal: string
        mode?: ResearchMode
        primary_url?: string
        secondary_url?: string
        seed_arxiv_id?: string
        keywords?: string[]
        workflow?: string
    }) {
        // Reset state
        isRunning.value = true
        error.value = null
        steps.value = []
        content.value = ''
        currentStep.value = ''

        // Create abort controller for cancellation
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
                const errText = await response.text()
                throw new Error(`Research request failed: ${errText}`)
            }

            const reader = response.body?.getReader()
            if (!reader) {
                throw new Error('No response stream available')
            }

            const decoder = new TextDecoder()
            let buffer = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n')
                buffer = lines.pop() || ''

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.slice(6).trim()
                        if (!dataStr || dataStr === '[DONE]') continue

                        try {
                            const data = JSON.parse(dataStr)
                            handleSSEEvent(data)
                        } catch {
                            // Append raw text content
                            content.value += dataStr
                        }
                    } else if (line.startsWith('event: ')) {
                        // Some SSE formats use separate event: lines
                        currentStep.value = line.slice(7).trim()
                    }
                }
            }

            isRunning.value = false
            options.onComplete?.(content.value)
        } catch (err: any) {
            if (err.name === 'AbortError') {
                // User cancelled
                isRunning.value = false
                return
            }
            error.value = err.message || 'Research request failed'
            isRunning.value = false
            options.onError?.(error.value!)
        }
    }

    function handleSSEEvent(data: any) {
        // Handle different event types from agno
        if (data.event === 'RunStarted' || data.run_id) {
            // Run started
            currentStep.value = 'Starting research...'
        } else if (data.event === 'WorkflowStarted' || data.workflow_id) {
            currentStep.value = data.step_name || 'Starting workflow...'
            steps.value.push({
                name: data.step_name || 'Step',
                status: 'running',
                content: ''
            })
        } else if (data.event === 'WorkflowStepCompleted') {
            // Mark current step as completed
            const step = steps.value.find(s => s.name === data.step_name)
            if (step) {
                step.status = 'completed'
                step.content = data.content || ''
            }
            options.onStep?.({
                name: data.step_name,
                status: 'completed',
                content: data.content || ''
            })
        } else if (data.content) {
            // Streaming content
            content.value += data.content
        } else if (data.event === 'RunResponse') {
            content.value += data.data?.content || ''
        } else if (data.event === 'RunCompleted' || data.event === 'WorkflowCompleted') {
            if (data.data?.content || data.content) {
                content.value = data.data?.content || data.content || content.value
            }
        } else if (data.event === 'RunError') {
            error.value = data.data?.message || data.message || 'Unknown error'
        }
    }

    function stop() {
        abortController.value?.abort()
        isRunning.value = false
    }

    function reset() {
        isRunning.value = false
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
