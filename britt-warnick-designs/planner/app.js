/* Britt Warnick Designs — wedding design planner. Vanilla JS, no build step.
   Style scoring mirrors build/reachability.py exactly (same weights, same 5-step tie-break, same top-3 percent rounding). */
'use strict';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const D = {};
const STORE = 'bwd-planner-v6';
const SESSION = 'bwd-planner-v6-session';
const RATINGS = 'bwd-planner-v6-ratings';
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const MON3 = MONTHS.map(m => m.slice(0, 3));
const SEASON_M = { spring: [3, 4, 5], summer: [6, 7, 8], fall: [9, 10, 11], winter: [12, 1, 2] };
const TIERS = ['Under $35k', '$35-70k', '$70k+'];
const reduceMotion = () => window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function lsGet(k, store) { try { return JSON.parse((store || localStorage).getItem(k)); } catch (e) { return null; } }
function lsSet(k, v, store) { try { (store || localStorage).setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }

function freshState() {
  return { names: ['', ''], answers: {}, picks: [], plan: { region: [] }, sample: false, sampleEdited: false, details: null, swaps: {}, checks: {}, done: false };
}
let S = lsGet(SESSION, window.sessionStorage) || freshState();
let RATE = lsGet(RATINGS) || {};
function persist() { lsSet(SESSION, S, window.sessionStorage); }

/* ---------------- data ---------------- */
const getJSON = n => fetch('data/' + n + '.json').then(r => { if (!r.ok) throw new Error(n); return r.json(); });
function loadFail() { $('#view').innerHTML = '<div class="wrap"><p class="empty">The planner could not load. Please refresh the page.</p></div>'; }
/* Only quiz + styles load up front (the quiz is usable at once). Venues, places and design ideas load on the first
   interaction or when a screen needs them. */
function loadRest() {
  if (!D.restP) {
    D.restP = Promise.all(['venues', 'cities', 'options'].map(getJSON)).then(([v, c, o]) => {
      D.venues = v; D.cities = c; D.options = o; indexRest(); D.ready = true;
      if (!location.hash || location.hash === '#/' || location.hash === '#') fillWelcome();
    });
    D.restP.catch(loadFail);
  }
  return D.restP;
}
async function load() {
  try { const [q, s] = await Promise.all(['quiz', 'styles'].map(getJSON)); D.quiz = q; D.styles = s; }
  catch (e) { loadFail(); return; }
  indexData();
  window.addEventListener('hashchange', route);
  document.addEventListener('keydown', onKey);
  ['pointerdown', 'keydown', 'touchstart'].forEach(ev => document.addEventListener(ev, loadRest, { once: true, passive: true }));
  document.addEventListener('error', e => { const t = e.target; if (t && t.tagName === 'IMG') { const ph = t.closest('.ph'); if (ph) ph.classList.add('noimg'); } }, true);
  $('#sheet').addEventListener('click', e => { if (e.target.id === 'sheet' || e.target.closest('[data-close]')) closeSheet(); });
  $('#sheet').addEventListener('close', () => { if (D._ratingChanged) { D._ratingChanged = false; refreshLists(); } });
  window.addEventListener('beforeprint', () => $$('details.fold:not([open])').forEach(d => { d.dataset.printOpen = '1'; d.open = true; }));
  window.addEventListener('afterprint', () => $$('details[data-print-open]').forEach(d => { d.open = false; delete d.dataset.printOpen; }));
  route();
}

function indexData() {
  D.STY = D.styles.styles;
  D.SIDS = D.STY.map(s => s.id);
  D.SIDX = Object.fromEntries(D.SIDS.map((s, i) => [s, i]));
  D.styleById = Object.fromEntries(D.STY.map(s => [s.id, s]));
  D.QS = D.quiz.questions;
  D.ANCH = new Set(D.QS.filter(q => q.anchor).map(q => q.id));
  D.CS = D.quiz.color_step;
  D.PAL = D.CS.palettes;
  D.MAXP = D.CS.max_picks;
  D.WPP = D.CS.weight_per_pick;
  D.palById = Object.fromEntries(D.PAL.map(p => [p.palette_id, p]));
  D.PAL_STYLE = Object.fromEntries(D.PAL.map(p => [p.palette_id, p.style_id]));
  D.PD = Object.fromEntries(D.quiz.planning_details.concat(D.quiz.extra_optional).map(q => [q.id, q]));
  D.regionOrder = D.quiz.planning_details.find(q => q.id === 'region').options.filter(o => o.region_value).map(o => o.region_value);
  // quiz steps: two anchor questions, the color step, the other style questions, then planning details
  const steps = [];
  D.QS.forEach((q, i) => { steps.push({ kind: 'q', q }); if (i === 1) steps.push({ kind: 'color' }); });
  ['occasion', 'guest_count', 'budget_band', 'season', 'region', 'setting', 'priority', 'kids'].forEach(id => steps.push({ kind: 'p', q: D.PD[id] }));
  D.STEPS = steps;
}
function indexRest() {
  D.V = D.venues.venues;
  D.vById = Object.fromEntries(D.V.map(v => [v.id, v]));
  D.AREAS = D.cities.areas;
  D.areaById = Object.fromEntries(D.AREAS.map(a => [a.id, a]));
  D.vArea = D.cities.venue_area;
  D.CATS = D.options.categories;
  D.regions = [...new Set(D.AREAS.map(a => a.region))];
}

/* ---------------- style scoring (mirror of reachability.py) ---------------- */
function scoreStyles(answers, picks) {
  const tot = {}, br = {}, an = {}, pc = {};
  D.SIDS.forEach(s => { tot[s] = 0; br[s] = 0; an[s] = 0; pc[s] = 0; });
  for (const q of D.QS) {
    const oid = answers[q.id];
    if (oid == null) continue;
    const opt = q.options.find(o => o.id === oid);
    if (!opt) continue;
    for (const [s, w] of Object.entries(opt.weights)) {
      tot[s] = (tot[s] || 0) + w; br[s] = (br[s] || 0) + 1;
      if (D.ANCH.has(q.id)) an[s] = (an[s] || 0) + w;
    }
  }
  (picks || []).slice(0, D.MAXP).forEach(p => { const s = D.PAL_STYLE[p]; if (!s) return; tot[s] += D.WPP; pc[s] += 1; });
  const ranked = D.SIDS.slice().sort((a, b) => (tot[b] - tot[a]) || (br[b] - br[a]) || (an[b] - an[a]) || (pc[b] - pc[a]) || (D.SIDX[a] - D.SIDX[b]));
  return ranked.map(s => ({ id: s, score: tot[s], breadth: br[s], anchor: an[s], picks: pc[s] }));
}
function top3pct(ranked) {
  const top = ranked.slice(0, 3);
  const total = top.reduce((a, x) => a + x.score, 0);
  if (!total) return top.map(x => Object.assign({}, x, { pct: 0 }));
  const raw = top.map(x => 100 * x.score / total);
  const fl = raw.map(x => Math.floor(x));
  const rem = 100 - fl.reduce((a, b) => a + b, 0);
  const order = [0, 1, 2].sort((i, j) => (raw[j] - fl[j]) - (raw[i] - fl[i]));
  order.slice(0, rem).forEach(i => { fl[i] += 1; });
  return top.map((x, i) => Object.assign({}, x, { pct: fl[i] }));
}

/* ---------------- couple context ---------------- */
function regionValues() {
  const ids = S.plan.region || [];
  if (!ids.length || ids.includes('anywhere')) return [];
  const opts = D.PD.region.options;
  return ids.map(id => (opts.find(o => o.id === id) || {}).region_value).filter(Boolean);
}
function planMonth() {
  if (S.plan.date && /^\d{4}-\d{2}-\d{2}$/.test(S.plan.date)) return +S.plan.date.slice(5, 7);
  if (S.plan.month) return +S.plan.month;
  return null;
}
function seasonOfMonth(m) { return Object.keys(SEASON_M).find(k => SEASON_M[k].includes(m)); }
function planSeason() {
  const m = planMonth();
  if (m) return seasonOfMonth(m);
  const s = S.plan.season;
  return s && s !== 'flexible' ? s : null;
}
function planMonths() { const m = planMonth(); if (m) return [m]; const s = planSeason(); return s ? SEASON_M[s] : null; }
function guestOpt() {
  let id = S.plan.guest_count;
  if (!id && S.plan.occasion === 'elopement') id = 'under_20';
  return id ? D.PD.guest_count.options.find(o => o.id === id) : null;
}
function bandIndex() {
  const id = S.plan.budget_band;
  if (!id) return null;
  const o = D.PD.budget_band.options.find(x => x.id === id);
  return o && o.budget_tier_index != null ? o.budget_tier_index : null;
}
function hasStyleAnswers() { return Object.keys(S.answers).length > 0 || S.picks.length > 0; }
function context() {
  const ranked = scoreStyles(S.answers, S.picks);
  const top3 = top3pct(ranked);
  const has = top3.some(x => x.score > 0);
  return {
    ranked, top3, hasStyle: has,
    topIds: has ? top3.map(x => x.id) : [],
    band: bandIndex(), guest: guestOpt(), season: planSeason(), months: planMonths(), month: planMonth(),
    regions: regionValues(), elopement: S.plan.occasion === 'elopement'
  };
}
function chosenPalettes(ctx) {
  const picks = S.picks.filter(p => D.palById[p]);
  let main = null;
  if (ctx.hasStyle) main = picks.find(p => D.PAL_STYLE[p] === ctx.topIds[0]) || picks[0] || D.styleById[ctx.topIds[0]].primary_palette_id;
  else main = picks[0] || null;
  let alt = null;
  if (ctx.hasStyle) {
    const s2 = D.styleById[ctx.topIds[1]];
    const cands = [s2.primary_palette_id].concat(D.PAL.filter(p => p.style_id === s2.id).map(p => p.palette_id));
    alt = cands.find(p => !picks.includes(p) && p !== main) || null;
  }
  return { main, picks, alt };
}

/* ---------------- venue helpers ---------------- */
const num = x => (typeof x === 'number' && isFinite(x)) ? x : null;
const hasPrice = v => v.price_from && typeof v.price_from === 'object' && typeof v.price_from.amount === 'number';
function tierIdx(v) { const i = TIERS.indexOf(v.budget_tier); return i < 0 ? null : i; }
function normCountry(c) { return c === 'USA' ? 'United States' : c; }
function hostOf(u) { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return ''; } }
const MONTH_RE = /\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b\.?(?:\s*(?:-|–|—|to|through)\s*(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b)?/g;
function monthsIn(text) {
  const t = String(text || '').toLowerCase().replace(/\b(december|dec)\s+is\b[^;.)]*/g, ' ');
  const set = new Set();
  let m; MONTH_RE.lastIndex = 0;
  while ((m = MONTH_RE.exec(t))) {
    const a = MON3.findIndex(x => m[1].startsWith(x.toLowerCase()));
    const b = m[2] ? MON3.findIndex(x => m[2].startsWith(x.toLowerCase())) : a;
    if (a < 0 || b < 0) continue;
    let i = a; set.add(i + 1); let guard = 0;
    while (i !== b && guard++ < 12) { i = (i + 1) % 12; set.add(i + 1); }
  }
  return set;
}
function seasonNamed(v, season) {
  const raw = String(v.best_season || '');
  const t = raw.toLowerCase();
  if (!t || t === 'not published') return false;
  if (/year[- ]round|all year|any time|anytime|all seasons/.test(t)) return true;
  const words = season === 'fall' ? ['fall', 'autumn'] : [season];
  const cleaned = t.replace(/\b(december|dec)\s+is\b[^;.)]*/g, ' ');
  if (words.some(w => new RegExp('\\b' + w + '\\b').test(cleaned))) return true;
  const ms = monthsIn(raw);
  return SEASON_M[season].some(m => ms.has(m));
}
function venueArea(v) { return D.areaById[D.vArea[v.id]] || null; }
/* A starting venue fee (rental, site fee, ceremony fee) is not a wedding total: its budget tier counts less. */
const FULL_COST_RE = /full (reception )?package|all[- ]inclusive|per[- ]?person|per[- ]guest|\bpp\b|food|catering|dinner|menu|meal|drink|\bbar\b|buffet/i;
function feeOnly(v) { return hasPrice(v) && !v.price_from.guests_basis && !FULL_COST_RE.test(String(v.price_from.what_it_covers || '')); }
function tierLabel(v) { return v.budget_tier === 'unknown' ? 'Tier unknown' : v.budget_tier + (feeOnly(v) ? ' · starting fee only' : ''); }
/* Climate text follows the couple's month. The data only has a written December note, so it shows only for December. */
const DEC_RE = /\bdecember\b/i;
function stripDecember(t) { return String(t || '').replace(/[;,]?\s*\b(december|dec)\s+is\b[^;.()]*(\([^)]*\))?/gi, '').replace(/\s{2,}/g, ' ').trim(); }

