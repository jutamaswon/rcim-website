<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
header('Content-Type: application/xml; charset=utf-8');
header('Cache-Control: public, max-age=3600');
echo '<?xml version="1.0" encoding="UTF-8"?>';
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
$rows = db()->query("SELECT slug,updated_at FROM news_articles WHERE status='published' AND published_at <= NOW() ORDER BY published_at DESC");
foreach ($rows as $row) echo '<url><loc>https://www.rcim.in.th/news/story/' . htmlspecialchars($row['slug'], ENT_XML1) . '/</loc><lastmod>' . substr($row['updated_at'],0,10) . '</lastmod></url>';
echo '</urlset>';
