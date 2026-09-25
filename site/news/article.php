<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
$slug = (string)($_GET['slug'] ?? '');
if (!preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/', $slug)) { http_response_code(404); exit('Not found.'); }
$stmt = db()->prepare("SELECT title,category,summary,body,cover_path,attachment_path,attachment_label,published_at,updated_at FROM news_articles WHERE slug=? AND status='published' AND published_at <= NOW()");
$stmt->execute([$slug]);
$row = $stmt->fetch();
if (!$row) { http_response_code(404); exit('Not found.'); }
$canonical = '/news/story/' . $slug . '/';
public_header($row['title'], mb_substr($row['summary'],0,155), $canonical);
echo '<div class="page-hero"><div class="wrap"><span class="eyebrow">ข่าวสาร RCIM</span><h1>' . e($row['title']) . '</h1><time datetime="' . e(substr($row['published_at'],0,10)) . '">' . e(substr($row['published_at'],0,10)) . '</time></div></div><div class="wrap content-layout"><article class="prose">';
if ($row['cover_path']) echo '<img src="' . e($row['cover_path']) . '" alt="ภาพประกอบข่าว ' . e($row['title']) . '" width="1200" loading="lazy">';
echo '<p class="lead">' . e($row['summary']) . '</p>';
foreach (preg_split('/\R\s*\R/u', trim($row['body'])) as $paragraph) echo '<p>' . nl2br(e($paragraph), false) . '</p>';
if ($row['attachment_path']) echo '<p><a href="' . e($row['attachment_path']) . '">ดาวน์โหลดเอกสาร: ' . e($row['attachment_label'] ?: 'PDF') . '</a></p>';
echo '<p><a href="/news/">← ข่าวสารทั้งหมด</a></p></article></div>';
$schema = ['@context'=>'https://schema.org','@type'=>'NewsArticle','headline'=>$row['title'],'description'=>$row['summary'],'datePublished'=>$row['published_at'],'dateModified'=>$row['updated_at'],'mainEntityOfPage'=>'https://www.rcim.in.th'.$canonical,'publisher'=>['@type'=>'CollegeOrUniversity','name'=>'วิทยาลัยนวัตกรรมการจัดการ']];
echo '<script type="application/ld+json">' . str_replace('<','\\u003c',json_encode($schema,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES)) . '</script>';
public_footer();
