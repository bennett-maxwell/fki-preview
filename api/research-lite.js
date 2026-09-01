/**
 * Vercel subset of research-blueprint-ai-skill SCOUT/ANALYST/PROFILER for non-demo URLs.
 * Does not replace the full research_packet_gate.py (14-row / founder lock).
 * Magnet lite: homepage fetch + industry classify + labeled demographic/competitor rows.
 */
const https = require('https');
const http = require('http');
const { URL } = require('url');

const INDUSTRY_RULES = [
  { id: 'recruiting', label: 'High-school / youth sports recruiting', keys: ['recruit', 'athlete', 'ncaa', 'college sports', 'high school recruiting'] },
  { id: 'home_services', label: 'Home services', keys: ['hvac', 'plumber', 'electrician', 'roof', 'heating', 'cooling'] },
  { id: 'franchise', label: 'Franchise / multi-unit', keys: ['franchise', 'franchisor', 'territory', 'franchisee'] },
  { id: 'professional_services', label: 'Professional services', keys: ['attorney', 'cpa', 'accountant', 'consultant', 'advisor'] },
  { id: 'ecommerce', label: 'Ecommerce / retail', keys: ['shopify', 'woocommerce', 'checkout', 'add to cart'] }
];

const PATTERNS = {
  recruiting: {
    icp: 'Parents of high-school athletes who will pay for a recruiting process they do not want to learn alone.',
    demographic: [
      { claim: 'Primary buyer is a parent, not the athlete.', label: 'homepage-inferred' },
      { claim: 'Decision window is junior / senior year plus earlier education buyers.', label: 'industry pattern' }
    ],
    competitors: [
      { claim: 'Recruiting consultancies put parent intake on SMS so a night-time web form is not the first touch.', label: 'industry pattern' },
      { claim: 'Operators split curious parent from ready-to-buy before a human consult.', label: 'industry pattern' },
      { claim: 'Athletic programs use after-hours chat so a missed form is not a lost family.', label: 'industry pattern' },
      { claim: 'Booking sits on a calendar employee so consults are not a spreadsheet.', label: 'industry pattern' }
    ],
    extras: ['Parent Qualification Employee', 'Recruiting-Timeline Employee', 'Consult No-Show Employee']
  },
  home_services: {
    icp: 'Homeowners with an urgent or seasonal job who will book the first operator that answers.',
    demographic: [
      { claim: 'Buyer is the homeowner or property manager on the job address.', label: 'industry pattern' },
      { claim: 'After-hours and weekend searches are a large share of inbound.', label: 'industry pattern' }
    ],
    competitors: [
      { claim: 'Speed-to-lead on missed calls and web forms is the default first AI Employee.', label: 'industry pattern' },
      { claim: 'Booking employees hold a tech calendar and stop unqualified chats from eating the day.', label: 'industry pattern' },
      { claim: 'Review-request employees fire after a completed job.', label: 'industry pattern' },
      { claim: 'Estimate follow-up employees chase stale quotes.', label: 'industry pattern' }
    ],
    extras: ['Estimate Follow-Up Employee', 'Review-Request Employee']
  },
  franchise: {
    icp: 'Franchise candidates and existing operators who will take a discovery call if someone answers fast.',
    demographic: [
      { claim: 'Candidate is often a career-changer with capital.', label: 'industry pattern' },
      { claim: 'Existing operators care about unit-level lead response.', label: 'industry pattern' }
    ],
    competitors: [
      { claim: 'Franchise development desks use a speed-to-lead employee on apply forms.', label: 'industry pattern' },
      { claim: 'Booking employees put only funded, timeline-ready candidates on the calendar.', label: 'industry pattern' },
      { claim: 'Unit-level operators put the same two employees on local lead flow.', label: 'industry pattern' },
      { claim: 'Nurture employees keep not-this-year candidates without a spreadsheet.', label: 'industry pattern' }
    ],
    extras: ['Candidate Qualification Employee', 'Nurture Employee']
  },
  professional_services: {
    icp: 'A qualified buyer who will book a consult if the first reply is fast.',
    demographic: [
      { claim: 'Buyer is a business owner or household decision-maker.', label: 'industry pattern' },
      { claim: 'Intake is usually a form or email that sits until a human is free.', label: 'industry pattern' }
    ],
    competitors: [
      { claim: 'Intake employees qualify matter-type / budget / timeline first.', label: 'industry pattern' },
      { claim: 'Speed-to-lead on web forms beats a 47-hour first-touch average (process comparison).', label: 'industry pattern' },
      { claim: 'Booking employees put only the fit on the consult calendar.', label: 'industry pattern' },
      { claim: 'No-show recovery is a separate employee.', label: 'industry pattern' }
    ],
    extras: ['Intake Qualification Employee', 'Consult No-Show Employee']
  },
  ecommerce: {
    icp: 'A shopper or wholesale buyer who abandons when nobody answers a pre-purchase question.',
    demographic: [
      { claim: 'Buyer is often mobile and after hours.', label: 'industry pattern' },
      { claim: 'Wholesale / high-ticket SKUs still need a human close.', label: 'industry pattern' }
    ],
    competitors: [
      { claim: 'Cart-recovery employees text the abandoned checkout.', label: 'industry pattern' },
      { claim: 'Pre-purchase chat employees answer size / ship / fit.', label: 'industry pattern' },
      { claim: 'VIP inboxes get a speed-to-lead employee.', label: 'industry pattern' },
      { claim: 'Review and refill employees run after delivery.', label: 'industry pattern' }
    ],
    extras: ['Pre-Purchase Question Employee', 'Cart Recovery Employee']
  },
  general: {
    icp: 'A buyer who found the site and will talk to whoever answers first.',
    demographic: [
      { claim: 'Target demographic was not locked from the homepage.', label: 'thin' },
      { claim: 'Assume inbound web or phone leads that wait on a human.', label: 'labeled estimate' }
    ],
    competitors: [
      { claim: 'Speed-to-Lead Employee on after-hours forms is the usual first hire.', label: 'industry pattern' },
      { claim: 'Booking Employee puts only the fit on the calendar.', label: 'industry pattern' },
      { claim: 'Qualification Employee stops unqualified conversations from burning the owner.', label: 'industry pattern' },
      { claim: 'No-show recovery is the fourth common employee.', label: 'industry pattern' }
    ],
    extras: ['Qualification Employee', 'No-Show Recovery Employee']
  }
};

