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
    const token = Deno.env.get("SLACK_BOT_TOKEN");
    if (!token) {
      return new Response(JSON.stringify({ error: "Missing SLACK_BOT_TOKEN secret" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const url = new URL(req.url);
    const includeTypes = url.searchParams.get("types") || "public_channel,private_channel";

    const resp = await fetch(
      `https://slack.com/api/conversations.list?limit=1000&types=${encodeURIComponent(includeTypes)}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    const data = await resp.json();

    if (!data?.ok) {
      console.error("slack-channels error", data);
      return new Response(
        JSON.stringify({ error: "Failed to fetch channels", details: data }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const channels = (data.channels || []).map((c: any) => ({
      id: c.id,
      name: c.name,
      is_private: c.is_private,
    }));

    return new Response(JSON.stringify({ ok: true, channels }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error in slack-channels:", error);
    return new Response(JSON.stringify({ error: error.message || String(error) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
