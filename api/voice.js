/**
 * ElevenLabs TTS proxy for the Advaita talking globe.
 * Key stays on Vercel. Never ship xi-api-key in public JS.
 * Interactive globe uses turbo for latency; static openers are rendered separately.
 */
const https = require('https');

const VOICE_ID = process.env.ELEVENLABS_VOICE_ID || 'CwhRBWXzGAHq8TQ4Fs17'; // Roger — conversational male, not Bennett PVC
const MODEL = process.env.ELEVENLABS_MODEL || 'eleven_turbo_v2_5';
const MAX_CHARS = 420;

function cors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function cleanText(raw) {
  return String(raw || '')
    .replace(/<break\b[^>]*>/gi, ' ')
    .replace(/\[[^\]]+\]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, MAX_CHARS);
}

function tts(text, apiKey) {
  const payload = JSON.stringify({
    text: text,
    model_id: MODEL,
    voice_settings: {
      stability: 0.55,
      similarity_boost: 0.78,
      style: 0.22,
      use_speaker_boost: true
    }
  });
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.elevenlabs.io',
      path: '/v1/text-to-speech/' + VOICE_ID + '?output_format=mp3_44100_128',
      method: 'POST',
      headers: {
        'xi-api-key': apiKey,
        'Content-Type': 'application/json',
        'Accept': 'audio/mpeg',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        const buf = Buffer.concat(chunks);
        if (res.statusCode !== 200) {
          return reject(new Error('elevenlabs ' + res.statusCode + ' ' + buf.toString('utf8').slice(0, 180)));
        }
        resolve(buf);
      });
    });
    req.setTimeout(12000, () => { req.destroy(); reject(new Error('timeout')); });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

module.exports = async function handler(req, res) {
  cors(res);
  if (req.method === 'OPTIONS') { res.statusCode = 204; res.end(); return; }
  if (req.method !== 'POST') { res.statusCode = 405; res.end('POST only'); return; }
  const apiKey = process.env.ELEVENLABS_API_KEY || '';
  if (!apiKey) { res.statusCode = 503; res.end(JSON.stringify({ error: 'voice_unconfigured' })); return; }
  let body = '';
  await new Promise((resolve) => {
    req.on('data', (c) => { body += c; if (body.length > 8000) req.destroy(); });
    req.on('end', resolve);
  });
  let text = '';
  try { text = cleanText(JSON.parse(body || '{}').text); } catch (e) { text = ''; }
  if (!text) { res.statusCode = 400; res.end(JSON.stringify({ error: 'text required' })); return; }
  try {
    const audio = await tts(text, apiKey);
    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Cache-Control', 'no-store');
    res.statusCode = 200;
    res.end(audio);
  } catch (err) {
    res.statusCode = 502;
    res.end(JSON.stringify({ error: 'tts_failed' }));
  }
};
