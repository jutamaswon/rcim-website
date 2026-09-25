<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
session_start_safe();
$exists = (int)db()->query('SELECT COUNT(*) FROM news_users')->fetchColumn() > 0;
if ($exists) { http_response_code(404); exit('Setup is closed.'); }
$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_csrf();
    $email = trim((string)($_POST['email'] ?? ''));
    $password = (string)($_POST['password'] ?? '');
    if (strlen((string)$config['setup_key']) < 20 || $config['setup_key'] === 'CHANGE_TO_A_LONG_RANDOM_PHRASE') $error = 'Set a long random setup key in config.php first.';
    elseif (!hash_equals((string)$config['setup_key'], (string)($_POST['setup_key'] ?? ''))) $error = 'Setup key is incorrect.';
    elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) $error = 'Enter a valid email.';
    elseif (strlen($password) < 12) $error = 'Use at least 12 characters for the password.';
    else {
        $stmt = db()->prepare('INSERT INTO news_users (email,password_hash) VALUES (?,?)');
        $stmt->execute([$email, password_hash($password, PASSWORD_DEFAULT)]);
        header('Location: /admin/login.php'); exit;
    }
}
admin_header('สร้างบัญชีผู้ดูแลข่าว');
if ($error) echo '<p class="error">' . e($error) . '</p>';
echo '<form method="post"><input type="hidden" name="csrf" value="' . e(csrf_token()) . '"><label>Setup key<input name="setup_key" type="password" required></label><label>อีเมล<input name="email" type="email" required></label><label>รหัสผ่าน (อย่างน้อย 12 ตัวอักษร)<input name="password" type="password" minlength="12" required></label><button>สร้างบัญชี</button></form>';
admin_footer();
