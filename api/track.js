// Shadow Del Valle R — Analytics Tracker
// Endpoint: POST /api/track
// Body: { slug: "guia-lesiones", type: "pageview"|"click", referrer?: string }
// Uses Vercel KV (Redis) for persistence — free tier included in Vercel

import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const { slug = 'home', type = 'pageview', referrer = '' } = req.body;
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const hour = new Date().getHours();
    const key = type === 'pageview' ? `pv:${today}` : `click:${today}`;
    const slugKey = type === 'pageview' ? `pv:slug:${today}:${slug}` : `click:slug:${today}:${slug}`;
    const totalKey = type === 'pageview' ? 'pv:total' : 'click:total';

    // Incrementar contadores en paralelo
    const pipeline = kv.pipeline();
    
    // Contador diario total
    pipeline.hincrby(key, slug, 1);
    pipeline.hincrby(key, '_total', 1);
    
    // Contador por slug (histórico)
    pipeline.hincrby(slugKey, '_count', 1);
    
    // Contador total absoluto
    pipeline.incr(totalKey);
    
    // Contador por hora (para gráficos)
    pipeline.hincrby(`hourly:${today}`, `${hour}`, 1);

    // Registrar referrer si existe
    if (referrer) {
      pipeline.hincrby(`ref:${today}`, referrer, 1);
    }

    await pipeline.exec();

    return res.status(200).json({ ok: true });
  } catch (error) {
    console.error('Track error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
