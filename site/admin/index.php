<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
require_editor();
$articles = db()->query('SELECT id,title,status,published_at,updated_at FROM news_articles ORDER BY updated_at DESC LIMIT 200')->fetchAll();
admin_header('จัดการข่าว');
echo '<p><a class="button" href="/admin/edit.php">+ เพิ่มข่าว</a> <a href="/news/">ดูหน้าเว็บไซต์</a></p><table><thead><tr><th>ชื่อข่าว</th><th>สถานะ</th><th>วันที่เผยแพร่</th></tr></thead><tbody>';
foreach ($articles as $row) echo '<tr><td><a href="/admin/edit.php?id=' . (int)$row['id'] . '">' . e($row['title']) . '</a></td><td>' . e($row['status']) . '</td><td>' . e($row['published_at']) . '</td></tr>';
echo '</tbody></table><form method="post" action="/admin/logout.php"><input type="hidden" name="csrf" value="' . e(csrf_token()) . '"><button class="secondary">ออกจากระบบ</button></form>';
admin_footer();
