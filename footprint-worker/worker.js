export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    if (request.method === "OPTIONS") return new Response(null, {headers:cors});
    const url = new URL(request.url);
    if (url.pathname !== "/api/footprint" || request.method !== "POST") {
      return new Response(JSON.stringify({error:"Not found"}), {status:404,headers:{"Content-Type":"application/json",...cors}});
    }
    try {
      const body = await request.json();
      const type = String(body.type || "").toLowerCase();
      const value = String(body.value || "").trim();
      if (!["email","username","url"].includes(type) || !value || value.length > 320) {
        return json({error:"Invalid input"},400,cors);
      }
      if (type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        return json({error:"Invalid email address"},400,cors);
      }
      if (type === "url") {
        try { new URL(value); } catch { return json({error:"Invalid URL"},400,cors); }
      }

      const result = {
        query:{type,value},
        summary:{message:"Scan completed using configured public/security providers.",items:[]},
        accounts:[], breaches:[], security:[], timeline:[]
      };

      if (type === "username") {
        const gh = await githubUsername(value);
        if (gh.length) {
          for (const u of gh.slice(0,8)) {
            result.accounts.push({
              name:"GitHub · @"+(u.login || value),
              detail:u.html_url || "Public GitHub profile",
              url:u.html_url,
              status:"FOUND"
            });
            result.timeline.push({
              date:u.created_at ? u.created_at.slice(0,10) : "Undated",
              title:"GitHub public profile found",
              detail:u.html_url || "GitHub",
              source:"GitHub"
            });
          }
        }
        result.summary.items.push({
          title:"GitHub public search",
          detail:gh.length ? gh.length+" public profile result(s) returned." : "No public GitHub result returned.",
          status:gh.length ? "FOUND" : "NOT FOUND"
        });
      }

      if (type === "email" && env.HIBP_API_KEY) {
        const breaches = await hibp(value, env.HIBP_API_KEY);
        for (const b of breaches.slice(0,25)) {
          const classes = Array.isArray(b.DataClasses) ? b.DataClasses.join(", ") : "Exposure metadata";
          result.breaches.push({
            name:b.Name || b.Title || "Known breach",
            detail:(b.BreachDate || "Undated")+" · Exposed classes: "+classes,
            status:"EXPOSED"
          });
          result.timeline.push({
            date:b.BreachDate || "Undated",
            title:(b.Title || b.Name || "Known breach")+" exposure",
            detail:classes,
            source:"Have I Been Pwned"
          });
        }
        result.summary.items.push({
          title:"Have I Been Pwned",
          detail:breaches.length ? breaches.length+" known breach record(s) returned." : "No breach records returned.",
          status:breaches.length ? "EXPOSED" : "CLEAR"
        });
        if (breaches.some(b => (b.DataClasses||[]).some(x => /password|credential/i.test(x)))) {
          result.security.push({title:"Password-related exposure",detail:"At least one returned breach lists password-related data classes. No password is displayed.",status:"EXPOSED"});
        }
      } else if (type === "email") {
        result.summary.items.push({
          title:"Breach provider",
          detail:"HIBP API key is not configured on the Worker.",
          status:"PENDING"
        });
      }

      if (type === "email") {
        const gh = await githubUsername(value);
        for (const u of gh.slice(0,5)) {
          result.accounts.push({
            name:"Possible GitHub public match · @"+u.login,
            detail:"Public GitHub search result; this is not identity proof.",
            url:u.html_url,
            status:"POSSIBLE"
          });
        }
        if (gh.length) result.summary.items.push({
          title:"GitHub public search",
          detail:gh.length+" possible public result(s). Verify manually before treating as an association.",
          status:"POSSIBLE"
        });
      }

      if (type === "url") {
        result.security.push({
          title:"URL syntax",
          detail:"The submitted URL is syntactically valid. Reputation checks require an optional provider such as Google Web Risk.",
          status:"READY"
        });
        result.timeline.push({
          date:new Date().toISOString().slice(0,10),
          title:"URL submitted for analysis",
          detail:value,
          source:"Laxman Digital Footprint"
        });
      }

      result.timeline.sort((a,b)=>String(a.date).localeCompare(String(b.date)));
      return json(result,200,cors);
    } catch (err) {
      return json({error:"Scan failed",message:String(err?.message || err)},500,cors);
    }
  }
};

async function githubUsername(query) {
  const url = "https://api.github.com/search/users?q="+encodeURIComponent(query)+"&per_page=8";
  const r = await fetch(url,{headers:{"Accept":"application/vnd.github+json","User-Agent":"Laxman-Digital-Footprint"}});
  if (!r.ok) return [];
  const d = await r.json();
  return Array.isArray(d.items) ? d.items : [];
}

async function hibp(email,key) {
  const url = "https://haveibeenpwned.com/api/v3/breachedaccount/"+encodeURIComponent(email)+"?truncateResponse=false";
  const r = await fetch(url,{headers:{
    "hibp-api-key":key,
    "user-agent":"Laxman-Digital-Footprint/1.0"
  }});
  if (r.status === 404) return [];
  if (!r.ok) throw new Error("HIBP returned "+r.status);
  const d = await r.json();
  return Array.isArray(d) ? d : [];
}

function json(data,status,extra={}) {
  return new Response(JSON.stringify(data),{
    status,
    headers:{"Content-Type":"application/json","Cache-Control":"no-store",...extra}
  });
}
