/**
 * TypeScript interfaces for the nova-forge backend.
 * Single source of truth for the contract between frontend and backend.
 */

export type ChatMode = 'deep' | 'wide'
export type ResearchMode = ChatMode | 'builder' | 'read' | 'ideate'

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

export type MessagePart = 
    | { type: 'text', text: string }
    | { type: 'reasoning', text: string, state: 'running' | 'done' }
    | { type: 'file', url: string, mediaType: string }
    | { type: 'paper', paper: PaperReview }
    | { type: 'tool-weather', invocation: any }
    | { type: 'tool-chart', invocation: any }

export interface ChatMessage {
    id: string
    role: 'user' | 'assistant' | 'system'
    content?: string
    parts: MessagePart[]
    createdAt?: string | Date
}

/** Ideate job status from GET /ideate/{job_id} */
export interface IdeateJob {
    status: 'queued' | 'running' | 'completed' | 'failed'
    result: string | null
    error: string | null
}

/** Ideate job creation response from POST /ideate */
export interface IdeateJobStart {
    job_id: string
    arxiv_id: string
    status: 'queued'
}

/** Pipeline phase info for visualization */
export interface PipelinePhase {
    id: string
    name: string
    description: string
    status: 'pending' | 'running' | 'completed' | 'failed'
    duration?: number
}
