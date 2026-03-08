export type ResearchMode = 'deep' | 'wide' | 'chained'

const RESEARCH_MODES = [
    {
        value: 'deep',
        label: 'Deep Research',
        description: 'Follow a focused question through papers, evidence, and tradeoffs.',
        icon: 'lucide:scan-search'
    },
    {
        value: 'wide',
        label: 'Wide Research',
        description: 'Survey the landscape quickly across papers, approaches, and signals.',
        icon: 'lucide:network'
    },
    {
        value: 'chained',
        label: 'Chained Research',
        description: 'Full pipeline: wide scan → 3-pass reading → deep synthesis.',
        icon: 'lucide:workflow'
    }
] as const

export function useResearchMode() {
    const mode = useCookie<ResearchMode>('research-mode', {
        default: () => 'deep'
    })

    return {
        mode,
        modes: RESEARCH_MODES
    }
}
