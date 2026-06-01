// Pitch-email attribution capture v1 (2026-05-11)
// Persists UTM params from URL → localStorage → first-party cookie so any
// downstream form/booking can read them. No 3rd-party calls yet (GA4 wiring
// gated on Bennett's analytics property pick).
(function () {
  try {
    var qs = new URLSearchParams(window.location.search);
    var keys = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term'];
    var capture = {};
    var ts = new Date().toISOString();
    keys.forEach(function (k) {
      var v = qs.get(k);
      if (v) capture[k] = v;
    });
    if (Object.keys(capture).length) {
      capture._captured_at = ts;
      capture._landing_path = window.location.pathname;
      localStorage.setItem('fki_attribution', JSON.stringify(capture));
      document.cookie = 'fki_attribution=' + encodeURIComponent(JSON.stringify(capture)) + '; path=/; max-age=2592000; SameSite=Lax';
    }
    // GA4 placeholder — Bennett-gate on measurement ID. When wired, uncomment:
    // window.dataLayer = window.dataLayer || [];
    // function gtag(){dataLayer.push(arguments);}
    // gtag('js', new Date());
    // gtag('config', 'G-XXXXXXX', { 'send_page_view': true });
  } catch (e) { /* swallow — analytics never blocks the page */ }
})();