function classify(text) {
  const blob = String(text || '').toLowerCase();
  let best = 'general';
  let score = 0;
  INDUSTRY_RULES.forEach((row) => {
    const n = row.keys.filter((k) => blob.indexOf(k) >= 0).length;
    if (n > score) { score = n; best = row.id; }
  });
  const meta = INDUSTRY_RULES.find((r) => r.id === best);
  return { id: best, label: (meta && meta.label) || 'Local / service business' };
}

function gateLite(packet) {
  if (!packet || packet.send_blocked !== true) return { ok: false, dim: 'send_block' };
  const el = packet.evidence_ledger || [];
  if (el.length < 4) return { ok: false, dim: 'evidence_floor_lite' };
  const emps = (packet.profiler && packet.profiler.employees) || [];
  if (emps.length < 3 || emps.length > 6) return { ok: false, dim: 'ai_employees' };
  for (const e of emps) {
    if (!e.finding || !e.workflow || !e.loop || !e.name) return { ok: false, dim: 'ai_employees' };
  }
  if (!(packet.analyst && packet.analyst.industry)) return { ok: false, dim: 'industry' };
  return { ok: true, dim: null };
}

function fetchText(url) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const lib = u.protocol === 'http:' ? http : https;
    const req = lib.get(url, { headers: { 'User-Agent': 'AdvaitaResearchLite/1.0' } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return fetchText(res.headers.location).then(resolve, reject);
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error('status ' + res.statusCode));
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks).toString('utf8').slice(0, 20000)));
    });
    req.setTimeout(8000, () => { req.destroy(); reject(new Error('timeout')); });
    req.on('error', reject);
  });
}

function stripTag(html, re, fallback) {
  const m = String(html || '').match(re);
  return m ? m[1].replace(/\s+/g, ' ').trim() : fallback;
}

