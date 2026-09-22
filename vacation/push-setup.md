# V11 Background Push Setup

## Generate VAPID keys

Run:

~~~bash
npx web-push generate-vapid-keys --json
~~~

Keep the private key secret.

## Add GitHub Actions secrets

Repository → Settings → Secrets and variables → Actions → New repository secret.

Create:

- VAPID_SUBJECT = mailto:YOUR-EMAIL
- VAPID_PUBLIC_KEY = generated public key
- VAPID_PRIVATE_KEY = generated private key
- VACATION_PUSH_SUBSCRIPTIONS_JSON = PushSubscription JSON copied from the Vacation page

## Schedule

GitHub Actions sends at 08:00, 13:00 and 20:00 Kuwait time.

## Test

GitHub → Actions → Vacation Background Push → Run workflow.

Do not commit VAPID private keys or subscription secrets.
