---
name: stack-finder
description: Finds the tools a company uses (CRM, email, support, AI accounts, sales tools) from public records only, with proof for every tool, then writes a pre-call brief. Use when the user types /stack-finder, gives one or more company domains, or asks what tools/stack/CRM a prospect uses.
---

# Stack Finder

You give it a company domain. It returns every tool that company uses that shows up in public records, the proof for each one, and a short brief for your next call.

## Sources (public only)

1. **DNS records** of the domain
   - SPF (the list of services allowed to send email for the company): Salesforce, HubSpot, Zendesk, Marketo, SendGrid...
   - Ownership codes that software vendors ask companies to add: OpenAI, Anthropic, Atlassian, DocuSign, Slack, Cursor...
   - MX (who hosts their email): Google Workspace, Microsoft, Proofpoint...
2. **Homepage scripts**: HubSpot, Intercom, Chili Piper, 6sense, Segment...
3. **Public job boards** (Greenhouse, Lever, Ashby): tools named in their job posts, with the exact line.

Nothing from LinkedIn and no personal data. Only company-level signals.

## Step 1: know what the user sells (once)

If this is the first run in the conversation and you don't know what the user sells, ask one question: "What do you sell, and to which team?" Use the answer for the brief. Don't ask again.

## Step 2: run the script

```bash
cd "<this skill's folder>/scripts" && python3 stack.py domain1.com domain2.com
```

- Accepts bare domains or URLs. For a list, save it to a file and run `python3 stack.py -f domains.txt`.
- About 1 second per domain for DNS, longer when the company has hundreds of job posts.
- Output: `stack_results.json` (tools + evidence) and `stack_results.csv` in the same folder.

Read `stack_results.json`. Each tool has 1 to 3 evidence lines, prefixed by their source (`DNS SPF`, `DNS TXT`, `DNS MX`, `Website`, `Job post`).

## No terminal available (Claude app, Claude web)

The script needs a terminal and internet access. In Claude Code and Cowork it just runs. In the Claude app or on the web, when running it fails, do the same work by hand with web fetch, on ONE domain at a time:

1. DNS, the important part. Fetch these three URLs and read the `data` fields:
   - `https://dns.google/resolve?name=<domain>&type=TXT`
   - `https://dns.google/resolve?name=<domain>&type=MX`
   - any `redirect=` domain found in the SPF record, fetched the same way
   Match what you find against the tables at the top of `scripts/stack.py` (SPF, MX, TXT). That file is the reference list, read it first.
2. Job posts. Try, in order, until one answers:
   - `https://boards-api.greenhouse.io/v1/boards/<name>/jobs?content=true`
   - `https://api.lever.co/v0/postings/<name>?mode=json`
   - `https://api.ashbyhq.com/posting-api/job-board/<name>`
   `<name>` is usually the domain without its extension. Read the sales, marketing and operations posts, and keep the exact line naming each tool.
3. Homepage. Fetch `https://<domain>` and look for the script addresses listed in the HTML table of `scripts/stack.py`.

Then follow steps 3 and 4 below exactly as if the script had run. Say in one line that you worked without the script, since it reads fewer job posts this way.

## Step 3: read the evidence correctly

These rules matter more than the list itself. Do not break them.

- **"domain verified" is not "paying customer".** An `openai-domain-verification` or `anthropic-domain-verification` record proves the company set up an organization account with that vendor. It does not prove ChatGPT Enterprise, Claude Enterprise, or any plan. Say "they verified their domain with OpenAI", never "they use ChatGPT Enterprise".
- **SPF = they send email through it.** Strong signal that the tool is active.
- **Job post = they want people who know it.** Usually means they use it. When the tool shows up in only one ad, and only as "nice to have", mark it as weaker.
- **A tool named in a job post as the company's own product doesn't count.** The script already skips the company's own name.
- **"(unmapped)"** = a verification code from a vendor the script doesn't know yet. Show the raw name. Don't guess what the product is.
- **Old records stay.** A verification code can remain after a company leaves a tool. When a tool has one DNS signal and nothing else, say "possibly".
- **No result is not proof of absence.** Many companies use tools that leave no public trace.
- `jobs_read: 0` usually means their job board isn't on Greenhouse, Lever, or Ashby under the domain name. Say so in one line. Don't treat it as "no hiring".

## Step 4: output

For each domain:

```
## <company> (<N> tools found)

**Sales & CRM:** Salesforce (SPF + 4 job posts), Gong (job post), Outreach (job post)
**Marketing & email:** HubSpot (website script), Marketo (SPF)
**Support:** Zendesk (SPF)
**AI accounts:** OpenAI (domain verified), Anthropic (domain verified), Cursor (domain verified)
**Work & docs:** Notion, Slack, Atlassian, DocuSign
**Data:** Snowflake, dbt, Looker (job posts)
**Other / unmapped:** ...

**Proof:** one line per tool, the strongest evidence only. Job posts include the ad title and link.

**Brief for the call** (based on what the user sells):
- What their stack says about them (3 bullets max, only from the evidence)
- Where your product plugs in or what it replaces
- One first line to open the email or the call, naming a tool they actually use
- What you still don't know (the question to ask them)
```

Group tools by category, most solid signal first. Keep the brief under 120 words. Every claim in the brief must point to a tool in the list above it.

For 5 domains or more: skip the per-company brief. Give a table instead (domain · CRM · email tool · support · AI accounts · number of tools), then offer the brief for the ones the user picks.

## Limits to tell the user when relevant

- Only public signals: it misses tools that leave no trace in DNS, on the homepage, or in job posts.
- Job posts are only read from Greenhouse, Lever, and Ashby.
- Heavily tech companies leave far more traces than others. A company with 5 tools found isn't necessarily a small stack.
