// Shadow Del Valle R — Analytics Stats API
// Endpoint: GET /api/stats
// Returns aggregated pageviews and clicks

import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');

  try {
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
    
    // Obtener totales históricos
    const totalViews = await kv.get('pv:total') || 0;
    const totalClicks = await kv.get('click:total') || 0;
    
    // Obtener datos de hoy
    const todayViews = await kv.hgetall(`pv:${today}`) || {};
    const todayClicks = await kv.hgetall(`click:${today}`) || {};
    
    // Obtener datos de ayer (para comparación)
    const yesterdayViews = await kv.hgetall(`pv:${yesterday}`) || {};

    // Obtener datos por hora (hoy)
    const hourlyRaw = await kv.hgetall(`hourly:${today}`) || {};
    const hourly = Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      count: parseInt(hourlyRaw[String(i)] || '0', 10)
    }));

    // Obtener referrers de hoy
    const referrersRaw = await kv.hgetall(`ref:${today}`) || {};
    const referrers = Object.entries(referrersRaw)
      .map(([source, count]) => ({ source, count: parseInt(count, 10) }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Calcular stats por slug
    const slugs = new Set();
    Object.keys(todayViews).forEach(k => { if (k !== '_total') slugs.add(k); });
    
    const pageStats = await Promise.all(
      Array.from(slugs).map(async (slug) => {
        const pv = parseInt(todayViews[slug] || '0', 10);
        const clickKey = `click:slug:${today}:${slug}`;
        const clickData = await kv.hgetall(clickKey) || {};
        const clicks = parseInt(clickData._count || '0', 10);
        return { slug, pageviews: pv, clicks, ctr: pv > 0 ? ((clicks / pv) * 100).toFixed(1) + '%' : '0%' };
      })
    );

    pageStats.sort((a, b) => b.pageviews - a.pageviews);

    const totalTodayViews = parseInt(todayViews._total || '0', 10);
    const totalTodayClicks = parseInt(todayClicks._total || '0', 10);
    const totalYesterdayViews = parseInt(yesterdayViews._total || '0', 10);

    return res.status(200).json({
      today: {
        pageviews: totalTodayViews,
        clicks: totalTodayClicks,
        ctr: totalTodayViews > 0 ? ((totalTodayClicks / totalTodayViews) * 100).toFixed(1) + '%' : '0%'
      },
      yesterday: {
        pageviews: totalYesterdayViews
      },
      allTime: {
        pageviews: parseInt(totalViews, 10),
        clicks: parseInt(totalClicks, 10)
      },
      pages: pageStats,
      hourly,
      referrers,
      date: today
    });

  } catch (error) {
    console.error('Stats error:', error);
    return res.status(200).json({
      today: { pageviews: 0, clicks: 0, ctr: '0%' },
      yesterday: { pageviews: 0 },
      allTime: { pageviews: 0, clicks: 0 },
      pages: [],
      hourly: Array.from({ length: 24 }, (_, i) => ({ hour: i, count: 0 })),
      referrers: [],
      date: new Date().toISOString().split('T')[0],
      error: 'KV not configured yet. Run: vercel kv create'
    });
  }
}
