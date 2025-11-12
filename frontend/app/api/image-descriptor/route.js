/**
 * Next.js API Route: Image Descriptor Proxy
 * 
 * This route proxies image upload requests to the backend's /imageDescriptor endpoint.
 * It handles FormData uploads and streams the response back to the client.
 * 
 * Environment variables:
 * - INTERNAL_API_URL: Internal Kubernetes service URL (staging/prod)
 * - NEXT_PUBLIC_API_BASE: External URL (fallback, causes SSO issues in Kanopy)
 * - Hardcoded fallback: http://localhost:8080 (local development)
 */

export async function POST(request) {
  try {
    // Get the FormData from the request
    const formData = await request.formData();
    
    // Determine backend URL based on environment
    const backendUrl = process.env.INTERNAL_API_URL || 
                       process.env.NEXT_PUBLIC_API_BASE || 
                       "http://localhost:8080";

    console.log(`[Image Descriptor] Proxying request to: ${backendUrl}/imageDescriptor`);

    // Forward the request to the backend
    const response = await fetch(`${backendUrl}/imageDescriptor`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header - let fetch handle it for FormData
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      console.error(`[Image Descriptor] Backend error: ${response.status} - ${errorText}`);
      return new Response(
        JSON.stringify({ 
          error: 'Failed to process image', 
          status: response.status,
          details: errorText 
        }), 
        {
          status: response.status,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Stream the response back to the client
    // The backend returns a streaming text response
    return new Response(response.body, {
      status: response.status,
      headers: {
        'Content-Type': 'text/plain',
        'Transfer-Encoding': 'chunked',
      }
    });

  } catch (error) {
    console.error('[Image Descriptor] Proxy error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Failed to connect to backend', 
        details: error.message 
      }), 
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}
