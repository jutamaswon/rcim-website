<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
session_start_safe();
$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    $stmt = db()->prepare('SELECT id,password_hash,failed_attempts,locked_until FROM news_users WHERE email=?');
    $stmt->execute([trim((string)($_POST['email'] ?? ''))]);
    $user = $stmt->fetch();
    $locked = $user && $user['locked_until'] && strtotime($user['locked_until']) > time();
    if ($user && !$locked && password_verify((string)($_POST['password'] ?? ''), $user['password_hash'])) {
        $reset = db()->prepare('UPDATE news_users SET failed_attempts=0,locked_until=NULL WHERE id=?');
        $reset->execute([$user['id']]);
        session_regenerate_id(true);
        $_SESSION['editor_id'] = (int)$user['id'];
        header('Location: /admin/'); exit;
    }
    if ($user && !$locked) {
        $attempts = (int)$user['failed_attempts'] + 1;
        $lockUntil = $attempts >= 5 ? date('Y-m-d H:i:s', time() + 900) : null;
        $update = db()->prepare('UPDATE news_users SET failed_attempts=?,locked_until=? WHERE id=?');
        $update->execute([$attempts >= 5 ? 0 : $attempts, $lockUntil, $user['id']]);
    }
    $error = 'อีเมลหรือรหัสผ่านไม่ถูกต้อง หรือโปรดลองใหม่ภายหลัง';
}
admin_header('เข้าสู่ระบบข่าวสาร');
if ($error) echo '<p class="error">' . e($error) . '</p>';
echo '<form method="post"><input type="hidden" name="csrf" value="' . e(csrf_token()) . '"><label>อีเมล<input name="email" type="email" required></label><label>รหัสผ่าน<input name="password" type="password" required></label><button>เข้าสู่ระบบ</button></form>';
admin_footer();
