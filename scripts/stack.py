#!/usr/bin/env python3
"""stack.py - find the tools a company uses, from public signals only.
Usage: python3 stack.py domain1.com domain2.com ...   (or -f domains.txt)
Sources: DNS (SPF, MX, TXT verification records), homepage scripts, public job boards (Greenhouse, Lever, Ashby).
Every tool comes with the source and the exact evidence."""
import sys, re, json, csv, subprocess, urllib.request, concurrent.futures as cf

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

SPF = {  # substring in SPF include -> tool
 "_spf.google.com":"Google Workspace","spf.protection.outlook.com":"Microsoft 365","_spf.salesforce.com":"Salesforce",
 "hubspotemail.net":"HubSpot","mktomail.com":"Marketo","pardot.com":"Salesforce Pardot","mail.zendesk.com":"Zendesk",
 "sendgrid.net":"SendGrid","mailgun.org":"Mailgun","amazonses.com":"Amazon SES","servers.mcsv.net":"Mailchimp",
 "mandrillapp.com":"Mailchimp Transactional","spf.freshdesk.com":"Freshdesk","freshemail.io":"Freshworks","zoho":"Zoho",
 "intercom.io":"Intercom","helpscoutemail.com":"Help Scout","customeriomail.com":"Customer.io","klaviyo":"Klaviyo",
 "postmarkapp.com":"Postmark","sparkpostmail.com":"SparkPost","mailjet.com":"Mailjet","sendinblue.com":"Brevo","brevo":"Brevo",
 "spf.mailshake":"Mailshake","outreach.io":"Outreach","salesloft":"Salesloft","gorgias":"Gorgias","notion":"Notion",
 "atlassian.net":"Atlassian","smtp.github.com":"GitHub","docusign.net":"DocuSign","workday.com":"Workday","greenhouse.io":"Greenhouse",
 "lever.co":"Lever","ashbyhq":"Ashby","braze":"Braze","iterable":"Iterable","mimecast":"Mimecast","pphosted.com":"Proofpoint",
 "ppe-hosted.com":"Proofpoint","servicenow":"ServiceNow","zuora":"Zuora","netsuite":"NetSuite","sfdc":"Salesforce",
 "rippling":"Rippling","gusto":"Gusto","bamboohr":"BambooHR","hibob":"HiBob","qualtrics":"Qualtrics","marketo":"Marketo",
 "stripe.com":"Stripe","shopify":"Shopify","emarsys":"Emarsys","eloqua":"Oracle Eloqua","mailerlite":"MailerLite","loops.so":"Loops",
 "resend":"Resend","activecampaign":"ActiveCampaign","apollo.io":"Apollo","lemlist":"lemlist","instantly":"Instantly",
}
MX = {"google.com":"Google Workspace","googlemail.com":"Google Workspace","outlook.com":"Microsoft 365","pphosted.com":"Proofpoint",
      "mimecast":"Mimecast","barracudanetworks":"Barracuda","zoho":"Zoho","messagelabs":"Broadcom Symantec","iphmx.com":"Cisco Secure Email"}
