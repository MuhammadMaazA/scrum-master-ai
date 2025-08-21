import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const baseUrl = Deno.env.get("JIRA_URL");
    const username = Deno.env.get("JIRA_USERNAME");
    const apiToken = Deno.env.get("JIRA_API_TOKEN");
    const projectKey = Deno.env.get("JIRA_PROJECT_KEY");

    if (!baseUrl || !username || !apiToken || !projectKey) {
      return new Response(
        JSON.stringify({ error: "Missing JIRA_URL/JIRA_USERNAME/JIRA_API_TOKEN/JIRA_PROJECT_KEY secrets" }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const { summary, description, issueType } = await req.json();
    if (!summary) {
      return new Response(JSON.stringify({ error: "summary is required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const auth = btoa(`${username}:${apiToken}`);

    const payload = {
      fields: {
        project: { key: projectKey },
        summary,
        issuetype: { name: issueType || "Task" },
        description: {
          type: "doc",
          version: 1,
          content: [
            {
              type: "paragraph",
              content: [
                { type: "text", text: description || "" },
              ],
            },
          ],
        },
      },
    };

    const resp = await fetch(`${baseUrl}/rest/api/3/issue`, {
      method: "POST",
      headers: {
        Authorization: `Basic ${auth}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const text = await resp.text();
    if (!resp.ok) {
      console.error("jira-create-issue error", resp.status, text);
      return new Response(
        JSON.stringify({ error: `Create issue failed: ${resp.status}`, details: text }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const data = JSON.parse(text);
    console.log("jira-create-issue success", data);

    return new Response(
      JSON.stringify({ ok: true, id: data.id, key: data.key, self: data.self }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error in jira-create-issue:", error);
    return new Response(JSON.stringify({ error: error.message || String(error) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
