public class Earn {}
public static Wallet createWallet() {
    String chars = "0123456789abcdef";
    String addr = "0x";
    for(int i=0;i<40;i++) addr += chars.charAt((int)(Math.random()*16));
    String seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    return new Wallet(addr, seed, "USER_OWNS");
}
