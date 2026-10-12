/* Renvara Labs preview v2. One shared script, vanilla JS, no libraries, no network calls.
   Every page reads fully with JavaScript off. Motion uses transform and opacity only and is
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

  /* =======================================================================================
     MOTION. Apple style motion tied to scroll: one pinned section on home, a quiet turning
     vial on product pages. requestAnimationFrame + IntersectionObserver, transform/opacity only.
     ======================================================================================= */
  var rm = W.matchMedia ? W.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var vh = W.innerHeight, ticking = false, live = [];

  // the specular sweep is masked to the vial's own pixels (the client's PNG); if the mask
  // cannot load, the sweep simply does not show
  qsa('[data-sheen]').forEach(function (s) {
    var img = s.parentNode.querySelector('img');
    if (img) s.style.setProperty('--vial', 'url("' + (img.currentSrc || img.src) + '")');
  });

  function drawTrace(fig, d, q) {
    if (!fig) return;
    var r = fig.querySelector('.draw-rect'), ms = fig.querySelector('.ms'), pk = fig.querySelector('.lbl-peak');
    if (r) r.setAttribute('transform', 'scale(' + d.toFixed(4) + ' 1)');
    if (ms) ms.style.transform = 'scaleY(' + q.toFixed(4) + ')';
    if (pk) pk.style.opacity = d > 0.62 ? 1 : 0;
    fig.classList.toggle('is-drawing', d > 0.02);
  }
  function resetTrace(fig) {
    if (!fig) return;
    var r = fig.querySelector('.draw-rect'), ms = fig.querySelector('.ms'), pk = fig.querySelector('.lbl-peak');
    if (r) r.removeAttribute('transform');
    if (ms) ms.style.transform = '';
    if (pk) pk.style.opacity = '';
    fig.classList.remove('is-drawing');
  }

  /* -- home: sticky storytelling section, scrubbed animation -- */
  var scene = qs('[data-scene]'), sc = null;
  if (scene) {
    sc = {
      el: scene, vial: qs('[data-vial] .vial', scene), sheen: qs('[data-sheen]', scene), glow: qs('[data-glow]', scene),
      trace: qs('[data-trace]', scene), bar: qs('[data-progress]', scene), beats: qsa('[data-beat]', scene), idx: -1
    };
    // keyboard users: focusing a link in a hidden beat scrolls the scene to that beat
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
    var p = clamp(span > 0 ? -r.top / span : 0);
    // vial: scale in, tumble on its axis, tilt in perspective
    var s = 0.88 + 0.18 * easeOut(clamp(p / 0.42)) - 0.06 * easeOut(clamp((p - 0.62) / 0.38));
    var rot = -14 + 24 * p, ry = -26 + 52 * p, ty = (1 - easeOut(clamp(p / 0.3))) * 3;
    if (sc.vial) sc.vial.style.transform = 'translate3d(0,' + ty.toFixed(2) + 'vh,0) rotate(' + rot.toFixed(2) + 'deg) rotateY(' + ry.toFixed(2) + 'deg) scale(' + s.toFixed(4) + ')';
    if (sc.sheen) sc.sheen.style.transform = 'translateX(' + (-70 + 140 * ((p * 2.4) % 1)).toFixed(1) + '%)';
    if (sc.glow) { sc.glow.style.transform = 'scale(' + (0.82 + 0.3 * easeOut(p)).toFixed(4) + ')'; sc.glow.style.opacity = (0.55 + 0.45 * clamp(p / 0.4)).toFixed(3); }
    // SVG line draw: the chromatogram draws, then the mass-spectrum sticks rise
    drawTrace(sc.trace, clamp((p - 0.14) / 0.34), easeOut(clamp((p - 0.5) / 0.16)));
    if (sc.bar) sc.bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
    var n = sc.beats.length, idx = Math.min(n - 1, Math.floor(p * n));
    if (idx !== sc.idx) {
      sc.idx = idx;
      sc.beats.forEach(function (b, i) {
        b.classList.toggle('is-on', i === idx);
        b.classList.toggle('was-on', i < idx);
      });
    }
  }
  function sceneReset() {
    if (!sc) return;
    [sc.vial, sc.sheen, sc.glow, sc.bar].forEach(function (el) { if (el) { el.style.transform = ''; el.style.opacity = ''; } });
    resetTrace(sc.trace);
    sc.beats.forEach(function (b) { b.classList.remove('is-on', 'was-on'); });
    sc.idx = -1;
  }

  /* -- product pages: the vial turns slowly with scroll; type pages draw the trace -- */
  var ps = qs('[data-pscene]');
  function pFrame() {
    var r = ps.getBoundingClientRect(), p = clamp((vh - r.top) / (vh + r.height));
    var v = qs('[data-vial] .vial', ps), sh = qs('[data-sheen]', ps), tr = qs('[data-trace]', ps);
    if (v) v.style.transform = 'rotate(' + ((p - 0.5) * 14).toFixed(2) + 'deg) rotateY(' + ((p - 0.5) * 40).toFixed(2) + 'deg) scale(' + (0.96 + 0.06 * Math.sin(p * Math.PI)).toFixed(4) + ')';
    if (sh) sh.style.transform = 'translateX(' + (-70 + 140 * ((p * 1.8) % 1)).toFixed(1) + '%)';
    if (tr) drawTrace(tr, clamp(0.3 + p * 1.25), easeOut(clamp((p - 0.42) / 0.2)));
  }
  function pReset() {
    if (!ps) return;
    var v = qs('[data-vial] .vial', ps), sh = qs('[data-sheen]', ps);
    if (v) v.style.transform = ''; if (sh) sh.style.transform = '';
    resetTrace(qs('[data-trace]', ps));
  }

  /* -- home: the three-vial image scales in (scale in animation, scrubbed) -- */
  var fan = qs('[data-fan-art]');
  function fanFrame() {
    var r = fan.getBoundingClientRect(), p = easeOut(clamp((vh - r.top) / (vh * 0.85)));
    fan.style.transform = 'translate3d(0,' + ((1 - p) * 56).toFixed(1) + 'px,0) scale(' + (0.84 + 0.16 * p).toFixed(4) + ')';
    fan.style.opacity = (0.3 + 0.7 * p).toFixed(3);
  }
  function fanReset() { if (fan) { fan.style.transform = ''; fan.style.opacity = ''; } }

  function frame() {
    ticking = false;
    if (!root.classList.contains('motion')) return;
    if (sc && live.indexOf(sc.el) > -1) sceneFrame();
    if (ps && live.indexOf(ps) > -1) pFrame();
    if (fan && live.indexOf(fan) > -1) fanFrame();
  }
  function request() { if (!ticking) { ticking = true; W.requestAnimationFrame(frame); } }

  // only scenes on screen are updated (viewport threshold via IntersectionObserver)
  var watched = [sc && sc.el, ps, fan].filter(Boolean);
  if ('IntersectionObserver' in W) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var i = live.indexOf(en.target);
        if (en.isIntersecting && i < 0) live.push(en.target);
        if (!en.isIntersecting && i > -1) live.splice(i, 1);
      });
      request();
    }, { rootMargin: '10% 0px 10% 0px' });
    watched.forEach(function (el) { io.observe(el); });
  } else { live = watched.slice(); }

  function setMotion() {
    var on = !rm.matches && watched.length > 0;
    root.classList.toggle('motion', on);
    if (on) { vh = W.innerHeight; request(); }
    else { sceneReset(); pReset(); fanReset(); }
  }
  setMotion();
  if (rm.addEventListener) rm.addEventListener('change', setMotion); else if (rm.addListener) rm.addListener(setMotion);
  W.addEventListener('scroll', request, { passive: true });
  W.addEventListener('resize', function () { vh = W.innerHeight; request(); });
})();