/* 100-point venue score (ported partner rubric; AUTO parts computed, MANUAL parts rated on tour) */
function scoreVenue(v, ctx) {
  const parts = [];
  const add = (id, label, max, pts, note) => parts.push({ id, label, max, pts, note, on: pts != null });
  const crit = Object.fromEntries(D.quiz.venue_rubric.criteria.map(c => [c.id, c]));
  // budget fit
  if (ctx.band != null) {
    const ti = tierIdx(v);
    const fee = feeOnly(v); let p;
    if (ti == null) p = 7;
    else if (ti <= ctx.band) p = fee ? 9 : 14;
    else if (ti === ctx.band + 1) p = fee ? 3 : 5;
    else p = 0;
    add('budget_fit', 'Budget', crit.budget_fit.points, p, ti == null ? 'price on request' : v.budget_tier + (fee ? ' (starting fee only)' : ''));
  } else add('budget_fit', 'Budget', crit.budget_fit.points, null, 'answer budget to score');
  // capacity
  if (ctx.guest) {
    const c = num(v.capacity_reception); const g = ctx.guest; const need = g.max != null ? g.max : g.min;
    let p; if (c == null) p = 5; else if (c >= need) p = 10; else if (c >= g.min) p = 7; else p = 0;
    add('capacity_fit', 'Capacity', crit.capacity_fit.points, p, c == null ? 'not published' : 'seats ' + c);
  } else add('capacity_fit', 'Capacity', crit.capacity_fit.points, null, 'answer guests to score');
  // style match
  if (ctx.hasStyle) {
    const tags = v.style_tags || []; let p = 0, note = 'no match';
    if (tags.includes(ctx.topIds[0])) { p = 30; note = D.styleById[ctx.topIds[0]].name; }
    else if (tags.includes(ctx.topIds[1])) { p = 22; note = D.styleById[ctx.topIds[1]].name; }
    else if (tags.includes(ctx.topIds[2])) { p = 15; note = D.styleById[ctx.topIds[2]].name; }
    else {
      const aff = D.styleById[ctx.topIds[0]].venue_type_affinity || [];
      const ty = String(v.type || '').toLowerCase();
      if (aff.some(a => ty.includes(a.toLowerCase()))) { p = 8; note = 'venue type fits'; }
    }
    add('style_match', 'Style', crit.style_match.points, p, note);
  } else add('style_match', 'Style', crit.style_match.points, null, 'take the quiz to score');
  // season fit
  if (ctx.season) {
    const bs = String(v.best_season || '').toLowerCase(); let p;
    if (!bs || bs === 'not published') p = 4;
    else if (seasonNamed(v, ctx.season)) p = bs.startsWith('region typical') ? 6 : 8;
    else p = (v.setting === 'indoor' || v.setting === 'both') ? 5 : 2;
    add('season_fit', 'Season', crit.season_fit.points, p, ctx.season);
  } else add('season_fit', 'Season', crit.season_fit.points, null, 'answer season to score');
  // vendor access
  const cat = { 'outside allowed': 6, 'in-house optional': 5, 'in-house required': 3, 'not published': 3 }[v.catering];
  add('vendor_access', 'Catering', crit.vendor_access.points, cat == null ? 3 : cat, v.catering);
  // guest logistics
  let gl = v.onsite_lodging === 'yes' ? 4 : v.onsite_lodging === 'no' ? 0 : 2;
  if (v.nearest_airport && String(v.nearest_airport).toLowerCase() !== 'not published') gl += 2;
  add('guest_logistics', 'Lodging + airport', crit.guest_logistics.points, gl, 'lodging ' + v.onsite_lodging);
  // one site
  const prosT = (v.pros || []).join(' ').toLowerCase();
  const one = v.setting === 'both' || (/ceremon/.test(prosT) && /reception/.test(prosT)) ? 8 : 4;
  add('one_site', 'One site', crit.one_site.points, one, v.setting);
  // manual: wow
  const r = RATE[v.id] || {};
  add('wow_factor', 'Wow factor', crit.wow_factor.points, r.wow != null ? r.wow : null, 'rate on your tour');
  // rain plan
  let rain;
  if (v.setting === 'both' || v.setting === 'indoor') rain = 5;
  else rain = /tent|indoor backup|rain|covered/.test((prosT + ' ' + (v.cons || []).join(' ')).toLowerCase()) ? 3 : 1;
  add('rain_plan', 'Rain plan', crit.rain_plan.points, rain, v.setting);
  add('planner_network', 'Planner network', crit.planner_network.points, r.net != null ? r.net : null, 'rate on your tour');
  const used = parts.filter(p => p.on);
  const earned = used.reduce((a, p) => a + p.pts, 0);
  const avail = used.reduce((a, p) => a + p.max, 0);
  const sp = parts.find(x => x.id === 'style_match');
  const styleTier = !(sp && sp.on && sp.pts > 0) ? 0 : sp.note === 'venue type fits' ? 1 : 2;
  return { score: avail ? Math.round(100 * earned / avail) : 0, earned, avail, parts, styleMatch: styleTier > 0, styleTier };
}
/* Style-first: when the couple has a style, venues tagged with one of their top 3 styles rank first, then venues
   that only fit by venue type, then venues with no style match. The 100-point score orders venues inside each group. */
function rankVenues(list, ctx) {
  const scored = list.map(v => ({ v, s: scoreVenue(v, ctx) }));
  const styleHit = x => ctx.topIds.reduce((a, id, i) => a + ((x.v.style_tags || []).includes(id) ? 3 - i : 0), 0);
  const grp = x => ctx.hasStyle ? x.s.styleTier : 0;
  scored.sort((a, b) => (grp(b) - grp(a)) || (b.s.score - a.s.score) || (styleHit(b) - styleHit(a)) ||
    (ctx.elopement ? ((num(a.v.capacity_reception) || 1e9) - (num(b.v.capacity_reception) || 1e9)) : 0) ||
    ((b.v.photo ? 1 : 0) - (a.v.photo ? 1 : 0)) || ((hasPrice(b.v) ? 1 : 0) - (hasPrice(a.v) ? 1 : 0)) || a.v.name.localeCompare(b.v.name));
  return scored;
}

/* ---------------- area ranking ---------------- */
function scoreArea(a, ctx) {
  const R = a.ranking || {}; const parts = []; const why = []; let regionHit = 1, styleTier = 0;
  if (ctx.regions.length) {
    const hit = ctx.regions.includes(a.region); regionHit = hit ? 1 : 0;
    parts.push({ label: 'Region', max: 25, pts: hit ? 25 : 0 });
    why.push(hit ? `${a.region} is one of your regions` : `${a.region} is outside your regions`);
  }
  if (ctx.months) {
    let best = 0, bm = ctx.months[0];
    ctx.months.forEach(m => { const f = (R.season_fit || {})[String(m)] || 0; if (f > best) { best = f; bm = m; } });
    parts.push({ label: 'Month fit', max: 15, pts: best === 2 ? 15 : best === 1 ? 8 : 0 });
    const word = best === 2 ? 'in the best season' : best === 1 ? 'shoulder season' : 'outside the usual wedding season';
    why.push(`${MONTHS[bm - 1]} is ${word} here`);
  }
  if (ctx.band != null) {
    const tiers = (R.budget_tiers_present || []).map(t => TIERS.indexOf(t)).filter(i => i >= 0);
    let p; if (!tiers.length) p = 7; else p = tiers.some(i => i <= ctx.band) ? 15 : 0;
    parts.push({ label: 'Budget', max: 15, pts: p });
    why.push(!tiers.length ? 'venues here are price on request' : p ? `has venues in your budget band (${TIERS[Math.min(...tiers)]})` : 'listed venues sit above your budget band');
  }
  if (ctx.hasStyle) {
    const fits = R.style_fits || a.style_fits || []; const counts = R.style_counts || {};
    let p = 0, w = `${D.styleById[ctx.topIds[0]].name} is not tagged here`;
    if (fits.includes(ctx.topIds[0])) { p = 30; w = `${D.styleById[ctx.topIds[0]].name} (your #1 style) fits here`; }
    else if (fits.includes(ctx.topIds[1])) { p = 21; w = `${D.styleById[ctx.topIds[1]].name} (your #2 style) fits here`; }
    else if (fits.includes(ctx.topIds[2])) { p = 12; w = `${D.styleById[ctx.topIds[2]].name} (your #3 style) fits here`; }
    else if (counts[ctx.topIds[0]] > 0) { p = 6; w = `${counts[ctx.topIds[0]]} venue(s) tagged ${D.styleById[ctx.topIds[0]].name}`; }
    parts.push({ label: 'Style', max: 30, pts: p }); why.push(w); styleTier = p >= 12 ? 2 : p > 0 ? 1 : 0;
  }
  if (ctx.guest) {
    const need = ctx.guest.max != null ? ctx.guest.max : ctx.guest.min; const cap = R.max_capacity || 0;
    const p = cap >= need ? 15 : cap >= ctx.guest.min ? 8 : 0;
    parts.push({ label: 'Capacity', max: 15, pts: p });
    why.push(cap ? `largest listed venue seats ${cap} (you need about ${need})` : 'capacity not published here');
  }
  const earned = parts.reduce((x, p) => x + p.pts, 0), avail = parts.reduce((x, p) => x + p.max, 0);
  return { score: avail ? Math.round(100 * earned / avail) : 0, parts, why, avail, regionHit, styleTier };
}
/* Places in your regions come first (region works like a filter). Inside that, places that fit one of your top 3
   styles rank above places that only have a few tagged venues, and those above places with no style match. */
function rankAreas(ctx) {
  return D.AREAS.map(a => ({ a, s: scoreArea(a, ctx) }))
    .sort((x, y) => (y.s.regionHit - x.s.regionHit) || (y.s.styleTier - x.s.styleTier) || (y.s.score - x.s.score) || ((y.a.venue_count || 0) - (x.a.venue_count || 0)) || x.a.name.localeCompare(y.a.name));
}

/* ---------------- design picks ---------------- */
function guestFit(ctx) { if (!ctx.guest) return null; const n = ctx.guest.max != null ? ctx.guest.max : ctx.guest.min; return n <= 50 ? 'intimate' : n <= 150 ? 'mid' : 'large'; }
function rankOptions(cat, ctx, pals) {
  const gf = guestFit(ctx);
  return cat.options.map((o, i) => {
    const st = o.styles || o.style_ids || []; let s = 0; const why = [];
    ctx.topIds.forEach((id, k) => { if (st.includes(id)) { s += [10, 6, 3][k]; why.push(D.styleById[id].name); } });
    const pm = pals.find(p => (o.palettes || []).includes(p));
    if (pm) { s += 4; why.push(D.palById[pm].name + ' palette'); }
    if (ctx.season && (o.season_fit || []).includes(ctx.season)) { s += 2; why.push(ctx.season); }
    if (gf && o.guest_count_fit === gf) { s += 1; why.push(gf + ' guest count'); }
    return { o, i, s, why };
  }).sort((a, b) => (b.s - a.s) || (a.i - b.i));
}
function designPicks(ctx, pals) {
  return D.CATS.map(cat => {
    const ranked = rankOptions(cat, ctx, pals); const top = ranked.slice(0, 3);
    const sw = S.swaps[cat.id]; let pick = top[0], alts = top.slice(1);
    const hit = top.find(x => x.o.id === sw);
    if (hit) { pick = hit; alts = top.filter(x => x !== hit); }
    return { cat, pick, alts };
  });
}

/* ---------------- budget split ---------------- */
function budgetSplit(ctx) {
  if (!ctx.hasStyle) return null;
  const st = D.styleById[ctx.topIds[0]];
  const split = Object.assign({}, st.budget_split);
  const map = D.styles.budget_priority_boost.priority_to_category;
  const to = S.plan.priority ? map[S.plan.priority] : null;
  let boosted = null, moved = 0;
  if (to && split[to] != null) {
    let need = 5;
    ['misc', 'stationery'].forEach(k => { if (k === to || !need) return; const take = Math.min(need, split[k] || 0); split[k] -= take; need -= take; });
    split[to] += 5 - need; boosted = to; moved = 5 - need;
  }
  return { style: st, split, boosted, moved };
}

