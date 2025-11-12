/**
 * Next.js API Route: Run Agent Proxy
 * 
 * This route proxies agent execution requests to the backend's /runAgent endpoint.
 * It triggers the LangGraph agent workflow and returns the claim document.
 * 
 * Environment variables:
 * - INTERNAL_API_URL: Internal Kubernetes service URL (staging/prod)
 * - NEXT_PUBLIC_API_BASE: External URL (fallback, causes SSO issues in Kanopy)
 * - Hardcoded fallback: http://localhost:8080 (local development)
 */

export async function POST(request) {
  try {
    // Determine backend URL based on environment
    const backendUrl = process.env.INTERNAL_API_URL || 
                       process.env.NEXT_PUBLIC_API_BASE || 
                       "http://localhost:8080";

    console.log(`[Run Agent] Proxying request to: ${backendUrl}/runAgent`);

    // Forward the request to the backend
    const response = await fetch(`${backendUrl}/runAgent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ 
        detail: 'Agent processing failed' 
      }));
      console.error(`[Run Agent] Backend error: ${response.status}`, errorData);
      return Response.json(errorData, { status: response.status });
    }

    // Parse and return the claim document
    const data = await response.json();
    console.log('[Run Agent] Successfully retrieved claim document');
    return Response.json(data);

  } catch (error) {
    console.error('[Run Agent] Proxy error:', error);
    return Response.json(
      { 
        error: 'Failed to connect to backend', 
        details: error.message 
      }, 
      { status: 500 }
    );
  }
}
