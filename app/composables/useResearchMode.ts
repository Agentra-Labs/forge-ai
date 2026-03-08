export type ResearchMode = 'deep' | 'wide'

const RESEARCH_MODES = [
  {
    value: 'deep',
    label: 'Deep Research',
    description: 'Follow a focused question through papers, evidence, and tradeoffs.'
  },
  {
    value: 'wide',
    label: 'Wide Research',
    description: 'Survey the landscape quickly across papers, approaches, and signals.'
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
