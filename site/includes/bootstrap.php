<?php
declare(strict_types=1);

$configFile = dirname(__DIR__) . '/config.php';
if (!is_file($configFile)) {
    http_response_code(503);
    exit('News is not configured yet.');
}
$config = require $configFile;
date_default_timezone_set('Asia/Bangkok');

function db(): PDO {
    global $config;
    static $pdo = null;
    if ($pdo === null) {
        $dsn = 'mysql:host=' . $config['db_host'] . ';dbname=' . $config['db_name'] . ';charset=utf8mb4';
        try {
            $pdo = new PDO($dsn, $config['db_user'], $config['db_password'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ]);
            $pdo->exec("SET time_zone = '+07:00'");
        } catch (PDOException $exception) {
            error_log('RCIM news database connection failed.');
            http_response_code(503);
            exit('News is temporarily unavailable.');
        }
    }
    return $pdo;
}

function e(?string $value): string {
    return htmlspecialchars($value ?? '', ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function session_start_safe(): void {
    if (session_status() === PHP_SESSION_ACTIVE) return;
    session_name('rcim_news_admin');
    session_set_cookie_params([
        'httponly' => true,
        'secure' => !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off',
        'samesite' => 'Lax',
        'path' => '/admin',
    ]);
    session_start();
}

function csrf_token(): string {
    session_start_safe();
    if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(32));
    return $_SESSION['csrf'];
}

function check_csrf(): void {
    session_start_safe();
    if (!hash_equals($_SESSION['csrf'] ?? '', (string)($_POST['csrf'] ?? ''))) {
        http_response_code(403);
        exit('Invalid form token.');
    }
}

function require_editor(): void {
    session_start_safe();
    if (empty($_SESSION['editor_id'])) {
        header('Location: /admin/login.php');
        exit;
    }
}

function admin_header(string $title): void {
    echo '<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>' . e($title) . ' | RCIM</title><link rel="stylesheet" href="/assets/admin.css"></head><body><header><a href="/admin/">RCIM · ข่าวสาร</a></header><main><h1>' . e($title) . '</h1>';
}

function admin_footer(): void { echo '</main></body></html>'; }

function public_header(string $title, string $description, string $canonical): void {
    echo '<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' . e($title) . ' | RCIM</title><meta name="description" content="' . e($description) . '"><link rel="canonical" href="https://www.rcim.in.th' . e($canonical) . '"><link rel="stylesheet" href="/assets/site.css"></head><body><a class="skip" href="#main">ข้ามไปยังเนื้อหา</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="/"><img class="brand-mark-image" src="/media/2022/06/Logo-RCIM2019-TH-480.webp" width="52" height="52" alt=""><span><strong>RCIM</strong><small>วิทยาลัยนวัตกรรมการจัดการ</small></span></a><nav style="display:flex"><a href="/">หน้าหลัก</a><a href="/news/">ข่าวสาร</a><a href="/news/archive/">ข่าวย้อนหลัง</a></nav></div></header><main id="main">';
}

function public_footer(): void { echo '</main><footer><div class="wrap">วิทยาลัยนวัตกรรมการจัดการ · มทร.รัตนโกสินทร์</div></footer></body></html>'; }
