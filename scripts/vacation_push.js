const webpush = require("web-push");

const subscriptions = JSON.parse(process.env.VACATION_PUSH_SUBSCRIPTIONS_JSON || "[]");
const title = process.env.PUSH_TITLE || "Laxman Nepal Vacation";
const body = process.env.PUSH_BODY || "🇳🇵 Vacation reminder";
const url = process.env.PUSH_URL || "https://laxmannepal.com.np/vacation/";

if (!Array.isArray(subscriptions) || subscriptions.length === 0) {
  console.log("No push subscriptions configured.");
  process.exit(0);
}

webpush.setVapidDetails(process.env.VAPID_SUBJECT, process.env.VAPID_PUBLIC_KEY, process.env.VAPID_PRIVATE_KEY);

const payload = JSON.stringify({
  title, body, url,
  icon: "https://laxmannepal.com.np/assets/icons/icon-192.png",
  badge: "https://laxmannepal.com.np/assets/icons/icon-192.png",
  tag: "laxman-vacation"
});

(async () => {
  let delivered = 0;
  for (const sub of subscriptions) {
    try {
      await webpush.sendNotification(sub, payload, { TTL: 3600, urgency: "normal" });
      delivered++;
      console.log("Delivered:", sub.endpoint.slice(0, 80));
    } catch (err) {
      console.error("Push failed:", err.statusCode || "", err.message || err);
    }
  }
  console.log(JSON.stringify({ delivered, total: subscriptions.length }));
})();
