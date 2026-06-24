<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <xsl:output method="html" encoding="UTF-8" indent="yes" doctype-system="about:legacy-compat"/>

  <xsl:template match="/">
    <html lang="mai">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title>विदेह · Sitemap</title>
        <style>
          :root{ --crimson:#8B1A1A; --crimson-d:#671111; --gold:#C49A3C; --cream:#FAF6EE; --cream2:#F3EAD7; --ink:#2b211c; --line:#E4D3A8; }
          *{ box-sizing:border-box; }
          body{ margin:0; background:var(--cream); color:var(--ink); font:15px/1.6 "Noto Serif Devanagari","Segoe UI",system-ui,serif; }
          .wrap{ max-width:1120px; margin:0 auto; padding:0 16px 56px; }
          header{ background:linear-gradient(135deg,var(--crimson),var(--crimson-d)); color:var(--cream); padding:30px 24px; border-bottom:4px solid var(--gold); }
          header .wrap{ padding-bottom:0; }
          .eyebrow{ letter-spacing:.16em; text-transform:uppercase; font-size:12px; color:var(--gold); margin:0 0 6px; }
          h1{ margin:0; font-size:30px; }
          .sub{ margin:8px 0 0; opacity:.92; font-size:14px; }
          .stats{ display:flex; flex-wrap:wrap; gap:14px; margin:22px 0 8px; }
          .chip{ background:#fff; border:1px solid var(--line); border-left:4px solid var(--crimson); border-radius:8px; padding:12px 18px; box-shadow:0 1px 2px rgba(0,0,0,.05); }
          .chip b{ display:block; font-size:26px; color:var(--crimson); line-height:1.1; }
          .chip span{ font-size:12px; letter-spacing:.04em; color:#6b5d52; }
          table{ width:100%; border-collapse:collapse; margin-top:14px; background:#fff; border:1px solid var(--line); border-radius:10px; overflow:hidden; }
          thead th{ background:var(--cream2); color:var(--crimson-d); text-align:left; font-size:12px; letter-spacing:.06em; text-transform:uppercase; padding:12px 14px; border-bottom:2px solid var(--gold); }
          tbody td{ padding:11px 14px; border-bottom:1px solid #F0E7D4; vertical-align:top; }
          tbody tr:nth-child(even){ background:#FFFDF8; }
          tbody tr:hover{ background:#FDF6E6; }
          td.idx{ color:#B7A98F; font-variant-numeric:tabular-nums; width:46px; }
          a{ color:var(--crimson); text-decoration:none; word-break:break-all; }
          a:hover{ text-decoration:underline; }
          .pill{ display:inline-block; font-size:12px; padding:2px 9px; border-radius:999px; background:var(--cream2); border:1px solid var(--line); color:#6b5d52; }
          .prio{ font-variant-numeric:tabular-nums; font-weight:600; color:var(--crimson); }
          .imgs{ color:var(--gold); font-weight:600; }
          footer{ margin-top:26px; font-size:12.5px; color:#7c6e62; text-align:center; }
          @media(max-width:700px){ .hide-sm{ display:none; } h1{ font-size:24px; } }
        </style>
      </head>
      <body>
        <header>
          <div class="wrap">
            <p class="eyebrow">विदेह · ISSN 2229-547X · Since 2000</p>
            <h1>विदेह — XML Sitemap</h1>
            <p class="sub">First Maithili Fortnightly eJournal · Styled human view; crawlers read the raw XML.</p>
          </div>
        </header>
        <div class="wrap">
          <div class="stats">
            <div class="chip"><b><xsl:value-of select="count(s:urlset/s:url)"/></b><span>URLS · पृष्ठ</span></div>
            <div class="chip"><b><xsl:value-of select="count(s:sitemapindex/s:sitemap)"/></b><span>SITEMAPS · सूची</span></div>
            <div class="chip"><b><xsl:value-of select="count(s:urlset/s:url/image:image)"/></b><span>IMAGES · छवि</span></div>
          </div>

          <xsl:if test="s:sitemapindex/s:sitemap">
            <table>
              <thead><tr><th>#</th><th>Sitemap</th><th class="hide-sm">Last modified</th></tr></thead>
              <tbody>
                <xsl:for-each select="s:sitemapindex/s:sitemap">
                  <tr>
                    <td class="idx"><xsl:value-of select="position()"/></td>
                    <td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td>
                    <td class="hide-sm"><xsl:value-of select="s:lastmod"/></td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </xsl:if>

          <xsl:if test="s:urlset/s:url">
            <table>
              <thead><tr><th>#</th><th>URL</th><th class="hide-sm">Last modified</th><th class="hide-sm">Frequency</th><th>Priority</th><th class="hide-sm">Images</th></tr></thead>
              <tbody>
                <xsl:for-each select="s:urlset/s:url">
                  <tr>
                    <td class="idx"><xsl:value-of select="position()"/></td>
                    <td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td>
                    <td class="hide-sm"><xsl:value-of select="s:lastmod"/></td>
                    <td class="hide-sm"><span class="pill"><xsl:value-of select="s:changefreq"/></span></td>
                    <td class="prio"><xsl:value-of select="s:priority"/></td>
                    <td class="hide-sm imgs"><xsl:choose><xsl:when test="count(image:image) &gt; 0"><xsl:value-of select="count(image:image)"/></xsl:when><xsl:otherwise>—</xsl:otherwise></xsl:choose></td>
                  </tr>
                </xsl:for-each>
              </tbody>
            </table>
          </xsl:if>
          <footer>Generated for search engines · Sitemaps protocol 0.9 with optional Google Image extension.</footer>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
