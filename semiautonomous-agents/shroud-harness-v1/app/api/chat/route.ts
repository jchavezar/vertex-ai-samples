import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { messages } = await req.json();
  const token = process.env.GCLOUD_TOKEN;

  if (!token) {
    console.error(">>> [API Error] GCLOUD_TOKEN is missing on the server.");
    return NextResponse.json({ error: "GCLOUD_TOKEN is missing. Please run ./start_harness.sh" }, { status: 500 });
  }

  const endpoint = "https://aiplatform.googleapis.com/v1/projects/vtxdemos/locations/global/publishers/anthropic/models/claude-sonnet-4-6:rawPredict";

  console.log(`>>> [API] Sending request to Vertex AI... (Token Length: ${token.length})`);

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({
        anthropic_version: "vertex-2023-10-16",
        messages: messages.map((m: any) => ({
          role: m.role,
          content: [{ type: "text", text: m.content }]
        })),
        max_tokens: 4096,
        temperature: 1,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`>>> [API Error] Vertex AI Response (${response.status}):`, errorText);
      return NextResponse.json({ 
        error: `API Error: ${response.statusText}`, 
        details: errorText 
      }, { status: response.status });
    }

    return new NextResponse(response.body, {
      headers: { "Content-Type": "text/event-stream" },
    });
  } catch (error: any) {
    console.error(">>> [API Error] Prediction failed:", error.message);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