TXT = {  # prefix of TXT verification record -> tool
 "atlassian-domain-verification":"Atlassian","docusign=":"DocuSign","stripe-verification":"Stripe","facebook-domain-verification":"Meta Business",
 "ms=":"Microsoft (domain verified)","apple-domain-verification":"Apple Business","adobe-idp-site-verification":"Adobe","zoom_verify":"Zoom",
 "slack-domain-verification":"Slack","miro-verification":"Miro","onetrust-domain-verification":"OneTrust","openai-domain-verification":"OpenAI (domain verified)",
 "anthropic-domain-verification":"Anthropic (domain verified)","dropbox-domain-verification":"Dropbox","box-domain-verification":"Box",
 "webexdomainverification":"Webex","citrix-verification":"Citrix","knowbe4-site-verification":"KnowBe4","mongodb-site-verification":"MongoDB",
 "hubspot-developer-verification":"HubSpot (developer account, not proof of use)","hubspot-domain-verification":"HubSpot","figma-domain-verification":"Figma","1password":"1Password",
 "notion-domain-verification":"Notion","asana-domain-verification":"Asana","canva-site-verification":"Canva","cursor-domain-verification":"Cursor",
 "loom-site-verification":"Loom","gong-verification":"Gong","linear-domain-verification":"Linear","airtable-verification":"Airtable",
 "calendly-site-verification":"Calendly","workplace-domain-verification":"Workplace","smartsheet-site-validation":"Smartsheet",
 "okta-verification":"Okta","duo_sso_verification":"Duo","jamf-site-verification":"Jamf","segment-site-verification":"Segment",
 "postman-domain-verification":"Postman","github-verification":"GitHub","_github-challenge":"GitHub","vercel":"Vercel","cisco-ci-domain-verification":"Cisco",
 "wrike-verification":"Wrike","clickup-domain-verification":"ClickUp","intercom-domain-verification":"Intercom","zapier-domain-verification":"Zapier",
 "sendinblue-code":"Brevo","brevo-code":"Brevo","mailru-verification":"Mail.ru","yandex-verification":"Yandex","klaviyo-site-verification":"Klaviyo",
 "have-i-been-pwned-verification":"HIBP","lastpass-verification-code":"LastPass","paddle-verification":"Paddle","whimsical":"Whimsical",
 "shopify-verification-code":"Shopify","pinterest-site-verification":"Pinterest","tiktok-developers-site-verification":"TikTok","ahrefs-site-verification":"Ahrefs",
 "status-page-domain-verification":"Atlassian Statuspage","wiz-domain-verification":"Wiz","crowdstrike":"CrowdStrike","drata":"Drata","vanta":"Vanta",
 "grammarly":"Grammarly","typeform":"Typeform","datadog":"Datadog","sentry":"Sentry","mixpanel":"Mixpanel","amplitude":"Amplitude",
}
HTML = {
 "js.hs-scripts.com":"HubSpot","js.hsforms.net":"HubSpot","hs-analytics.net":"HubSpot","munchkin.marketo.net":"Marketo","pi.pardot.com":"Salesforce Pardot",
 "widget.intercom.io":"Intercom","js.intercomcdn.com":"Intercom","js.driftt.com":"Drift","cdn.segment.com":"Segment","googletagmanager.com":"Google Tag Manager",
 "clarity.ms":"Microsoft Clarity","static.hotjar.com":"Hotjar","fullstory.com":"FullStory","js.qualified.com":"Qualified","cdn.cookielaw.org":"OneTrust",
 "chilipiper.com":"Chili Piper","assets.calendly.com":"Calendly","6sc.co":"6sense","clearbitscripts.com":"Clearbit","ws.zoominfo.com":"ZoomInfo",
 "reb2b":"RB2B","warmly.ai":"Warmly","getkoala.com":"Koala","mutinycdn.com":"Mutiny","snap.licdn.com":"LinkedIn Insight Tag","connect.facebook.net":"Meta Pixel",
 "js.stripe.com":"Stripe","static.zdassets.com":"Zendesk","wchat.freshchat.com":"Freshchat","client.crisp.chat":"Crisp","cdn.amplitude.com":"Amplitude",
 "cdn.mxpnl.com":"Mixpanel","cdn.heapanalytics.com":"Heap","posthog":"PostHog","plausible.io":"Plausible","webflow":"Webflow","wp-content":"WordPress",
 "framerusercontent.com":"Framer","cdn.shopify.com":"Shopify","navattic":"Navattic","storylane":"Storylane","gong.io":"Gong","vector.co":"Vector",
 "unifyintent":"Unify","default.com":"Default","g2crowd.com":"G2 tracking","bizible":"Marketo Measure","dreamdata":"Dreamdata","hockeystack":"HockeyStack",
 "js.usemessages.com":"HubSpot chat","cdn.pendo.io":"Pendo","appcues":"Appcues","userpilot":"Userpilot","chameleon":"Chameleon","sprig":"Sprig",
 "rudderstack":"RudderStack","hightouch":"Hightouch","optimizely":"Optimizely","vwo.com":"VWO","ada.support":"Ada","sierra.ai":"Sierra","decagon":"Decagon",
}
JOBS = ["Salesforce","HubSpot","Pipedrive","Attio","Close.com","Zoho CRM","Dynamics 365","Outreach","Salesloft","Apollo","Gong","Chorus","Clari",
 "Clay","ZoomInfo","Sales Navigator","Seamless.AI","Lusha","Chili Piper","Calendly","Marketo","Pardot","Customer.io","Braze","Iterable","Intercom",
 "Zendesk","Gainsight","ChurnZero","Vitally","Totango","Planhat","Looker","Tableau","Power BI","Snowflake","dbt","Segment","Amplitude","Mixpanel",
 "Notion","Jira","Asana","Monday.com","Slack","Zapier","Make.com","n8n","Claude","ChatGPT","Copilot","Cursor","Gemini","Lemlist","Instantly","Smartlead",
 "HeyReach","Highspot","Seismic","Mutiny","6sense","Demandbase","Bombora","Common Room","Drift","Gorgias","Klaviyo","NetSuite","QuickBooks"]

