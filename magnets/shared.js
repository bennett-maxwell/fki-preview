(function () {
  var PHONE = '(801) 980-0308';
  var PHONE_HREF = 'tel:+18019800308';
  var APPLY = '/apply/';
  var EMAIL = 'contact@franchiseki.com';
  var OFFER = '$5,000 setup + $1,000/mo';
  var GHL_LOC = '14RD8KklxR9G4e0Rf7v2';
  var WEBHOOK = 'https://blueprint-ghl-relay.vercel.app/api/blueprint-lead';
  var SAMPLE = 'https://recruiting4parents.com';
  var HIRE_FIRST_MONTH = 6000;
  var HUMAN_STACK = 20500;
  var AI_STACK = 1000;

  var DEMO = {
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
    labeled: false
  };

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function qs(name) {
    try { return new URLSearchParams(location.search).get(name) || ''; }
    catch (e) { return ''; }
  }
  function fire(name, detail) {
    var payload = Object.assign({ event: name, ts: new Date().toISOString(), page: document.body.getAttribute('data-magnet') }, detail || {});
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(payload);
    try { window.dispatchEvent(new CustomEvent('advaita-magnet', { detail: payload })); } catch (e) {}
    try { console.debug('magnet_event', payload); } catch (e2) {}
  }
  function money(n) {
    n = Math.round(Number(n) || 0);
    return n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  }
  function hostOf(url) {
    try { return new URL(normalizeUrl(url)).hostname.replace(/^www\./, ''); }
    catch (e) { return ''; }
  }
  function normalizeUrl(raw) {
    var u = String(raw || '').trim();
    if (!u) return '';
    if (!/^https?:\/\//i.test(u)) u = 'https://' + u;
    return u;
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    var ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    return Promise.resolve();
  }
  var VOICE_APIS = [
    'https://advaita-research-lite.vercel.app/api/voice',
    'https://blueprint-ghl-relay.vercel.app/api/voice'
  ];
  var voiceAudio = null;
  var voiceMuted = false;
  var voiceCache = {};

  function voiceApis() {
    var list = VOICE_APIS.slice();
    try {
      if (location.origin && !/github\.io$|aiblueprintmarketing\.com$|pages\.dev$/i.test(location.hostname)) {
        list.unshift(location.origin + '/api/voice');
      }
    } catch (e) {}
    return list;
  }
  function setSpeaking(on) {
    $all('.orb').forEach(function (o) { o.classList.toggle('speaking', !!on); });
  }
  function stopVoice() {
    if (voiceAudio) {
      try { voiceAudio.pause(); voiceAudio.src = ''; } catch (e) {}
      voiceAudio = null;
    }
    setSpeaking(false);
  }
  function playUrl(url, kind) {
    stopVoice();
    voiceAudio = new Audio(url);
    voiceAudio.onended = function () { fire('voice_complete', { kind: kind || 'elevenlabs' }); setSpeaking(false); };
    voiceAudio.onerror = function () { setSpeaking(false); };
    setSpeaking(true);
    return voiceAudio.play();
  }
  function playBlob(blob) {
    return playUrl(URL.createObjectURL(blob), 'elevenlabs');
  }
  function staticVoiceUrl(text) {
    var t = String(text || '');
    var pack = {
      'Got it. What is the name of the business?': 'ask-biz.mp3',
      'Do you have a website? Paste it or say it — I will pull the homepage, the industry, and what the top operators in that space are doing with AI Employees.': 'ask-url.mp3',
      'No site is fine — I will keep estimates labeled. How quickly does someone on your team contact a new lead today — minutes, hours, or next day?': 'no-site.mp3',
      'Paste the site as yourcompany.com and I will open it. Or say skip.': 'paste-site.mp3',
      'Still opening the page. One more beat.': 'still-opening.mp3',
      'How quickly does someone on your team contact a new lead today — minutes, hours, or next day?': 'ask-speed.mp3',
      'Roughly how many new leads do you get in a typical month from ads plus the website?': 'ask-volume.mp3',
      'What is a typical closed job or sale worth in dollars?': 'ask-ticket.mp3',
      'I opened the site. Want to try the first AI Employee live for your business?': 'pitch-plan.mp3',
      'I have the leak in dollars. Want to try the employee live for your business?': 'pitch-calculator.mp3',
      'I scored the worst leak. Want to try that employee live?': 'pitch-score.mp3',
      'You are now a new lead. I am the first AI Employee. This is a demo on this page, not a recording of a live customer call, and I will not invent a calendar link. Go ahead. Say why you are calling.': 'roleplay.mp3',
      'Thanks for calling. I can get you a qualified conversation with the owner. What are you hoping to get done — a new job, a quote, or a question on something already open?': 'roleplay-1.mp3',
      'Got it. I am holding a callback from the owner, not a fake calendar hold. Live install confirms by phone at 801 980 0308. Anything else I should pass to them before I wrap this demo?': 'roleplay-2.mp3',
      'That was the live demo — you just felt the employee, not a form. Real install is 5,000 dollars setup plus 1,000 a month, month-to-month, 14 days. Calendly on file is 404, so I will not invent a link. Call 801 980 0308 or use apply.': 'debrief.mp3'
    };
    if (pack[t]) return '/magnets/audio/' + pack[t] + '?v=20260820d';
    if (t.indexOf('What should I call you') >= 0) {
      if (t.indexOf('score the leak') >= 0) return '/magnets/audio/opener-score.mp3?v=20260820d';
      if (t.indexOf('take your numbers') >= 0) return '/magnets/audio/opener-calculator.mp3?v=20260820d';
      return '/magnets/audio/opener-plan.mp3?v=20260820d';
    }
    if (t.indexOf('Give me about ten seconds') === 0) return '/magnets/audio/researching.mp3?v=20260820d';
    return '';
  }
  async function elevenSpeak(text) {
    var body = JSON.stringify({ text: text });
    var apis = voiceApis();
    var i;
    for (i = 0; i < apis.length; i += 1) {
      try {
        var res = await fetch(apis[i], {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: body
        });
        if (!res.ok) continue;
        var blob = await res.blob();
        if (!blob || blob.size < 800) continue;
        voiceCache[text] = blob;
        return playBlob(blob);
      } catch (e) {}
    }
    return null;
  }
  function speak(text) {
    var t = String(text || '').replace(/<break\b[^>]*>/gi, ' ').replace(/\s+/g, ' ').trim();
    if (!t || voiceMuted) { fire('voice_skipped', { reason: voiceMuted ? 'muted' : 'empty' }); return; }
    fire('voice_start', { kind: 'elevenlabs' });
    if (voiceCache[t]) { playBlob(voiceCache[t]); return; }
    var packed = staticVoiceUrl(t);
    if (packed) {
      playUrl(packed, 'elevenlabs-static').catch(function () { elevenSpeak(t); });
      return;
    }
    elevenSpeak(t).then(function (played) {
      if (played) return;
      fire('voice_fallback', { kind: 'silent' });
      setSpeaking(false);
    });
  }
  function listenOnce(onText) {
    var Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Rec) { onText(''); return; }
    fire('voice_start', { kind: 'stt' });
    var rec = new Rec();
    rec.lang = 'en-US';
    rec.interimResults = false;
    rec.onresult = function (ev) {
      var t = ev.results[0][0].transcript;
      fire('voice_complete', { kind: 'stt' });
      onText(t);
    };
    rec.onerror = function () { onText(''); };
    rec.start();
  }

  async function researchUrl(raw, opts) {
    opts = opts || {};
    var AR = window.AdvaitaResearch;
    var url = normalizeUrl(raw);
    var host = hostOf(url);
    if (opts.demo || host === 'recruiting4parents.com') {
      return AR && AR.demoPacket ? AR.demoPacket() : Object.assign({ url: url || SAMPLE }, DEMO);
    }
    if (!url) return null;
    if (AR && AR.fetchServerLite) {
      var server = await AR.fetchServerLite(url);
      if (server && server.packet) return server;
    }
    var out = {
      url: url,
      host: host,
      name: host,
      what: 'This looks like ' + host + '. Exact offer copy was not readable from this browser, so the plan uses labeled estimates until we confirm on the call.',
      offer: 'Offer signal not confirmed from this fetch.',
      capture: 'Lead capture method not confirmed. Typical leak: form or phone sitting until a human is free.',
      tech: 'Not confirmed',
      leak: 'Speed-to-lead: if nobody answers after hours, the lead goes cold.',
      fact: 'We opened ' + host + ' as the working site.',
      ownerNote: 'Owner / LinkedIn lookup is public-only and not invented.',
      labeled: true
    };
    var pageText = '';
    var proxies = [
      'https://r.jina.ai/http://' + host,
      'https://api.allorigins.win/raw?url=' + encodeURIComponent(url)
    ];
    for (var i = 0; i < proxies.length; i++) {
      try {
        var ctrl = typeof AbortController !== 'undefined' ? new AbortController() : null;
        var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 8000) : null;
        var res = await fetch(proxies[i], ctrl ? { signal: ctrl.signal } : {});
        if (timer) clearTimeout(timer);
        if (!res.ok) continue;
        var text = await res.text();
        pageText = text.slice(0, 8000);
        var title = (text.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || text.match(/^#\s+(.+)$/m) || [])[1];
        var desc = (text.match(/name=["']description["']\s+content=["']([^"']+)/i) || text.match(/og:description["']\s+content=["']([^"']+)/i) || [])[1];
        title = title ? title.replace(/\s+/g, ' ').trim() : '';
        desc = desc ? desc.replace(/\s+/g, ' ').trim() : '';
        if (title) {
          out.name = title.split('|')[0].trim();
          out.fact = 'Page title: “' + title.slice(0, 140) + '.”';
          out.what = desc ? desc.slice(0, 220) : ('Public title on ' + host + ': ' + title.slice(0, 140));
          out.labeled = false;
          if (/wix/i.test(text)) out.tech = 'Wix';
          if (/wordpress|wp-content/i.test(text)) out.tech = 'WordPress';
          if (/shopify/i.test(text)) out.tech = 'Shopify';
          if (/gohighlevel|leadconnector/i.test(text)) out.tech = 'GoHighLevel';
          if (/form|contact|schedule|book/i.test(text)) out.capture = 'A form or booking control is visible. The leak is still how fast a human answers it.';
          break;
        }
      } catch (e) {}
    }
    if (AR && AR.buildLitePacket) return AR.buildLitePacket(out, pageText);
    return out;
  }

  function wowPoints(research, answers) {
    answers = answers || {};
    var leads = Number(answers.leads) || 40;
    var value = Number(answers.value) || 5000;
    var conv = Number(answers.conv) || 40;
    var close = Number(answers.close) || 20;
    var leadsLabeled = !answers.leads;
    var monthlyUnspoken = leads * (1 - conv / 100);
    var monthlyLeak = monthlyUnspoken * value * (close / 100);
    var name = answers.person || 'you';
    var company = (research && research.name) || 'your company';
    return [
      {
        t: 'What we opened on ' + (research.host || 'your site'),
        d: research.fact + ' ' + research.what + (research.labeled ? ' Labeled until we confirm on the call.' : '')
      },
      {
        t: 'Where the lead sits unanswered',
        d: research.capture + (research.tech !== 'Not confirmed' ? ' Stack signal: ' + research.tech + '.' : '') +
          ' Industry first-touch average is 47 hours. Target comparison is 2 seconds. Process claim, not a promised lift for ' + company + '.'
      },
      {
        t: 'Unspoken-lead math for ' + name,
        d: (leadsLabeled ? 'Labeled estimates: ' : 'Your numbers: ') +
          leads + ' leads / month × ' + (100 - conv) + '% with no real conversation × ' + money(value) +
          ' × ' + close + '% close ≈ ' + money(monthlyLeak) + ' / month sitting in silence. Full formula is on the leak calculator.'
      },
      {
        t: 'Two AI Employees on that leak',
        d: 'Speed-to-Lead Employee texts and qualifies in 2 seconds. Booking Employee puts only the fit on the calendar. Noun: AI Employees. Not agents. ' + company + ' keeps the close.'
      },
      {
        t: '14-day install at the locked offer',
        d: OFFER + ', month-to-month. Named proof: Anthony’s ad employee + lead employee paid the hire back in under 30 days. $140,000 collected was his baseline before the hire — not Advaita’s win. ' + research.ownerNote
      }
    ];
  }

  function leakMath(a) {
    var leads = Number(a.leads) || 0;
    var value = Number(a.value) || 0;
    var conv = Number(a.conv) || 0;
    var close = Number(a.close) || 20;
    var unspoken = leads * (1 - conv / 100);
    var monthly = unspoken * value * (close / 100);
    var yearly = monthly * 12;
    var jobs = value > 0 ? Math.ceil(HIRE_FIRST_MONTH / value) : null;
    return { leads: leads, value: value, conv: conv, close: close, unspoken: unspoken, monthly: monthly, yearly: yearly, jobs: jobs };
  }

  function auditFrom(research, chips) {
    var score = 100;
    var notes = [];
    chips = chips || [];
    if (chips.indexOf('after-hours') >= 0) { score -= 22; notes.push({ k: 'After-hours', n: 'Leads that arrive when nobody is working wait until morning.' }); }
    if (chips.indexOf('slow') >= 0) { score -= 18; notes.push({ k: 'Slow follow-up', n: 'First touch in hours or the next day, not seconds.' }); }
    if (chips.indexOf('unqualified') >= 0) { score -= 14; notes.push({ k: 'Unqualified on the calendar', n: 'Humans spend the appointment on people who were never a fit.' }); }
    if (chips.indexOf('noshow') >= 0) { score -= 12; notes.push({ k: 'No-shows', n: 'Booked conversations that never happen still cost the calendar.' }); }
    if (research && research.tech === 'Wix') { score -= 8; notes.push({ k: 'Site stack', n: 'Wix capture without a 2-second AI Employee is a typical leak.' }); }
    if (research && research.labeled) { score -= 6; notes.push({ k: 'Unknown capture', n: 'We could not confirm the form. Score uses homepage-only signals and your chips.' }); }
    if (score < 8) score = 8;
    if (!notes.length) notes.push({ k: 'Baseline', n: 'Paste a URL or tap a leak chip to personalize this score.' });
    notes.sort(function (x, y) { return 1; });
    var worst = notes[0];
    return { score: score, notes: notes, worst: worst };
  }

  function persistIdentity(d) {
    var identity = {
      firstName: d.firstName || '',
      lastName: d.lastName || '',
      email: d.email || '',
      phone: d.phone || '',
      businessName: d.businessName || '',
      website: d.website || '',
      source: d.source || 'magnet',
      magnet: document.body.getAttribute('data-magnet') || '',
      updatedAt: new Date().toISOString()
    };
    try { localStorage.setItem('advaitaMagnetIdentity', JSON.stringify(identity)); } catch (e) {}
    return identity;
  }

  async function captureContact(d) {
    var identity = persistIdentity(d);
    var payload = {
      event_name: 'blueprint_magnet_complete',
      form_version: '2026-08-19-magnet-v1',
      locationId: GHL_LOC,
      firstName: identity.firstName,
      lastName: identity.lastName,
      email: identity.email,
      phone: identity.phone,
      businessName: identity.businessName,
      website: identity.website,
      source: 'blueprint_ai_magnet_' + identity.magnet,
      magnet: identity.magnet,
      note: d.note || '',
      submitted_at: new Date().toISOString()
    };
    try {
      var response = await fetch(WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('webhook ' + response.status);
      fire('form_complete', { magnet: identity.magnet, relay: 'ok' });
    } catch (e) {
      try { localStorage.setItem('advaitaApplyPending_' + Date.now(), JSON.stringify(payload)); } catch (err) {}
    }
  }

  function navHtml(active) {
    var links = [
      ['/magnets/', 'Doors', 'hub'],
      ['/plan/', 'Wow Plan', 'plan'],
      ['/calculator/', 'Leak math', 'calculator'],
      ['/score/', '60-sec audit', 'score'],
      ['/anthony/', 'Anthony', 'anthony'],
      ['/apply/', 'Full blueprint', 'apply']
    ];
    return '<a class="skip" href="#main">Skip to content</a><div class="nav-shell"><nav><a class="nav-logo" href="/magnets/">Advaita <span>AI</span></a><div class="nav-links">' +
      links.map(function (l) {
        return '<a href="' + l[0] + '"' + (active === l[2] ? ' class="active"' : '') + '>' + l[1] + '</a>';
      }).join('') +
      '<a class="nav-call" href="' + PHONE_HREF + '">Call ' + PHONE + '</a></div></nav></div>';
  }

  function jabStripHtml() {
    return '<div class="jab-strip">' +
      '<div class="jab"><b>Door 1</b><span>Site research — 20 expert angles, labeled</span></div>' +
      '<div class="jab"><b>Door 2</b><span>Leak math from your numbers</span></div>' +
      '<div class="jab"><b>Door 3</b><span>Follow-up score in 60 seconds</span></div>' +
      '<div class="jab jab-hook"><b>Then the ask</b><span>Call ' + PHONE + ' — Calendly is 404</span></div></div>';
  }

  function trustRowHtml() {
    return '<div class="trust-row" aria-label="Proof and locks">' +
      '<div><b>Named proof</b><span>Anthony’s hire paid back in under 30 days</span></div>' +
      '<div><b>Locked offer</b><span>' + OFFER + ' · 14 days · month-to-month</span></div>' +
      '<div><b>Public noun</b><span>AI Employees, not agents</span></div>' +
      '<div><b>Voice</b><span>ElevenLabs — not the browser robot</span></div></div>';
  }

  function faqHtml(magnet) {
    var q = {
      plan: [
        ['What do I walk out with?', 'A labeled industry report: who they sell to, 20 expert angles on the site, and which AI Employees fit. Then a live role-play. No invented lift.'],
        ['Is the voice a real person?', 'ElevenLabs. It is an AI Employee demo, not a recording of a live customer call, and not Cody’s personal clone.'],
        ['Do you scrape things nobody else can?', 'We open the public homepage and run 20 expert methods (CRO, SEO, stack, capture, tracking, ICP). We label every thin row. Full DEEP website-audit-skill is after /apply/.'],
        ['What happens if I call?', 'A human. Calendly on file is 404, so we will not invent a link.']
      ],
      calculator: [
        ['Is the leak a forecast?', 'No. It is your numbers × the formula on the page. Hire payback is labeled.'],
        ['Can I skip the globe?', 'Yes. Type the numbers. The globe is the interview, not a gate.']
      ],
      score: [
        ['Is 0–100 a certified audit?', 'No. It is a 60-second follow-up score from chips you tap plus homepage signals.'],
        ['What is the one thing?', 'The worst leak chip. That is the employee we role-play.']
      ]
    };
    var rows = q[magnet] || q.plan;
    return '<section class="faq" id="faq"><h2>Before you call</h2>' + rows.map(function (row) {
      return '<details><summary>' + row[0] + '</summary><p>' + row[1] + '</p></details>';
    }).join('') + '</section>';
  }

  function hookCtaHtml(prefix, line) {
    return '<div class="cta-dark sticky-cta" id="' + prefix + '-hook"><p>' + (line || 'You already have the value. The ask is a call.') + '</p>' +
      '<div class="actions"><a class="btn btn-light" href="' + PHONE_HREF + '" id="' + prefix + '-call">Call ' + PHONE + '</a>' +
      '<a class="btn btn-ghost" href="' + APPLY + '" id="' + prefix + '-apply">Full blueprint</a></div></div>';
  }

  function shareLineHtml(id) {
    return '<div class="share-line"><button class="btn btn-ghost" type="button" id="' + id + '">Copy this result</button></div>';
  }

  function leakBarHtml(yearly) {
    var hire = HIRE_FIRST_MONTH;
    var max = Math.max(yearly, hire, 1);
    var yPct = Math.min(100, Math.round((yearly / max) * 100));
    var hPct = Math.min(100, Math.round((hire / max) * 100));
    return '<div class="leak-compare">' +
      '<div class="leak-row"><span>Yearly unspoken leak (your math)</span><b>' + money(yearly) + '</b></div>' +
      '<div class="leak-track"><i style="width:' + yPct + '%"></i></div>' +
      '<div class="leak-row"><span>First-month hire — labeled, not a forecast</span><b>' + money(hire) + '</b></div>' +
      '<div class="leak-track hire"><i style="width:' + hPct + '%"></i></div></div>';
  }

  function bindShare(id, textFn) {
    var b = $('#' + id);
    if (!b) return;
    b.onclick = function () {
      copyText(textFn()).then(function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy this result'; }, 1500); });
    };
  }

  function cardOpen(label) {
    return '<div class="card"><div class="card-bar">' + label + '</div><div class="card-body">';
  }
  function cardClose() { return '</div></div>'; }

  function stepsHtml(pts) {
    return pts.map(function (p, idx) {
      return '<div class="step"><div class="step-num">' + (idx + 1) + '</div><div><h3>' + p.t + '</h3><p>' + p.d + '</p></div></div>';
    }).join('');
  }

  function timelineHtml(firstName) {
    var day1 = firstName
      ? ('<strong>Day 1</strong> — first employee on the lead flow: ' + esc(firstName) + '.')
      : '<strong>Day 1</strong> — first AI Employee configured on your lead flow.';
    return '<div class="timeline"><p>What comes after</p>' +
      '<div class="t-row"><div class="t-dot"></div><div>' + day1 + '</div></div>' +
      '<div class="t-row"><div class="t-dot"></div><div><strong>Day 7</strong> — they are live: contact, qualify, book.</div></div>' +
      '<div class="t-row"><div class="t-dot"></div><div><strong>Day 14</strong> — install complete. Month-to-month after that.</div></div></div>';
  }

  function calendarHtml() {
    var html = '<div class="cal">';
    var d;
    for (d = 1; d <= 14; d += 1) {
      var cls = d <= 3 ? 'on' : (d <= 7 ? 'mid' : '');
      html += '<span class="cal-day ' + cls + '">' + d + '</span>';
    }
    return html + '</div><p class="cal-legend"><b>1–3</b> onboard &nbsp; <b>4–7</b> live &nbsp; <b>8–14</b> install complete</p>';
  }

  function tag(label) {
    return '<span class="tag">' + esc(label) + '</span>';
  }

  function employeeCardsHtml(employees) {
    employees = employees || [];
    return '<div class="emp-grid emp-grid-3">' + employees.map(function (e) {
      return '<div class="emp"><h3>' + esc(e.name) + '</h3>' +
        '<p><strong>Finding.</strong> ' + esc(e.finding) + '</p>' +
        '<p><strong>Workflow.</strong> ' + esc(e.workflow) + '</p>' +
        '<p><strong>Loop.</strong> ' + esc(e.loop) + '</p></div>';
    }).join('') + '</div>';
  }

  function reportHtml(research, answers) {
    answers = answers || {};
    var packet = research.packet || {};
    var scout = packet.scout || {};
    var analyst = packet.analyst || {};
    var profiler = packet.profiler || {};
    var employees = (profiler.employees || []).slice(0, 6);
    var leads = Number(answers.leads) || 40;
    var value = Number(answers.value) || 5000;
    var conv = Number(answers.conv) || 40;
    var close = Number(answers.close) || 20;
    var monthlyLeak = leads * (1 - conv / 100) * value * (close / 100);
    var labeled = !answers.leads;
    var who = answers.person || 'the operator of ' + (research.name || 'this business');
    var date = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    var demoRows = (analyst.demographic || []).map(function (d) {
      return '<li>' + esc(d.claim) + ' ' + tag(d.label) + '</li>';
    }).join('');
    var compRows = (analyst.competitors || []).map(function (c) {
      return '<li>' + esc(c.claim) + ' ' + tag(c.label) + '</li>';
    }).join('');
    var angleRows = (analyst.angles || []).map(function (a) {
      return '<li><strong>' + esc(a.method) + '</strong> · ' + esc(a.brain || '') +
        '<br>' + esc(a.found || a.looked_at || '') +
        (a.not_invented ? '<br><span class="tiny">' + esc(a.not_invented) + '</span>' : '') +
        ' ' + tag(a.label || 'labeled') + '</li>';
    }).join('');
    return '<p class="kicker">Industry research report</p>' +
      '<div class="doc-hero"><h2>' + esc(research.name) + ' — who they sell to, and which AI Employees fit</h2>' +
      '<p class="who">Prepared for ' + esc(who) + ' · ' + esc(research.host) + ' · ' + date + '</p></div>' +
      '<p class="pull">' + esc(research.fact) + '</p>' +
      '<p class="tiny proof-line">Named proof: Anthony’s hire paid back in under 30 days. $140,000 collected was his baseline before the hire — not Advaita’s win.</p>' +
      '<p class="kicker">What we opened</p>' +
      '<p class="muted" style="margin:0 0 24px">' + esc(scout.what || research.what) +
      (scout.tech && scout.tech !== 'Not confirmed' ? ' Stack signal: ' + esc(scout.tech) + '.' : '') +
      ' ' + esc(scout.capture || research.capture) + '</p>' +
      '<p class="kicker">Who they sell to</p>' +
      '<p class="muted" style="margin:0 0 8px"><strong>Industry.</strong> ' + esc(analyst.industry || 'Not locked') +
      (analyst.labeled ? ' ' + tag('labeled') : '') + '</p>' +
      '<p class="muted" style="margin:0 0 8px"><strong>ICP.</strong> ' + esc(analyst.icp || '') + '</p>' +
      '<ul class="report-list">' + demoRows + '</ul>' +
      '<p class="kicker">What similar operators do with AI Employees</p>' +
      '<ul class="report-list">' + compRows + '</ul>' +
      (angleRows ? '<p class="kicker">20 expert angles — what we actually opened</p><ul class="report-list angle-list">' + angleRows + '</ul>' : '') +
      '<div class="money-hero"><b>' + money(monthlyLeak) + '/mo</b>' +
      '<span>' + (labeled ? 'Labeled unspoken-lead math from homepage signals — not a forecast of your return.' : 'Unspoken-lead math from the numbers you entered — not a forecast of your return.') +
      ' Full formula is on the leak calculator. Process comparison: industry first-touch average 47 hours vs 2-second target.</span></div>' +
      '<p class="kicker">AI Employees for this industry</p>' +
      employeeCardsHtml(employees) +
      '<p class="kicker">How to start in 14 days</p>' +
      calendarHtml() +
      timelineHtml(employees[0] && employees[0].name) +
      (employees[0] ? '<div class="one-thing"><h3>Walk out with Day 1 named</h3><p>First employee: <strong>' + esc(employees[0].name) + '</strong>. ' + esc(employees[0].loop || employees[0].workflow || '') + '</p></div>' : '') +
      shareLineHtml('share-plan') +
      '<p class="muted" style="margin:0 0 16px">' + esc(profiler.start_14_days || (OFFER + ', month-to-month, 14-day install.')) + '</p>' +
      '<div class="invest"><div><p class="kicker" style="margin:0">Locked offer</p><strong>' + OFFER + '</strong></div>' +
      '<div style="text-align:right"><p class="kicker" style="margin:0">After that</p><strong>Month-to-month</strong></div></div>' +
      '<p class="tiny" style="margin:0 0 16px">Named proof: Anthony’s ad employee + lead employee paid the hire back in under 30 days. $140,000 collected was his baseline before the hire — not Advaita’s win. ' +
      esc(research.ownerNote) + ' Founder bio is not invented on this magnet.</p>' +
      '<div class="cta-dark sticky-cta"><p>Ready to run this on live leads. Calendly on file returned 404 today — call or use the blueprint form.</p>' +
      '<div class="actions"><a class="btn btn-light" href="' + PHONE_HREF + '" id="plan-call">Call ' + PHONE + '</a>' +
      '<a class="btn btn-ghost" href="' + APPLY + '" id="plan-apply">Full blueprint</a>' +
      '<button class="btn btn-ghost" id="hear" type="button">Hear the report</button>' +
      '<button class="btn btn-ghost" id="one-pager" type="button">Download one-pager</button>' +
      '<button class="btn btn-ghost" id="ask-cody" type="button">Talk to the orb</button>' +
      '<button class="btn btn-ghost" id="save-plan" type="button">Save this report</button>' +
      '<button class="btn btn-ghost" id="another" type="button">Another site</button></div></div>';
  }

  function blueprintHtml(research, answers, pts) {
    return reportHtml(research, answers);
  }

  function onePagerHtml(research, answers) {
    return '<!DOCTYPE html><html><head><meta charset="utf-8"><title>' + esc(research.name) + ' — AI Employee report</title>' +
      '<style>body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#1D1D1F;max-width:720px;margin:40px auto;padding:0 24px;line-height:1.5}' +
      'h1{font-size:22px}h2{font-size:13px;letter-spacing:2px;text-transform:uppercase;color:#6E6E73} .bar{background:#0071E3;color:#fff;padding:12px 16px;font-size:12px;letter-spacing:2px;text-transform:uppercase}' +
      '.emp{border-top:4px solid #0071E3;background:#F5F5F7;padding:12px;margin:8px 0} .tiny{color:#6E6E73;font-size:12px}</style></head><body>' +
      '<div class="bar">Advaita AI · Industry research report</div>' +
      reportHtml(research, answers).replace(/<button[\s\S]*?<\/button>/g, '').replace(/id="[^"]*"/g, '') +
      '<p class="tiny">Offer ' + OFFER + ' · Noun: AI Employees · ' + PHONE + '</p></body></html>';
  }

  function extractSite(t) {
    var m = String(t || '').match(/(?:https?:\/\/)?(?:www\.)?([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+)/i);
    if (!m) return '';
    var host = m[1].toLowerCase();
    if (/\.(png|jpe?g|gif|webp|svg|js|css|pdf)$/.test(host)) return '';
    if (host.indexOf('.') < 0) return '';
    return m[0];
  }

  function firstNameOf(t) {
    var s = String(t || '').replace(/["']/g, '').trim();
    s = s.replace(/^(hey|hi|hello|yo)[,!.\s]+/i, '');
    s = s.replace(/^(i('?m| am)|my name is|this is|it'?s|call me)\s+/i, '');
    var tok = (s.split(/[\s,]+/)[0] || '').replace(/[^A-Za-z'-]/g, '');
    if (tok.length < 2 || /^(yes|yeah|yep|no|nope|ok|okay|sure|hi|hey|please)$/i.test(tok)) return '';
    return tok.charAt(0).toUpperCase() + tok.slice(1).toLowerCase();
  }

  function youLine(s) { return s && s.person ? s.person : 'there'; }

  function lockReply(msg) {
    var m = String(msg || '').toLowerCase();
    if (/price|cost|how much|offer|invest/.test(m)) {
      return 'Locked offer is ' + OFFER + ', month-to-month, 14-day install. Not a custom quote from me. Call ' + PHONE + ' or use /apply/.';
    }
    if (/anthony|proof|140|result/.test(m)) {
      return '$140,000 collected was Anthony’s baseline before the hire. One sale through the ad employee plus lead employee paid the hire back in under 30 days. Not typical. Not a guarantee. Do not quote him.';
    }
    if (/calendly|booking link|appointment link/.test(m)) {
      return 'Calendly on file returned 404 today. I will not invent a link. Call ' + PHONE + ' or open /apply/.';
    }
    if (/\bagents?\b/.test(m) && !/ai employee/.test(m)) {
      return 'Public noun is AI Employees. Not agents. Speed-to-Lead and Booking are the first two; the rest are industry-specific.';
    }
    if (/emergency/.test(m)) {
      return 'This globe talks to the business owner, not a homeowner emergency line. I will not ask if this is an emergency.';
    }
    return null;
  }

  function globeOpenerSpoken(magnet) {
    var door = {
      plan: 'I will pull your site and we can role-play the first AI Employee.',
      calculator: 'I will take your numbers, then role-play the employee that stops the leak.',
      score: 'I will score the leak, then role-play the employee that fixes it first.'
    };
    return 'Hey — I am Cody, an Advaita AI Employee. I talk to owners, not homeowners, and I do not ask if this is an emergency. ' +
      (door[magnet] || door.plan) + ' What should I call you?';
  }

  function globeOpener(magnet) {
    var door = {
      plan: 'I will pull your site, name the AI Employees that fit, then we can role-play the first one.',
      calculator: 'I will take your lead numbers, show the unspoken leak in dollars, then we can role-play the employee that stops it.',
      score: 'I will score the follow-up leak, name the one thing to fix first, then we can role-play that employee.'
    };
    return 'Hey — I am Cody, an Advaita AI Employee. I help owners run the parts of the business that leak: first touch, old-lead reactivation, follow-up, reviews. I am not a homeowner emergency line and I do not ask if this is an emergency. ' +
      (door[magnet] || door.plan) +
      ' I can set this up for your specific business in about a minute if you answer a few questions. What should I call you?';
  }

  function salesBrief(research) {
    var bits = [
      'I am Cody, an Advaita AI Employee — talking to the owner, not a homeowner.',
      'Offer is ' + OFFER + ', month-to-month, 14-day install.',
      'Anthony’s $140,000 was his baseline before the hire. One sale paid the hire back in under 30 days. Not typical.',
      'Calendly is 404. Call ' + PHONE + ' or use /apply/.',
      'I will not invent a booking link.'
    ];
    if (research && research.packet) {
      bits.push('I already opened ' + research.host + '. Industry: ' + research.packet.analyst.industry + '.');
      bits.push(research.fact);
    } else {
      bits.push('Say your name, the business, and a website. I will open a research report — industry, who they sell to, and AI Employees that fit — then we role-play.');
    }
    return bits.join(' ');
  }

  function firstEmployeeName(research) {
    var emps = research && research.packet && research.packet.profiler && research.packet.profiler.employees;
    return (emps && emps[0] && emps[0].name) || 'Speed-to-Lead';
  }

  function magnetPitch(s) {
    var r = (s && s.research) || window.__research || null;
    var name = youLine(s);
    var biz = (s && s.biz) || (r && r.name) || 'your business';
    var industry = (r && r.packet && r.packet.analyst && r.packet.analyst.industry) || 'this industry';
    var fact = (r && r.fact) || '';
    var host = (r && r.host) || (s && s.url) || '';
    var first = firstEmployeeName(r);
    var opened = host ? ('I just opened ' + host + '. ') : '';
    var siteBit = fact ? (fact + ' ') : '';
    if (s && s.magnet === 'calculator') {
      return name + ', ' + opened + siteBit + (s.leakLine || '') +
        ' Owners in ' + industry + ' already use AI Employees to touch new leads in about a minute instead of hours. Want to try it live — you be the customer, I will be that employee for ' + biz + '?';
    }
    if (s && s.magnet === 'score') {
      var worst = (s && s.worst) || 'slow follow-up';
      return name + ', ' + opened + siteBit + (s.scoreLine || '') +
        ' The one thing to fix first is ' + worst + '. Want to try it live — you be the customer, I will be the ' + worst + ' employee for ' + biz + '?';
    }
    return name + ', ' + opened + siteBit +
      'Industry read: ' + industry + '. Top operators in this space already use AI Employees to contact new leads inside a minute and keep follow-up from dying after hours. For ' + biz + ' I would start with ' + first +
      '. Want to try it live — you be the customer, I will be that employee?';
  }

  function magnetPitchSpoken(s) {
    if (s && s.magnet === 'calculator') return 'I have the leak in dollars. Want to try the employee live for your business?';
    if (s && s.magnet === 'score') return 'I scored the worst leak. Want to try that employee live?';
    return 'I opened the site. Want to try the first AI Employee live for your business?';
  }

  function tapScoreChips(msg) {
    var low = String(msg || '').toLowerCase();
    $all('.chip[data-k]').forEach(function (c) {
      var k = c.getAttribute('data-k');
      if (k === 'after-hours' && /after.?hours|nights|weekend|5 ?p\.?m/.test(low)) c.classList.add('on');
      if (k === 'slow' && /slow|hours later|next day|tomorrow/.test(low)) c.classList.add('on');
      if (k === 'unqualified' && /unqualif|tire.?kicker|window shop/.test(low)) c.classList.add('on');
      if (k === 'noshow' && /no.?show|ghost|no show/.test(low)) c.classList.add('on');
    });
  }

  function roleplayOpener(s) {
    var biz = (s && s.biz) || (s && s.research && s.research.name) || 'the business';
    var role = (s && s.worst) || firstEmployeeName(s && s.research) || 'Speed-to-Lead';
    var lead = (s && s.person) ? (s.person + ' — ') : '';
    return lead + 'You are now a new lead calling ' + biz + '. I am the ' + role + ' AI Employee. This is a demo on this page, not a recording of a live customer call, and I will not invent a calendar link. Go ahead. Say why you are calling.';
  }

  function roleplayDebrief(s) {
    var biz = (s && s.biz) || (s && s.research && s.research.name) || 'your business';
    return (s && s.person ? (s.person + ', ') : '') + 'that was the live demo — you just felt the employee, not a form. This globe is a page demo, not a recorded live customer call. Real install for ' + biz + ' is ' + OFFER + ', month-to-month, 14 days. Calendly on file is 404, so I will not invent a link. Call ' + PHONE + ' or use /apply/. I can also save this conversation if you drop an email.';
  }

  function roleplayReply(s, msg) {
    var biz = (s && s.biz) || (s && s.research && s.research.name) || 'the business';
    var name = youLine(s);
    s.roleTurns = (s.roleTurns || 0) + 1;
    if (s.roleTurns === 1) {
      var industry = s.research && s.research.packet && s.research.packet.analyst && s.research.packet.analyst.industry;
      var ind = industry ? ('For a ' + industry + ' lead, ') : '';
      return 'Thanks for calling ' + biz + ', ' + name + '. ' + ind + 'I can get you a qualified conversation with the owner. What are you hoping to get done — a new job, a quote, or a question on something already open?';
    }
    if (s.roleTurns === 2) {
      return 'Got it. I am holding a callback from the owner, not a fake calendar hold. Live install confirms by phone at ' + PHONE + '. Anything else I should pass to them before I wrap this demo?';
    }
    s.phase = 'close';
    return roleplayDebrief(s);
  }

  function globeHtml(magnet) {
    var status = {
      plan: 'Tap the globe. Cody asks a few owner questions, pulls your site, then role-plays the first AI Employee.',
      calculator: 'Tap the globe. Cody takes your numbers, names the leak, then role-plays the employee that stops it.',
      score: 'Tap the globe. Cody scores the follow-up leak, then role-plays the employee that fixes it first.'
    };
    return '<div class="orb-row">' +
      '<button class="orb" id="orb" type="button" aria-label="Talk to Cody, an Advaita AI Employee">' +
      '<span class="orb-core"></span><span class="orb-ring"></span><span class="orb-wave" aria-hidden="true"></span></button>' +
      '<div><p class="kicker" style="margin:0 0 6px">Cody · ElevenLabs voice</p>' +
      '<p class="muted" id="orb-status">' + (status[magnet] || status.plan) + '</p>' +
      '<p class="tiny">Human voice. Not the browser robot. Demo, not a live customer recording.</p>' +
      '<button class="btn btn-ghost btn-tiny" type="button" id="voice-mute">Mute voice</button></div></div>' +
      '<div class="chat" id="orb-chat" style="margin-top:1rem"><div class="chat-log" id="orb-log"></div>' +
      '<form class="chat-form" id="orb-form"><input id="orb-in" placeholder="Your name, site, or a question about the offer" autocomplete="name">' +
      '<button class="btn btn-primary" type="submit">Send</button></form></div>';
  }

  function createGlobe(opts) {
    opts = opts || {};
    var magnet = opts.magnet || document.body.getAttribute('data-magnet') || 'plan';
    var s = window.__globe;
    if (!s || opts.reset) {
      s = {
        phase: 'greet', person: '', biz: '', url: '', speed: '', volume: '',
        roleTurns: 0, magnet: magnet, log: [], research: null,
        leakLine: '', scoreLine: '', worst: 'Speed-to-Lead'
      };
    }
    s.magnet = magnet;
    window.__globe = s;

    function paint() {
      var el = $('#orb-log') || $('#chat-log');
      if (!el) return;
      el.innerHTML = s.log.map(function (m) {
        return '<div class="bubble ' + m.who + '"></div>';
      }).join('');
      $all('.bubble', el).forEach(function (b, idx) { b.textContent = s.log[idx].t; });
      el.scrollTop = el.scrollHeight;
    }

    var lastSpoken = '';
    function say(t, doSpeak, spokenAlt) {
      s.log.push({ who: 'bot', t: t });
      var box = $('#orb-chat') || $('#chat');
      if (box) box.style.display = 'block';
      paint();
      if ($('#orb-status')) $('#orb-status').textContent = t;
      lastSpoken = spokenAlt || t;
      if (doSpeak !== false) speak(lastSpoken);
    }

    function hear(t) {
      s.log.push({ who: 'me', t: t });
      paint();
    }

    function maybeCapture() {
      bindCapture(function () {
        return 'Globe ' + magnet + ':\n' + s.log.map(function (m) { return m.who + ': ' + m.t; }).join('\n');
      });
    }

    function nextAfterResearch() {
      if (!s.speed) {
        s.phase = 'speed';
        say(youLine(s) + ', how quickly does someone on your team contact a new lead today — minutes, hours, or next day?', true, 'How quickly does someone on your team contact a new lead today — minutes, hours, or next day?');
        return;
      }
      if (!s.volume) {
        s.phase = 'volume';
        say('Roughly how many new leads do you get in a typical month from ads plus the website?', true, 'Roughly how many new leads do you get in a typical month from ads plus the website?');
        return;
      }
      s.phase = 'roleplay_ask';
      say(magnetPitch(s), true, magnetPitchSpoken(s));
    }

    function ingestResearch(research, force) {
      if (research) s.research = research;
      window.__research = s.research;
      if (!force && (s.phase === 'greet' || s.phase === 'name' || s.phase === 'biz')) return;
      nextAfterResearch();
    }

    function ingestLeak(line) { if (line) s.leakLine = line; }
    function ingestScore(line, worst) {
      if (line) s.scoreLine = line;
      if (worst) s.worst = worst;
    }

    async function handle(raw) {
      var v = String(raw || '').trim();
      if (!v) return;
      hear(v);
      var lock = lockReply(v);
      if (lock) { say(lock); return; }

      if (s.phase === 'close' && /email|save|send/i.test(v)) {
        maybeCapture();
        say('Drop your email in the box below. If the CRM relay is blocked from this domain, it stays queued on this device. Call ' + PHONE + ' to actually book.');
        return;
      }

      if (s.phase === 'roleplay') {
        var line = roleplayReply(s, v);
        var spoken = 'That was the live demo — you just felt the employee, not a form. Real install is 5,000 dollars setup plus 1,000 a month, month-to-month, 14 days. Calendly on file is 404, so I will not invent a link. Call 801 980 0308 or use apply.';
        if (s.phase !== 'close' && s.roleTurns === 1) spoken = 'Thanks for calling. I can get you a qualified conversation with the owner. What are you hoping to get done — a new job, a quote, or a question on something already open?';
        if (s.phase !== 'close' && s.roleTurns === 2) spoken = 'Got it. I am holding a callback from the owner, not a fake calendar hold. Live install confirms by phone at 801 980 0308. Anything else I should pass to them before I wrap this demo?';
        say(line, true, spoken);
        if (s.phase === 'close') maybeCapture();
        return;
      }

      if (s.phase === 'roleplay_ask') {
        if (/^(n|no|nope|not now|later|skip)\b/i.test(v) || /don'?t|not interested/.test(v.toLowerCase())) {
          s.phase = 'close';
          say(roleplayDebrief(s), true, 'That was the live demo — you just felt the employee, not a form. Real install is 5,000 dollars setup plus 1,000 a month, month-to-month, 14 days. Calendly on file is 404, so I will not invent a link. Call 801 980 0308 or use apply.');
          maybeCapture();
          return;
        }
        s.phase = 'roleplay';
        s.roleTurns = 0;
        s.worst = s.worst || firstEmployeeName(s.research);
        say(roleplayOpener(s), true, 'You are now a new lead. I am the first AI Employee. This is a demo on this page, not a recording of a live customer call, and I will not invent a calendar link. Go ahead. Say why you are calling.');
        return;
      }

      var site = extractSite(v);
      if (site && s.phase !== 'roleplay') {
        s.url = site;
        if ($('#url')) $('#url').value = site;
        s.phase = 'researching';
        say('Give me about ten seconds. I am opening ' + site + ' to read the industry and what similar operators are doing with AI Employees.');
        if (typeof opts.onSite === 'function') {
          await opts.onSite(site);
          return;
        }
        var research = await researchUrl(site);
        if (window.AdvaitaResearch && research && !research.packet) {
          research = window.AdvaitaResearch.buildLitePacket(research, '');
        }
        ingestResearch(research);
        return;
      }

      if (s.phase === 'greet' || s.phase === 'name') {
        var nm = firstNameOf(v);
        if (nm) s.person = nm;
        if ($('#person') && s.person) $('#person').value = s.person;
        if ($('#c-first') && s.person) $('#c-first').value = s.person;
        s.phase = 'biz';
        say((s.person ? (s.person + ', got it. ') : '') + 'What is the name of the business?', true, 'Got it. What is the name of the business?');
        return;
      }
      if (s.phase === 'biz') {
        s.biz = v.replace(/^(it'?s|we are|we'?re)\s+/i, '').trim();
        if ($('#c-biz') && s.biz) $('#c-biz').value = s.biz;
        s.phase = 'url';
        say('Do you have a website? Paste it or say it — I will pull the homepage, the industry, and what the top operators in that space are doing with AI Employees.', true, 'Do you have a website? Paste it or say it — I will pull the homepage, the industry, and what the top operators in that space are doing with AI Employees.');
        return;
      }
      if (s.phase === 'url') {
        if (/don'?t|no site|no website|none|skip/i.test(v)) {
          s.phase = 'speed';
          say('No site is fine — I will keep estimates labeled. How quickly does someone on your team contact a new lead today — minutes, hours, or next day?');
          return;
        }
        say('Paste the site as yourcompany.com and I will open it. Or say skip.');
        return;
      }
      if (s.phase === 'researching') {
        say('Still opening the page. One more beat.');
        return;
      }
      if (s.phase === 'speed') {
        if (s.magnet === 'score') tapScoreChips(v);
        var low = v.toLowerCase();
        if (/minute/.test(low)) s.speed = 'minutes';
        else if (/next|overnight|tomorrow|day/.test(low)) s.speed = 'nextday';
        else s.speed = 'hours';
        if ($('#speed')) $('#speed').value = s.speed;
        s.phase = 'volume';
        say((s.person ? (s.person + ', ') : '') + 'roughly how many new leads do you get in a typical month from ads plus the website?', true, 'Roughly how many new leads do you get in a typical month from ads plus the website?');
        return;
      }
      if (s.phase === 'volume') {
        if (s.magnet === 'score') tapScoreChips(v);
        var n = parseInt(v.replace(/[^0-9]/g, ''), 10);
        if (n) {
          s.volume = n;
          if ($('#leads')) $('#leads').value = n;
        } else s.volume = v;
        if (s.magnet === 'calculator') {
          s.phase = 'ticket';
          say((s.person ? (s.person + ', ') : '') + 'what is a typical closed job or sale worth in dollars?', true, 'What is a typical closed job or sale worth in dollars?');
          return;
        }
        s.phase = 'roleplay_ask';
        say(magnetPitch(s), true, magnetPitchSpoken(s));
        return;
      }
      if (s.phase === 'ticket') {
        var dollars = parseInt(v.replace(/[^0-9]/g, ''), 10);
        if (dollars && $('#value')) $('#value').value = dollars;
        if ($('#leads') && $('#value') && typeof leakMath === 'function') {
          var leaked = leakMath({
            leads: $('#leads').value, value: $('#value').value, conv: $('#conv').value, close: $('#close').value
          });
          ingestLeak('Yearly unspoken leak ' + money(leaked.yearly) + ' from your inputs, not a forecast. ');
        }
        s.phase = 'roleplay_ask';
        say(magnetPitch(s), true, magnetPitchSpoken(s));
        return;
      }
      say(salesBrief(s.research || window.__research));
    }

    function start(doSpeak) {
      if (s.log.length) { paint(); return; }
      s.phase = 'name';
      fire('chat_start', { via: 'globe', magnet: magnet });
      say(globeOpener(magnet), doSpeak, globeOpenerSpoken(magnet));
    }

    function listen() {
      var orb = $('#orb');
      var live = $('#orb-live');
      if (orb) orb.classList.add('on');
      if (live) live.classList.add('on');
      listenOnce(function (t) { if (t) handle(t); });
    }

    function bind() {
      start(false);
      var orb = $('#orb');
      if (orb) {
        orb.onclick = function () {
          fire('orb_click', { magnet: magnet });
          if (s.log[0]) speak(lastSpoken || globeOpenerSpoken(magnet));
          listen();
        };
      }
      var live = $('#orb-live');
      if (live) {
        live.onclick = function () {
          fire('orb_click', { where: 'float', magnet: magnet });
          if (s.log[0]) speak(lastSpoken || globeOpenerSpoken(magnet));
          listen();
        };
      }
      var mute = $('#voice-mute');
      if (mute) {
        mute.onclick = function () {
          voiceMuted = !voiceMuted;
          mute.textContent = voiceMuted ? 'Unmute voice' : 'Mute voice';
          if (voiceMuted) stopVoice();
          fire('voice_mute', { muted: voiceMuted });
        };
      }
      var form = $('#orb-form') || $('#chat-form');
      if (form) {
        form.onsubmit = function (e) {
          e.preventDefault();
          var inp = $('#orb-in') || $('#chat-in');
          var v = inp && inp.value.trim();
          if (!v) return;
          inp.value = '';
          handle(v);
        };
      }
    }

    var ctl = {
      start: start, handle: handle, bind: bind, listen: listen, say: say,
      ingestResearch: ingestResearch, ingestLeak: ingestLeak, ingestScore: ingestScore
    };
    window.__globeCtl = ctl;
    return ctl;
  }

  function orbReply(msg, research) {
    var lock = lockReply(msg);
    if (lock) return lock;
    return salesBrief(research);
  }

  function footerHtml() {
    return '<footer>Locked offer ' + OFFER + ' · Noun: AI Employees · ' +
      '<a href="' + PHONE_HREF + '">' + PHONE + '</a> · <a href="mailto:' + EMAIL + '">' + EMAIL + '</a><br>' +
      'Calendly link on file returned 404 on 2026-08-19 — call or use the blueprint form. Instant Form off.</footer>';
  }

  function captureHtml() {
    return '<div class="capture" id="capture"><h3>Where should we send this?</h3>' +
      '<p class="tiny">Email and phone after the wow — not before. We use the same Blueprint relay as /apply/.</p>' +
      '<div class="row" style="margin-top:.8rem">' +
      '<div><label>First name</label><input id="c-first" autocomplete="given-name"></div>' +
      '<div><label>Email</label><input id="c-email" type="email" autocomplete="email"></div>' +
      '<div><label>Phone</label><input id="c-phone" type="tel" autocomplete="tel"></div>' +
      '<div><label>Business</label><input id="c-biz"></div></div>' +
      '<div class="actions"><button class="btn btn-primary" id="c-send" type="button">Save my plan</button>' +
      '<a class="btn btn-ghost" href="' + PHONE_HREF + '" id="c-call">Call ' + PHONE + '</a>' +
      '<a class="btn btn-ghost" href="' + APPLY + '" id="c-apply">Get the full blueprint</a></div>' +
      '<p class="tiny" id="c-status"></p></div>';
  }

  function bindCapture(noteFn) {
    var box = $('#capture');
    if (!box) return;
    box.style.display = 'block';
    $('#c-send').onclick = async function () {
      var email = $('#c-email').value.trim();
      if (!email) { $('#c-status').textContent = 'Email is enough to save it.'; return; }
      await captureContact({
        firstName: $('#c-first').value.trim(),
        email: email,
        phone: $('#c-phone').value.trim(),
        businessName: $('#c-biz').value.trim(),
        website: qs('url') || (window.__research && window.__research.url) || '',
        note: noteFn ? noteFn() : ''
      });
      $('#c-status').textContent = 'Saved. If the CRM relay is blocked by CORS from this domain, it is queued on this device. Call or use the blueprint form to book.';
    };
    $('#c-call').addEventListener('click', function () { fire('booking_attempt', { via: 'phone' }); fire('cta_click', { via: 'phone' }); });
    $('#c-apply').addEventListener('click', function () { fire('booking_attempt', { via: 'apply' }); fire('cta_click', { via: 'apply' }); });
  }

  function downloadOnePager(research, answers) {
    var html = onePagerHtml(research, answers);
    var blob = new Blob([html], { type: 'text/html' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = (research.host || 'ai-employee-report') + '-one-pager.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    fire('one_pager_download', { host: research.host });
  }

  function copyLinkBtn() {
    var b = $('#copy-link');
    if (!b) return;
    b.onclick = function () {
      var u = location.origin + location.pathname + location.search;
      copyText(u).then(function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy link'; }, 1500); });
    };
  }

  function renderHub() {
    document.body.innerHTML = navHtml('hub') +
      '<div class="page-intro"><h1>Paste a website.<br>Walk out with a 14-day plan.</h1>' +
      '<p>Three free doors. Research nobody else does on a lead magnet — 20 expert angles on their actual site — then one ask: call.</p>' +
      '<p class="offer">' + OFFER + ' · 14-day install · month-to-month</p></div>' +
      trustRowHtml() +
      jabStripHtml() +
      '<main class="wrap" id="main"><div class="grid-3">' +
      '<a class="door" href="/plan/?demo=1"><div class="card-bar">Door 1 · Wow Plan</div><div class="card-body"><h3>Hear the employee. Leave with the research.</h3><p class="muted">Owner interview, public-site forensics, 20 labeled expert angles, then a live role-play. Not a homeowner emergency bot.</p><p class="proof">Walk out with the report before anyone asks for a call.</p></div></a>' +
      '<a class="door" href="/calculator/"><div class="card-bar">Door 2 · Leak math</div><div class="card-body"><h3>Your numbers. Yearly leak. Formula on the page.</h3><p class="muted">Globe interview optional. Monthly and yearly unspoken leads vs first-month hire — labeled, not a forecast.</p><p class="proof">Labeled math. Not a forecast.</p></div></a>' +
      '<a class="door" href="/score/"><div class="card-bar">Door 3 · 60-sec audit</div><div class="card-body"><h3>One score. One thing to fix first.</h3><p class="muted">Tap the leaks. Get 0–100. Role-play the employee on the worst one.</p><p class="proof">Teaser, not the full Blueprint.</p></div></a>' +
      '</div>' + hookCtaHtml('hub', 'Those three doors are free. The ask is a call — the online calendar on file is 404.') +
      faqHtml('plan') +
      '</main>' + footerHtml();
    var hc = $('#hub-call'); if (hc) hc.addEventListener('click', function () { fire('booking_attempt', { via: 'phone' }); });
    var ha = $('#hub-apply'); if (ha) ha.addEventListener('click', function () { fire('booking_attempt', { via: 'apply' }); });
  }

  function renderPlan() {
    document.body.innerHTML = navHtml('plan') +
      '<div class="page-intro" id="intro"><h1>Paste the site. Hear the employee. Leave with the plan.</h1>' +
      '<p>We open the public homepage and run 20 expert angles on it — CRO, SEO, stack, capture, ICP — then name the AI Employees that fit and role-play the first one. Not a homeowner emergency bot.</p>' +
      '<p class="offer">' + OFFER + '</p>' +
      '<ul class="preview-list"><li>ElevenLabs voice — tap the globe, not the Mac robot</li><li>Who they sell to, labeled, from the page that actually loaded</li><li>Role-play the first employee before anyone asks for a call</li></ul></div>' +
      trustRowHtml() +
      jabStripHtml() +
      '<main class="wrap" id="main">' +
      '<div class="card" id="intake"><div class="card-bar">Advaita AI · Wow Plan</div><div class="card-body">' +
      globeHtml('plan') +
      '<label>Website</label><input id="url" placeholder="yourcompany.com" value="">' +
      '<div class="actions">' +
      '<button class="btn btn-primary" id="go" type="button">Run the research</button>' +
      '<button class="btn btn-ghost" id="sample" type="button">Open recruiting4parents.com</button>' +
      '<button class="btn btn-ghost" id="talk" type="button">Talk a URL</button>' +
      '<button class="btn btn-ghost" id="copy-link" type="button">Copy link</button>' +
      '</div>' +
      '<div class="progress" id="bar"><i></i></div><p class="tiny" id="status">Ready.</p>' +
      '<div id="qbox" style="margin-top:1rem">' +
      '<p class="muted">Optional — your numbers beat estimates.</p>' +
      '<div class="row" style="grid-template-columns:1fr 1fr;margin-top:.6rem">' +
      '<div><label>Your name</label><input id="person"></div>' +
      '<div><label>Leads / month</label><input id="leads" type="number" min="0" placeholder="40"></div>' +
      '<div><label>Value per close ($)</label><input id="value" type="number" min="0" placeholder="5000"></div>' +
      '<div><label>% that get a real conversation</label><input id="conv" type="number" min="0" max="100" placeholder="40"></div>' +
      '</div></div></div></div>' +
      '<div class="card card-wide" id="doc"><div class="card-bar">Advaita AI · Industry research report</div><div class="card-body" id="plan-out"></div>' +
      '<div class="card-body" id="after" style="padding-top:0;display:none">' +
      captureHtml() +
      '</div></div>' +
      '<button class="orb orb-float" id="orb-live" type="button" aria-label="Talk to Cody, an Advaita AI Employee">' +
      '<span class="orb-core"></span><span class="orb-ring"></span><span class="orb-wave" aria-hidden="true"></span></button>' +
      faqHtml('plan') +
      '</main>' + footerHtml();

    copyLinkBtn();
    var bar = $('#bar i');
    function setBar(n, msg) { bar.style.width = n + '%'; $('#status').textContent = msg; }

    async function run(url, demo) {
      fire('cta_click', { via: 'plan' });
      setBar(12, 'Opening the homepage…');
      var t = setInterval(function () {
        var w = parseFloat(bar.style.width) || 12;
        if (w < 88) bar.style.width = Math.min(88, w + 6) + '%';
      }, 400);
      var research = await researchUrl(url, { demo: demo });
      clearInterval(t);
      if (window.AdvaitaResearch && !research.packet) {
        research = window.AdvaitaResearch.buildLitePacket(research, '');
      }
      if (research.packet && research.packet.analyst && !research.packet.analyst.angles && window.AdvaitaResearch) {
        research.packet.analyst.angles = window.AdvaitaResearch.buildExpertAngles(research, '', { id: research.packet.analyst.industry_id, label: research.packet.analyst.industry, icp: research.packet.analyst.icp });
      }
      window.__research = research;
      if (window.__globe && $('#person').value.trim()) window.__globe.person = firstNameOf($('#person').value);
      if (window.__globe && $('#leads').value) window.__globe.volume = parseInt($('#leads').value, 10) || window.__globe.volume;
      setBar(100, research.labeled ? 'Homepage-only. Estimates are labeled.' : 'Locked a page fact. Research report ready.');
      var answers = {
        person: $('#person').value.trim(),
        leads: $('#leads').value,
        value: $('#value').value,
        conv: $('#conv').value,
        close: 20
      };
      $('#intro').style.display = 'none';
      if ($('#qbox')) $('#qbox').style.display = 'none';
      $('#doc').style.display = 'block';
      $('#after').style.display = 'block';
      $('#plan-out').innerHTML = reportHtml(research, answers);
      try { $('#doc').scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (e) {}
      fire('plan_ready', { magnet: 'plan', host: research.host, industry: research.packet && research.packet.analyst.industry_id });
      $('#hear').onclick = function () {
        var emps = (research.packet && research.packet.profiler.employees) || [];
        var txt = research.fact + '. Industry: ' + ((research.packet && research.packet.analyst.industry) || '') + '. ' +
          emps.map(function (e) { return e.name + ': ' + e.loop; }).join('. ');
        speak(txt || salesBrief(research));
      };
      $('#one-pager').onclick = function () { downloadOnePager(research, answers); };
      $('#another').onclick = function () {
        $('#doc').style.display = 'none';
        $('#after').style.display = 'none';
        $('#intake').style.display = 'block';
        $('#intro').style.display = 'block';
        if ($('#qbox')) $('#qbox').style.display = 'block';
      };
      $('#ask-cody').onclick = function () {
        try { $('#orb-in').focus(); } catch (e) {}
        if (window.__globeCtl) window.__globeCtl.listen();
      };
      $('#plan-call').addEventListener('click', function () { fire('booking_attempt', { via: 'phone' }); });
      $('#plan-apply').addEventListener('click', function () { fire('booking_attempt', { via: 'apply' }); });
      bindShare('share-plan', function () {
        var emps = (research.packet && research.packet.profiler.employees) || [];
        var first = emps[0] ? emps[0].name : 'the first AI Employee';
        return research.name + ' — Day 1 starts with ' + first + '. Offer ' + OFFER + '. Call ' + PHONE + '. ' + location.href;
      });
      $('#save-plan').onclick = function () {
        bindCapture(function () {
          return JSON.stringify({ host: research.host, packet: research.packet && { analyst: research.packet.analyst.industry, employees: (research.packet.profiler.employees || []).map(function (e) { return e.name; }) } });
        });
      };
      var u = new URL(location.href);
      u.searchParams.set('url', research.url || url);
      history.replaceState({}, '', u);
      if (window.__globeCtl) {
        var phase = window.__globe && window.__globe.phase;
        var talking = phase === 'researching' || phase === 'url' || phase === 'speed' || phase === 'volume' || phase === 'ticket';
        window.__globeCtl.ingestResearch(research, talking);
      }
    }

    var globe = createGlobe({
      magnet: 'plan',
      onSite: function (site) { return run(site, hostOf(site) === 'recruiting4parents.com'); }
    });
    globe.bind();

    $('#go').onclick = function () { run($('#url').value, false); };
    $('#sample').onclick = function () { $('#url').value = SAMPLE; run(SAMPLE, true); };
    $('#talk').onclick = function () {
      $('#status').textContent = 'Listening… say your website or what the business does.';
      listenOnce(function (t) {
        if (t) $('#url').value = t;
        run(t || $('#url').value, false);
      });
    };
    if (qs('demo') === '1') { $('#url').value = SAMPLE; run(SAMPLE, true); }
    else if (qs('url')) { $('#url').value = qs('url'); run(qs('url'), false); }
  }

  function renderCalculator() {
    document.body.innerHTML = navHtml('calculator') +
      '<div class="page-intro"><h1>Your numbers. The yearly leak. The formula stays on the page.</h1>' +
      '<p>Unspoken leads × job value × close rate. Hire payback is labeled, not a forecast. The globe is optional.</p>' +
      '<p class="offer">' + OFFER + '</p></div>' +
      trustRowHtml() +
      jabStripHtml() +
      '<main class="wrap" id="main">' + cardOpen('Advaita AI · Leak calculator') +
      globeHtml('calculator') +
      '<div class="presets" id="presets"></div>' +
      '<div class="row" style="grid-template-columns:1fr 1fr">' +
      '<div><label>Monthly leads</label><input id="leads" type="number" min="0" value="80"></div>' +
      '<div><label>Value per close ($)</label><input id="value" type="number" min="0" value="8000"></div>' +
      '<div><label>Current first-touch</label><select id="speed"><option value="minutes">Minutes</option><option value="hours" selected>Hours</option><option value="nextday">Next day</option></select></div>' +
      '<div><label>% that get a real conversation</label><input id="conv" type="number" min="0" max="100" value="35"></div>' +
      '<div><label>Close rate % (optional)</label><input id="close" type="number" min="0" max="100" value="20"></div>' +
      '<div><label>Website (optional, reuses Magnet 1 research)</label><input id="url" placeholder="yourcompany.com"></div>' +
      '</div>' +
      '<pre class="formula">unspoken_leads = monthly_leads × (1 − conversation%)\nmonthly_leak = unspoken_leads × value_per_close × close%\nyearly_leak = monthly_leak × 12\nfirst_month_hire = $5,000 + $1,000 = $6,000  (not a forecast of your return)\njobs_to_cover_hire = ceil(6000 / value_per_close)  — labeled, not a forecast\nhuman_stack $20,500 / mo vs AI Employee stack $1,000 / mo — staffing comparison, not your P&amp;L</pre>' +
      '<div class="actions"><button class="btn btn-primary" id="go" type="button">Run the leak math</button>' +
      '<button class="btn btn-ghost" id="copy-link" type="button">Copy link</button></div>' +
      '<div class="metrics" id="metrics"></div>' +
      '<p class="tiny" id="proof">Anthony proof: one sale through the ad employee + lead employee paid the hire back in under 30 days. Do not use $3,500 ads → $140k as Advaita’s win.</p>' +
      captureHtml() +
      cardClose() +
      '<button class="orb orb-float" id="orb-live" type="button" aria-label="Talk to Cody, an Advaita AI Employee">' +
      '<span class="orb-core"></span><span class="orb-ring"></span><span class="orb-wave" aria-hidden="true"></span></button>' +
      faqHtml('calculator') +
      '</main>' + footerHtml();

    copyLinkBtn();
    var presets = [
      { id: 'home', l: 'Home services', leads: 60, value: 4500, conv: 30, close: 25 },
      { id: 'install', l: 'Install / retail', leads: 90, value: 2500, conv: 40, close: 22 },
      { id: 'franchise', l: 'Franchise unit', leads: 40, value: 12000, conv: 35, close: 18 }
    ];
    $('#presets').innerHTML = presets.map(function (p) {
      return '<button class="chip" type="button" data-id="' + p.id + '">' + p.l + '</button>';
    }).join('');
    $all('#presets .chip').forEach(function (btn, idx) {
      btn.onclick = function () {
        $all('#presets .chip').forEach(function (c) { c.classList.remove('on'); });
        btn.classList.add('on');
        var p = presets[idx];
        $('#leads').value = p.leads; $('#value').value = p.value; $('#conv').value = p.conv; $('#close').value = p.close;
      };
    });
    $('#go').onclick = async function () {
      var m = leakMath({
        leads: $('#leads').value, value: $('#value').value, conv: $('#conv').value, close: $('#close').value
      });
      $('#metrics').innerHTML =
        '<div class="metric"><span class="tiny">Yearly unspoken leak</span><b>' + money(m.yearly) + '</b><span class="tiny">From your inputs. Not a forecast.</span></div>' +
        '<div class="metric"><span class="tiny">Unspoken leads / mo</span><b>' + Math.round(m.unspoken) + '</b></div>' +
        '<div class="metric"><span class="tiny">Monthly leak</span><b>' + money(m.monthly) + '</b></div>' +
        '<div class="metric"><span class="tiny">First-month hire vs that leak</span><b>' + money(HIRE_FIRST_MONTH) + '</b><span class="tiny">Jobs to cover hire: ' + (m.jobs || '—') + ' (not a forecast)</span></div>' +
        '<div class="metric"><span class="tiny">Human stack vs AI Employee</span><b>' + money(HUMAN_STACK) + ' vs ' + money(AI_STACK) + '</b></div>' +
        '<div class="metric"><span class="tiny">First-touch you selected</span><b>' + $('#speed').value + '</b><span class="tiny">Target comparison is 2 seconds, not a guarantee.</span></div>' +
        leakBarHtml(m.yearly) +
        shareLineHtml('share-leak') +
        hookCtaHtml('calc', 'You already have the leak in dollars. The ask is a call.');
      bindShare('share-leak', function () {
        return 'Yearly unspoken leak ' + money(m.yearly) + ' vs first-month hire ' + money(HIRE_FIRST_MONTH) + ' (labeled, not a forecast). Call ' + PHONE + '. ' + location.href;
      });
      var cc = $('#calc-call'); if (cc) cc.addEventListener('click', function () { fire('booking_attempt', { via: 'phone' }); });
      var ca = $('#calc-apply'); if (ca) ca.addEventListener('click', function () { fire('booking_attempt', { via: 'apply' }); });
      fire('calculator_complete', m);
      var url = $('#url').value;
      var research = url ? await researchUrl(url) : { fact: 'No site pasted — math only.', name: 'your business' };
      window.__research = research;
      if (window.__globe) {
        window.__globe.volume = parseInt($('#leads').value, 10) || window.__globe.volume;
        window.__globe.speed = $('#speed').value;
      }
      if (window.__globeCtl) {
        window.__globeCtl.ingestLeak('Yearly unspoken leak ' + money(m.yearly) + ' from your inputs, not a forecast. First-month hire is ' + money(HIRE_FIRST_MONTH) + ', labeled, not a forecast. ');
        window.__globeCtl.ingestResearch(research, true);
      }
      bindCapture(function () { return JSON.stringify(m); });
    };
    createGlobe({
      magnet: 'calculator',
      onSite: async function (site) {
        $('#url').value = site;
        var research = await researchUrl(site);
        if (window.AdvaitaResearch && research && !research.packet) {
          research = window.AdvaitaResearch.buildLitePacket(research, '');
        }
        if (window.__globeCtl) {
          var phase = window.__globe && window.__globe.phase;
          var talking = phase === 'researching' || phase === 'url' || phase === 'speed' || phase === 'volume' || phase === 'ticket';
          window.__globeCtl.ingestResearch(research, talking);
        }
      }
    }).bind();
  }

  function renderScore() {
    document.body.innerHTML = navHtml('score') +
      '<div class="page-intro"><h1>One score. The one thing to fix first.</h1>' +
      '<p>Tap the leaks that are true. Get 0–100 from homepage signals plus your chips. Then role-play the employee on the worst leak. Teaser, not the full Blueprint.</p>' +
      '<p class="offer">' + OFFER + '</p></div>' +
      trustRowHtml() +
      jabStripHtml() +
      '<main class="wrap" id="main">' + cardOpen('Advaita AI · 60-second audit') +
      globeHtml('score') +
      '<label>Website (or skip and use chips)</label><input id="url" placeholder="yourcompany.com">' +
      '<p class="muted" style="margin:.7rem 0 .4rem">Tap every leak that is true</p>' +
      '<div class="presets">' +
      '<button class="chip" type="button" data-k="after-hours">After-hours leads</button>' +
      '<button class="chip" type="button" data-k="slow">Slow follow-up</button>' +
      '<button class="chip" type="button" data-k="unqualified">Unqualified on the calendar</button>' +
      '<button class="chip" type="button" data-k="noshow">No-shows</button>' +
      '</div>' +
      '<div class="actions"><button class="btn btn-primary" id="go" type="button">Score it</button>' +
      '<button class="btn btn-ghost" id="sample" type="button">Sample site</button>' +
      '<button class="btn btn-ghost" id="copy-link" type="button">Copy link</button></div>' +
      '<p class="tiny" id="timer">Timer starts when you score.</p>' +
      '<div class="ring-wrap"><svg class="ring" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" stroke="#E5E5EA" stroke-width="10" fill="none"/><circle id="arc" cx="60" cy="60" r="52" stroke="#0071E3" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="327" stroke-dashoffset="327" transform="rotate(-90 60 60)"/><text id="score-txt" x="60" y="66" text-anchor="middle" font-size="28" font-weight="700" fill="#1D1D1F">—</text></svg></div>' +
      '<div id="notes"></div>' +
      '<div class="cta-dark" id="mini" style="display:none">' +
      '<p class="kicker" style="color:rgba(255,255,255,0.55)">Mini employee</p><h3 id="mini-h" style="margin:.4rem 0;color:#fff"></h3><p id="mini-p"></p>' +
      '<div class="actions"><button class="btn btn-light" id="hear-leak" type="button">Hear the worst leak</button>' +
      '<a class="btn btn-light" href="' + PHONE_HREF + '" id="mini-call">Book by phone</a></div></div>' +
      captureHtml() +
      cardClose() +
      '<button class="orb orb-float" id="orb-live" type="button" aria-label="Talk to Cody, an Advaita AI Employee">' +
      '<span class="orb-core"></span><span class="orb-ring"></span><span class="orb-wave" aria-hidden="true"></span></button>' +
      faqHtml('score') +
      '</main>' + footerHtml();

    copyLinkBtn();
    $all('.chip[data-k]').forEach(function (c) {
      c.onclick = function () { c.classList.toggle('on'); };
    });
    var started = 0;
    $('#sample').onclick = function () { $('#url').value = SAMPLE; };
    $('#go').onclick = async function () {
      started = Date.now();
      var tick = setInterval(function () {
        var s = Math.min(60, Math.round((Date.now() - started) / 1000));
        $('#timer').textContent = s + 's / 60s';
        if (s >= 60) clearInterval(tick);
      }, 250);
      var chips = $all('.chip.on').map(function (c) { return c.getAttribute('data-k'); });
      var research = await researchUrl($('#url').value, { demo: hostOf($('#url').value) === 'recruiting4parents.com' });
      if (!research) research = { fact: 'No URL — chips only.', name: 'your follow-up', labeled: true, tech: 'Not confirmed' };
      window.__research = research;
      var a = auditFrom(research, chips);
      var circ = 2 * Math.PI * 52;
      $('#arc').style.strokeDashoffset = String(circ * (1 - a.score / 100));
      $('#score-txt').textContent = String(a.score);
      $('#notes').innerHTML = '<div class="one-thing"><h3>The one thing to fix first: ' + a.worst.k + '</h3>' +
        '<p>Score ' + a.score + '/100. Next free doors: Wow Plan and leak math. Then call.</p>' +
        '<div class="actions"><a class="btn btn-primary" href="/plan/">Wow Plan</a>' +
        '<a class="btn btn-ghost" href="/calculator/">Leak math</a></div></div>' +
        a.notes.map(function (n, idx) {
        return '<div class="step"><div class="step-num">' + (idx + 1) + '</div><div><h3>' + n.k + '</h3><p>' + n.n + (research.fact ? ' ' + research.fact : '') + '</p></div></div>';
      }).join('') + shareLineHtml('share-score') + hookCtaHtml('score', 'You already have the one thing to fix. The ask is a call.');
      $('#mini').style.display = 'block';
      $('#mini-h').textContent = 'Starting on: ' + a.worst.k;
      $('#mini-p').textContent = 'Hi — I am the ' + a.worst.k + ' AI Employee for ' + research.name +
        '. I take the ' + a.worst.n + ' First touch target is 2 seconds. I book only qualified conversations. This is a teaser, not a full Blueprint.';
      fire('audit_score', { score: a.score, worst: a.worst.k });
      $('#hear-leak').onclick = function () { speak($('#mini-p').textContent); };
      $('#mini-call').addEventListener('click', function () { fire('booking_attempt', { via: 'phone' }); });
      bindShare('share-score', function () {
        return research.name + ' follow-up score ' + a.score + '/100. One thing to fix first: ' + a.worst.k + '. Call ' + PHONE + '. ' + location.href;
      });
      var sc = $('#score-call'); if (sc) sc.addEventListener('click', function () { fire('booking_attempt', { via: 'phone' }); });
      var sa = $('#score-apply'); if (sa) sa.addEventListener('click', function () { fire('booking_attempt', { via: 'apply' }); });
      if (window.__globeCtl) {
        window.__globeCtl.ingestScore('Score ' + a.score + '/100. ', a.worst.k);
        window.__globeCtl.ingestResearch(research, true);
      }
      bindCapture(function () { return 'score=' + a.score + ' worst=' + a.worst.k; });
    };
    createGlobe({
      magnet: 'score',
      onSite: async function (site) {
        $('#url').value = site;
        var research = await researchUrl(site, { demo: hostOf(site) === 'recruiting4parents.com' });
        if (window.AdvaitaResearch && research && !research.packet) {
          research = window.AdvaitaResearch.buildLitePacket(research, '');
        }
        if (window.__globeCtl) window.__globeCtl.ingestResearch(research);
      }
    }).bind();
    if (qs('demo') === '1') { $('#url').value = SAMPLE; }
    else if (qs('url')) { $('#url').value = qs('url'); }
  }

  function renderAnthony() {
    document.body.innerHTML = navHtml('anthony') +
      '<div class="page-intro"><h1>Anthony Castillo — use this story, not the old one.</h1>' +
      '<p>One named result. Not typical. Not a guarantee. Do not quote him.</p></div>' +
      '<main class="wrap">' + cardOpen('Advaita AI · Named proof') +
      '<p><strong>Wrong headline (do not use):</strong> $3,500 ads → $140,000 collected as the Advaita result.</p>' +
      stepsHtml([
        { t: 'Before the hire', d: '$140,000 collected was already his baseline. That is not our win.' },
        { t: 'The hire', d: 'Ad employee + lead employee. Contact, qualify, book. He shows up.' },
        { t: 'After the hire', d: 'One sale through those two employees paid the hire back in under 30 days.' }
      ]) +
      '<p class="tiny" style="margin-top:1rem">Do not say first paying customer. Do not use 91.9%, 184 aged leads, or “we collected $140k for him.” Locked offer ' + OFFER + '.</p>' +
      '<div class="actions"><a class="btn btn-primary" href="/plan/?demo=1">See the Wow Plan</a>' +
      '<a class="btn btn-ghost" href="' + PHONE_HREF + '">Call ' + PHONE + '</a></div>' +
      cardClose() + '</main>' + footerHtml();
  }

  var page = document.body.getAttribute('data-magnet');
  if (page === 'hub') renderHub();
  else if (page === 'plan') renderPlan();
  else if (page === 'calculator') renderCalculator();
  else if (page === 'score') renderScore();
  else if (page === 'anthony') renderAnthony();
})();
