import { defineConfig } from "astro/config";
import { siteUrl } from "./src/data/site.js";
import { writeFile } from "node:fs/promises";
export default defineConfig({
  site: siteUrl,
  trailingSlash: "always",
  output: "static",
  integrations: [{
    name: "site-discovery",
    hooks: {
      "astro:build:done": async ({ pages, dir }) => {
        const escapeXml = (value) => value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll('"', "&quot;");
        const urls = [...new Set(pages.map(({ pathname }) => new URL(pathname, `${siteUrl}/`).href))].sort();
        const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map(url => `  <url><loc>${escapeXml(url)}</loc></url>`).join("\n")}\n</urlset>\n`;
        await writeFile(new URL("sitemap.xml", dir), xml);
        await writeFile(new URL("robots.txt", dir), `User-agent: *\nAllow: /\n\nSitemap: ${siteUrl}/sitemap.xml\n`);
      }
    }
  }]
});
