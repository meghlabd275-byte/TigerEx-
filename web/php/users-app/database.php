<?php // Database connection
$host = 'localhost';
$db = 'tigerex';
$user = 'tigerex_user';
$pass = 'password';
try {
    $pdo = new PDO("mysql:host=$host;dbname=$db", $user, $pass);
} catch(PDOException $e) { die($e->getMessage()); }
session_start();
// All apps connect to same MySQL database
?>
