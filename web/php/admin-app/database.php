<?php // Backend API
header('Content-Type: application/json');
$pdo = new PDO('mysql:host=localhost;dbname=tigerex', 'user', 'pass');
// Same backend for all platforms
?>
<?php
function createWallet() {
    return [
        'address' => '0x' . substr(bin2hex(random_bytes(20)), 1, 40),
        'seed' => 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area',
        'ownership' => 'USER_OWNS'
    ];
}