/* ---------------- formatting ---------------- */
function fmtMoney(amount, cur) {
  try { return new Intl.NumberFormat('en-US', { style: 'currency', currency: cur, maximumFractionDigits: 0 }).format(amount); }
  catch (e) { return cur + ' ' + amount.toLocaleString('en-US'); }
}
function fmtDate(iso) {
  if (!iso) return '';
  const m = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})/); if (!m) return String(iso);
  const d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
}
function coupleName() {
  const n = (S.names || []).map(x => String(x || '').trim()).filter(Boolean);
  return n.length ? n.join(' & ') : 'You two';
}
function capText(v) { const c = num(v.capacity_reception); return c == null ? 'Capacity not published' : `Up to ${c.toLocaleString('en-US')} guests`; }
function priceHTML(v, long) {
  const p = v.price_from;
  if (!hasPrice(v)) return `<p class="price"><strong>Price on request</strong> <small>· checked ${esc(fmtDate(v.checked_utc))}</small></p>`;
  const host = hostOf(p.source_url), off = hostOf(v.source_url);
  const per = host && host !== off ? `per ${host}` : `per ${host || 'official site'}`;
  const amt = p.amount === 0 ? 'No fee (source lists 0)' : 'From ' + fmtMoney(p.amount, p.currency);
  const basis = p.guests_basis ? ` · based on ${p.guests_basis} guests` : '';
  return `<p class="price"><strong>${esc(amt)}</strong> — ${esc(p.what_it_covers)}${esc(basis)}<br><small>Price ${esc(per)}, <a href="${esc(p.source_url)}" target="_blank" rel="noopener">source</a> dated ${esc(fmtDate(p.source_date))}</small></p>`;
}
function photoFig(photo, alt, tag) {
  if (!photo || !photo.image_url) return '';
  return `<figure><div class="ph">${tag ? `<span class="tag">${esc(tag)}</span>` : ''}<img src="${esc(photo.image_url)}" alt="${esc(alt)}" loading="lazy" decoding="async" width="960" height="640"></div>` +
    `<figcaption class="credit">${tag ? esc(tag) + ' — ' : ''}Photo: <a href="${esc(photo.file_page)}" target="_blank" rel="noopener">${esc(photo.author)} · ${esc(photo.license)} · Wikimedia Commons</a></figcaption></figure>`;
}
function venuePhoto(v) {
  if (v.photo && v.photo.image_url) return photoFig(v.photo, `${v.name}, ${v.city}`, '');
  const a = venueArea(v);
  if (a && a.photo) return photoFig(a.photo, `Area photo of ${a.name}, not the venue itself`, `Area photo: ${a.name}`);
  return '';
}
function swatchRow(p) {
  const names = p.color_names || [];
  return `<div class="swatch-row" role="list" aria-label="${esc(p.name)} palette colors">` + p.hex.map((h, i) =>
    `<div role="listitem"><span style="background:${esc(h)}" title="${esc((names[i] || '') + ' ' + h)}"></span>${esc(names[i] || '')}<br>${esc(h)}</div>`).join('') + '</div>';
}
function styleNames(ids) { return (ids || []).map(id => D.styleById[id] ? D.styleById[id].name : id).join(', '); }
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('on'), 2600); }
function setView(html) { $('#view').innerHTML = html; }
function focusMain(sel) { const h = $(sel || '#view h1'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); } }

