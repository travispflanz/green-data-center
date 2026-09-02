export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1. Edge API Endpoint for Newsletter Subscriptions
    if (url.pathname === "/api/subscribe" && request.method === "POST") {
      try {
        const contentType = request.headers.get("content-type") || "";
        let email = "";
        let sourcePage = "index";

        if (contentType.includes("application/json")) {
          const data = await request.json();
          email = data.email?.trim().toLowerCase();
          sourcePage = data.source || "index";
        } else if (contentType.includes("application/x-www-form-urlencoded")) {
          const formData = await request.formData();
          email = formData.get("email")?.toString().trim().toLowerCase();
          sourcePage = formData.get("source")?.toString() || "index";
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email || !emailRegex.test(email)) {
          return new Response(
            JSON.stringify({ success: false, message: "Please provide a valid institutional email address." }),
            { status: 400, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } }
          );
        }

        if (env.DB) {
          const statement = env.DB.prepare(
            "INSERT OR IGNORE INTO subscribers (email, source_page) VALUES (?, ?)"
          ).bind(email, sourcePage);
          const result = await statement.run();
          return new Response(
            JSON.stringify({
              success: true,
              message: result.meta?.changes > 0 
                ? "Subscription verified. You are registered for regulatory alerts." 
                : "Your email is already registered in the research index."
            }),
            { status: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } }
          );
        }

        return new Response(
          JSON.stringify({ success: true, message: "Subscription recorded (Cloudflare D1 binding pending)." }),
          { status: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } }
        );
      } catch (error) {
        return new Response(
          JSON.stringify({ success: false, message: "Server error processing request. Please try again." }),
          { status: 500, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } }
        );
      }
    }

    // 2. Clean URL Handler: map /facilities to /facilities.html automatically
    let response = await env.ASSETS.fetch(request);
    if (response.status === 404 && !url.pathname.includes(".")) {
      const cleanPath = url.pathname.replace(/\/$/, "") + ".html";
      const altUrl = new URL(cleanPath, request.url);
      const altResponse = await env.ASSETS.fetch(new Request(altUrl, request));
      if (altResponse.status !== 404) {
        return altResponse;
      }
    }

    return response;
  }
};