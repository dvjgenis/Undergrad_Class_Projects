# Slack human-in-the-loop replies

You can have the AI help you reply to Slack mentions **with your approval before anything is sent**.

## How to use it

1. **Trigger in Cursor**  
   Ask in chat, for example:
   - “Check my Slack mentions”
   - “Reply to my Slack pings” / “Handle my @-mentions in Slack”
   - “Get my Slack mentions and draft replies”

2. **What the AI does**
   - Lists channels and fetches recent channel history.
   - Finds messages where you’re mentioned (messages containing `<@...>`).
   - **Drafts** replies only (does not send).
   - Shows you each draft (channel, context, proposed reply).

3. **You approve**
   - Say which drafts to send: e.g. “Send 1 and 3”, “Approve all”, “Edit #2 then send”, or “Don’t send any”.
   - The AI will **only** call Slack to send messages you explicitly approve.

The rule that enforces this is in `.cursor/rules/slack-human-in-the-loop.mdc`.

## Making it easier to trigger

- **Quick phrase:** Use a short phrase you like, e.g. “Slack mentions” or “check Slack and draft replies,” and the AI will follow the same workflow.
- **Optional: your Slack user ID**  
  If you tell the AI your Slack user ID once (e.g. `U01234ABCD`), it can filter to only messages that mention you. You can find your ID in Slack (profile → “Copy member ID”) or in the Slack API.

## “Automatic” vs “when I ask”

- **When you ask (current setup):**  
  Nothing is sent until you ask in Cursor and then approve. Slack does not notify Cursor when you’re mentioned.

- **Fully automatic (Slack notifies something first):**  
  That would require a separate piece of infrastructure: e.g. a Slack app using the Events API, a small server that receives “user mentioned” events and stores “pending replies,” and then a way for you to open those in Cursor (or another UI) and approve. The human-in-the-loop rule still applies: the AI would only send what you approve.

Summary: **you see the messages and drafts first, and you approve before the AI sends anything.**