def dig(name, typ):
    """DNS lookup. Uses dig when available, otherwise DNS-over-HTTPS (works anywhere with internet)."""
    try:
        out = subprocess.run(["dig","+short",typ,name],capture_output=True,text=True,timeout=10).stdout
        if out.strip(): return out
    except Exception: pass
    try:
        raw = urllib.request.urlopen(urllib.request.Request(
            f"https://dns.google/resolve?name={name}&type={typ}", headers=UA), timeout=12).read()
        return "\n".join(a.get("data","") for a in json.loads(raw).get("Answer",[]))
    except Exception: return ""

def get(url, t=12, cap=3_000_000):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=t) as r: return r.read(cap).decode("utf-8","ignore")
    except Exception: return ""

def scan(domain):
    domain = re.sub(r"^https?://|/.*$|^www\.","",domain.strip().lower())
    found = {}
    def add(tool, source, ev):
        found.setdefault(tool, [])
        if len(found[tool]) < 3: found[tool].append(f"{source}: {ev[:120]}")
    txt = dig(domain,"TXT")
    for line in txt.splitlines():
        l = line.strip('"').lower()
        if l.startswith("v=spf1"):
            for inc in re.findall(r"include:(\S+)", l):
                for k,v in SPF.items():
                    if k in inc: add(v,"DNS SPF",f"include:{inc}")
        else:
            hit = False
            for k,v in TXT.items():
                if l.startswith(k) or (k in l and "verif" in l):
                    add(v,"DNS TXT",l); hit = True; break
            if not hit:
                m = re.match(r"([a-z0-9_\-]+?)[-_](?:site-|domain-)?verification", l)
                if m: add(m.group(1).title()+" (unmapped)","DNS TXT",l)
    for spfname in re.findall(r"redirect=(\S+)", txt.lower()):
        for inc in re.findall(r"include:(\S+)", dig(spfname,"TXT").lower()):
            for k,v in SPF.items():
                if k in inc: add(v,"DNS SPF",f"include:{inc}")
    for line in dig(domain,"MX").splitlines():
        for k,v in MX.items():
            if k in line.lower(): add(v,"DNS MX",line.strip())
    html = get(f"https://{domain}") or get(f"https://www.{domain}")
    for k,v in HTML.items():
        i = html.find(k)
        if i >= 0: add(v,"Website",html[max(0,i-40):i+60].replace("\n"," "))
    root = domain.split(".")[0]
    jobs = []
    g = get(f"https://boards-api.greenhouse.io/v1/boards/{root}/jobs?content=true", 30, 40_000_000)
    def js(x):
        try: return json.loads(x)
        except Exception: return {} if x.startswith("{") else []
    if g.startswith("{"):
        for j in js(g).get("jobs",[]): jobs.append((j["title"], re.sub("<[^>]+>"," ",__import__("html").unescape(j.get("content",""))), j.get("absolute_url","")))
    l = get(f"https://api.lever.co/v0/postings/{root}?mode=json", 30, 40_000_000)
    if l.startswith("["):
        for j in js(l): jobs.append((j.get("text",""), j.get("descriptionPlain","")+" "+" ".join(x.get("content","") for x in j.get("lists",[])), j.get("hostedUrl","")))
    a = get(f"https://api.ashbyhq.com/posting-api/job-board/{root}", 30, 40_000_000)
    if a.startswith("{"):
        for j in js(a).get("jobs",[]): jobs.append((j.get("title",""), j.get("descriptionPlain",""), j.get("jobUrl","")))
    for title, body, url in jobs:
        low = " "+body+" "
        for tool in JOBS:
            if tool.lower().split(".")[0] == root: continue
            m = re.search(r"(?<![A-Za-z])"+re.escape(tool)+r"(?![A-Za-z])", low)
            if m:
                s = low[max(0,m.start()-70):m.end()+50]
                add(tool,"Job post",f"{title} | ...{' '.join(s.split())}... {url}")
    return {"domain":domain,"jobs_read":len(jobs),"tools":found}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0]=="-f": args = [x for x in open(args[1]).read().split() if x]
    with cf.ThreadPoolExecutor(8) as ex: res = list(ex.map(scan,args))
    json.dump(res,open("stack_results.json","w"),indent=1)
    with open("stack_results.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(["domain","tool","evidence"])
        for r in res:
            for t,evs in r["tools"].items(): w.writerow([r["domain"],t," || ".join(evs)])
    for r in res:
        print(f"\n## {r['domain']}  ({len(r['tools'])} tools, {r['jobs_read']} job posts read)")
        for t,evs in sorted(r["tools"].items()): print(f"  - {t}  <- {evs[0][:110]}")
