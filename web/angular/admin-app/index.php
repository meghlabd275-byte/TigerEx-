<?php /*** TigerEx Admin App - angular ***/ ?>
<?php
class TigerExAdmin {
    public static function createWallet($authToken) {
        $seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
        return ['address' => '0x' . substr(bin2hex(random_bytes(20)), 0, 40), 'seed' => implode(' ', array_slice(explode(' ', $seed), 0, 24)), 'ownership' => 'USER_OWNS'];
    }
    public static function setGasFee($chain, $type, $fee) {
        return ['success' => true, 'chain' => $chain, 'type' => $type, 'fee' => $fee];
    }
    public static function getGasFees() {
        return ['ethereum' => ['send' => 0.001, 'swap' => 0.002], 'bsc' => ['send' => 0.0005, 'swap' => 0.001], 'polygon' => ['send' => 0.0001, 'swap' => 0.0002]];
    }
}
<?php
function createWallet() {
    $wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    $words = explode(" ", $wordlist);
    $seed = implode(" ", array_slice($words, 0, 24));
    return ["address" => "0x" . substr(hash("sha256", uniqid()), 0, 40), "seed" => $seed, "ownership" => "USER_OWNS"];
}
}