/* ---------------- routing ---------------- */
async function route() {
  if ($('#sheet').open) $('#sheet').close();
  const parts = (location.hash.replace(/^#/, '') || '/').split('/').filter(Boolean);
  const r = parts[0] || '';
  if (['plan', 'browse', 'hire', 'example'].includes(r) && !D.ready) {
    setView('<p class="loading">Loading venues and places…</p>');
    try { await loadRest(); } catch (e) { return; }
    if ((location.hash.replace(/^#/, '') || '/').split('/').filter(Boolean)[0] !== r) return;
  }
  if (r === 'quiz') renderStep(Math.max(1, Math.min(D.STEPS.length, +parts[1] || 1)));
  else if (r === 'plan') renderPlan();
  else if (r === 'browse') renderBrowse(parts[1] === 'areas' ? 'areas' : 'venues');
  else if (r === 'hire') renderHire();
  else if (r === 'how') renderHow();
  else if (r === 'example') { loadSample(); location.replace('#/plan'); return; }
  else renderWelcome();
  window.scrollTo(0, 0);
  focusMain();
}

/* ---------------- welcome ---------------- */
function renderWelcome() {
  const saved = lsGet(STORE);
  const bandPal = D.palById[D.STY[0].primary_palette_id];
  setView(`<section class="hero">
    <p class="eyebrow">Britt Warnick Designs · Wedding design planner</p>
    <h1>Plan your wedding design in <em>10 minutes</em> — free</h1>
    <p class="lede">Answer quick questions, pick the colors you love, and get one plan: your style, palette, design picks, ranked places and venues, a budget split and a month-by-month checklist. No sign-up.</p>
    <div class="names">
      <div class="field"><label for="n1">Your first name (optional)</label><input id="n1" autocomplete="given-name" value="${esc(S.names[0])}"></div>
      <div class="field"><label for="n2">Partner's first name (optional)</label><input id="n2" autocomplete="off" value="${esc(S.names[1])}"></div>
    </div>
    <div class="row">
      <button class="btn" id="start" type="button">Start the quiz</button>
      <a class="btn ghost" href="#/example" id="example">See an example</a>
    </div>
    <p class="hint" style="margin-top:12px">The example loads sample answers for a real couple's December wedding in Korea. You can also <a href="#/browse/venues">browse all <span data-count="venues">the</span> venues</a> and <a href="#/browse/areas"><span data-count="areas">all</span> places</a> without the quiz.</p>
    ${saved && saved.done ? `<div class="resume"><p class="label">Saved on this device</p><p>Your saved plan${saved.names && saved.names.filter(Boolean).length ? ' for ' + esc(saved.names.filter(Boolean).join(' & ')) : ''} is here.</p><button class="btn small ghost" id="resume" type="button">Open my saved plan</button></div>` : ''}
    <div class="band" aria-hidden="true">${bandPal.hex.map(h => `<i style="background:${h}"></i>`).join('')}</div>
    <ol class="steps3">
      <li><span class="no">No 01</span><span><strong>${D.QS.length} quick style questions + colors.</strong> Choose from ${D.STY.length} styles and ${D.PAL.length} palettes.</span></li>
      <li><span class="no">No 02</span><span><strong>A few planning details.</strong> Guests, budget, season, region, setting — all optional.</span></li>
      <li><span class="no">No 03</span><span><strong>Your plan.</strong> Copy it, print it, email it to yourself, or share it with Britt.</span></li>
    </ol>
    <div class="hero-fig" id="herofig"></div>
  </section>`);
  if (D.ready) fillWelcome();
  const saveNames = () => { S.names = [$('#n1').value, $('#n2').value]; persist(); };
  $('#n1').addEventListener('input', saveNames); $('#n2').addEventListener('input', saveNames);
  $('#start').addEventListener('click', () => {
    const names = [$('#n1').value, $('#n2').value];
    if (S.sample || S.done) { S = freshState(); }
    S.names = names; persist(); location.hash = '#/quiz/1';
  });
  const rs = $('#resume'); if (rs) rs.addEventListener('click', () => { S = Object.assign(freshState(), lsGet(STORE)); persist(); location.hash = '#/plan'; });
}
function fillWelcome() {
  const h = $('#herofig'); if (!h) return;
  const kyoto = D.areaById.kyoto;
  if (kyoto && kyoto.photo && !h.innerHTML) h.innerHTML = photoFig(kyoto.photo, 'Kyoto, one of the places in the planner', '');
  $$('[data-count]').forEach(el => { el.textContent = el.dataset.count === 'venues' ? D.V.length : D.AREAS.length; });
}
function loadSample() {
  const d = D.quiz.demo_couple;
  S = freshState();
  S.names = d.couple.split('&').map(x => x.trim());
  S.answers = Object.assign({}, d.answers);
  S.picks = d.palette_picks.slice();
  S.plan = Object.assign({ region: [] }, d.planning);
  S.plan.region = (d.planning.region || []).slice();
  S.plan.date = d.details.wedding_date;
  S.details = Object.assign({}, d.details);
  S.sample = true; S.done = true;
  persist();
}

/* ---------------- quiz ---------------- */
function stepTotal() { return D.STEPS.length; }
function renderStep(n) {
  const st = D.STEPS[n - 1]; const total = stepTotal();
  const pct = Math.round(100 * (n - 1) / total);
  const head = `<div class="qtop"><button class="btn quiet small" type="button" id="back" aria-label="Back to the previous question">← Back</button>
    <span class="qcount">Question ${n} of ${total}</span><span class="qcount" id="pctdone">${pct}% done</span></div>
    <div class="progress" role="progressbar" aria-label="Quiz progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}"><i style="width:${pct}%"></i></div>
    ${S.sample ? `<span class="sample-flag">${S.sampleEdited ? 'Started from sample answers' : 'Sample answers'}</span>` : ''}`;
  if (st.kind === 'color') return renderColor(n, head);
  const q = st.q; const isStyle = st.kind === 'q';
  const multi = !!q.multi;
  const cur = isStyle ? S.answers[q.id] : S.plan[q.id];
  const two = q.options.length > 4;
  const opts = q.options.map((o, i) => {
    const pressed = multi ? (cur || []).includes(o.id) : cur === o.id;
    let strip = '';
    if (isStyle && o.weights) {
      const topS = Object.entries(o.weights).sort((a, b) => b[1] - a[1])[0];
      const pal = topS && D.styleById[topS[0]] ? D.palById[D.styleById[topS[0]].primary_palette_id] : null;
      if (pal) strip = `<span class="strip" aria-hidden="true">${pal.hex.map(h => `<i style="background:${h}"></i>`).join('')}</span>`;
    }
    const key = String.fromCharCode(97 + i);
    return `<button class="opt" type="button" data-id="${esc(o.id)}" aria-pressed="${pressed}" aria-keyshortcuts="${key}">
      <span class="k">${key}</span>${o.icon ? `<span class="ic" aria-hidden="true">${o.icon}</span>` : '<span class="ic" aria-hidden="true">◦</span>'}
      <span class="lb">${esc(o.label)}${o.sub ? `<small>${esc(o.sub)}</small>` : ''}</span>${strip}</button>`;
  }).join('');
  let extra = '';
  if (q.id === 'season') {
    extra = `<div class="more-q"><div class="field"><label for="month">Or pick a month (optional)</label><select id="month"><option value="">No month yet</option>${MONTHS.map((m, i) => `<option value="${i + 1}" ${+S.plan.month === i + 1 ? 'selected' : ''}>${m}</option>`).join('')}</select></div>
      <div class="field"><label for="wdate">Wedding date, if you have one (optional)</label><input type="date" id="wdate" value="${esc(S.plan.date || '')}"></div></div>`;
  }
  const needsContinue = multi || q.id === 'season';
  setView(`<section class="quiz" aria-labelledby="qh">${head}
    <p class="eyebrow">${esc(q.category)}${q.optional ? ' · optional' : ''}</p>
    <h1 id="qh" tabindex="-1">${esc(q.text)}</h1>
    ${multi ? '<p class="hint">Pick as many as you like.</p>' : ''}
    <div class="opts ${two ? 'two' : ''}" role="group" aria-labelledby="qh">${opts}</div>
    ${extra}
    <div class="qfoot">
      <span class="hint">${isStyle ? 'Tip: press a letter key to answer.' : 'Optional — skip if you are not sure.'}</span>
      <div class="row">${needsContinue ? '' : `<button class="btn quiet small" type="button" id="skip">Skip</button>`}
      ${needsContinue ? `<button class="btn" type="button" id="next">${n === total ? 'See my plan' : 'Continue'}</button>` : (cur != null ? `<button class="btn ghost small" type="button" id="next">${n === total ? 'See my plan' : 'Next'}</button>` : '')}</div>
    </div></section>`);
  $('#back').addEventListener('click', () => goStep(n - 1));
  const sk = $('#skip'); if (sk) sk.addEventListener('click', () => goStep(n + 1));
  const nx = $('#next'); if (nx) nx.addEventListener('click', () => goStep(n + 1));
  $$('.opt').forEach(b => b.addEventListener('click', () => choose(n, b.dataset.id)));
  if (q.id === 'season') {
    $('#month').addEventListener('change', e => { S.plan.month = e.target.value || null; persist(); });
    $('#wdate').addEventListener('change', e => { S.plan.date = e.target.value || null; if (S.plan.date) { S.plan.month = +S.plan.date.slice(5, 7); $('#month').value = String(S.plan.month); } persist(); });
  }
}
function markEdited() { if (S.sample) S.sampleEdited = true; }
function choose(n, id) {
  const st = D.STEPS[n - 1]; const q = st.q; markEdited();
  if (st.kind === 'q') S.answers[q.id] = id;
  else if (q.multi) {
    let cur = (S.plan[q.id] || []).slice();
    if (id === 'anywhere') cur = cur.includes('anywhere') ? [] : ['anywhere'];
    else { cur = cur.filter(x => x !== 'anywhere'); cur = cur.includes(id) ? cur.filter(x => x !== id) : cur.concat(id); }
    S.plan[q.id] = cur;
  } else {
    S.plan[q.id] = id;
    if (q.id === 'occasion' && id === 'elopement' && !S.plan.guest_count) { /* guest default applied in context() */ }
  }
  persist();
  $$('.opt').forEach(b => b.setAttribute('aria-pressed', q.multi ? String((S.plan[q.id] || []).includes(b.dataset.id)) : String(b.dataset.id === id)));
  if (!q.multi && q.id !== 'season') setTimeout(() => { if (location.hash === '#/quiz/' + n) goStep(n + 1); }, reduceMotion() ? 0 : 220);
}
function goStep(n) {
  if (n < 1) { location.hash = '#/'; return; }
  if (n > stepTotal()) { S.done = true; persist(); location.hash = '#/plan'; return; }
  location.hash = '#/quiz/' + n;
}
function seededOrder(arr) {
  let seed = lsGet('bwd-seed', window.sessionStorage);
  if (!seed) { seed = Math.floor(Math.random() * 1e9) + 1; lsSet('bwd-seed', seed, window.sessionStorage); }
  let x = seed; const rnd = () => { x = (x * 1103515245 + 12345) % 2147483648; return x / 2147483648; };
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}
function renderColor(n, head) {
  const order = seededOrder(D.PAL);
  const tiles = order.map(p => {
    const on = S.picks.includes(p.palette_id);
    return `<button class="pal" type="button" data-id="${esc(p.palette_id)}" aria-pressed="${on}" aria-label="${esc(p.name)} palette: ${esc((p.color_names || []).join(', '))}">
      <span class="sw" aria-hidden="true">${p.hex.map((h, i) => `<i style="background:${h}" title="${esc((p.color_names || [])[i] + ' ' + h)}"></i>`).join('')}</span>
      <span class="check">${on ? '✓ ' + (S.picks.indexOf(p.palette_id) + 1) : ''}</span><span class="pn">${esc(p.name)}</span>
      <span class="ps">${esc((p.color_names || []).slice(0, 3).join(' · '))}</span></button>`;
  }).join('');
  setView(`<section class="quiz" aria-labelledby="qh">${head}
    <p class="eyebrow">color</p>
    <h1 id="qh" tabindex="-1">${esc(D.CS.text)}</h1>
    <p class="picked-count" id="pc" aria-live="polite">${S.picks.length} of ${D.MAXP} picked</p>
    <div class="pal-grid" role="group" aria-labelledby="qh">${tiles}</div>
    <div class="qfoot"><span class="hint">${D.PAL.length} palettes. Hover or long-press a swatch for its name and hex.</span>
    <button class="btn" type="button" id="next">Continue</button></div></section>`);
  $('#back').addEventListener('click', () => goStep(n - 1));
  $('#next').addEventListener('click', () => goStep(n + 1));
  $$('.pal').forEach(b => b.addEventListener('click', () => {
    const id = b.dataset.id; markEdited();
    if (S.picks.includes(id)) S.picks = S.picks.filter(x => x !== id);
    else if (S.picks.length >= D.MAXP) { toast(`Pick up to ${D.MAXP}. Tap a picked palette to remove it.`); return; }
    else S.picks = S.picks.concat(id);
    persist();
    $$('.pal').forEach(x => { const on = S.picks.includes(x.dataset.id); x.setAttribute('aria-pressed', String(on)); x.querySelector('.check').textContent = on ? '✓ ' + (S.picks.indexOf(x.dataset.id) + 1) : ''; });
    $('#pc').textContent = `${S.picks.length} of ${D.MAXP} picked`;
  }));
}
function onKey(e) {
  const m = location.hash.match(/^#\/quiz\/(\d+)/); if (!m) return;
  if (e.target && /INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const n = +m[1]; const st = D.STEPS[n - 1];
  if (e.key === 'Backspace') { e.preventDefault(); goStep(n - 1); return; }
  if (!st || st.kind === 'color') return;
  const k = e.key.toLowerCase();
  if (k.length === 1 && k >= 'a' && k <= 'z') {
    const o = st.q.options[k.charCodeAt(0) - 97];
    if (o) { e.preventDefault(); choose(n, o.id); }
  }
}

/* ---------------- plan ---------------- */
let PF = null; // plan venue filters
let BF = null; // browse venue filters
let BA = { region: '', sort: 'rank' };
function defaultFilters(ctx, fromQuiz) {
  const F = { region: [], country: '', area: '', tier: '', cap: '', capNP: true, setting: '', season: '', style: '', price: false, q: '', sort: fromQuiz ? 'match' : 'region', shown: 12 };
  if (fromQuiz) {
    F.region = ctx.regions.slice();
    if (ctx.band != null) F.tier = 'band';
    if (ctx.guest) F.cap = String(ctx.guest.max != null ? ctx.guest.max : ctx.guest.min);
    const set = S.plan.setting;
    if (set === 'indoor') F.setting = 'indoor_any'; else if (set === 'outdoor') F.setting = 'outdoor_any'; else if (set === 'both') F.setting = 'both';
  }
  return F;
}
function renderPlan() {
  if (!S.done && !hasStyleAnswers()) {
    setView(`<section class="hero"><p class="eyebrow">Your plan</p><h1>Your plan starts with the <em>quiz</em></h1>
      <p class="lede">Take the quiz to build your plan, or open the example to see what you get.</p>
      <div class="row"><a class="btn" href="#/quiz/1">Start the quiz</a><a class="btn ghost" href="#/example">See an example</a></div></section>`);
    return;
  }
  const ctx = context();
  PF = defaultFilters(ctx, true);
  const pals = chosenPalettes(ctx);
  const sections = [['sec-style', 'Style'], ['sec-colors', 'Colors'], ['sec-design', 'Design'], ['sec-places', 'Places'], ['sec-venues', 'Venues'], ['sec-budget', 'Budget'], ['sec-timeline', 'Timeline'], ['sec-save', 'Save'], ['sec-britt', 'Britt']];
  setView(`${planHead(ctx)}
    <nav class="secnav" aria-label="Plan sections"><div class="in">${sections.map(([id, l]) => `<a href="#/plan" data-jump="${id}">${l}</a>`).join('')}</div></nav>
    ${styleSection(ctx)}
    ${colorSection(ctx, pals)}
    <section class="sec" id="sec-design" aria-labelledby="h-design"><p class="label">No 03 · Design picks</p><h2 id="h-design">One pick per <em>design category</em></h2>
      <p class="sec-intro">Design ideas / inspiration, not vendor quotes. Each pick is matched to your styles, palette, season and guest count. Swap in an alternate any time.</p><div id="picks"></div></section>
    <section class="sec" id="sec-places" aria-labelledby="h-places"><p class="label">No 04 · Places</p><h2 id="h-places">Places ranked for <em>you</em></h2>
      <p class="sec-intro">Each place is scored from your answers: region, month or season, budget band, styles and guest count. The breakdown shows the points.</p><div id="areas"></div></section>
    <section class="sec" id="sec-venues" aria-labelledby="h-venues"><p class="label">No 05 · Venues</p><h2 id="h-venues">Venues ranked by your <em>100-point score</em></h2>
      <p class="sec-intro">Filters start from your answers; change any of them. Points you can only judge in person are marked “rate on your tour” and left out until you rate them.</p><div id="vlist"></div></section>
    ${budgetSection(ctx)}
    ${timelineSection()}
    ${saveSection()}
    ${hireBlock()}
    <div class="sticky-pad" aria-hidden="true"></div>
    <a class="btn sticky-britt no-print" id="sticky-britt" href="${esc(brittMailto(ctx))}">Email Britt</a>`);
  $$('[data-jump]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); const t = document.getElementById(a.dataset.jump); if (t) { t.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth' }); const h = t.querySelector('h2'); if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); } } }));
  renderPicks(ctx, pals);
  renderAreaList($('#areas'), ctx, { limit: 5, inPlan: true });
  PF.shown = 10;
  mountVenueList($('#vlist'), PF, ctx);
  wireSticky();
  wireTimeline(); wireSave(ctx);
  requestAnimationFrame(() => requestAnimationFrame(() => $$('.bar i[data-w]').forEach(i => { i.style.width = i.dataset.w + '%'; })));
}
function planHead(ctx) {
  const d = S.details; const facts = [];
  if (S.plan.date) facts.push(`Wedding: ${fmtDate(S.plan.date)}`);
  if (d && d.destination) facts.push(`Destination: ${d.destination}`);
  if (d && d.arrive) facts.push(`Arrive: ${fmtDate(d.arrive)}`);
  if (d && d.honeymoon) facts.push(`Honeymoon after: ${d.honeymoon}`);
  if (d && d.prep_done_by) facts.push(`Prep done by: ${fmtDate(d.prep_done_by)}`);
  const g = ctx.guest; if (g) facts.push(`Guests: ${g.sub}`);
  const b = D.PD.budget_band.options.find(o => o.id === S.plan.budget_band); if (b) facts.push(`Budget: ${b.label}`);
  if (ctx.month && !S.plan.date) facts.push(`Month: ${MONTHS[ctx.month - 1]}`);
  else if (ctx.season && !S.plan.date) facts.push(`Season: ${ctx.season}`);
  if (ctx.regions.length) facts.push(`Region: ${ctx.regions.join(', ')}`);
  const set = D.PD.setting.options.find(o => o.id === S.plan.setting); if (set) facts.push(`Setting: ${set.label}`);
  if (S.plan.occasion) facts.push(`Occasion: ${S.plan.occasion}`);
  const t = ctx.top3;
  const primary = ctx.hasStyle ? D.quiz.results.summary_templates.primary
    .replace('{couple}', coupleName()).replace('{style1}', D.styleById[t[0].id].name).replace('{pct1}', t[0].pct)
    .replace('{style2}', D.styleById[t[1].id].name).replace('{pct2}', t[1].pct).replace('{style3}', D.styleById[t[2].id].name).replace('{pct3}', t[2].pct)
    .replace('{signature_moment}', D.styleById[t[0].id].signature_moment) : `${coupleName()}, answer a few style questions to see your style match.`;
  const honey = d && d.honeymoon ? D.AREAS.find(a => a.name.toLowerCase() === String(d.honeymoon).toLowerCase()) : null;
  return `<section class="plan-head" aria-labelledby="ph">
    ${S.sample ? `<span class="sample-flag">${S.sampleEdited ? 'Started from sample answers' : 'Sample answers — an example plan'}</span>` : ''}
    <p class="eyebrow">Your wedding design plan</p>
    <h1 id="ph">${esc(coupleName())}${coupleName() === 'You two' ? ', here is <em>your plan</em>' : ': <em>your plan</em>'}</h1>
    ${ctx.hasStyle ? `<p class="one">${esc(oneLiner(ctx))}</p>` : ''}
    <p>${esc(primary)}</p>
    ${facts.length ? `<ul class="facts">${facts.map(f => `<li>${esc(f)}</li>`).join('')}</ul>` : ''}
    ${S.plan.kids === 'yes' ? '<p class="small muted">Kids are invited: ask venues about a quiet room, early kids’ meals and lawn space for games.</p>' : S.plan.kids === 'adults' ? '<p class="small muted">Adults only: say so clearly on your invitations and website.</p>' : ''}
    ${honey ? `<p class="small">Honeymoon after in ${esc(honey.name)}: <button class="btn quiet small" type="button" data-area="${esc(honey.id)}">see ${esc(honey.name)} details</button></p>` : ''}
    <div class="row no-print"><a class="btn ghost small" href="#/quiz/1">${S.sample ? 'Walk through the sample answers' : 'Change my answers'}</a><button class="btn quiet small" type="button" id="restart">Start over</button></div>
  </section>`;
}
function oneLiner(ctx) {
  const t = D.quiz.results.summary_templates.one_liner;
  const cp = D.QS.find(q => q.id === 'ceremony_place').options.find(o => o.id === S.answers.ceremony_place);
  const dn = D.QS.find(q => q.id === 'dinner').options.find(o => o.id === S.answers.dinner);
  const seasonLabel = ctx.season ? (D.PD.season.label_for_summary[ctx.season] || '') : '';
  const occ = S.plan.occasion ? D.PD.occasion.label_for_summary[S.plan.occasion] : 'wedding';
  const g = S.plan.guest_count ? D.PD.guest_count.label_for_summary[S.plan.guest_count] : 'the people you love';
  return t.replace('{season_label}', seasonLabel).replace('{setting_label}', cp ? cp.short || '' : '').replace('{occasion_label}', occ)
    .replace('{guest_label}', g).replace('{style1}', D.styleById[ctx.topIds[0]].name).replace('{style2}', D.styleById[ctx.topIds[1]].name)
    .replace('{food_label}', dn ? dn.short || 'meal' : 'meal').replace(/\s{2,}/g, ' ').replace(/^A ([aeiou])/i, (m, c) => 'An ' + c);
}
function stylePhoto(id, ctx) {
  const cands = D.V.filter(v => v.photo && (v.style_tags || []).includes(id));
  const pref = cands.find(v => ctx.regions.includes(v.region)) || cands[0];
  if (pref) return photoFig(pref.photo, `${pref.name}, a venue tagged ${D.styleById[id].name}`, `Venue photo: ${pref.name}`);
  const a = D.AREAS.find(x => x.photo && (x.style_fits || []).includes(id));
  return a ? photoFig(a.photo, `Area photo of ${a.name}`, `Area photo: ${a.name}`) : '';
}
function styleSection(ctx) {
  if (!ctx.hasStyle) return `<section class="sec" id="sec-style"><p class="label">No 01 · Style</p><h2>Not enough answers yet</h2><p>Answer a few style questions to see your top 3 styles.</p><a class="btn" href="#/quiz/1">Answer style questions</a></section>`;
  const labels = D.quiz.results.rank_labels;
  return `<section class="sec" id="sec-style" aria-labelledby="h-style"><p class="label">No 01 · Style</p><h2 id="h-style">Your top three <em>styles</em></h2>
    <p class="sec-intro">Match percentages compare your top three only, so they add to 100.</p>
    ${ctx.top3.map((x, i) => { const st = D.styleById[x.id]; const pal = D.palById[st.primary_palette_id]; const rl = labels[i];
      return `<article class="card style-card" aria-labelledby="st-${i}">
        <div class="rank"><b>${esc(rl.number)}</b><span>${esc(rl.label)}</span></div>
        <h3 id="st-${i}">${esc(st.name)}</h3>
        <div class="row" style="justify-content:space-between"><span class="pct">${x.pct}%</span><span class="small muted">${x.score} points</span></div>
        <div class="bar" role="img" aria-label="${x.pct} percent match"><i data-w="${x.pct}"></i></div>
        <p class="tagline">${esc(st.tagline)}</p>
        ${i === 0 ? stylePhoto(st.id, ctx) : ''}
        <p>${esc((st.essence || []).join(' '))}</p>
        <div class="swatches">${pal.hex.map((h, j) => `<span class="swatch" style="background:${h}" title="${esc((pal.color_names || [])[j] + ' ' + h)}" role="img" aria-label="${esc((pal.color_names || [])[j] + ' ' + h)}"></span>`).join('')}</div>
        <dl class="kv"><div><dt>Venue direction</dt><dd>${esc(st.venue_direction)}</dd></div>
        <div><dt>Florals</dt><dd>${esc(st.floral_notes)}</dd></div>
        <div><dt>Attire</dt><dd>${esc(st.attire_notes)}</dd></div>
        <div><dt>Signature moment</dt><dd>${esc(st.signature_moment)}</dd></div>
        <div><dt>Best seasons</dt><dd>${esc((st.season_fit || []).join(', '))}</dd></div></dl></article>`; }).map((h, i) => i === 1 ? `<details class="fold"><summary><span>See your #2 and #3 styles</span><span aria-hidden="true">＋</span></summary>${h}` : i === 2 ? h + '</details>' : h).join('')}
  </section>`;
}
function colorSection(ctx, pals) {
  const main = pals.main ? D.palById[pals.main] : null; const alt = pals.alt ? D.palById[pals.alt] : null;
  const others = pals.picks.filter(p => p !== pals.main).map(p => D.palById[p]);
  const card = (p, label) => `<article class="card pal-card"><p class="label">${esc(label)}</p><h3>${esc(p.name)}</h3><p class="small muted">From the ${esc(D.styleById[p.style_id].name)} style</p>${swatchRow(p)}</article>`;
  return `<section class="sec" id="sec-colors" aria-labelledby="h-colors"><p class="label">No 02 · Colors</p><h2 id="h-colors">Your <em>palette</em></h2>
    ${main ? card(main, S.picks.includes(main.palette_id) ? 'Your palette' : 'Your palette (from your #1 style)') : '<p>Pick palettes in the color step to see them here.</p>'}
    ${others.map(p => card(p, 'Also picked')).join('')}
    ${alt && (!main || alt.palette_id !== main.palette_id) ? card(alt, 'Alternate color story') : ''}
  </section>`;
}
function renderPicks(ctx, pals) {
  const host = $('#picks'); if (!host) return;
  const palIds = pals.picks.length ? pals.picks : (pals.main ? [pals.main] : []);
  const list = designPicks(ctx, palIds);
  const wasOpen = !!(host.querySelector('details.fold') && host.querySelector('details.fold').open);
  const SHOW = 6;
  host.innerHTML = list.map(({ cat, pick, alts }) => `<div class="pick" data-cat="${esc(cat.id)}">
    <p class="label">${esc(cat.label)}</p><h3>${esc(pick.o.label || pick.o.name)}</h3><p>${esc(pick.o.description)}</p>
    ${pick.why.length ? `<p class="why">Matched to: ${esc(pick.why.join(' · '))}</p>` : ''}
    ${pick.o.planner_tip ? `<p class="small muted">Tip: ${esc(pick.o.planner_tip)}</p>` : ''}
    <div class="alts">${alts.map(a => `<div class="alt"><span>Alternate: <strong>${esc(a.o.label || a.o.name)}</strong></span><button class="btn ghost small" type="button" data-swap="${esc(a.o.id)}" data-cat="${esc(cat.id)}" aria-label="Use ${esc(a.o.label || a.o.name)} instead">Use this</button></div>`).join('')}</div></div>`)
    .map((h, i, arr) => arr.length > SHOW && i === SHOW ? `<details class="fold"${wasOpen ? ' open' : ''}><summary><span>Show all ${arr.length} design picks</span><span aria-hidden="true">＋</span></summary>${h}` : h)
    .join('') + (list.length > SHOW ? '</details>' : '');
  $$('[data-swap]', host).forEach(b => b.addEventListener('click', () => { S.swaps[b.dataset.cat] = b.dataset.swap; persist(); renderPicks(ctx, pals); const el = $(`.pick[data-cat="${b.dataset.cat}"] h3`, host); if (el) { el.setAttribute('tabindex', '-1'); el.focus(); } toast('Swapped. Copy or save your plan to keep it.'); }));
}
/* Weather text follows the couple's chosen month. The written climate note in the data is December-only, so it
   shows only for a December wedding. Other months use the area's season_fit table (2 best, 1 shoulder, 0 outside).
   With no month chosen, the Best months row stands in (plus a season line when only a season was picked). */
function areaClimate(a, ctx) {
  const m = ctx.month; const fitT = ((a.ranking || {}).season_fit) || {};
  const best = (a.best_months || []).map(x => MON3[x - 1]).join(', ');
  const keepDec = m === 12;
  const pros = (a.pros || []).filter(x => keepDec || !DEC_RE.test(x));
  const cons = (a.cons || []).filter(x => keepDec || !DEC_RE.test(x));
  let row = null;
  if (m === 12) row = ['December', a.december_note];
  else if (m) {
    const f = fitT[String(m)]; const M = MONTHS[m - 1];
    const txt = f === 2 ? `${M} is in this area's best season (best months: ${best}).`
      : f === 1 ? `${M} is shoulder season here (best months: ${best}). Check the weather for your dates.`
      : `${M} is outside the usual wedding season here (best months: ${best}) — check weather.`;
    row = [M, txt];
    if (f === 2) pros.push(`${M}, your month, is in this area's best season.`);
    else if (f === 1) cons.push(`${M}, your month, is shoulder season here — check the weather for your dates.`);
    else cons.push(`${M}, your month, is outside the usual wedding season here (best months: ${best}) — check weather.`);
  } else if (ctx.season) {
    const ms = SEASON_M[ctx.season]; const good = ms.filter(x => fitT[String(x)] === 2);
    row = ['Your season', `${ctx.season[0].toUpperCase() + ctx.season.slice(1)}: ${good.length ? good.map(x => MONTHS[x - 1]).join(', ') + (good.length === 1 ? ' is a best month' : ' are best months') : 'no best months fall in this season'} here (best: ${best}). Check the season for your month.`];
    if (good.length) pros.push(`Your season includes ${good.map(x => MONTHS[x - 1]).join(' and ')}, among the best months here.`);
    else cons.push(`None of the best months here (${best}) fall in ${ctx.season}; check the season for your month.`);
  }
  return { row, pros, cons };
}
function regCountry(a) { return a.region === a.country ? a.region : `${a.region} · ${a.country}`; }
function areaCard(a, s, rank, ctx) {
  const src = (a.sources || []);
  const legal = src.find(x => /legal/.test(x.field));
  const clim = src.find(x => /climate/.test(x.field));
  const m = ctx.month;
  const cl = areaClimate(a, ctx);
  const pr = a.price_range && a.price_range.by_currency ? Object.entries(a.price_range.by_currency).map(([c, r]) => `${fmtMoney(r.min, c)}–${fmtMoney(r.max, c)} (${r.count} venue${r.count === 1 ? '' : 's'})`).join('; ') : '';
  return `<article class="card area-card" id="area-${esc(a.id)}" aria-labelledby="ah-${esc(a.id)}">
    ${a.photo ? photoFig(a.photo, `${a.name}, ${a.country}`, '') : ''}
    <div class="top"><div>${rank ? `<p class="rank"><b>No ${String(rank).padStart(2, '0')}</b><span>${esc(regCountry(a))}</span></p>` : `<p class="rank"><span>${esc(regCountry(a))}</span></p>`}<h3 id="ah-${esc(a.id)}">${esc(a.name)}</h3></div>
    ${s.avail ? `<div class="score"><b>${s.score}</b><span>of 100</span></div>` : ''}</div>
    ${s.avail ? `<p class="whyline"><strong>Why it ranks here:</strong> ${esc(s.why.join(' · '))}.</p><ul class="breakdown">${s.parts.map(p => `<li><span>${esc(p.label)}</span><b>${p.pts}/${p.max}</b></li>`).join('')}</ul>` : ''}
    <p>${esc(a.summary)}</p>
    <details class="fold"><summary><span>Weather, travel, pros and cons</span><span aria-hidden="true">＋</span></summary>
    <dl class="kv">
      ${cl.row ? `<div><dt>${esc(cl.row[0])}</dt><dd>${esc(cl.row[1])}${clim ? ` <a href="${esc(clim.url)}" target="_blank" rel="noopener">Climate source</a>` : ''}</dd></div>` : ''}
      <div><dt>Best months</dt><dd>${esc((a.best_months || []).map(x => MONTHS[x - 1]).join(', '))}</dd></div>
      <div><dt>Airports</dt><dd>${esc((a.main_airports || []).map(x => `${x.iata} ${x.name}`).join('; '))}</dd></div>
      <div><dt>Language · currency</dt><dd>${esc(a.language)} · ${esc(a.currency)}</dd></div>
      <div><dt>Legal ceremony note</dt><dd>${esc(a.legal_ceremony_note)}${legal ? ` <a href="${esc(legal.url)}" target="_blank" rel="noopener">Official source</a>` : ''}</dd></div>
      <div><dt>Venues on file</dt><dd>${a.venue_count}${pr ? ` · starting figures ${esc(pr)}` : ''}</dd></div>
    </dl>
    <p class="pc-h">Pros</p><ul class="pc">${cl.pros.map(p => `<li>${esc(p)}</li>`).join('')}</ul>
    <p class="pc-h">Cons</p><ul class="pc">${cl.cons.map(p => `<li>${esc(p)}</li>`).join('')}</ul>
    </details>
    ${a.venue_count ? `<button class="btn ghost small" type="button" data-area-venues="${esc(a.id)}">See ${a.venue_count} venue${a.venue_count === 1 ? '' : 's'} here</button>` : '<p class="small muted">No venues listed here yet.</p>'}
  </article>`;
}
function renderAreaList(host, ctx, opt) {
  let list = rankAreas(ctx);
  const anyAns = list.length && list[0].s.avail;
  if (opt.region) list = list.filter(x => x.a.region === opt.region);
  if (opt.sort === 'name') list = list.slice().sort((x, y) => x.a.name.localeCompare(y.a.name));
  if (opt.sort === 'region') list = list.slice().sort((x, y) => D.regionOrder.indexOf(x.a.region) - D.regionOrder.indexOf(y.a.region) || x.a.name.localeCompare(y.a.name));
  const limit = opt.limit || list.length;
  const ranked = anyAns && (!opt.sort || opt.sort === 'rank');
  host.innerHTML = `<p class="count-line"><span><strong>${list.length}</strong> places${ranked ? ', ranked' : ''}</span></p>` +
    list.slice(0, limit).map((x, i) => areaCard(x.a, x.s, ranked ? i + 1 : 0, ctx)).join('') +
    (list.length > limit ? `<div class="list-actions"><button class="btn ghost" type="button" id="more-areas">Show all ${list.length} places</button></div>` : '');
  const more = $('#more-areas', host); if (more) more.addEventListener('click', () => { renderAreaList(host, ctx, Object.assign({}, opt, { limit: list.length })); });
  $$('[data-area-venues]', host).forEach(b => b.addEventListener('click', () => {
    const id = b.dataset.areaVenues;
    if (opt.inPlan) { PF.area = id; PF.region = []; PF.shown = 12; mountVenueList($('#vlist'), PF, ctx); $('#sec-venues').scrollIntoView(); const h = $('#h-venues'); h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
    else { BF = BF || defaultFilters(ctx, false); BF.area = id; BF.region = []; BF.shown = 12; location.hash = '#/browse/venues'; }
  }));
}

/* ---------------- venue list + filters ---------------- */
function filterVenues(F) {
  return D.V.filter(v => {
    if (F.region.length && !F.region.includes(v.region)) return false;
    if (F.country && normCountry(v.country) !== F.country) return false;
    if (F.area && D.vArea[v.id] !== F.area) return false;
    if (F.tier) {
      if (F.tier === 'band') { const ti = tierIdx(v); if (!(ti == null || ti <= F.band)) return false; }
      else if (v.budget_tier !== F.tier) return false;
    }
    if (F.cap) { const c = num(v.capacity_reception); if (c == null) { if (!F.capNP) return false; } else if (c < +F.cap) return false; }
    if (F.setting) {
      const keep = { indoor_any: ['indoor', 'both'], outdoor_any: ['outdoor', 'both'], both: ['both'], indoor: ['indoor'], outdoor: ['outdoor'] }[F.setting];
      if (!keep.includes(v.setting)) return false;
    }
    if (F.season && !seasonNamed(v, F.season)) return false;
    if (F.style && !(v.style_tags || []).includes(F.style)) return false;
    if (F.price && !hasPrice(v)) return false;
    if (F.q) {
      const a = venueArea(v);
      const hay = [v.name, v.city, v.country, v.region, v.type, a ? a.name : ''].join(' ').toLowerCase();
      if (!F.q.toLowerCase().split(/\s+/).filter(Boolean).every(w => hay.includes(w))) return false;
    }
    return true;
  });
}
function sortVenues(scored, F) {
  const s = scored.slice();
  if (F.sort === 'name') s.sort((a, b) => a.v.name.localeCompare(b.v.name));
  else if (F.sort === 'cap_desc') s.sort((a, b) => (num(b.v.capacity_reception) || -1) - (num(a.v.capacity_reception) || -1) || a.v.name.localeCompare(b.v.name));
  else if (F.sort === 'cap_asc') s.sort((a, b) => (num(a.v.capacity_reception) || 1e9) - (num(b.v.capacity_reception) || 1e9) || a.v.name.localeCompare(b.v.name));
  else if (F.sort === 'price_first') s.sort((a, b) => (hasPrice(b.v) - hasPrice(a.v)) || (b.s.score - a.s.score) || a.v.name.localeCompare(b.v.name));
  else if (F.sort === 'region') s.sort((a, b) => D.regionOrder.indexOf(a.v.region) - D.regionOrder.indexOf(b.v.region) || a.v.city.localeCompare(b.v.city) || a.v.name.localeCompare(b.v.name));
  return s; // 'match' keeps rankVenues order
}
function opt(v, label, cur) { return `<option value="${esc(v)}"${String(cur) === String(v) ? ' selected' : ''}>${esc(label)}</option>`; }
function filterForm(F, ctx) {
  const regs = D.regionOrder.filter(r => D.V.some(v => v.region === r));
  const regVal = F.region.length > 1 ? '__multi' : (F.region[0] || '');
  const countries = [...new Set(D.V.map(v => normCountry(v.country)))].sort();
  const areaOpts = regs.map(r => `<optgroup label="${esc(r)}">${D.AREAS.filter(a => a.region === r).map(a => opt(a.id, a.name, F.area)).join('')}</optgroup>`).join('');
  const band = ctx.band;
  return `<details class="filters" ${F.open ? 'open' : ''}><summary><span>Filters &amp; sort</span><span aria-hidden="true">＋</span></summary>
  <div class="fgrid">
    <div class="field"><label for="f-region">Region</label><select id="f-region">${opt('', 'All regions', regVal)}${F.region.length > 1 ? opt('__multi', 'Your regions: ' + F.region.join(' + '), regVal) : ''}${regs.map(r => opt(r, r, regVal)).join('')}</select></div>
    <div class="field"><label for="f-country">Country</label><select id="f-country">${opt('', 'All countries', F.country)}${countries.map(c => opt(c, c, F.country)).join('')}</select></div>
    <div class="field"><label for="f-area">Area</label><select id="f-area">${opt('', 'All areas', F.area)}${areaOpts}</select></div>
    <div class="field"><label for="f-tier">Budget tier</label><select id="f-tier">${opt('', 'Any budget tier', F.tier)}${band != null ? opt('band', `Fits my band (${TIERS[band]} or less + price on request)`, F.tier) : ''}${TIERS.map(t => opt(t, `${t} (${D.V.filter(v => v.budget_tier === t).length} venues)`, F.tier)).join('')}${opt('unknown', `Price on request — tier unknown (${D.V.filter(v => v.budget_tier === 'unknown').length})`, F.tier)}</select></div>
    <div class="field"><label for="f-cap">Capacity</label><select id="f-cap">${opt('', 'Any size', F.cap)}${[20, 50, 100, 150, 250].map(n => opt(n, `Seats ${n}+`, F.cap)).join('')}${F.cap && ![20, 50, 100, 150, 250].includes(+F.cap) ? opt(F.cap, `Seats ${F.cap}+`, F.cap) : ''}</select></div>
    <div class="field"><label for="f-setting">Setting</label><select id="f-setting">${opt('', 'Any setting', F.setting)}${opt('indoor_any', 'Indoor space (indoor or both)', F.setting)}${opt('outdoor_any', 'Outdoor space (outdoor or both)', F.setting)}${opt('both', 'Indoor + outdoor (both)', F.setting)}${opt('indoor', 'Indoor only', F.setting)}${opt('outdoor', 'Outdoor only', F.setting)}</select></div>
    <div class="field"><label for="f-season">Season</label><select id="f-season">${opt('', 'Any season', F.season)}${['spring', 'summer', 'fall', 'winter'].map(s => opt(s, `Best season names ${s}`, F.season)).join('')}</select></div>
    <div class="field"><label for="f-style">Style</label><select id="f-style">${opt('', 'Any style', F.style)}${D.STY.map(s => opt(s.id, s.name, F.style)).join('')}</select></div>
    <div class="field"><label for="f-sort">Sort</label><select id="f-sort">${opt('match', 'Best match (score)', F.sort)}${opt('region', 'Region, then city', F.sort)}${opt('name', 'Name A–Z', F.sort)}${opt('cap_desc', 'Largest capacity', F.sort)}${opt('cap_asc', 'Smallest capacity', F.sort)}${opt('price_first', 'Published price first', F.sort)}</select></div>
    <div class="field full"><label for="f-q">Search</label><input type="search" id="f-q" value="${esc(F.q)}"></div>
    <label class="check"><input type="checkbox" id="f-price" ${F.price ? 'checked' : ''}> Has a published price</label>
    <label class="check"><input type="checkbox" id="f-capnp" ${F.capNP ? 'checked' : ''}> Keep venues that don't publish capacity</label>
  </div>
  <div class="row" style="margin-top:12px"><button class="btn quiet small" type="button" id="f-reset">Clear filters</button></div></details>`;
}
function venueCard(x, rank) {
  const v = x.v, s = x.s; const a = venueArea(v);
  return `<article class="card v-card" aria-labelledby="vh-${esc(v.id)}">
    ${venuePhoto(v)}
    <div class="top"><div><p class="rank"><b>No ${String(rank).padStart(2, '0')}</b><span>${esc(v.type)}</span></p><h3 id="vh-${esc(v.id)}">${esc(v.name)}</h3>
    <p class="meta">${esc(v.city)}, ${esc(normCountry(v.country))}${a ? ' · ' + esc(a.name) : ''}</p></div>
    <div class="score"><b>${s.score}</b><span>match</span></div></div>
    <div class="chips"><span class="chip tier">${esc(tierLabel(v))}</span><span class="chip">${esc(capText(v))}</span><span class="chip">${esc(v.setting)}</span></div>
    ${priceHTML(v)}
    <ul class="breakdown" aria-label="Score breakdown">${s.parts.filter(p => p.on || (p.id !== 'wow_factor' && p.id !== 'planner_network')).map(p => `<li class="${p.on ? '' : 'off'}"><span>${esc(p.label)}</span><b>${p.on ? `${p.pts}/${p.max}` : '—'}</b></li>`).join('')}</ul>
    <button class="btn small" type="button" data-venue="${esc(v.id)}">View details</button></article>`;
}
let LISTS = [];
function mountVenueList(host, F, ctx) {
  F.band = ctx.band;
  const draw = () => {
    const filtered = filterVenues(F);
    const ranked = sortVenues(rankVenues(filtered, ctx), F);
    const shown = ranked.slice(0, F.shown || 12);
    $('.vresults', host).innerHTML = `<div class="count-line"><span>Showing <strong id="vcount">${filtered.length}</strong> of ${D.V.length} venues</span></div>` +
      (shown.length ? shown.map((x, i) => venueCard(x, i + 1)).join('') : '<p class="empty">No venues match these filters. Try clearing one.</p>') +
      (ranked.length > shown.length ? `<div class="list-actions"><button class="btn ghost" type="button" data-more>Show 12 more (${ranked.length - shown.length} left)</button></div>` : '');
    $$('[data-venue]', host).forEach(b => b.addEventListener('click', () => openVenue(b.dataset.venue, ctx)));
    const m = $('[data-more]', host); if (m) m.addEventListener('click', () => { F.shown = (F.shown || 12) + 12; draw(); });
  };
  host.innerHTML = filterForm(F, ctx) + '<div class="vresults" aria-live="polite"></div>';
  const bind = (id, fn, ev) => { const el = $('#' + id, host); if (el) el.addEventListener(ev || 'change', e => { fn(e.target); F.shown = 12; draw(); }); };
  bind('f-region', t => { F.region = t.value === '__multi' ? F.region : (t.value ? [t.value] : []); });
  bind('f-country', t => { F.country = t.value; });
  bind('f-area', t => { F.area = t.value; });
  bind('f-tier', t => { F.tier = t.value; });
  bind('f-cap', t => { F.cap = t.value; });
  bind('f-setting', t => { F.setting = t.value; });
  bind('f-season', t => { F.season = t.value; });
  bind('f-style', t => { F.style = t.value; });
  bind('f-sort', t => { F.sort = t.value; });
  bind('f-price', t => { F.price = t.checked; });
  bind('f-capnp', t => { F.capNP = t.checked; });
  bind('f-q', t => { F.q = t.value.trim(); }, 'input');
  $('details', host).addEventListener('toggle', e => { F.open = e.target.open; });
  $('#f-reset', host).addEventListener('click', () => { Object.assign(F, defaultFilters(ctx, false), { sort: F.sort, open: true }); mountVenueList(host, F, ctx); });
  LISTS = LISTS.filter(l => document.body.contains(l.host)).concat({ host, draw });
  draw();
}
function refreshLists() { LISTS.filter(l => document.body.contains(l.host)).forEach(l => l.draw()); }

/* ---------------- venue detail sheet ---------------- */
function openVenue(id, ctx) {
  const v = D.vById[id]; if (!v) return;
  ctx = ctx || context();
  const s = scoreVenue(v, ctx); const a = venueArea(v);
  const pros = Array.isArray(v.pros_source) ? v.pros_source : [v.pros_source].filter(Boolean);
  const r = RATE[v.id] || {};
  const row = (k, val) => `<tr><th scope="row">${esc(k)}</th><td>${val}</td></tr>`;
  const t = x => esc(x == null || x === '' ? 'not published' : x);
  const p = v.price_from;
  $('#sheet-body').innerHTML = `${venuePhoto(v)}
    <p class="eyebrow" style="margin-top:16px">${esc(v.type)} · ${esc(v.region)}</p>
    <h2 id="sheet-title">${esc(v.name)}</h2>
    <p class="meta">${esc(v.city)}, ${esc(normCountry(v.country))}${a ? ' · area: ' + esc(a.name) : ''}</p>
    <div class="row" style="justify-content:space-between;margin-top:12px"><span class="pct">${s.score}<span class="small muted"> / 100 match</span></span></div>
    <ul class="breakdown wide" aria-label="Score breakdown">${s.parts.map(q => `<li class="${q.on ? '' : 'off'}"><span>${esc(q.label)} <small class="muted">· ${esc(q.note || '')}</small></span><b>${q.on ? `${q.pts}/${q.max}` : (q.id === 'wow_factor' || q.id === 'planner_network' ? 'rate on your tour' : '—')}</b></li>`).join('')}</ul>
    <p class="small muted">Score = points earned ÷ points available × 100 (${s.earned} ÷ ${s.avail}). Parts with no answer or no rating are left out.</p>
    <div class="card"><p class="label">Rate on your tour</p>
      <div class="rate"><label for="r-wow">Wow factor (0–8)</label><select id="r-wow">${opt('', 'Not rated', r.wow == null ? '' : r.wow)}${[0, 1, 2, 3, 4, 5, 6, 7, 8].map(n => opt(n, n, r.wow == null ? '' : r.wow)).join('')}</select></div>
      <div class="rate"><label for="r-net">Planner network (0–5)</label><select id="r-net">${opt('', 'Not rated', r.net == null ? '' : r.net)}${[0, 1, 2, 3, 4, 5].map(n => opt(n, n, r.net == null ? '' : r.net)).join('')}</select></div>
      <p class="small muted">Ratings stay on this device and add to the score.</p></div>
    <h3>Price</h3>${priceHTML(v, true)}
    <table class="ftable"><tbody>
      ${row('Setting', t(v.setting))}
      ${row('Reception capacity', esc(capText(v)) + (v.capacity_note && v.capacity_note !== 'not published' ? `<br><small class="muted">${esc(v.capacity_note)}</small>` : ''))}
      ${row('Budget tier', t(v.budget_tier) + (feeOnly(v) ? ' · starting fee only (not a wedding total)' : '') + (v.tier_reason ? `<br><small class="muted">${esc(v.tier_reason)}</small>` : ''))}
      ${row('Price covers', hasPrice(v) ? esc(p.what_it_covers) + (p.guests_basis ? ` (${esc(p.guests_basis)} guests)` : '') : 'price on request')}
      ${row('Styles', esc(styleNames(v.style_tags)))}
      ${row('Best season', t(ctx.month === 12 ? v.best_season : stripDecember(v.best_season)))}
      ${row('On-site lodging', t(v.onsite_lodging))}
      ${row('Catering', t(v.catering) + (v.catering_note ? `<br><small class="muted">${esc(v.catering_note)}</small>` : ''))}
      ${row('Nearest airport', t(v.nearest_airport))}
      ${row('Region · country', esc(v.region) + ' · ' + esc(normCountry(v.country)))}
      ${row('Facts checked', esc(fmtDate(v.checked_utc)) + (v.http_ok ? ' · official page loaded' : ' · confirmed via listed source'))}
      ${v.note ? row('Research note', esc(v.note)) : ''}
      ${v.fetch_note ? row('Source note', esc(v.fetch_note)) : ''}
    </tbody></table>
    <h3>Pros</h3><ul class="pc">${(v.pros || []).map(x => `<li>${esc(x)}</li>`).join('')}</ul>
    <h3>Cons</h3><ul class="pc">${(v.cons || []).map(x => `<li>${esc(x)}</li>`).join('')}</ul>
    <p class="small">Pros and cons source: ${pros.map(u => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(hostOf(u) || u)}</a>`).join(', ')}</p>
    <div class="links">
      <a class="btn" href="${esc(v.source_url)}" target="_blank" rel="noopener">Official site</a>
      ${v.gallery_url ? `<a class="btn ghost" href="${esc(v.gallery_url)}" target="_blank" rel="noopener">Venue gallery</a>` : ''}
      ${hasPrice(v) ? `<a class="btn ghost" href="${esc(p.source_url)}" target="_blank" rel="noopener">Price source</a>` : ''}
    </div>
    <p class="small muted">Photos of the venue itself are in its own gallery. Prices are starting figures and change — confirm with the venue.</p>`;
  const sh = $('#sheet');
  const rate = (k, val) => { RATE[v.id] = Object.assign({}, RATE[v.id], { [k]: val === '' ? null : +val }); lsSet(RATINGS, RATE); D._ratingChanged = true; openVenue(id, ctx); };
  $('#r-wow').addEventListener('change', e => rate('wow', e.target.value));
  $('#r-net').addEventListener('change', e => rate('net', e.target.value));
  if (!sh.open) { D._opener = document.activeElement; if (sh.showModal) sh.showModal(); else sh.setAttribute('open', ''); }
  const h = $('#sheet-title'); h.setAttribute('tabindex', '-1'); h.focus();
}
function closeSheet() { const sh = $('#sheet'); if (sh.open) { sh.close(); if (D._opener && document.body.contains(D._opener)) D._opener.focus(); } }

/* ---------------- budget, timeline, save ---------------- */
function budgetSection(ctx) {
  const b = budgetSplit(ctx);
  if (!b) return `<section class="sec" id="sec-budget"><p class="label">No 06 · Budget split</p><h2>Budget split</h2><p>Answer a few style questions to see a split.</p></section>`;
  const cats = D.styles.budget_categories; const total = Object.values(b.split).reduce((a, x) => a + x, 0);
  return `<section class="sec" id="sec-budget" aria-labelledby="h-budget"><p class="label">No 06 · Budget split — planning guide</p><h2 id="h-budget">Where your budget <em>goes</em></h2>
    <p class="sec-intro">A planning guide in percent shares for the ${esc(b.style.name)} look — not market data and not vendor pricing. ${esc(b.style.budget_note || '')}</p>
    <div class="bud">${cats.map(c => `<div class="b"><span>${esc(c.label)}${b.boosted === c.id ? ` <span class="boost">+${b.moved} for your splurge</span>` : ''}</span><b>${b.split[c.id] || 0}%</b><div class="bar"><i data-w="${b.split[c.id] || 0}"></i></div></div>`).join('')}</div>
    <p class="small muted">Shares add to ${total}%. ${b.boosted ? `Your one splurge moved ${b.moved} points from misc and stationery.` : 'Pick a splurge in the quiz to shift 5 points toward it.'}</p></section>`;
}
/* Checklist tasks show only their task text. Any internal tool label (e.g. "Kit skill: ...") is never shown. */
const taskText = t => String((t && t.task) || '').replace(/\s*[(\[]?\s*(?:kit\s+)?skills?\s*:[^)\]]*[)\]]?/gi, '').trim();
function msDate(when) {
  if (!S.plan.date) return null;
  const m = S.plan.date.match(/^(\d{4})-(\d{2})-(\d{2})$/); if (!m) return null;
  const d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
  const w = String(when).toLowerCase(); const n = parseInt(w, 10);
  if (/month/.test(w)) d.setUTCMonth(d.getUTCMonth() - n);
  else if (/week of/.test(w)) d.setUTCDate(d.getUTCDate() - 7);
  else if (/week/.test(w)) d.setUTCDate(d.getUTCDate() - 7 * n);
  return d;
}
function timelineSection() {
  const ms = D.options.plan_template.milestones; const today = new Date();
  const prep = S.details && S.details.prep_done_by;
  let total = 0;
  const body = ms.map((m, i) => {
    const d = msDate(m.when); const past = d && d < today;
    const when = d ? `${m.when} out · by ${d.toLocaleDateString('en-US', { month: 'short', year: 'numeric', timeZone: 'UTC' })}${past ? ' · date has passed, catch up now' : ''}` : `${m.when} out`;
    return `<details class="ms fold"${i === 0 ? ' open' : ''}><summary><span><span class="when">${esc(when)}</span><span class="ms-h">${esc(m.when === 'Week of' ? 'The week of' : m.when + ' before')} · ${m.tasks.length} tasks</span></span><span aria-hidden="true">＋</span></summary><ul class="tasks">${m.tasks.map((t, j) => { total++; const key = i + '-' + j;
      return `<li><label><input type="checkbox" data-check="${key}" ${S.checks[key] ? 'checked' : ''}><span>${esc(taskText(t))}</span></label></li>`; }).join('')}</ul></details>`;
  }).join('');
  const done = Object.values(S.checks).filter(Boolean).length;
  return `<section class="sec" id="sec-timeline" aria-labelledby="h-time"><p class="label">No 07 · Timeline &amp; checklist</p><h2 id="h-time">Month by <em>month</em></h2>
    <p class="sec-intro">${S.plan.date ? `Dated back from your wedding on ${esc(fmtDate(S.plan.date))}.` : 'Add a wedding date in the quiz to date each step.'}${prep ? ` Your prep-done target: ${esc(fmtDate(prep))}.` : ''} Ticks save on this device.</p>
    <p class="picked-count" id="checkcount">${done} of ${total} done</p>${body}</section>`;
}
function wireTimeline() {
  $$('[data-check]').forEach(c => c.addEventListener('change', () => {
    S.checks[c.dataset.check] = c.checked; persist(); if (S.done) lsSet(STORE, S);
    const all = $$('[data-check]'); $('#checkcount').textContent = `${all.filter(x => x.checked).length} of ${all.length} done`;
  }));
}
function planText(ctx, short) {
  const L = []; const pals = chosenPalettes(ctx);
  L.push(`WEDDING DESIGN PLAN — ${coupleName()}`);
  if (S.sample) L.push('(Sample answers — example plan)');
  if (S.plan.date) L.push(`Wedding date: ${fmtDate(S.plan.date)}`);
  const d = S.details; if (d) { if (d.destination) L.push(`Destination: ${d.destination}`); if (d.arrive) L.push(`Arrive: ${fmtDate(d.arrive)}`); if (d.honeymoon) L.push(`Honeymoon after: ${d.honeymoon}`); if (d.prep_done_by) L.push(`Prep done by: ${fmtDate(d.prep_done_by)}`); }
  L.push('');
  if (ctx.hasStyle) {
    L.push('STYLE'); ctx.top3.forEach((x, i) => L.push(`${i + 1}. ${D.styleById[x.id].name} — ${x.pct}%`));
    L.push(oneLiner(ctx)); L.push('');
  }
  if (pals.main) { const p = D.palById[pals.main]; L.push(`PALETTE: ${p.name} — ${p.hex.map((h, i) => (p.color_names || [])[i] + ' ' + h).join(', ')}`); }
  if (pals.alt) { const p = D.palById[pals.alt]; L.push(`Alternate color story: ${p.name} — ${p.hex.join(' ')}`); }
  L.push('');
  if (!short) L.push('DESIGN PICKS (ideas, not vendor quotes)');
  if (!short) designPicks(ctx, pals.picks.length ? pals.picks : (pals.main ? [pals.main] : [])).forEach(x => L.push(`- ${x.cat.label}: ${x.pick.o.label || x.pick.o.name}`));
  L.push('');
  L.push('TOP PLACES');
  rankAreas(ctx).slice(0, short ? 3 : 5).forEach((x, i) => L.push(`${i + 1}. ${x.a.name} (${x.a.country}) — ${x.s.score}/100${x.s.why.length && !short ? ': ' + x.s.why.join('; ') : ''}`));
  L.push('');
  L.push('TOP VENUES');
  const F = PF || defaultFilters(ctx, true); F.band = ctx.band;
  sortVenues(rankVenues(filterVenues(F), ctx), F).slice(0, short ? 5 : 10).forEach((x, i) => {
    const v = x.v; const p = hasPrice(v) ? `from ${fmtMoney(v.price_from.amount, v.price_from.currency)} (${v.price_from.what_it_covers}; source ${hostOf(v.price_from.source_url)}, ${v.price_from.source_date})` : 'price on request';
    const ps = hasPrice(v) ? `from ${fmtMoney(v.price_from.amount, v.price_from.currency)} per ${hostOf(v.price_from.source_url)} (${v.price_from.source_date})` : 'price on request';
    L.push(short ? `${i + 1}. ${v.name}, ${v.city} — ${x.s.score}/100 — ${ps}` : `${i + 1}. ${v.name}, ${v.city} — ${x.s.score}/100 — ${p} — ${v.source_url}`);
  });
  const b = budgetSplit(ctx);
  if (b) { L.push(''); L.push('BUDGET SPLIT (planning guide, percent shares)'); D.styles.budget_categories.forEach(c => L.push(`- ${c.label}: ${b.split[c.id] || 0}%`)); }
  if (!short) {
    L.push(''); L.push('TIMELINE');
    D.options.plan_template.milestones.forEach((m, i) => { const dd = msDate(m.when); L.push(`${m.when}${dd ? ' (by ' + dd.toLocaleDateString('en-US', { month: 'short', year: 'numeric', timeZone: 'UTC' }) + ')' : ''}:`); m.tasks.forEach((t, j) => L.push(`  [${S.checks[i + '-' + j] ? 'x' : ' '}] ${taskText(t)}`)); });
  }
  L.push(''); L.push('Prices are starting figures from each cited source and change — confirm with the venue.');
  L.push('Made with the Britt Warnick Designs wedding design planner · brittwarnickdesigns.com');
  return L.join('\n');
}
function saveSection() {
  return `<section class="sec no-print-sec" id="sec-save" aria-labelledby="h-save"><p class="label">No 08 · Keep your plan</p><h2 id="h-save">Save, copy, print or <em>email</em></h2>
    <div class="actions no-print">
      <button class="btn" type="button" id="save">Save my plan</button>
      <button class="btn ghost" type="button" id="copy">Copy my plan</button>
      <button class="btn ghost" type="button" id="print">Print / save as PDF</button>
      <a class="btn ghost" id="mail" href="#">Email this plan to me</a>
    </div>
    <div class="field no-print" style="margin-top:16px"><label for="mailto-addr">Your email for the mail app (optional — nothing is sent from this site)</label><input id="mailto-addr" type="email" autocomplete="email"></div>
    <p class="small muted no-print" id="savestatus" role="status"></p>
    <details class="no-print" style="margin-top:12px"><summary class="btn quiet small">Show the plan text</summary><textarea class="plan-text" id="plantext" readonly aria-label="Your plan as text"></textarea></details>
  </section>`;
}
function wireSave(ctx) {
  const full = planText(ctx, false), short = planText(ctx, true);
  $('#plantext').value = full;
  const mailHref = () => `mailto:${encodeURIComponent(($('#mailto-addr').value || '').trim())}?subject=${encodeURIComponent('Our wedding design plan')}&body=${encodeURIComponent(short)}`;
  $('#mail').href = mailHref();
  $('#mailto-addr').addEventListener('input', () => { $('#mail').href = mailHref(); });
  $('#copy').addEventListener('click', async () => {
    const text = planText(ctx, false); let ok = false;
    try { await navigator.clipboard.writeText(text); ok = true; } catch (e) {
      const ta = $('#plantext'); ta.value = text; ta.closest('details').open = true; ta.select();
      try { ok = document.execCommand('copy'); } catch (e2) { ok = false; }
    }
    $('#savestatus').textContent = ok ? 'Copied. Paste it anywhere.' : 'Select the text below and copy it.'; toast(ok ? 'Plan copied' : 'Select the text to copy');
  });
  $('#print').addEventListener('click', () => window.print());
  $('#save').addEventListener('click', () => {
    S.done = true; const ok = lsSet(STORE, S);
    try {
      const blob = new Blob([planText(ctx, false)], { type: 'text/plain' }); const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'wedding-design-plan.txt'; document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    } catch (e) { /* download not available */ }
    $('#savestatus').textContent = ok ? 'Saved on this device and downloaded as a text file.' : 'Downloaded as a text file.'; toast('Plan saved');
  });
  const rs = $('#restart'); if (rs) rs.addEventListener('click', () => { S = freshState(); persist(); location.hash = '#/'; });
  $$('[data-area]').forEach(b => b.addEventListener('click', () => { const t = document.getElementById('area-' + b.dataset.area); if (t) t.scrollIntoView(); else { BA.region = D.areaById[b.dataset.area].region; location.hash = '#/browse/areas'; } }));
}
function brittMailto(ctx) {
  const body = ctx ? planText(ctx, true) : 'Hi Britt, I would love to talk about our wedding.';
  return `mailto:hello@brittwarnickdesigns.com?subject=${encodeURIComponent('Wedding design plan')}&body=${encodeURIComponent(body)}`;
}
function wireSticky() {
  const b = $('#sticky-britt'), cta = $('#sec-britt'); if (!b || !cta || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver(es => es.forEach(e => b.classList.toggle('hide', e.isIntersecting || e.boundingClientRect.top < 0)), { threshold: 0 });
  io.observe(cta);
}
function hireBlock() {
  const ctx = S.done ? context() : null;
  const body = ctx ? planText(ctx, true) : 'Hi Britt, I would love to talk about our wedding.';
  return `<section class="cta" id="sec-britt" aria-labelledby="h-britt"><p class="label" style="color:#E9D9CF">Britt Warnick Designs</p>
    <h2 id="h-britt">Want Britt to bring it <em>to life?</em></h2>
    <p>Britt Warnick Designs does wedding planning and event design. Send her your plan and your date, and start the conversation.</p>
    <p class="contact">Email: <a href="mailto:hello@brittwarnickdesigns.com?subject=${encodeURIComponent('Wedding design plan')}&body=${encodeURIComponent(body)}">hello@brittwarnickdesigns.com</a><br>
    Website: <a href="https://brittwarnickdesigns.com" target="_blank" rel="noopener">brittwarnickdesigns.com</a></p>
    <div class="row no-print"><a class="btn" href="mailto:hello@brittwarnickdesigns.com?subject=${encodeURIComponent('Wedding design plan')}&body=${encodeURIComponent(body)}">Email Britt</a></div></section>`;
}
function renderHire() {
  setView(`<section class="hire-page"><p class="eyebrow">Work with Britt</p><h1>From plan to <em>party</em></h1>
    <p class="lede muted">Your plan is yours to keep and use, free. If you want help making it real, Britt is one email away.</p></section>${hireBlock()}`);
}

/* ---------------- browse ---------------- */
function renderBrowse(tab) {
  const ctx = context();
  setView(`<section class="hire-page"><p class="eyebrow">Browse</p><h1>All venues and <em>places</em></h1>
    <p class="lede muted">No quiz needed. ${D.V.length} venues in ${D.AREAS.length} places. ${hasStyleAnswers() ? 'Scores use your quiz answers.' : 'Take the quiz to score them for you.'}</p>
    <div class="tabs" role="tablist" aria-label="Browse">
      <button role="tab" id="tab-venues" aria-controls="panel" aria-selected="${tab === 'venues'}" tabindex="${tab === 'venues' ? 0 : -1}">Venues</button>
      <button role="tab" id="tab-areas" aria-controls="panel" aria-selected="${tab === 'areas'}" tabindex="${tab === 'areas' ? 0 : -1}">Places</button>
    </div>
    <div id="panel" role="tabpanel" aria-labelledby="tab-${tab}"></div></section>`);
  const tabs = $$('[role=tab]');
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => { location.hash = '#/browse/' + (t.id === 'tab-areas' ? 'areas' : 'venues'); });
    t.addEventListener('keydown', e => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); const nx = tabs[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length]; nx.focus(); nx.click(); } });
  });
  const panel = $('#panel');
  if (tab === 'venues') {
    BF = BF || defaultFilters(ctx, false);
    mountVenueList(panel, BF, ctx);
  } else {
    const regs = D.regionOrder;
    if (!(hasStyleAnswers() || S.done) && BA.sort === 'rank') BA.sort = 'region';
    panel.innerHTML = `<div class="filters"><div class="fgrid"><div class="field"><label for="a-region">Region</label><select id="a-region">${opt('', 'All regions', BA.region)}${regs.map(r => opt(r, r, BA.region)).join('')}</select></div>
      <div class="field"><label for="a-sort">Sort</label><select id="a-sort">${hasStyleAnswers() || S.done ? opt('rank', 'Ranked for you', BA.sort) : ''}${opt('region', 'Region', BA.sort)}${opt('name', 'Name A–Z', BA.sort)}</select></div></div></div><div id="alist"></div>`;
    const draw = () => renderAreaList($('#alist'), ctx, { region: BA.region, sort: BA.sort, limit: 12 });
    $('#a-region').addEventListener('change', e => { BA.region = e.target.value; draw(); });
    $('#a-sort').addEventListener('change', e => { BA.sort = e.target.value; draw(); });
    draw();
  }
}

/* ---------------- how it works ---------------- */
function renderHow() {
  const vr = D.quiz.venue_rubric;
  setView(`<section class="how"><p class="eyebrow">How the scores work</p><h1>Plain rules, <em>shown in full</em></h1>
    <h2>Your style</h2><p>${esc(D.quiz.scoring.method)}</p>
    <p>${esc(D.quiz.scoring.match_percent)}</p>
    <p class="label">Ties are broken in this order</p><ol>${D.quiz.scoring.tie_break.map(t => `<li>${esc(t.replace(/^\d+\.\s*/, ''))}</li>`).join('')}</ol>
    <h2>Venue match (100 points)</h2><p>${esc(vr.how_scored)}</p>
    <p><strong>Style comes first.</strong> Style match is the biggest single part: 30 of the 100 points (your #1 style 30, #2 22, #3 15, venue type fits your #1 style 8). Budget is 14, capacity 10, season 8, catering 6, lodging + airport 6, one site 8 and rain plan 5. Wow factor (8) and planner network (5) are the parts you rate on your tour. A price that is only a starting venue fee (rental, site fee, ceremony fee) is labelled “starting fee only” and earns at most 9 budget points, because a fee is not a wedding total.</p>
    <p><strong>Ranking order:</strong> venues tagged with one of your top 3 styles always rank first. Next come venues that only fit by venue type. Venues with no style match come last, so a great budget or size fit can never lift a no-style venue above a style match. Inside each group, the higher score ranks first.</p>
    <table class="ftable"><tbody>${vr.criteria.map(c => `<tr><th scope="row">${esc(c.criterion)} · ${c.points}</th><td>${esc(c.mode === 'MANUAL' ? 'Rate on your tour. ' + c.compute : c.compute)}</td></tr>`).join('')}</tbody></table>
    <h2>Places</h2><p>Each place earns points only for answers you gave, then the total is scaled to 100. Style is the biggest part: 30 (your #1 style among the place's common styles 30, #2 21, #3 12, a few venues tagged with your #1 style 6). Region 25, month fit 15 (best season 15, shoulder season 8, from the climate table), budget 15 (a listed venue at or under your band; 7 if all are price on request), capacity 15 (largest listed venue seats your guest count 15, your minimum 8).</p>
    <p><strong>Ranking order:</strong> places in your regions come first. Inside that, places that fit one of your top 3 styles rank above places with only a few tagged venues, and those rank above places with no style match. Then the higher score wins; ties go to the place with more venues on file.</p>
    <p><strong>Weather text follows your month:</strong> each place says if your month is in its best season, shoulder season, or outside the usual wedding season. The written December weather note shows only for a December wedding. With no month picked, you see the place's best months.</p>
    <h2>Design picks</h2><p>Each idea earns 10 / 6 / 3 points if it suits your #1 / #2 / #3 style, 4 if it uses one of your palettes, 2 if it suits your season and 1 for your guest count. The top idea is your pick; the next two are alternates.</p>
    <h2>Budget split</h2><p>${esc(D.styles.budget_priority_boost.method)} It is a planning guide in percent shares, not market data.</p>
    <p><a class="btn" href="#/quiz/1">Start the quiz</a></p></section>`);
}

window.BWD = { scoreStyles, top3pct, scoreVenue, rankVenues, feeOnly, scoreArea, rankAreas, filterVenues, seasonNamed, context, get state() { return S; }, set state(v) { S = v; }, D };
load();
