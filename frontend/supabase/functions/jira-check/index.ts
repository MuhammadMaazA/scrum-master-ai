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

    if (!baseUrl || !username || !apiToken) {
      return new Response(JSON.stringify({ error: "Missing JIRA_URL/JIRA_USERNAME/JIRA_API_TOKEN secrets" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const auth = btoa(`${username}:${apiToken}`);

    const resp = await fetch(`${baseUrl}/rest/api/3/myself`, {
      headers: {
        Authorization: `Basic ${auth}`,
        Accept: "application/json",
      },
    });

    if (!resp.ok) {
      const text = await resp.text();
      console.error("jira-check error", resp.status, text);
      return new Response(JSON.stringify({ error: `Jira check failed: ${resp.status}`, details: text }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const data = await resp.json();
    console.log("jira-check response", data);

    return new Response(JSON.stringify({
      ok: true,
      accountId: data.accountId,
      displayName: data.displayName,
      timeZone: data.timeZone,
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in jira-check:", error);
    return new Response(JSON.stringify({ error: error.message || String(error) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
