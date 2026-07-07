// Top 10 Mundial 2026 news. Source: Google News RSS (es-MX).
// Cached 24h via Next.js fetch revalidation.

export const revalidate = 86400;

type NewsItem = {
  title: string;
  link: string;
  source: string;
  pubDate: string;
};

const FEED_URL =
  "https://news.google.com/rss/search?q=%22Mundial+2026%22+OR+%22Copa+del+Mundo+2026%22+OR+%22FIFA+World+Cup+2026%22&hl=es-419&gl=MX&ceid=MX:es-419";

function decodeEntities(s: string): string {
  return s
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(parseInt(n, 10)));
}

function stripCdata(s: string): string {
  return s.replace(/^<!\[CDATA\[/, "").replace(/\]\]>$/, "");
}

function pick(block: string, tag: string): string {
  const m = block.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`));
  return m ? decodeEntities(stripCdata(m[1].trim())) : "";
}

function parseRss(xml: string): NewsItem[] {
  const items: NewsItem[] = [];
  const re = /<item>([\s\S]*?)<\/item>/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(xml)) && items.length < 20) {
    const block = m[1];
    let title = pick(block, "title");
    const link = pick(block, "link");
    const pubDate = pick(block, "pubDate");
    const source = pick(block, "source");
    // Google News titles end with " - Source Name"; if we already have <source>, trim it from title.
    if (source && title.endsWith(` - ${source}`)) {
      title = title.slice(0, -(source.length + 3)).trim();
    }
    if (title && link) items.push({ title, link, source, pubDate });
  }
  return items.slice(0, 10);
}

export async function GET() {
  try {
    const res = await fetch(FEED_URL, {
      next: { revalidate: 86400 },
      headers: { "User-Agent": "Mozilla/5.0 (compatible; QuinielaCharales/1.0)" },
    });
    if (!res.ok) {
      return Response.json({ items: [], error: `feed ${res.status}` }, { status: 200 });
    }
    const xml = await res.text();
    const items = parseRss(xml);
    return Response.json({ items, fetchedAt: Date.now() });
  } catch (e) {
    return Response.json({ items: [], error: String(e) }, { status: 200 });
  }
}
