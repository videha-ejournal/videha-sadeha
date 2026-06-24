<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Videha Sitemap</title>
<style>
:root{--ink:#1f1b16;--muted:#5f5548;--rule:#d8cfc0;--paper:#fbf7ec;--field:#f1ead6;--accent:#8B1A1A;--blue:#1F3864}*{box-sizing:border-box}body{margin:0;background:var(--field);color:var(--ink);font-family:Georgia,'Noto Serif Devanagari',serif;line-height:1.65}.wrap{max-width:1100px;margin:0 auto;padding:2rem 1rem}header{border-bottom:2px solid var(--rule);padding-bottom:1rem;margin-bottom:1.5rem}h1{font-size:clamp(1.7rem,3vw,2.5rem);color:var(--accent);margin:.2rem 0}.sub{color:var(--muted);font-size:1rem}.card{background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:1rem;overflow:auto}table{border-collapse:collapse;width:100%;min-width:720px}th,td{text-align:left;border-bottom:1px solid var(--rule);padding:.65rem .7rem;vertical-align:top}th{background:#fff6e8;color:var(--blue);position:sticky;top:0}a{color:var(--blue);word-break:break-all}a:focus{outline:3px solid var(--accent);outline-offset:2px}.count{font-weight:bold;color:var(--accent)}footer{margin-top:1rem;color:var(--muted);font-size:.9rem}</style>
</head>
<body><main class="wrap"><header><h1>Videha Sitemap</h1><div class="sub">Videha — First Maithili Fortnightly eJournal | Accessibility-friendly sitemap view</div></header><div class="card">
<xsl:choose>
<xsl:when test="s:sitemapindex"><p class="count"><xsl:value-of select="count(s:sitemapindex/s:sitemap)"/> sitemap files</p><table aria-label="Sitemap index"><thead><tr><th>Section sitemap</th><th>Last modified</th></tr></thead><tbody><xsl:for-each select="s:sitemapindex/s:sitemap"><tr><td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td><td><xsl:value-of select="s:lastmod"/></td></tr></xsl:for-each></tbody></table></xsl:when>
<xsl:otherwise><p class="count"><xsl:value-of select="count(s:urlset/s:url)"/> URLs</p><table aria-label="Sitemap URLs"><thead><tr><th>URL</th><th>Last modified</th><th>Change frequency</th><th>Priority</th></tr></thead><tbody><xsl:for-each select="s:urlset/s:url"><tr><td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td><td><xsl:value-of select="s:lastmod"/></td><td><xsl:value-of select="s:changefreq"/></td><td><xsl:value-of select="s:priority"/></td></tr></xsl:for-each></tbody></table></xsl:otherwise>
</xsl:choose></div><footer>© Gajendra Thakur, Editor — Videha eJournal</footer></main></body></html>
</xsl:template>
</xsl:stylesheet>
