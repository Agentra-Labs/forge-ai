/**
 * TypeScript interfaces mirroring the Python research agent models.
 * Single source of truth for the contract between frontend and backend.
 */

export type ResearchMode = 'deep' | 'wide' | 'chained'

export interface ResearchQuery {
    goal: string
    primary_url?: string
    secondary_url?: string
    seed_arxiv_id?: string
    keywords?: string[]
    mode: ResearchMode
}

export interface PaperMeta {
    arxiv_id?: string
    ss_id?: string
    title: string
    authors: string[]
    abstract: string
    url: string
    year?: number
    citation_count?: number
    venue?: string
}

export interface PaperReview extends PaperMeta {
    relevance_score: number
    techniques: string[]
    claims: string[]
    limitations: string[]
    methods: string[]
    key_results: string[]
    review_pass: 1 | 2 | 3
    code_url?: string
    critique?: string
}

export interface ResearchStep {
    step_name: string
    step_number: number
    status: 'running' | 'completed' | 'failed'
    content?: string
}

export interface ResearchSession {
    session_id: string
    workflow_id?: string
    agent_id?: string
    created_at: string
    steps: ResearchStep[]
    papers: PaperReview[]
    synthesis?: string
}

/** SSE event types from the agno backend */
export type AgnoSSEEvent =
    | { event: 'RunStarted', data: { run_id: string } }
    | { event: 'RunResponse', data: { content: string, content_type: string } }
    | { event: 'RunCompleted', data: { content: string } }
    | { event: 'RunError', data: { message: string } }
    | { event: 'WorkflowStarted', data: { workflow_id: string, step_name: string } }
    | { event: 'WorkflowStepCompleted', data: { step_name: string, content: string } }
    | { event: 'WorkflowCompleted', data: { content: string } }
