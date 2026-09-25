<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: public, max-age=300');
$rows = db()->query("SELECT slug,title,category,summary,cover_path,attachment_path,attachment_label,published_at FROM news_articles WHERE status='published' AND published_at <= NOW() ORDER BY published_at DESC LIMIT 50")->fetchAll();
echo json_encode(['news'=>$rows],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
