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

    const { channel, text } = await req.json();
    if (!channel || !text) {
      return new Response(JSON.stringify({ error: "channel and text are required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const raw = String(channel);
    const nameOrId = raw.startsWith("#") ? raw.slice(1) : raw;

    let channelId = nameOrId;
    // If it does not look like an ID, try to resolve by name
    if (!/^([CDG])[A-Z0-9]+$/i.test(nameOrId)) {
      const listResp = await fetch(
        "https://slack.com/api/conversations.list?limit=1000&types=public_channel,private_channel",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const listData = await listResp.json();
      if (listData?.ok) {
        const match = (listData.channels || []).find(
          (c: any) => c?.name === nameOrId || c?.name_normalized === nameOrId
        );
        if (match?.id) channelId = match.id;
      }
    }

    const postResp = await fetch("https://slack.com/api/chat.postMessage", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ channel: channelId, text }),
    });

    let data = await postResp.json();
    if (!data?.ok && data?.error === "not_in_channel") {
      // Attempt to join the channel then retry once
      const joinResp = await fetch("https://slack.com/api/conversations.join", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ channel: channelId }),
      });
      const joinData = await joinResp.json();
      if (joinData?.ok) {
        const retryResp = await fetch("https://slack.com/api/chat.postMessage", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ channel: channelId, text }),
        });
        data = await retryResp.json();
      } else {
        console.error("slack-post join error", joinData);
        return new Response(JSON.stringify({
          error: "Slack post failed",
          hint: "Invite the bot to the channel with /invite @your_bot or add it via channel members.",
          details: joinData,
        }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
    }
    if (!data?.ok) {
      console.error("slack-post error", data);
      return new Response(JSON.stringify({ error: "Slack post failed", details: data }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    console.log("slack-post success", data);
    return new Response(
      JSON.stringify({ ok: true, channel: data.channel, ts: data.ts }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error in slack-post:", error);
    return new Response(JSON.stringify({ error: error.message || String(error) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
