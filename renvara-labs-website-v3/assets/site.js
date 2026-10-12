/* Renvara Labs preview v3. One shared script (plus vial.js), vanilla JS, no libraries, no network calls.
   Every page reads fully with JavaScript off. Motion uses transform, opacity and canvas only and is
   switched off entirely under prefers-reduced-motion (static, un-pinned frame). */
(function () {
  'use strict';
  var D = document, W = window, root = D.documentElement;

  function store(kind, op, key, val) {
    try {
      var s = kind === 'l' ? W.localStorage : W.sessionStorage;
      if (op === 'g') return s.getItem(key);
      s.setItem(key, val);
    } catch (e) { /* blocked storage: page still works */ }
    return null;
  }
  function qs(sel, ctx) { return (ctx || D).querySelector(sel); }
  function qsa(sel, ctx) { return Array.prototype.slice.call((ctx || D).querySelectorAll(sel)); }
  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
  function focusables(ctx) {
    return qsa('a[href],button:not([disabled]),input:not([disabled]):not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"])', ctx)
      .filter(function (el) { return el.offsetParent !== null || el === D.activeElement; });
  }

  /* ---- 21+ / researcher gate: content stays in the HTML; Escape never bypasses ---- */
  var scope = qsa('[data-gate-scope]');
  function setInert(on) {
    scope.forEach(function (el) {
      if (on) { el.setAttribute('inert', ''); el.setAttribute('aria-hidden', 'true'); }
      else { el.removeAttribute('inert'); el.removeAttribute('aria-hidden'); }
    });
  }
  var GATE_KEY = 'renvaraPreviewGate.v1', GATE_DAYS = 30, gate = qs('#gate');
  function gateAccepted() {
    var t = parseInt(store('l', 'g', GATE_KEY) || store('s', 'g', GATE_KEY), 10);
    return !!t && (Date.now() - t) < GATE_DAYS * 864e5;
  }
  if (gate) {
    var boxes = qsa('input[type=checkbox]', gate), enter = qs('[data-gate-enter]', gate);
    var sync = function () {
      var ok = boxes.every(function (b) { return b.checked; });
      enter.disabled = !ok;
      enter.setAttribute('aria-disabled', ok ? 'false' : 'true');
    };
    boxes.forEach(function (b) { b.addEventListener('change', sync); });
    sync();
    enter.addEventListener('click', function () {
      if (enter.disabled) return;
      var now = String(Date.now());
      store('l', 's', GATE_KEY, now); store('s', 's', GATE_KEY, now);
      gate.hidden = true; root.classList.remove('gate-open'); setInert(false);
      var main = qs('#main');
      if (main) { main.setAttribute('tabindex', '-1'); main.focus({ preventScroll: true }); }
    });
    gate.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); return; }
      if (e.key !== 'Tab') return;
      var f = focusables(gate); if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && D.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && D.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    if (!gateAccepted()) {
      gate.hidden = false; root.classList.add('gate-open'); setInert(true);
      var b0 = qs('input[type=checkbox]', gate); if (b0) b0.focus();
    }
  }

  /* ---- mobile nav ---- */
  var toggle = qs('#nav-toggle'), nav = qs('#site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    D.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); toggle.focus();
      }
    });
  }

  /* ---- catalog filter chips + text filter ---- */
  var chipWrap = qs('[data-chips]');
  if (chipWrap) {
    var items = qsa('[data-type]'), countEl = qs('[data-count]'), textIn = qs('[data-filter-text]'), active = 'all';
    var apply = function () {
      var q = textIn ? textIn.value.trim().toLowerCase() : '', n = 0;
      items.forEach(function (el) {
        var show = (active === 'all' || el.getAttribute('data-type') === active) && (!q || el.textContent.toLowerCase().indexOf(q) > -1);
        el.hidden = !show; if (show) n++;
      });
      if (countEl) countEl.textContent = 'Showing ' + n + ' of ' + items.length + ' products';
    };
    qsa('button[data-filter]', chipWrap).forEach(function (b) {
      b.addEventListener('click', function () {
        active = b.getAttribute('data-filter');
        qsa('button[data-filter]', chipWrap).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        apply();
      });
    });
    if (textIn) textIn.addEventListener('input', apply);
  }

  /* ---- COA table search ---- */
  var coaQ = qs('[data-coa-search]');
  if (coaQ) {
    var rows = qsa('[data-coa-row]'), none = qs('[data-coa-none]'), cnt = qs('[data-coa-count]');
    coaQ.addEventListener('input', function () {
      var q = coaQ.value.trim().toLowerCase(), n = 0;
      rows.forEach(function (r) { var show = !q || r.textContent.toLowerCase().indexOf(q) > -1; r.hidden = !show; if (show) n++; });
      if (none) none.hidden = n !== 0;
      if (cnt) cnt.textContent = n + ' of ' + rows.length + ' public lot reports shown';
    });
  }

  /* ---- lot lookup over the six public lots (in the browser only) ---- */
  var lotForm = qs('#lot-form');
  if (lotForm) {
    var data = [];
    try { data = JSON.parse(qs('#lots-data').textContent); } catch (e) { data = []; }
    var out = qs('#lot-result'), inp = qs('#lot'), rootPath = D.body.getAttribute('data-root') || '';
    var norm = function (s) { return s.toUpperCase().replace(/[^A-Z0-9]/g, ''); };
    var run = function () {
      var raw = inp.value.trim();
      if (!raw) { out.textContent = ''; return; }
      var n = norm(raw), hit = data.filter(function (r) { var l = norm(r.lot); return l === n || l === 'DPS' + n; })[0];
      out.textContent = '';
      var card = D.createElement('div'), h = D.createElement('h3'), p = D.createElement('p');
      card.className = 'card';
      if (hit) {
        h.textContent = 'Match: ' + hit.product + ', lot ' + hit.lot;
        p.textContent = hit.strength + '. Analyzed ' + hit.analyzed + ' by ' + hit.lab + ' (report ' + hit.report + '). Result: ' + hit.result + '. ';
        var a = D.createElement('a'); a.href = hit.coa; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.textContent = 'Open the lab-hosted COA (new tab)';
        var a2 = D.createElement('a'); a2.href = rootPath + hit.page; a2.textContent = 'product page';
        p.appendChild(a); p.appendChild(D.createTextNode(' or the ')); p.appendChild(a2);
        p.appendChild(D.createTextNode('. Now compare the product, strength and lot on the report with your vial label.'));
      } else {
        card.className = 'card result-no';
        h.textContent = 'No public COA found for "' + raw + '" in this preview';
        p.textContent = 'This preview only knows the six public lots listed in the COA library. If your lot is not listed, email support@renvaralabs.com with the product name and lot number.';
      }
      card.appendChild(h); card.appendChild(p); out.appendChild(card);
    };
    lotForm.addEventListener('submit', function (e) { e.preventDefault(); run(); });
    var m = /[?&]lot=([^&]+)/.exec(W.location.search);
    if (m) { try { inp.value = decodeURIComponent(m[1]); } catch (e) { inp.value = m[1]; } run(); }
  }

  /* ---- preview-safe forms: nothing is sent or stored ---- */
  qsa('form[data-preview-form]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var msg = qs('[data-preview-msg]', f.parentNode) || qs('[data-preview-msg]', f);
      if (msg) {
        msg.hidden = false;
        msg.textContent = f.getAttribute('data-preview-text') || 'This is a preview. Nothing was sent or saved.';
        msg.setAttribute('tabindex', '-1'); msg.focus();
      }
    });
  });
  qsa('[data-print]').forEach(function (b) { b.addEventListener('click', function () { W.print(); }); });

  /* ---- home lot verifier: in-browser match over the six public lots ---- */
  var hv = qs('[data-lot-form]');
  if (hv) {
    var hvData = [];
    try { hvData = JSON.parse(qs('#hv-data').textContent); } catch (e) { hvData = []; }
    var hvIn = qs('input', hv), hvOut = qs('#hv-out');
    var hvNorm = function (s) { return s.toUpperCase().replace(/[^A-Z0-9]/g, ''); };
    var el = function (tag, cls, txt) { var n = D.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; return n; };
    var hvRun = function () {
      var raw = hvIn.value.trim(); hvOut.textContent = '';
      if (!raw) return;
      var n = hvNorm(raw), hit = hvData.filter(function (r) { var l = hvNorm(r.lot); return l === n || l === 'DPS' + n; })[0];
      var card = el('div', 'vcard' + (hit ? '' : ' no'));
      if (hit) {
        card.appendChild(el('p', 'tag', 'Match found'));
        card.appendChild(el('h3', null, hit.product));
        var dl = el('dl');
        [['Lot', hit.lot], ['Strength', hit.strength], ['Analyzed', hit.analyzed], ['Laboratory', hit.lab + ', report ' + hit.report], ['Result', hit.result]].forEach(function (r) {
          dl.appendChild(el('dt', null, r[0])); dl.appendChild(el('dd', null, r[1]));
        });
        card.appendChild(dl);
        var row = el('div', 'btn-row'), a = el('a', 'btn', 'Open the lab report');
        a.href = hit.coa; a.target = '_blank'; a.rel = 'noopener noreferrer';
        a.appendChild(el('span', 'sr-only', ' (opens in a new tab)'));
        var a2 = el('a', 'btn btn-out', 'Product page'); a2.href = (D.body.getAttribute('data-root') || '') + hit.page;
        row.appendChild(a); row.appendChild(a2); card.appendChild(row);
      } else {
        card.appendChild(el('p', 'tag', 'No public report found'));
        card.appendChild(el('h3', null, 'No match for ' + raw.slice(0, 40) + '.'));
        var p = el('p', null, 'Check the lot number on the vial label against the six public lots. If yours is not listed, email ');
        var m = el('a', null, 'support@renvaralabs.com'); m.href = 'mailto:support@renvaralabs.com';
        p.appendChild(m); p.appendChild(D.createTextNode(' with the product name, lot number and order number.'));
        card.appendChild(p);
      }
      hvOut.appendChild(card);
    };
    hv.addEventListener('submit', function (e) { e.preventDefault(); hvRun(); });
    qsa('[data-try]').forEach(function (b) { b.addEventListener('click', function () { hvIn.value = b.getAttribute('data-try'); hvRun(); }); });
  }

  /* =======================================================================================
     MOTION. Scroll-scrubbed vial spin on home (sticky storytelling, pinned), progressive
     text reveal, staggered shelf entrance, sticky counter, count-up numbers. rAF +
     IntersectionObserver; transform, opacity and canvas only. Off under reduced motion.
     ======================================================================================= */
  var rm = W.matchMedia ? W.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var vh = W.innerHeight, ticking = false, live = [];
  var TAU = Math.PI * 2;
  function easeInOut(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function lerp(a, b, t) { return a + (b - a) * t; }

  /* hero: two full turns over the scene; it settles for beat 1 with the label facing you */
  function angleAt(p) {
    if (p < 0.27) return lerp(0, TAU - 0.3, easeInOut(p / 0.27));
    if (p < 0.47) return lerp(TAU - 0.3, TAU + 0.3, (p - 0.27) / 0.2);
    return lerp(TAU + 0.3, 2 * TAU, easeInOut((p - 0.47) / 0.53));
  }
  var scene = qs('[data-scene]'), sc = null;
  if (scene) {
    sc = { el: scene, cv: qs('canvas[data-vial]', scene), beats: qsa('[data-beat]', scene), dots: qsa('.dots li', scene), idx: -1 };
    sc.beats.forEach(function (b, i) {
      b.addEventListener('focusin', function () {
        if (!root.classList.contains('motion')) return;
        var top = scene.getBoundingClientRect().top + W.pageYOffset, span = scene.offsetHeight - vh;
        W.scrollTo(0, top + span * (i + 0.5) / sc.beats.length);
      });
    });
  }
  function sceneFrame() {
    var r = sc.el.getBoundingClientRect(), span = sc.el.offsetHeight - vh;
    var p = clamp(span > 0 ? -r.top / span : 0), v = sc.cv && sc.cv.__vial;
    var n = sc.beats.length, idx = Math.min(n - 1, Math.floor(p * n * 0.999));
    if (v) { v.setAngle(angleAt(p)); v.setHighlight(idx === 1); }
    if (sc.cv) {
      var s = 0.9 + 0.16 * easeInOut(clamp(p / 0.85)), ty = (1 - easeOut(clamp(p / 0.5))) * 3;
      sc.cv.style.transform = 'translate3d(0,' + ty.toFixed(2) + 'vh,0) scale(' + s.toFixed(4) + ')';
    }
    if (idx !== sc.idx) {
      sc.idx = idx;
      sc.beats.forEach(function (b, i) { b.classList.toggle('is-on', i === idx); b.classList.toggle('was-on', i < idx); });
      sc.dots.forEach(function (d, i) { d.classList.toggle('is-on', i === idx); });
    }
  }
  function sceneReset() {
    if (!sc) return;
    if (sc.cv) { sc.cv.style.transform = ''; if (sc.cv.__vial) sc.cv.__vial.setAngle(parseFloat(sc.cv.dataset.still || '-0.4')).setHighlight(false); }
    sc.beats.forEach(function (b) { b.classList.remove('is-on', 'was-on'); });
    sc.idx = -1;
  }

  /* progressive text reveal: words go from faint to full as the line crosses the screen */
  var rv = qs('[data-reveal]'), words = [];
  if (rv) {
    var txt = rv.textContent.trim().split(/\s+/);
    var full = rv.textContent.trim();
    rv.textContent = '';
    var sr = D.createElement('span'); sr.className = 'sr-only'; sr.textContent = full; rv.appendChild(sr);
    txt.forEach(function (w, i) {
      var s = D.createElement('span'); s.className = 'w'; s.setAttribute('aria-hidden', 'true'); s.textContent = w;
      rv.appendChild(s); if (i < txt.length - 1) rv.appendChild(D.createTextNode(' '));
      words.push(s);
    });
  }
  function revealFrame() {
    var r = rv.getBoundingClientRect(), p = clamp((vh * 0.85 - r.top) / (vh * 0.55 + r.height * 0.6));
    var k = Math.round(p * words.length);
    words.forEach(function (w, i) { w.classList.toggle('on', i < k); });
  }

  /* sticky counter beside the seven tests */
  var tests = qs('[data-tests]');
  if (tests && 'IntersectionObserver' in W) {
    var cn = qs('[data-count-n]', tests), cname = qs('[data-count-name]', tests), rows = qsa('[data-test]', tests), cur = 1;
    var tio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var k = parseInt(e.target.getAttribute('data-test'), 10);
        if (k === cur) return;
        cur = k; cn.textContent = k; cname.textContent = e.target.getAttribute('data-name');
        if (root.classList.contains('motion')) { cn.classList.remove('flip'); void cn.offsetWidth; cn.classList.add('flip'); }
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    rows.forEach(function (r) { tio.observe(r); });
  }

  /* shelf staggered entrance + count-up numbers (once) */
  var onceEls = qsa('[data-shelf],[data-countup]');
  function countUp(elm) {
    var to = parseInt(elm.getAttribute('data-countup'), 10), suf = elm.getAttribute('data-suffix') || '', t0 = 0;
    if (!root.classList.contains('motion')) return;
    function step(t) {
      if (!t0) t0 = t;
      var q = clamp((t - t0) / 1100);
      elm.textContent = Math.round(to * easeOut(q)) + suf;
      if (q < 1) W.requestAnimationFrame(step);
    }
    W.requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in W) {
    var oio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        oio.unobserve(e.target);
        if (e.target.hasAttribute('data-shelf')) e.target.classList.add('is-in');
        else countUp(e.target);
      });
    }, { threshold: 0.3 });
    onceEls.forEach(function (x) { oio.observe(x); });
  } else onceEls.forEach(function (x) { x.classList.add('is-in'); });

  function frame() {
    ticking = false;
    if (!root.classList.contains('motion')) return;
    if (sc && live.indexOf(sc.el) > -1) sceneFrame();
    if (rv && live.indexOf(rv) > -1) revealFrame();
  }
  function request() { if (!ticking) { ticking = true; W.requestAnimationFrame(frame); } }

  var watched = [sc && sc.el, rv].filter(Boolean);
  if ('IntersectionObserver' in W) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var i = live.indexOf(en.target);
        if (en.isIntersecting && i < 0) live.push(en.target);
        if (!en.isIntersecting && i > -1) live.splice(i, 1);
      });
      request();
    }, { rootMargin: '10% 0px 10% 0px' });
    watched.forEach(function (el2) { io.observe(el2); });
  } else { live = watched.slice(); }

  function setMotion() {
    var on = !rm.matches;
    root.classList.toggle('motion', on);
    if (on) { vh = W.innerHeight; request(); }
    else { sceneReset(); words.forEach(function (w) { w.classList.add('on'); }); qsa('[data-shelf]').forEach(function (x) { x.classList.add('is-in'); }); }
  }
  setMotion();
  D.addEventListener('vials:ready', function () { if (root.classList.contains('motion')) { sc && (sc.idx = -1); request(); } else sceneReset(); });
  if (rm.addEventListener) rm.addEventListener('change', setMotion); else if (rm.addListener) rm.addListener(setMotion);
  W.addEventListener('scroll', request, { passive: true });
  W.addEventListener('resize', function () { vh = W.innerHeight; request(); });
})();
