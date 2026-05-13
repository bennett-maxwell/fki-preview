// Advaita Quiz → GHL Bridge
// BIZ-04: Tier routing + BIZ-05: GHL contact payload builder

const GHL_LOCATION_ID = '14RD8KklxR9G4e0Rf7v2';

const TIER_DATA = {
  bootcamp: {
    name: 'The Bootcamp',
    price: '$99',
    desc: '2-day live session. Learn agent harness, memory, custom GPTs, and skill architecture.',
    tag: 'tier-bootcamp'
  },
  arsenal: {
    name: 'The Arsenal',
    price: '$500',
    desc: 'All 86+ functional skills downloadable with integration guides and troubleshooting.',
    tag: 'tier-arsenal'
  },
  build: {
    name: 'The Build',
    price: '$5K–$12K',
    desc: 'Full Advaita stack deployed for your business. From calling agents to complete automation.',
    tag: 'tier-build'
  }
};

function getQuizResults() {
  try {
    const raw = localStorage.getItem('advaita-quiz-results');
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function getRecommendedTier(score, answers) {
  if (score >= 80) return 'build';
  if (score >= 50) return 'arsenal';
  return 'bootcamp';
}

function getLeadTier(score) {
  if (score >= 70) return 'hot';
  if (score >= 40) return 'warm';
  return 'cold';
}

function formatLeakage(score, monthlyRev) {
  const leakage = ((100 - score) / 100) * monthlyRev * 0.02;
  return leakage.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
}

function getUTMParams() {
  const params = new URLSearchParams(window.location.search);
  return {
    source: params.get('utm_source') || 'organic',
    medium: params.get('utm_medium') || 'quiz',
    campaign: params.get('utm_campaign') || '',
    content: params.get('utm_content') || ''
  };
}

function buildGHLPayload(pii, quizResults) {
  const score = quizResults.total;
  const leadTier = getLeadTier(score);
  const productTier = getRecommendedTier(score, quizResults.answers);
  const utm = getUTMParams();

  const noteLines = ['--- Advaita AI Readiness Quiz Results ---', ''];
  quizResults.answers.forEach((a, i) => {
    noteLines.push(`Q${i + 1} (${a.label}): ${a.choice} [${a.score}/10]`);
  });
  noteLines.push('', `Total Score: ${score}/100`);
  noteLines.push(`Band: ${quizResults.band}`);
  noteLines.push(`Recommended Tier: ${TIER_DATA[productTier].name}`);
  noteLines.push(`Lead Tier: ${leadTier.toUpperCase()}`);
  noteLines.push(`Monthly Revenue Estimate: $${quizResults.monthlyRev.toLocaleString()}`);
  noteLines.push(`Leakage Estimate: ${formatLeakage(score, quizResults.monthlyRev)}/mo`);
  noteLines.push(`Submitted: ${quizResults.timestamp}`);
  if (utm.source !== 'organic') {
    noteLines.push(`UTM: ${utm.source} / ${utm.medium} / ${utm.campaign} / ${utm.content}`);
  }

  const tags = [
    'advaita-quiz',
    leadTier,
    TIER_DATA[productTier].tag,
    `score-${score}`,
    `band-${quizResults.band}`,
    `source-${utm.source}`
  ];
  if (utm.campaign) tags.push(`campaign-${utm.campaign}`);

  return {
    firstName: pii.firstName,
    email: pii.email,
    phone: pii.phone || '',
    companyName: pii.businessName || '',
    locationId: GHL_LOCATION_ID,
    source: `advaita-quiz-${utm.source}`,
    tags,
    customFields: [
      { key: 'quiz_score', value: String(score) },
      { key: 'quiz_band', value: quizResults.band },
      { key: 'quiz_tier', value: productTier },
      { key: 'quiz_revenue', value: quizResults.band },
      { key: 'quiz_timeline', value: quizResults.answers[9]?.choice || '' },
      { key: 'quiz_bottleneck', value: quizResults.answers[8]?.choice || '' },
      { key: 'quiz_completed_at', value: quizResults.timestamp }
    ],
    note: noteLines.join('\n')
  };
}
