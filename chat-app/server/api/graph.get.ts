import { defineEventHandler, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  // Get query parameters
  const query = getQuery(event)
  const space = query.space || 'default'

  // Prepare request to Supermemory API
  const body = {
    page: query.page || 1,
    limit: query.limit || 20,
    sort: query.sort || 'created',
    order: query.order || 'desc'
  }

  try {
    // Forward request to Supermemory API
    const response = await fetch(`https://api.supermemory.ai/graph?space=${space}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.SUPERMEMORY_API_KEY}`
      },
      body: JSON.stringify(body)
    })

    // Check if response is successful
    if (!response.ok) {
      throw new Error(`Supermemory API error: ${response.status}`)
    }

    // Return the response data
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching graph data:', error)
    return {
      statusCode: 500,
      message: 'Failed to fetch graph data'
    }
  }
})
