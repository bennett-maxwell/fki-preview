// Advaita AI Readiness Quiz
// 10 questions, each scored 0-10. Total 0-100.

const QUESTIONS = [
  {
    q: "What's your annual revenue?",
    label: "Revenue",
    choices: [
      { t: "Under $1M", s: 2, band: "starter" },
      { t: "$1M – $3M", s: 5, band: "growth" },
      { t: "$3M – $10M", s: 8, band: "scale" },
      { t: "$10M+", s: 10, band: "enterprise" }
    ],
    key: "revenue"
  },
  {
    q: "How many people on your team?",
    label: "Team size",
    choices: [
      { t: "Just me", s: 2 },
      { t: "2 – 10", s: 5 },
      { t: "11 – 50", s: 8 },
      { t: "50+", s: 10 }
    ]
  },
  {
    q: "How much of your business already uses AI?",
    label: "AI adoption",
    choices: [
      { t: "Zero — we haven't started", s: 0 },
      { t: "A few people experiment", s: 3 },
      { t: "Used daily by some teams", s: 6 },
      { t: "Embedded in core workflows", s: 10 }
    ]
  },
  {
    q: "Where do most of your leads come from?",
    label: "Lead gen",
    choices: [
      { t: "Referrals only", s: 3 },
      { t: "1 paid channel (Meta/Google)", s: 5 },
      { t: "Multi-channel paid + organic", s: 8 },
      { t: "Predictable system we control", s: 10 }
    ]
  },
  {
    q: "How clean is your CRM and customer data?",
    label: "Data hygiene",
    choices: [
      { t: "Spreadsheets and chaos", s: 1 },
      { t: "CRM exists but messy", s: 4 },
      { t: "CRM is clean, used daily", s: 7 },
      { t: "Single source of truth, automated", s: 10 }
    ]
  },
  {
    q: "Hours per week you spend on admin / repeat tasks?",
    label: "Admin load",
    choices: [
      { t: "20+ hours — it's drowning me", s: 2 },
      { t: "10 – 20 hours", s: 5 },
      { t: "5 – 10 hours", s: 7 },
      { t: "Under 5 hours — mostly automated", s: 10 }
    ]
  },
  {
    q: "How many repeat tasks could AI do today?",
    label: "Automation surface",
    choices: [
      { t: "Tons — we just don't know how", s: 2 },
      { t: "Some, we've identified them", s: 5 },
      { t: "Few — most are automated", s: 8 },
      { t: "Almost zero — we're optimized", s: 10 }
    ]
  },
  {
    q: "How many tools in your tech stack?",
    label: "Stack",
    choices: [
      { t: "Under 5", s: 6 },
      { t: "5 – 15", s: 8 },
      { t: "15 – 30", s: 5 },
      { t: "30+ (we have stack sprawl)", s: 2 }
    ]
  },
  {
    q: "Your #1 growth bottleneck right now?",
    label: "Bottleneck",
    choices: [
      { t: "Not enough leads", s: 4 },
      { t: "Closing rate is low", s: 5 },
      { t: "Delivery / fulfillment", s: 6 },
      { t: "Owner is the bottleneck", s: 3 }
    ]
  },
  {
    q: "When do you want this fixed?",
    label: "Timeline",
    choices: [
      { t: "Yesterday", s: 10 },
      { t: "Next 30 days", s: 8 },
      { t: "Next 90 days", s: 5 },
      { t: "Just exploring", s: 2 }
    ]
  }
];

let state = JSON.parse(localStorage.getItem('advaita-quiz') || '{}');
let answers = state.answers || {};
let idx = state.idx || 0;

const root = document.getElementById('quiz-root');
const bar = document.getElementById('bar');
const qcount = document.getElementById('qcount');
const nextBtn = document.getElementById('next');
const backBtn = document.getElementById('back');

function render() {
  const q = QUESTIONS[idx];
  qcount.textContent = `Question ${idx + 1} of ${QUESTIONS.length}`;
  bar.style.width = `${((idx + 1) / QUESTIONS.length) * 100}%`;
  backBtn.style.visibility = idx === 0 ? 'hidden' : 'visible';

  const selected = answers[idx];
  nextBtn.disabled = selected === undefined;
  nextBtn.style.opacity = selected === undefined ? '0.4' : '1';
  nextBtn.textContent = idx === QUESTIONS.length - 1 ? 'See My Score →' : 'Next →';

  root.innerHTML = `
    <div class="question">
      <div class="q-label">${q.label}</div>
      <h2>${q.q}</h2>
      <div class="choices">
        ${q.choices.map((c, i) => `
          <button class="choice ${selected === i ? 'selected' : ''}" data-i="${i}">${c.t}</button>
        `).join('')}
      </div>
    </div>
  `;

  root.querySelectorAll('.choice').forEach(btn => {
    btn.addEventListener('click', () => {
      const i = parseInt(btn.dataset.i);
      answers[idx] = i;
      persist();
      render();
    });
  });
}

function persist() {
  localStorage.setItem('advaita-quiz', JSON.stringify({ answers, idx }));
}

function score() {
  let total = 0;
  let band = 'growth';
  let monthlyRev = 50000;
  QUESTIONS.forEach((q, i) => {
    const a = answers[i];
    if (a !== undefined) {
      const ch = q.choices[a];
      total += ch.s;
      if (q.key === 'revenue') {
        band = ch.band;
        monthlyRev = { starter: 50000, growth: 165000, scale: 540000, enterprise: 1500000 }[ch.band];
      }
    }
  });
  return { total, band, monthlyRev };
}

nextBtn.addEventListener('click', () => {
  if (idx < QUESTIONS.length - 1) {
    idx++;
    persist();
    render();
  } else {
    const { total, band, monthlyRev } = score();
    window.location.href = `result.html?score=${total}&band=${band}&rev=${monthlyRev}`;
  }
});

backBtn.addEventListener('click', () => {
  if (idx > 0) { idx--; persist(); render(); }
});

render();
