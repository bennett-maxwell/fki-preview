/* Renvara Labs preview rebuild. One shared script, no libraries, no network calls.
   Storage is wrapped in try/catch; every page works with JavaScript off. */
(function () {
  'use strict';
  var D = document, W = window, root = D.documentElement;
  root.classList.add('js');

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
  function focusables(ctx) {
    return qsa('a[href],button:not([disabled]),input:not([disabled]):not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"])', ctx)
      .filter(function (el) { return el.offsetParent !== null || el === D.activeElement; });
  }

  /* ---- dialogs: focus trap + inert background ---- */
  var scope = qsa('[data-gate-scope]');
  function setInert(on) {
    scope.forEach(function (el) {
      if (on) { el.setAttribute('inert', ''); el.setAttribute('aria-hidden', 'true'); }
      else { el.removeAttribute('inert'); el.removeAttribute('aria-hidden'); }
    });
  }
  function trap(dialog, e) {
    if (e.key !== 'Tab') return;
    var f = focusables(dialog);
    if (!f.length) { e.preventDefault(); return; }
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && (D.activeElement === first || !dialog.contains(D.activeElement))) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && (D.activeElement === last || !dialog.contains(D.activeElement))) { e.preventDefault(); first.focus(); }
  }

  /* ---- 21+ / researcher gate (Escape never bypasses; "Leave site" works) ---- */
  var GATE_KEY = 'renvaraPreviewGate.v1', GATE_DAYS = 30;
  var gate = qs('#gate');
  function gateAccepted() {
    var raw = store('l', 'g', GATE_KEY) || store('s', 'g', GATE_KEY);
    var t = parseInt(raw, 10);
    return !!t && (Date.now() - t) < GATE_DAYS * 864e5;
  }
  function openGate() {
    gate.hidden = false;
    root.classList.add('gate-open');
    setInert(true);
    var first = qs('input[type=checkbox]', gate);
    if (first) first.focus();
  }
  function closeGate() {
    gate.hidden = true;
    root.classList.remove('gate-open');
    setInert(false);
    var main = qs('#main');
    if (main) { main.setAttribute('tabindex', '-1'); main.focus({ preventScroll: true }); }
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
      store('l', 's', GATE_KEY, now);
      store('s', 's', GATE_KEY, now);
      closeGate();
    });
    gate.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); return; }
      trap(gate, e);
    });
    if (!gateAccepted()) openGate();
  }

  /* ---- mobile nav toggle ---- */
  var toggle = qs('#nav-toggle'), nav = qs('#site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    D.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* ---- catalog filter chips + text filter ---- */
  var chipWrap = qs('[data-chips]');
  if (chipWrap) {
    var items = qsa('[data-type]'), countEl = qs('[data-count]'), textIn = qs('[data-filter-text]');
    var active = 'all';
    var apply = function () {
      var q = textIn ? textIn.value.trim().toLowerCase() : '', n = 0;
      items.forEach(function (el) {
        var show = (active === 'all' || el.getAttribute('data-type') === active) &&
          (!q || el.textContent.toLowerCase().indexOf(q) > -1);
        el.hidden = !show;
        if (show) n++;
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
      rows.forEach(function (r) {
        var show = !q || r.textContent.toLowerCase().indexOf(q) > -1;
        r.hidden = !show;
        if (show) n++;
      });
      if (none) none.hidden = n !== 0;
      if (cnt) cnt.textContent = n + ' of ' + rows.length + ' public lot reports shown';
    });
  }

  /* ---- lot lookup over the six known public lots (client side only) ---- */
  var lotForm = qs('#lot-form');
  if (lotForm) {
    var data = [];
    try { data = JSON.parse(qs('#lots-data').textContent); } catch (e) { data = []; }
    var out = qs('#lot-result'), inp = qs('#lot'), rootPath = D.body.getAttribute('data-root') || '';
    var norm = function (s) { return s.toUpperCase().replace(/[^A-Z0-9]/g, ''); };
    var run = function () {
      var raw = inp.value.trim();
      if (!raw) { out.textContent = ''; return; }
      var n = norm(raw), hit = data.filter(function (r) {
        var l = norm(r.lot);
        return l === n || l === 'DPS' + n;
      })[0];
      out.textContent = '';
      var card = D.createElement('div'), h = D.createElement('h3'), p = D.createElement('p');
      card.className = 'card';
      if (hit) {
        h.textContent = 'Match: ' + hit.product + ', lot ' + hit.lot;
        p.textContent = hit.strength + '. Analyzed ' + hit.analyzed + ' by ' + hit.lab + ' (report ' + hit.report + '). Result: ' + hit.result + '. ';
        var a = D.createElement('a'); a.href = hit.coa; a.target = '_blank'; a.rel = 'noopener noreferrer'; a.className = 'ext'; a.textContent = 'Open the lab-hosted COA';
        var a2 = D.createElement('a'); a2.href = rootPath + hit.page; a2.textContent = 'Product page';
        p.appendChild(a); p.appendChild(D.createTextNode(' or ')); p.appendChild(a2); p.appendChild(D.createTextNode('. Now compare the product, strength and lot on the report with your vial label.'));
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
        msg.setAttribute('tabindex', '-1');
        msg.focus();
      }
    });
  });

  /* ---- exit-intent offer: desktop pointers only, once per session ---- */
  var exit = qs('#exit');
  if (exit && !D.body.hasAttribute('data-no-exit') &&
      W.matchMedia && W.matchMedia('(hover: hover) and (pointer: fine)').matches &&
      !store('s', 'g', 'renvaraExit.v1')) {
    var armed = false, shown = false, lastFocus = null;
    W.setTimeout(function () { armed = true; }, 6000);
    var closeExit = function () {
      exit.hidden = true;
      root.classList.remove('exit-open');
      setInert(false);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    };
    var openExit = function () {
      if (!armed || shown || (gate && !gate.hidden)) return;
      shown = true;
      store('s', 's', 'renvaraExit.v1', '1');
      lastFocus = D.activeElement;
      exit.hidden = false;
      root.classList.add('exit-open');
      setInert(true);
      var f = focusables(exit);
      if (f.length) f[0].focus();
    };
    D.addEventListener('mouseout', function (e) {
      if (!e.relatedTarget && e.clientY <= 0) openExit();
    });
    exit.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); closeExit(); return; }
      trap(exit, e);
    });
    exit.addEventListener('click', function (e) { if (e.target === exit) closeExit(); });
    qsa('[data-exit-close]', exit).forEach(function (b) { b.addEventListener('click', closeExit); });
  }

  /* ---- print button ---- */
  qsa('[data-print]').forEach(function (b) { b.addEventListener('click', function () { W.print(); }); });
})();