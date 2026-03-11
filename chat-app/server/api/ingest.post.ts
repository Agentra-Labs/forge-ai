import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  // Read request body
  const body = await readBody(event)

  // Get agent URL from environment variables
  const agentUrl = process.env.AGENT_URL || 'http://localhost:7777'

  try {
    // Forward request to research agent
    const response = await fetch(`${agentUrl}/ingest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })

    // Check if response is successful
    if (!response.ok) {
      throw new Error(`Agent API error: ${response.status}`)
    }

    // Return the response data
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error starting ingestion:', error)
    return {
      error: 'Failed to start ingestion process'
    }
  }
})
