<?php
require dirname(__DIR__) . '/includes/bootstrap.php';
require_editor();
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }
check_csrf();
$_SESSION = [];
session_destroy();
header('Location: /admin/login.php');
