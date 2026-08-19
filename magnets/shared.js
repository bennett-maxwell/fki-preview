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
  function speak(text) {
    fire('voice_start', { kind: 'tts' });
    try {
      window.speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(text);
      u.rate = 1.02;
      u.onend = function () { fire('voice_complete', { kind: 'tts' }); };
      window.speechSynthesis.speak(u);
    } catch (e) {}
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
    var url = normalizeUrl(raw);
    var host = hostOf(url);
    if (opts.demo || host === 'recruiting4parents.com') return Object.assign({ url: url || SAMPLE }, DEMO);
    if (!url) return null;
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
    return '<div class="nav-shell"><nav><a class="nav-logo" href="/magnets/">Advaita <span>AI</span></a><div class="nav-links">' +
      links.map(function (l) {
        return '<a href="' + l[0] + '"' + (active === l[2] ? ' class="active"' : '') + '>' + l[1] + '</a>';
      }).join('') + '</div></nav></div>';
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

  function timelineHtml() {
    return '<div class="timeline"><p>What comes after</p>' +
      '<div class="t-row"><div class="t-dot"></div><div><strong>72 hours</strong> — first two AI Employees configured on your lead flow.</div></div>' +
      '<div class="t-row"><div class="t-dot"></div><div><strong>Day 7</strong> — they are live: contact, qualify, book.</div></div>' +
      '<div class="t-row"><div class="t-dot"></div><div><strong>Day 14</strong> — install complete. Month-to-month after that.</div></div></div>';
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

  function codyBox(seed) {
    var qs6 = [
      'Roughly how many new leads do you get per week or month from ads + website?',
      'What is the average value of a closed lead / appointment / sale?',
      'How fast does someone from your team currently contact a new lead — minutes, hours, or next day?',
      'What percentage of your leads actually get a real conversation?',
      'If a never-stopping appointment desk contacted every lead in 2 seconds and booked only the qualified ones, what would that change in 90 days?',
      'Biggest leak right now: after-hours, slow follow-up, unqualified on the calendar, or no-shows?'
    ];
    var i = 0;
    var log = [];
    function render() {
      var el = $('#chat-log');
      el.innerHTML = log.map(function (m) {
        return '<div class="bubble ' + m.who + '"></div>';
      }).join('');
      $all('.bubble', el).forEach(function (b, idx) { b.textContent = log[idx].t; });
      el.scrollTop = el.scrollHeight;
    }
    function bot(t) { log.push({ who: 'bot', t: t }); render(); }
    bot('I am Cody. I already have ' + seed + ' Ask me anything, or answer these six so the install call is not a second form.');
    bot(qs6[0]);
    fire('chat_start', {});
    $('#chat-form').onsubmit = function (e) {
      e.preventDefault();
      var v = $('#chat-in').value.trim();
      if (!v) return;
      $('#chat-in').value = '';
      log.push({ who: 'me', t: v });
      render();
      i += 1;
      if (i < qs6.length) bot(qs6[i]);
      else {
        bot('Got it. The 14-day install is ' + OFFER + '. Calendly on file is 404 today, so tap Call or the full blueprint form. I will not invent a booking link.');
        fire('booking_attempt', { via: 'chat' });
        bindCapture(function () { return 'Cody chat: ' + log.map(function (m) { return m.who + ': ' + m.t; }).join('\n'); });
      }
    };
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
      '<div class="page-intro"><h1>Paste a website.<br>Walk out with a 5-point plan.</h1>' +
      '<p>Three short doors. Not the 149-point Blueprint. AI Employees, not agents.</p>' +
      '<p class="offer">' + OFFER + ' · 14-day install · month-to-month</p></div>' +
      '<main class="wrap"><div class="grid-3">' +
      '<a class="door" href="/plan/?demo=1"><div class="card-bar">Magnet 1</div><div class="card-body"><h3>Wow Plan</h3><p class="muted">Open a real homepage. Get five numbered moves, two named employees, and the 14-day install.</p></div></a>' +
      '<a class="door" href="/calculator/"><div class="card-bar">Magnet 2</div><div class="card-body"><h3>Leak calculator</h3><p class="muted">Your numbers in. Monthly and yearly unspoken-lead leak out. Formula on the page.</p></div></a>' +
      '<a class="door" href="/score/"><div class="card-bar">Magnet 3</div><div class="card-body"><h3>60-second audit</h3><p class="muted">Score 0–100 and a mini employee on the worst leak.</p></div></a>' +
      '</div></main>' + footerHtml();
  }

  function renderPlan() {
    document.body.innerHTML = navHtml('plan') +
      '<div class="page-intro"><h1>A Wow Plan for the site you actually run.</h1>' +
      '<p>Paste a URL. We pull a homepage fact, name the leak, and hand you five numbered moves — the shape of a Blueprint, in about 90 seconds.</p>' +
      '<p class="offer">' + OFFER + '</p></div>' +
      '<main class="wrap">' + cardOpen('Advaita AI · Wow Plan') +
      '<label>Website</label><input id="url" placeholder="yourcompany.com" value="">' +
      '<div class="actions">' +
      '<button class="btn btn-primary" id="go" type="button">Build my plan</button>' +
      '<button class="btn btn-ghost" id="sample" type="button">Open recruiting4parents.com</button>' +
      '<button class="btn btn-ghost" id="talk" type="button">Talk</button>' +
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
      '</div></div>' +
      '<div id="plan-out"></div>' +
      '<div class="actions"><button class="btn btn-ghost" id="hear" type="button">Hear the plan</button></div>' +
      '<div class="chat" id="chat" style="display:none"><div class="chat-log" id="chat-log"></div>' +
      '<form class="chat-form" id="chat-form"><input id="chat-in" placeholder="Type to Cody"><button class="btn btn-primary" type="submit">Send</button></form></div>' +
      captureHtml() +
      cardClose() + '</main>' + footerHtml();

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
      window.__research = research;
      setBar(100, research.labeled ? 'Homepage-only. Estimates are labeled.' : 'Pulled a real page fact.');
      var answers = {
        person: $('#person').value.trim(),
        leads: $('#leads').value,
        value: $('#value').value,
        conv: $('#conv').value,
        close: 20
      };
      var pts = wowPoints(research, answers);
      $('#plan-out').innerHTML =
        '<p class="kicker" style="margin-top:1.2rem">Prepared for</p>' +
        '<h2 style="font-size:1.45rem;letter-spacing:-0.03em;margin-bottom:.4rem">' + research.name + '</h2>' +
        '<div class="fact">' + research.fact + '</div>' +
        stepsHtml(pts) +
        '<div class="tiles">' +
        '<div class="tile"><b>2s</b><span>Speed-to-lead</span></div>' +
        '<div class="tile"><b>2</b><span>AI Employees</span></div>' +
        '<div class="tile"><b>14d</b><span>Install</span></div></div>' +
        timelineHtml() +
        '<div class="cta-dark"><p>Ready to run this on your live leads.</p>' +
        '<a class="btn btn-light" href="' + PHONE_HREF + '">Call ' + PHONE + '</a></div>';
      fire('plan_ready', { magnet: 'plan', host: research.host });
      $('#chat').style.display = 'block';
      codyBox(research.fact);
      bindCapture(function () { return pts.map(function (p) { return p.t + ': ' + p.d; }).join('\n'); });
      var u = new URL(location.href);
      u.searchParams.set('url', research.url || url);
      history.replaceState({}, '', u);
    }

    $('#go').onclick = function () { run($('#url').value, false); };
    $('#sample').onclick = function () { $('#url').value = SAMPLE; run(SAMPLE, true); };
    $('#hear').onclick = function () {
      var txt = $all('#plan-out .step').map(function (li) { return li.textContent; }).join('. ');
      if (txt) speak(txt);
    };
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
      '<div class="page-intro"><h1>Unspoken-lead leak, in your numbers.</h1>' +
      '<p>Not a forecast. Math from the inputs. Hire payback is labeled.</p>' +
      '<p class="offer">' + OFFER + '</p></div>' +
      '<main class="wrap">' + cardOpen('Advaita AI · Leak calculator') +
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
      '<div class="chat" id="chat" style="display:none;margin-top:1rem"><div class="chat-log" id="chat-log"></div>' +
      '<form class="chat-form" id="chat-form"><input id="chat-in" placeholder="Type to Cody"><button class="btn btn-primary" type="submit">Send</button></form></div>' +
      captureHtml() +
      cardClose() + '</main>' + footerHtml();

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
        '<div class="metric"><span class="tiny">Unspoken leads / mo</span><b>' + Math.round(m.unspoken) + '</b></div>' +
        '<div class="metric"><span class="tiny">Monthly leak</span><b>' + money(m.monthly) + '</b></div>' +
        '<div class="metric"><span class="tiny">Yearly leak</span><b>' + money(m.yearly) + '</b></div>' +
        '<div class="metric"><span class="tiny">First-month hire vs that leak</span><b>' + money(HIRE_FIRST_MONTH) + '</b><span class="tiny">Jobs to cover hire: ' + (m.jobs || '—') + ' (not a forecast)</span></div>' +
        '<div class="metric"><span class="tiny">Human stack vs AI Employee</span><b>' + money(HUMAN_STACK) + ' vs ' + money(AI_STACK) + '</b></div>' +
        '<div class="metric"><span class="tiny">First-touch you selected</span><b>' + $('#speed').value + '</b><span class="tiny">Target comparison is 2 seconds, not a guarantee.</span></div>';
      fire('calculator_complete', m);
      var url = $('#url').value;
      var research = url ? await researchUrl(url) : { fact: 'No site pasted — math only.', name: 'your business' };
      window.__research = research;
      $('#chat').style.display = 'block';
      codyBox(research.fact + ' Leak shown: ' + money(m.monthly) + '/mo.');
      bindCapture(function () { return JSON.stringify(m); });
    };
  }

  function renderScore() {
    document.body.innerHTML = navHtml('score') +
      '<div class="page-intro"><h1>60-second follow-up audit.</h1>' +
      '<p>Not the 149-point Blueprint. A teaser score and a mini employee on the worst leak.</p>' +
      '<p class="offer">' + OFFER + '</p></div>' +
      '<main class="wrap">' + cardOpen('Advaita AI · 60-second audit') +
      '<p class="tiny">The old Franchise KI 8-question quiz remains at /audit. This magnet is /score.</p>' +
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
      '<div class="chat" id="chat" style="display:none;margin-top:1rem"><div class="chat-log" id="chat-log"></div>' +
      '<form class="chat-form" id="chat-form"><input id="chat-in" placeholder="Type to Cody"><button class="btn btn-primary" type="submit">Send</button></form></div>' +
      captureHtml() +
      cardClose() + '</main>' + footerHtml();

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
      $('#notes').innerHTML = a.notes.map(function (n, idx) {
        return '<div class="step"><div class="step-num">' + (idx + 1) + '</div><div><h3>' + n.k + '</h3><p>' + n.n + (research.fact ? ' ' + research.fact : '') + '</p></div></div>';
      }).join('');
      $('#mini').style.display = 'block';
      $('#mini-h').textContent = 'Starting on: ' + a.worst.k;
      $('#mini-p').textContent = 'Hi — I am the ' + a.worst.k + ' AI Employee for ' + research.name +
        '. I take the ' + a.worst.n + ' First touch target is 2 seconds. I book only qualified conversations. This is a teaser, not a full Blueprint.';
      fire('audit_score', { score: a.score, worst: a.worst.k });
      $('#hear-leak').onclick = function () { speak($('#mini-p').textContent); };
      $('#mini-call').addEventListener('click', function () { fire('booking_attempt', { via: 'phone' }); });
      $('#chat').style.display = 'block';
      codyBox(research.fact + ' Score ' + a.score + '. Worst leak: ' + a.worst.k + '.');
      bindCapture(function () { return 'score=' + a.score + ' worst=' + a.worst.k; });
    };
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
