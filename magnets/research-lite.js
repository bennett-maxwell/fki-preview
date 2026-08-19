/**
 * Blueprint research lite — SCOUT → ANALYST → PROFILER mapper for magnets.
 * Magnet preview only. Full packet stays on blueprint-ai-skill after /apply/.
 * Public noun: AI Employees. Soft claims must be labeled.
 */
(function (root) {
  var SAMPLE = 'https://recruiting4parents.com';
  var RESEARCH_APIS = [
    'https://advaita-research-lite.vercel.app/api/research-lite',
    'https://blueprint-ghl-relay.vercel.app/api/research-lite'
  ];
  try {
    if (typeof location !== 'undefined' && location.origin &&
        !/github\.io$|aiblueprintmarketing\.com$|pages\.dev$/i.test(location.hostname)) {
      RESEARCH_APIS.unshift(location.origin + '/api/research-lite');
    }
  } catch (e) {}

  var INDUSTRIES = {
    recruiting: {
      id: 'recruiting',
      label: 'High-school / youth sports recruiting',
      keywords: ['recruit', 'athlete', 'ncaa', 'college sports', 'parent', 'high school recruiting', 'scholarship', 'coach'],
      icp: 'Parents of high-school athletes who will pay for a recruiting process they do not want to learn alone.',
      demographic: [
        { claim: 'Primary buyer is a parent, not the athlete.', label: 'homepage-inferred' },
        { claim: 'Decision window is junior / senior year plus earlier “education” buyers.', label: 'industry pattern' }
      ],
      industryAi: [
        { claim: 'Recruiting consultancies put parent intake on SMS so a night-time web form is not the first touch.', label: 'industry pattern' },
        { claim: 'Operators split “curious parent” from “ready to buy a process” before a human consult.', label: 'industry pattern' },
        { claim: 'Athletic programs use after-hours chat so a missed form is not a lost family.', label: 'industry pattern' },
        { claim: 'Booking sits on a calendar employee so consults are not a spreadsheet.', label: 'industry pattern' }
      ]
    },
    home_services: {
      id: 'home_services',
      label: 'Home services',
      keywords: ['hvac', 'plumber', 'electrician', 'roof', 'garage door', 'pest', 'lawn', 'hvac', 'heating', 'cooling', 'restoration'],
      icp: 'Homeowners with an urgent or seasonal job who will book the first operator that answers.',
      demographic: [
        { claim: 'Buyer is the homeowner or property manager on the job address.', label: 'industry pattern' },
        { claim: 'After-hours and weekend searches are a large share of inbound.', label: 'industry pattern' }
      ],
      industryAi: [
        { claim: 'Speed-to-lead on missed calls and web forms is the default first AI Employee in this category.', label: 'industry pattern' },
        { claim: 'Booking employees hold a tech’s calendar and stop unqualified “how much for…” chats from eating the day.', label: 'industry pattern' },
        { claim: 'Review-request employees fire after a completed job, not from a monthly blast.', label: 'industry pattern' },
        { claim: 'Estimate follow-up employees chase stale quotes instead of a human remembering to call back.', label: 'industry pattern' }
      ]
    },
    franchise: {
      id: 'franchise',
      label: 'Franchise / multi-unit',
      keywords: ['franchise', 'franchisor', 'territory', 'royalty', 'multi-unit', 'franchisee'],
      icp: 'Franchise candidates and existing operators who will take a discovery call if someone answers fast.',
      demographic: [
        { claim: 'Candidate is often a career-changer with capital, not a walk-in retail shopper.', label: 'industry pattern' },
        { claim: 'Existing operators care about unit-level lead response more than brand slogans.', label: 'industry pattern' }
      ],
      industryAi: [
        { claim: 'Franchise development desks use a speed-to-lead employee on FDD / apply forms.', label: 'industry pattern' },
        { claim: 'Booking employees put only funded, timeline-ready candidates on the calendar.', label: 'industry pattern' },
        { claim: 'Unit-level operators put the same two employees on local lead flow, not just HQ.', label: 'industry pattern' },
        { claim: 'Nurture employees keep “not this year” candidates without a human spreadsheet.', label: 'industry pattern' }
      ]
    },
    professional_services: {
      id: 'professional_services',
      label: 'Professional services',
      keywords: ['law', 'attorney', 'cpa', 'accountant', 'consultant', 'agency', 'advisor', 'wealth', 'insurance'],
      icp: 'A qualified buyer who will book a consult if the first reply is fast and not a generic form dump.',
      demographic: [
        { claim: 'Buyer is a business owner or household decision-maker shopping a high-consideration service.', label: 'industry pattern' },
        { claim: 'Intake is usually a form or email that sits until a human is free.', label: 'industry pattern' }
      ],
      industryAi: [
        { claim: 'Intake employees qualify matter-type / budget / timeline before a partner calendar opens.', label: 'industry pattern' },
        { claim: 'Speed-to-lead on web forms beats the 47-hour industry first-touch average (process comparison).', label: 'industry pattern' },
        { claim: 'Booking employees put only the fit on the consult calendar.', label: 'industry pattern' },
        { claim: 'No-show recovery is a separate employee, not a receptionist side task.', label: 'industry pattern' }
      ]
    },
    ecommerce: {
      id: 'ecommerce',
      label: 'Ecommerce / retail',
      keywords: ['shop', 'cart', 'shopify', 'woocommerce', 'store', 'product', 'checkout', 'sku'],
      icp: 'A shopper or wholesale buyer who abandons when nobody answers a pre-purchase question.',
      demographic: [
        { claim: 'Buyer is often mobile, after hours, and one question away from abandoning cart.', label: 'industry pattern' },
        { claim: 'Wholesale / high-ticket SKUs still need a human close after qualification.', label: 'industry pattern' }
      ],
      industryAi: [
        { claim: 'Cart-recovery employees text the abandoned checkout, not a 3-day email drip only.', label: 'industry pattern' },
        { claim: 'Pre-purchase chat employees answer size / ship / fit so the cart does not die in silence.', label: 'industry pattern' },
        { claim: 'VIP / wholesale inboxes get a speed-to-lead employee, not a shared Gmail.', label: 'industry pattern' },
        { claim: 'Review and refill employees run after delivery, not as a generic newsletter.', label: 'industry pattern' }
      ]
    },
    general: {
      id: 'general',
      label: 'Local / service business',
      keywords: [],
      icp: 'A buyer who found the site and will talk to whoever answers first.',
      demographic: [
        { claim: 'Target demographic was not locked from the homepage. Labeled until the call.', label: 'thin' },
        { claim: 'Assume inbound web or phone leads that wait on a human.', label: 'labeled estimate' }
      ],
      industryAi: [
        { claim: 'Speed-to-Lead Employee on after-hours forms is the usual first hire.', label: 'industry pattern' },
        { claim: 'Booking Employee puts only the fit on the calendar.', label: 'industry pattern' },
        { claim: 'Qualification Employee stops unqualified conversations from burning the owner.', label: 'industry pattern' },
        { claim: 'No-show recovery is the fourth common employee, not a generic “AI agent.”', label: 'industry pattern' }
      ]
    }
  };

  function classifyIndustry(text) {
    var blob = String(text || '').toLowerCase();
    var best = 'general';
    var score = 0;
    Object.keys(INDUSTRIES).forEach(function (id) {
      if (id === 'general') return;
      var n = 0;
      INDUSTRIES[id].keywords.forEach(function (k) {
        if (blob.indexOf(k) >= 0) n += 1;
      });
      if (n > score) { score = n; best = id; }
    });
    return INDUSTRIES[best];
  }

  function speedBooking(research) {
    var name = research.name || 'this business';
    var leak = research.leak || 'After-hours inquiries can sit until a human logs in.';
    var capture = research.capture || 'Lead capture method not confirmed.';
    return [
      {
        id: 'EMP-01',
        name: 'Speed-to-Lead Employee',
        finding: leak + ' ' + capture,
        workflow: 'The new lead texts in 2 seconds, nights and weekends included. Qualifies. Hands a human only what is warm.',
        loop: 'First-touch time: missed-hours → 2 seconds. Industry first-touch average is 47 hours — process comparison, not a promised lift for ' + name + '.',
        pain_point_ids: ['PAIN-after-hours'],
        justifying_finding_id: 'F-speed'
      },
      {
        id: 'EMP-02',
        name: 'Booking Employee',
        finding: name + ' still has to put the fit on a calendar. Unqualified conversations burn the close.',
        workflow: 'Only qualified conversations land on the calendar. ' + name + ' keeps the close.',
        loop: 'Booked qualified conversations / week, with no-show recovery as a later employee if the calendar dies.',
        pain_point_ids: ['PAIN-unqualified-calendar'],
        justifying_finding_id: 'F-booking'
      }
    ];
  }

  function extraEmployees(industry, research) {
    var name = research.name || 'this business';
    var map = {
      recruiting: [
        {
          id: 'EMP-03',
          name: 'Parent Qualification Employee',
          finding: 'Recruiting sites attract curious parents and ready buyers in the same form. A human consult on every click is the leak.',
          workflow: 'Asks sport, grad year, and whether they want education or a done-for-you process. Routes only the ready parent.',
          loop: 'Share of inbound parents who reach a consult already qualified on sport / year / intent.'
        },
        {
          id: 'EMP-04',
          name: 'Recruiting-Timeline Employee',
          finding: 'Education vs execute vs evaluate is the product. A generic chatbot cannot run that sequence.',
          workflow: 'Walks the parent through the stage they are in and books the next step instead of dumping a PDF.',
          loop: 'Parents who move from “education” content to a booked execute consult.'
        },
        {
          id: 'EMP-05',
          name: 'Consult No-Show Employee',
          finding: 'Booked parent consults that never happen still cost the calendar.',
          workflow: 'Confirms the consult, reschedules the miss, and keeps the slot from going quiet.',
          loop: 'Show rate on booked parent consults.'
        }
      ],
      home_services: [
        {
          id: 'EMP-03',
          name: 'Estimate Follow-Up Employee',
          finding: 'Quoted jobs that sit in the inbox are the quiet leak after speed-to-lead is fixed.',
          workflow: 'Follows the estimate until booked or dead. ' + name + ' does not rely on memory.',
          loop: 'Stale estimates touched within 24 hours.'
        },
        {
          id: 'EMP-04',
          name: 'Review-Request Employee',
          finding: 'Completed jobs that never ask for a review leave the next homeowner shopping in silence.',
          workflow: 'Asks for the review after the job, not in a monthly blast.',
          loop: 'Reviews requested / completed jobs.'
        }
      ],
      franchise: [
        {
          id: 'EMP-03',
          name: 'Candidate Qualification Employee',
          finding: 'Franchise apply forms mix tire-kickers with funded candidates.',
          workflow: 'Locks capital, timeline, and territory interest before a development calendar opens.',
          loop: 'Qualified candidates booked / apply-form submissions.'
        },
        {
          id: 'EMP-04',
          name: 'Nurture Employee',
          finding: '“Not this year” candidates die in a spreadsheet.',
          workflow: 'Keeps the candidate warm on a month-to-month cadence the brand already uses. No invented drip claims.',
          loop: 'Re-activated candidates who book a second call.'
        }
      ],
      professional_services: [
        {
          id: 'EMP-03',
          name: 'Intake Qualification Employee',
          finding: 'Web forms dump every matter onto a partner calendar.',
          workflow: 'Locks matter type, timeline, and fit before a human consult.',
          loop: 'Qualified consults / inbound forms.'
        },
        {
          id: 'EMP-04',
          name: 'Consult No-Show Employee',
          finding: 'No-shows still cost the calendar after booking is fixed.',
          workflow: 'Confirms and reschedules. ' + name + ' keeps the close.',
          loop: 'Show rate on booked consults.'
        }
      ],
      ecommerce: [
        {
          id: 'EMP-03',
          name: 'Pre-Purchase Question Employee',
          finding: 'Shoppers abandon when a size / ship / wholesale question sits in an inbox.',
          workflow: 'Answers the pre-purchase question in seconds. Hands a human the wholesale or high-ticket close.',
          loop: 'Answered pre-purchase questions / abandoned chats.'
        },
        {
          id: 'EMP-04',
          name: 'Cart Recovery Employee',
          finding: 'Abandoned checkouts are a different leak than a missed contact form.',
          workflow: 'Texts the abandoned checkout. Not a three-day email drip only.',
          loop: 'Recovered checkouts / abandoned carts (labeled until numbers are confirmed).'
        }
      ],
      general: [
        {
          id: 'EMP-03',
          name: 'Qualification Employee',
          finding: 'Unqualified conversations still reach the owner after a form is answered.',
          workflow: 'Asks the fit questions this industry actually uses. Labeled until we confirm on the call.',
          loop: 'Qualified conversations / inbound leads.'
        },
        {
          id: 'EMP-04',
          name: 'No-Show Recovery Employee',
          finding: 'Booked conversations that never happen still cost the calendar.',
          workflow: 'Confirms, reschedules, and keeps the slot from going quiet.',
          loop: 'Show rate on booked conversations.'
        }
      ]
    };
    var list = map[industry.id] || map.general;
    return list.map(function (e) {
      e.pain_point_ids = e.pain_point_ids || ['PAIN-industry'];
      e.justifying_finding_id = e.justifying_finding_id || e.id;
      return e;
    });
  }

  function demoPacket() {
    var research = {
      url: SAMPLE,
      host: 'recruiting4parents.com',
      name: 'Recruiting 4 Parents',
      what: 'Helps families run the high-school sports recruiting process — education, envision, execute, evaluate — so more athletes can reach the next level.',
      offer: 'Parent recruiting education and process support, positioned as accessible to every family.',
      capture: 'Wix site with contact / education capture. No 2-second speed-to-lead employee is visible.',
      tech: 'Wix',
      leak: 'After-hours parent inquiries can sit until someone logs into Wix.',
      fact: 'Homepage headline: “Leveling the Playing Field of High School Recruiting 4 Parents.”',
      ownerNote: 'Owner lookup is public-only and not guessed. Ask for the decision-maker on the call.',
      labeled: false,
      source: 'demo'
    };
    var industry = INDUSTRIES.recruiting;
    var employees = speedBooking(research).concat(extraEmployees(industry, research));
    research.packet = {
      route: 'research_only_lite',
      completeness_gate: 'lite',
      send_blocked: true,
      scout: {
        site: research.url,
        host: research.host,
        name: research.name,
        fact: research.fact,
        tech: research.tech,
        capture: research.capture,
        what: research.what
      },
      analyst: {
        industry: industry.label,
        industry_id: industry.id,
        icp: industry.icp,
        demographic: industry.demographic,
        pain: research.leak,
        competitors: industry.industryAi,
        labeled: false
      },
      profiler: {
        employees: employees,
        start_14_days: '$5,000 setup + $1,000/mo, month-to-month, 14-day install. Two employees live in the first week; the rest sequence after the leak is closed.'
      },
      unknowns: [
        'Decision-maker name and LinkedIn are not invented.',
        'Exact monthly lead volume is labeled until they type it.',
        'Named competitors on this homepage were not locked — industry patterns are labeled as patterns.'
      ],
      evidence_ledger: [
        { id: 'E-001', claim: research.fact, source_url: SAMPLE, dimension_tag: 'scout', confidence: 'high' },
        { id: 'E-002', claim: 'Stack signal: Wix.', source_url: SAMPLE, dimension_tag: 'scout', confidence: 'medium' },
        { id: 'E-003', claim: industry.icp, source_url: SAMPLE, dimension_tag: 'demographic', confidence: 'medium' },
        { id: 'E-004', claim: research.leak, source_url: SAMPLE, dimension_tag: 'pain', confidence: 'medium' }
      ]
    };
    return research;
  }

  function buildLitePacket(research, pageText) {
    var industry = classifyIndustry((pageText || '') + ' ' + (research.what || '') + ' ' + (research.fact || '') + ' ' + (research.host || ''));
    var employees = speedBooking(research).concat(extraEmployees(industry, research)).slice(0, 6);
    research.packet = {
      route: 'research_only_lite',
      completeness_gate: 'lite',
      send_blocked: true,
      scout: {
        site: research.url,
        host: research.host,
        name: research.name,
        fact: research.fact,
        tech: research.tech,
        capture: research.capture,
        what: research.what
      },
      analyst: {
        industry: industry.label,
        industry_id: industry.id,
        icp: industry.icp,
        demographic: industry.demographic,
        pain: research.leak,
        competitors: industry.industryAi,
        labeled: !!research.labeled || industry.id === 'general'
      },
      profiler: {
        employees: employees,
        start_14_days: '$5,000 setup + $1,000/mo, month-to-month, 14-day install.'
      },
      unknowns: [
        'Founder bio is not invented on this magnet.',
        'Demographic rows are homepage-inferred or industry pattern — labeled.',
        'Competitor names are not guessed; industry AI Employee patterns are labeled.'
      ],
      evidence_ledger: [
        { id: 'E-001', claim: research.fact, source_url: research.url, dimension_tag: 'scout', confidence: research.labeled ? 'low' : 'medium' },
        { id: 'E-002', claim: 'Industry classified as ' + industry.label, source_url: research.url, dimension_tag: 'industry', confidence: industry.id === 'general' ? 'low' : 'medium' },
        { id: 'E-003', claim: industry.demographic[0].claim, source_url: research.url, dimension_tag: 'demographic', confidence: 'low' },
        { id: 'E-004', claim: research.leak, source_url: research.url, dimension_tag: 'pain', confidence: 'medium' }
      ]
    };
    return research;
  }

  async function fetchServerLite(url) {
    var body = JSON.stringify({ url: url });
    for (var i = 0; i < RESEARCH_APIS.length; i++) {
      try {
        var ctrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
        var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 6000) : null;
        var res = await fetch(RESEARCH_APIS[i], {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: body,
          signal: ctrl ? ctrl.signal : undefined
        });
        if (timer) clearTimeout(timer);
        if (!res.ok) continue;
        var json = await res.json();
        if (json && json.research) return json.research;
      } catch (e) {}
    }
    return null;
  }

  root.AdvaitaResearch = {
    SAMPLE: SAMPLE,
    INDUSTRIES: INDUSTRIES,
    classifyIndustry: classifyIndustry,
    demoPacket: demoPacket,
    buildLitePacket: buildLitePacket,
    fetchServerLite: fetchServerLite
  };
})(typeof window !== 'undefined' ? window : this);
