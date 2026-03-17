import type { ChatMode, ResearchMode } from '#shared/types/research'

const RESEARCH_MODES = [
    {
        value: 'deep',
        label: 'Deep Research',
        description: 'Follow a focused question through papers, evidence, and tradeoffs.',
        icon: 'lucide:scan-search',
        group: 'research'
    },
    {
        value: 'wide',
        label: 'Wide Research',
        description: 'Survey the landscape quickly across papers, approaches, and signals.',
        icon: 'lucide:network',
        group: 'research'
    },
    {
        value: 'read',
        label: 'Paper Reader',
        description: '3-pass methodology for structured paper review and critique.',
        icon: 'lucide:book-open',
        group: 'research'
    }
] as const

const IDEATE_MODE = {
    value: 'ideate',
    label: 'Ideate',
    description: 'Transform arXiv papers into product opportunities.',
    icon: 'lucide:lightbulb',
    group: 'ideate'
} as const

export function useResearchMode() {
    const mode = useCookie<ResearchMode>('research-mode', {
        default: () => 'deep'
    })

    const isIdeateMode = computed(() => mode.value === 'ideate')
    const isResearchMode = computed(() => mode.value !== 'ideate')

    const currentModeInfo = computed(() => {
        if (mode.value === 'ideate') return IDEATE_MODE
        return RESEARCH_MODES.find(m => m.value === mode.value) || RESEARCH_MODES[0]
    })

    return {
        mode,
        modes: [...RESEARCH_MODES, IDEATE_MODE],
        researchModes: RESEARCH_MODES,
        ideateMode: IDEATE_MODE,
        isIdeateMode,
        isResearchMode,
        currentModeInfo
    }
}

export type ResearchModeOption = typeof RESEARCH_MODES[number] | typeof IDEATE_MODE