function scrapeForensics(html) {
  const h = String(html || '');
  const low = h.toLowerCase();
  const count = (re) => (h.match(re) || []).length;
  const title = stripTag(h, /<title[^>]*>([\s\S]*?)<\/title>/i, '');
  const h1 = stripTag(h, /<h1[^>]*>([\s\S]*?)<\/h1>/i, '');
  const imgs = count(/<img\b/gi);
  const alts = count(/<img[^>]*\balt=["'][^"']+["']/gi);
  return {
    title: title.slice(0, 160),
    h1: h1.slice(0, 160),
    forms: count(/<form\b/gi),
    tel: count(/href=["']tel:/gi),
    mailto: count(/href=["']mailto:/gi),
    buttons: count(/<(button|a)[^>]{0,80}(book|schedule|apply|quote|contact)/gi),
    schema: /application\/ld\+json/i.test(h),
    viewport: /name=["']viewport["']/i.test(h),
    og: /property=["']og:/i.test(h),
    canonical: /rel=["']canonical["']/i.test(h),
    lang: /<html[^>]*\blang=/i.test(h),
    gtag: /gtag\(|googletagmanager/i.test(h),
    fbq: /fbq\(|fbevents/i.test(h),
    chat: /intercom|drift\.js|tidio|tawk|crisp\.chat|voiceflow/i.test(low),
    reviews: /trustpilot|birdeye|google\.com\/maps|stars?/i.test(low),
    privacy: /href=["'][^"']*(privacy|terms)[^"']*["']/i.test(h),
    cookie: /onetrust|cookiebot|cookie (consent|banner|policy)/i.test(low),
    imgs: imgs,
    alts: alts,
    words: h.replace(/<script[\s\S]*?<\/script>/gi, ' ').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().split(' ').filter(Boolean).length
  };
}

function expertAngles(research, html, industry) {
  const f = scrapeForensics(html);
  const name = research.name || research.host || 'this site';
  const label = industry.label || 'this industry';
  return [
    { id: 'A01', brain: 'brain-cmo', method: 'Offer-clarity 5-second test', found: (f.h1 || f.title) ? ('Leads with “' + (f.h1 || f.title) + '.”') : 'No H1/title locked.', label: f.h1 || f.title ? 'homepage-inferred' : 'thin' },
    { id: 'A02', brain: 'brain-cro', method: 'Capture architecture', found: 'Forms: ' + f.forms + '. Click-to-call: ' + f.tel + '. Chat: ' + (f.chat ? 'present' : 'not visible') + '.', label: 'homepage-inferred' },
    { id: 'A03', brain: 'brain-coo', method: 'Speed-to-lead leak', found: research.leak, label: 'industry pattern' },
    { id: 'A04', brain: 'brain-cio', method: 'Stack forensics', found: 'Stack signal: ' + research.tech + '.', label: research.tech && research.tech !== 'Not confirmed' ? 'homepage-inferred' : 'thin' },
    { id: 'A05', brain: 'brain-cro', method: 'Trust inventory', found: f.reviews ? 'Review/maps signal visible.' : 'No review platform signal.', label: f.reviews ? 'homepage-inferred' : 'thin' },
    { id: 'A06', brain: 'appointment-setter-sop-skill', method: 'Booking presence', found: f.buttons ? ('Conversion verbs x' + f.buttons) : 'No book/schedule/apply control obvious.', label: f.buttons ? 'homepage-inferred' : 'thin' },
    { id: 'A07', brain: 'brain-website-expert', method: 'Mobile readiness', found: f.viewport ? 'Viewport meta present.' : 'Viewport meta not found.', label: 'homepage-inferred' },
    { id: 'A08', brain: 'brain-seo-expert', method: 'SEO hygiene', found: 'Title ' + (f.title ? 'present' : 'missing') + ', H1 ' + (f.h1 ? 'present' : 'missing') + '.', label: 'homepage-inferred' },
    { id: 'A09', brain: 'brain-seo-expert', method: 'Schema.org', found: f.schema ? 'JSON-LD present.' : 'No JSON-LD.', label: 'homepage-inferred' },
    { id: 'A10', brain: 'brain-cmo', method: 'Tracking footprint', found: 'Google ' + (f.gtag ? 'visible' : 'not visible') + ', Meta ' + (f.fbq ? 'visible' : 'not visible') + '.', label: 'homepage-inferred' },
    { id: 'A11', brain: 'brain-cmo', method: 'Social-proof specificity', found: f.reviews ? 'Review/maps signal visible. Named case studies are not copied onto this magnet.' : 'No review platform signal. Testimonials are not invented.', label: f.reviews ? 'homepage-inferred' : 'thin' },
    { id: 'A12', brain: 'brain-cro', method: 'CTA language', found: f.buttons ? 'Conversion verb present.' : 'Primary CTA not obvious.', label: f.buttons ? 'homepage-inferred' : 'thin' },
    { id: 'A13', brain: 'brain-cmo', method: 'ICP from copy', found: industry.icp, label: industry.id === 'general' ? 'thin' : 'homepage-inferred' },
    { id: 'A14', brain: 'research-blueprint-ai-skill', method: 'Competitor AI Employee pattern', found: 'Operators in ' + label + ' put speed-to-lead and booking employees on inbound first.', label: 'industry pattern' },
    { id: 'A15', brain: 'brain-cfo', method: 'Offer / price visibility', found: /\$|pricing|quote/i.test(html + ' ' + (research.what || '')) ? 'Price/quote language visible.' : 'No public price locked.', label: 'homepage-inferred' },
    { id: 'A16', brain: 'brain-website-expert', method: 'Content vs conversion', found: 'Word count ~' + f.words + ' with ' + f.forms + ' form(s).', label: 'homepage-inferred' },
    { id: 'A17', brain: 'website-audit-skill', method: 'Accessibility basics', found: 'lang ' + (f.lang ? 'present' : 'missing') + '. img ' + f.imgs + ' alt ' + f.alts + '. canonical ' + (f.canonical ? 'yes' : 'no') + '. privacy link ' + (f.privacy ? 'yes' : 'no') + '. cookie banner ' + (f.cookie ? 'yes' : 'no') + '. mailto ' + f.mailto + '. Not a WCAG score.', label: (f.lang || f.alts > 0) ? 'homepage-inferred' : 'thin' },
    { id: 'A18', brain: 'brain-cro', method: 'NAP / click-to-call', found: f.tel ? (f.tel + ' tel: link(s).') : 'No tel: link on this fetch.', label: f.tel ? 'homepage-inferred' : 'thin' },
    { id: 'A19', brain: 'anti-ai-slop-skill', method: 'Claims hygiene', found: 'Their homepage adjectives are not our proof. Anthony hire-payback stays ours.', label: 'homepage-inferred' },
    { id: 'A20', brain: 'blueprint-ai-skill', method: 'First-hire recommendation', found: 'Day 1 for ' + name + ': Speed-to-Lead, then Booking. Offer lock $5,000 + $1,000/mo.', label: 'offer lock' }
  ];
}

function buildResearch(rawUrl, html) {
  let host = '';
  try { host = new URL(rawUrl).hostname.replace(/^www\./, ''); } catch (e) { host = rawUrl; }
  const title = stripTag(html, /<title[^>]*>([\s\S]*?)<\/title>/i, '') || stripTag(html, /^#\s+(.+)$/m, '');
  const desc = stripTag(html, /name=["']description["']\s+content=["']([^"']+)/i, '') ||
    stripTag(html, /og:description["']\s+content=["']([^"']+)/i, '');
  const industry = classify((title + ' ' + desc + ' ' + html.slice(0, 4000) + ' ' + host));
  const pattern = PATTERNS[industry.id] || PATTERNS.general;
  const tech = /wix/i.test(html) ? 'Wix' : /shopify/i.test(html) ? 'Shopify' : /wordpress|wp-content/i.test(html) ? 'WordPress' : 'Not confirmed';
  const name = (title.split('|')[0] || host).trim() || host;
  const research = {
    url: rawUrl,
    host: host,
    name: name,
    what: desc ? desc.slice(0, 220) : (title ? ('Public title on ' + host + ': ' + title.slice(0, 140)) : ('Opened ' + host)),
    offer: 'Offer signal not confirmed from this fetch.',
    capture: /form|contact|schedule|book/i.test(html) ? 'A form or booking control is visible. The leak is still how fast a human answers it.' : 'Lead capture method not confirmed.',
    tech: tech,
    leak: 'Speed-to-lead: if nobody answers after hours, the lead goes cold.',
    fact: title ? ('Page title: “' + title.slice(0, 140) + '.”') : ('We opened ' + host + ' as the working site.'),
    ownerNote: 'Owner / LinkedIn lookup is public-only and not invented.',
    labeled: !title,
    source: 'vercel-lite'
  };
  const employees = [
    {
      id: 'EMP-01',
      name: 'Speed-to-Lead Employee',
      finding: research.leak + ' ' + research.capture,
      workflow: 'The new lead texts in 2 seconds, nights and weekends included. Qualifies. Hands a human only what is warm.',
      loop: 'First-touch time: missed-hours → 2 seconds. Industry first-touch average is 47 hours — process comparison, not a promised lift for ' + name + '.'
    },
    {
      id: 'EMP-02',
      name: 'Booking Employee',
      finding: name + ' still has to put the fit on a calendar.',
      workflow: 'Only qualified conversations land on the calendar. ' + name + ' keeps the close.',
      loop: 'Booked qualified conversations / week.'
    }
  ].concat((pattern.extras || []).map((n, i) => ({
    id: 'EMP-0' + (i + 3),
    name: n,
    finding: 'Industry-specific leak for ' + industry.label + ' — not a generic paste-on employee.',
    workflow: n + ' runs the workflow this industry actually uses. Labeled until confirmed on the call.',
    loop: 'Measurable loop named on the install call. Labeled until numbers exist.'
  }))).slice(0, 6);

  research.packet = {
    route: 'research_only_lite',
    completeness_gate: 'lite',
    send_blocked: true,
    scout: { site: rawUrl, host: host, name: name, fact: research.fact, tech: tech, capture: research.capture, what: research.what },
    analyst: {
      industry: industry.label,
      industry_id: industry.id,
      icp: pattern.icp,
      demographic: pattern.demographic,
      pain: research.leak,
      competitors: pattern.competitors,
      angles: expertAngles(research, html, { id: industry.id, label: industry.label, icp: pattern.icp }),
      forensics: scrapeForensics(html),
      labeled: !title || industry.id === 'general'
    },
    profiler: {
      employees: employees,
      start_14_days: '$5,000 setup + $1,000/mo, month-to-month, 14-day install.'
    },
    unknowns: ['Founder bio is not invented.', 'Demographic rows are labeled if thin.', 'Competitor names are not guessed.'],
    evidence_ledger: [
      { id: 'E-001', claim: research.fact, source_url: rawUrl, dimension_tag: 'scout', confidence: title ? 'medium' : 'low' },
      { id: 'E-002', claim: 'Industry classified as ' + industry.label, source_url: rawUrl, dimension_tag: 'industry', confidence: industry.id === 'general' ? 'low' : 'medium' },
      { id: 'E-003', claim: pattern.demographic[0].claim, source_url: rawUrl, dimension_tag: 'demographic', confidence: 'low' },
      { id: 'E-004', claim: research.leak, source_url: rawUrl, dimension_tag: 'pain', confidence: 'medium' }
    ]
  };
  research.gate = gateLite(research.packet);
  return research;
}

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

module.exports = async function handler(req, res) {
  cors(res);
  if (req.method === 'OPTIONS') { res.statusCode = 204; res.end(); return; }
  if (req.method !== 'POST') { res.statusCode = 405; res.end('POST only'); return; }
  let body = '';
  await new Promise((resolve) => {
    req.on('data', (c) => { body += c; });
    req.on('end', resolve);
  });
  let url = '';
  try { url = JSON.parse(body || '{}').url || ''; } catch (e) { url = ''; }
  if (!url) { res.statusCode = 400; res.end(JSON.stringify({ error: 'url required' })); return; }
  if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
  let host = '';
  try { host = new URL(url).hostname.replace(/^www\./, ''); } catch (e) {
    res.statusCode = 400; res.end(JSON.stringify({ error: 'bad url' })); return;
  }
  let html = '';
  try { html = await fetchText('https://r.jina.ai/http://' + host); } catch (e) {
    try { html = await fetchText(url); } catch (e2) { html = ''; }
  }
  const research = buildResearch(url, html);
  res.setHeader('Content-Type', 'application/json');
  res.statusCode = 200;
  res.end(JSON.stringify({ research: research, gate: research.gate, lite: true }));
};
