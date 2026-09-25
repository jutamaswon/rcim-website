<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
require_editor();
$id = max(0, (int)($_GET['id'] ?? $_POST['id'] ?? 0));
$article = ['slug'=>'','title'=>'','category'=>'ข่าวสาร','summary'=>'','body'=>'','cover_path'=>'','attachment_path'=>'','attachment_label'=>'','status'=>'draft','published_at'=>''];
if ($id) {
    $stmt = db()->prepare('SELECT * FROM news_articles WHERE id=?');
    $stmt->execute([$id]);
    $article = $stmt->fetch();
    if (!$article) { http_response_code(404); exit('Article not found.'); }
}
$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    foreach (['slug','title','category','summary','body','status','published_at'] as $field) $article[$field] = trim((string)($_POST[$field] ?? ''));
    $article['slug'] = strtolower($article['slug']);
    if ($article['slug'] === '') $article['slug'] = $id ? (string)$article['slug'] : 'news-' . date('Ymd') . '-' . bin2hex(random_bytes(3));
    if (!preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/', $article['slug'])) $error = 'Slug must contain English letters, numbers, and hyphens only.';
    elseif ($article['title'] === '' || $article['summary'] === '' || $article['body'] === '' || $article['category'] === '') $error = 'กรุณากรอกชื่อข่าว หมวดหมู่ สรุป และเนื้อหา';
    elseif (!in_array($article['status'], ['draft','published'], true)) $error = 'Invalid status.';
    elseif (strlen($article['title']) > 255 || strlen($article['slug']) > 190 || strlen($article['category']) > 100) $error = 'Title, category, or slug is too long.';
    $date = $article['published_at'] !== '' ? DateTime::createFromFormat('Y-m-d\TH:i', $article['published_at']) : new DateTime();
    if (!$date) $error = 'Invalid publication date.';
    if (!$error && !empty($_FILES['cover']['name'])) {
        $file = $_FILES['cover'];
        if ($file['error'] !== UPLOAD_ERR_OK || $file['size'] > 8 * 1024 * 1024) $error = 'Image must be smaller than 8 MB.';
        else {
            $info = @getimagesize($file['tmp_name']);
            if (!$info || !in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_WEBP], true)) $error = 'Use a JPG, PNG, or WebP image.';
            elseif ($info[0] > 6000 || $info[1] > 6000) $error = 'Image dimensions are too large.';
            elseif (!function_exists('imagewebp')) $error = 'PHP GD WebP support is required for image upload.';
            else {
                $source = match ($info[2]) {
                    IMAGETYPE_JPEG => imagecreatefromjpeg($file['tmp_name']),
                    IMAGETYPE_PNG => imagecreatefrompng($file['tmp_name']),
                    IMAGETYPE_WEBP => imagecreatefromwebp($file['tmp_name']),
                };
                if (!$source) $error = 'Could not read image.';
                else {
                    $width = imagesx($source); $height = imagesy($source);
                    $newWidth = min(1200, $width);
                    $newHeight = max(1, (int)round($height * $newWidth / $width));
                    $resized = imagecreatetruecolor($newWidth, $newHeight);
                    imagealphablending($resized, false); imagesavealpha($resized, true);
                    imagecopyresampled($resized, $source, 0, 0, 0, 0, $newWidth, $newHeight, $width, $height);
                    $dir = dirname(__DIR__) . '/media/news';
                    if (!is_dir($dir)) mkdir($dir, 0755, true);
                    $name = bin2hex(random_bytes(16)) . '.webp';
                    if (!imagewebp($resized, $dir . '/' . $name, 78)) $error = 'Could not save image.';
                    else $article['cover_path'] = '/media/news/' . $name;
                    imagedestroy($resized); imagedestroy($source);
                }
            }
        }
    }
    if (!$error && !empty($_FILES['attachment']['name'])) {
        $file = $_FILES['attachment'];
        if ($file['error'] !== UPLOAD_ERR_OK || $file['size'] > 20 * 1024 * 1024) $error = 'PDF must be smaller than 20 MB.';
        else {
            $probe = file_get_contents($file['tmp_name'], false, null, 0, 4);
            if ($probe !== '%PDF') $error = 'Only PDF attachments are supported.';
            else {
                $dir = dirname(__DIR__) . '/media/news/docs';
                if (!is_dir($dir)) mkdir($dir, 0755, true);
                $name = bin2hex(random_bytes(16)) . '.pdf';
                if (!move_uploaded_file($file['tmp_name'], $dir . '/' . $name)) $error = 'Could not save PDF.';
                else {
                    $article['attachment_path'] = '/media/news/docs/' . $name;
                    $article['attachment_label'] = basename((string)$file['name']);
                }
            }
        }
    }
    if (!$error) {
        try {
            $published = $article['status'] === 'published' ? $date->format('Y-m-d H:i:s') : null;
            if ($id) {
                $stmt = db()->prepare('UPDATE news_articles SET slug=?,title=?,category=?,summary=?,body=?,cover_path=?,attachment_path=?,attachment_label=?,status=?,published_at=? WHERE id=?');
                $stmt->execute([$article['slug'],$article['title'],$article['category'],$article['summary'],$article['body'],$article['cover_path'] ?: null,$article['attachment_path'] ?: null,$article['attachment_label'] ?: null,$article['status'],$published,$id]);
            } else {
                $stmt = db()->prepare('INSERT INTO news_articles (slug,title,category,summary,body,cover_path,attachment_path,attachment_label,status,published_at) VALUES (?,?,?,?,?,?,?,?,?,?)');
                $stmt->execute([$article['slug'],$article['title'],$article['category'],$article['summary'],$article['body'],$article['cover_path'] ?: null,$article['attachment_path'] ?: null,$article['attachment_label'] ?: null,$article['status'],$published]);
            }
            header('Location: /admin/'); exit;
        } catch (PDOException $exception) {
            if ($exception->getCode() === '23000') $error = 'This slug is already in use.';
            else throw $exception;
        }
    }
}
admin_header($id ? 'แก้ไขข่าว' : 'เพิ่มข่าว');
if ($error) echo '<p class="error">' . e($error) . '</p>';
echo '<p><a href="/admin/">← กลับไปรายการข่าว</a></p><form method="post" enctype="multipart/form-data"><input type="hidden" name="csrf" value="' . e(csrf_token()) . '"><input type="hidden" name="id" value="' . $id . '">';
echo '<label>ชื่อข่าว<input name="title" required maxlength="255" value="' . e($article['title']) . '"></label>';
echo '<label>URL slug ภาษาอังกฤษ (เว้นว่างได้ ระบบจะสร้างให้)<input name="slug" pattern="[a-z0-9]+(-[a-z0-9]+)*" maxlength="190" value="' . e($article['slug']) . '"><small>ตัวอย่าง: student-registration-2026</small></label>';
echo '<label>หมวดหมู่<input name="category" required maxlength="100" value="' . e($article['category']) . '"></label>';
echo '<label>สรุปข่าว<textarea name="summary" rows="3" required>' . e($article['summary']) . '</textarea></label>';
echo '<label>เนื้อหาข่าว (ข้อความธรรมดา เว้นบรรทัดเพื่อขึ้นย่อหน้า)<textarea name="body" rows="15" required>' . e($article['body']) . '</textarea></label>';
echo '<label>ภาพปก (JPG, PNG หรือ WebP ไม่เกิน 8 MB)<input name="cover" type="file" accept="image/jpeg,image/png,image/webp"></label>';
echo '<label>เอกสารแนบ PDF (ไม่เกิน 20 MB)<input name="attachment" type="file" accept="application/pdf"></label>';
if ($article['cover_path']) echo '<img class="preview" src="' . e($article['cover_path']) . '" alt="ภาพปกปัจจุบัน">';
if ($article['attachment_path']) echo '<p>เอกสารปัจจุบัน: <a href="' . e($article['attachment_path']) . '">' . e($article['attachment_label']) . '</a></p>';
$localDate = $article['published_at'] ? date('Y-m-d\TH:i', strtotime($article['published_at'])) : date('Y-m-d\TH:i');
echo '<label>วันเวลาเผยแพร่<input name="published_at" type="datetime-local" value="' . e($localDate) . '"></label><label>สถานะ<select name="status"><option value="draft"' . ($article['status']==='draft'?' selected':'') . '>ฉบับร่าง</option><option value="published"' . ($article['status']==='published'?' selected':'') . '>เผยแพร่</option></select></label><button>บันทึกข่าว</button></form>';
admin_footer();
