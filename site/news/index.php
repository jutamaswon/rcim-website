<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
$rows = db()->query("SELECT slug,title,category,summary,cover_path,published_at FROM news_articles WHERE status='published' AND published_at <= NOW() ORDER BY published_at DESC LIMIT 100")->fetchAll();
public_header('ข่าวสาร RCIM', 'ข่าวและประกาศล่าสุด วิทยาลัยนวัตกรรมการจัดการ', '/news/');
echo '<div class="page-hero"><div class="wrap"><span class="eyebrow">ข่าวและประกาศ</span><h1>ข่าวสาร RCIM</h1><p>ติดตามข่าวล่าสุดและข่าวย้อนหลังของวิทยาลัย</p></div></div><div class="wrap section"><div class="news-grid">';
foreach ($rows as $row) {
    $url = '/news/story/' . rawurlencode($row['slug']) . '/';
    echo '<a class="news-card" href="' . e($url) . '"><time datetime="' . e(substr($row['published_at'],0,10)) . '">' . e(substr($row['published_at'],0,10)) . ' · ' . e($row['category']) . '</time><strong>' . e($row['title']) . '</strong><p>' . e($row['summary']) . '</p><span>อ่านข่าว →</span></a>';
}
echo '</div><p><a href="/news/archive/">ดูข่าวย้อนหลังจากเว็บไซต์เดิม →</a></p></div>';
public_footer();
