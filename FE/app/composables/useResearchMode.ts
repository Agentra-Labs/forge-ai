import type { ChatMode } from '#shared/types/research'

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
    }
] as const

export function useResearchMode() {
    const mode = useCookie<ChatMode>('research-mode', {
        default: () => 'deep'
    })

    return {
        mode,
        modes: RESEARCH_MODES
    }
}
