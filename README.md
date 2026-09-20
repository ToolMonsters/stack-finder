# Stack Finder

A Claude skill. You give it a company domain, it tells you which tools that company uses, with the proof for each one, then writes the brief for your next call.

Everything comes from public records. Nothing from LinkedIn, no personal data, no paid API, no account to create.

```
/stack-finder attio.com
```

```
## Attio (23 tools found, 41 job posts read)

AI accounts:   Anthropic (domain verified), OpenAI (domain verified), Cursor
Marketing:     Mailchimp (they send through it), Google Workspace
Support:       Intercom (job post)
Automation:    Zapier, n8n, Segment (job posts)
Work:          Slack, Notion, Linear, Figma, 1Password
Payments:      Stripe

Claude Code | "Hands-on experience building with AI coding platforms
              (Claude Code, Cursor, or equivalent)"
              Forward Deployed GTM Engineer, jobs.ashbyhq.com/attio/...
Mailchimp   | SPF record: include:servers.mcsv.net
Anthropic   | anthropic-domain-verification=... (account set up, plan unknown)
```

Then a brief in a few lines: what their stack says about them, where your product fits, one opening line that names a tool they actually use, and the question you still need to ask them.

## Where the data comes from

**1. DNS records.** The public directory of the internet. Two things sit there.

Companies must list every service allowed to send email in their name, or their emails land in spam. `include:_spf.salesforce.com` means they run email through Salesforce. `servers.mcsv.net` means Mailchimp, `mail.zendesk.com` means Zendesk.

And when a company opens a team account with a software vendor, the vendor asks it to paste a code in its DNS to prove it owns the domain. The code usually stays there for years: `openai-domain-verification=`, `anthropic-domain-verification=`, `atlassian-domain-verification=`, `docusign=`.

**2. Their website.** The scripts loaded by the homepage name the tools behind them: HubSpot, Intercom, Chili Piper, 6sense, Segment.

**3. Their job posts.** Companies hiring through Greenhouse, Lever or Ashby publish every open role at one public address. Sales and marketing ads name the stack: "Salesforce experience required", "Gong", "Clay". The skill keeps the exact sentence as proof.

## Install

**Claude Code** (recommended)

```bash
git clone https://github.com/ToolMonsters/stack-finder.git ~/.claude/skills/stack-finder
```

Then type `/stack-finder` followed by one or more domains.

**Claude app and claude.ai**

Upload `stack-finder.zip` as a skill, then ask for a domain.

It works in both, and it is more powerful in Claude Code. There, the script runs directly: dozens of domains at a time, every job post read, about a second per domain. In the app, Claude falls back to reading the same public sources one request at a time, which covers one company at a time and fewer job posts.

## Reading the results honestly

This is most of what the skill does, and it is the part that matters.

- **A verified domain is not a paying customer.** An `anthropic-domain-verification` record proves someone set up an organization account. It says nothing about the plan, the number of seats, or whether anyone still uses it. The skill writes "domain verified", never "they use Claude Enterprise".
- **An email record is a strong signal.** A tool in the SPF record is a tool they actively send mail through.
- **A job post is an intention.** A tool named once, as a "nice to have", is a weak signal. The skill says so.
- **Old records stay.** A company can leave a tool and forget the code in its DNS. One lone DNS signal is reported as "possibly".
- **Finding nothing proves nothing.** Plenty of tools leave no public trace at all.
- **Unknown vendors are shown raw.** When a verification code comes from a vendor the list does not know, you get the raw name, not a guess.

## What it found across 101 SaaS companies

Ramp, Notion, Vercel, Linear, Clay, HubSpot, Stripe and 94 others. 40 seconds for all of them.

| | Companies |
|---|---|
| Average tools found per company | 29 |
| Companies with no result | 0 |
| Domain verified with OpenAI | 68 |
| Domain verified with Anthropic | 67 |
| Both | 57 |
| HubSpot | 74 |
| Salesforce | 57 |
| Gong | 27 |

That sample is almost entirely tech companies, which leave far more traces than a manufacturer or a clinic. Do not read those percentages as a market share.

## Adding a tool to the list

The tables at the top of `scripts/stack.py` are the whole detection logic: `SPF` for email senders, `TXT` for verification codes, `HTML` for website scripts, `JOBS` for names to look for in job ads. Add a line, and the tool is detected everywhere. Pull requests welcome.

## Run it without Claude

```bash
python3 scripts/stack.py attio.com notion.so
python3 scripts/stack.py -f domains.txt
```

Python 3, no dependency to install. Writes `stack_results.json` and `stack_results.csv` next to the script.

---

Built by [Tool Monsters](https://toolmonsters.com).
