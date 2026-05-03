class PlatformControlService {
  constructor() {
    this.globalState = {
      halted: false,
      paymentsPaused: false,
      withdrawalsPaused: false,
      depositsPaused: false,
      reason: null,
      updatedAt: new Date().toISOString(),
      updatedBy: 'system',
    };
  }

  getState() {
    return { ...this.globalState };
  }

  updateState(partial, actor = 'system') {
    const allowed = ['halted', 'paymentsPaused', 'withdrawalsPaused', 'depositsPaused', 'reason'];
    const sanitized = {};

    for (const key of allowed) {
      if (Object.prototype.hasOwnProperty.call(partial, key) && partial[key] !== undefined) {
        sanitized[key] = partial[key];
      }
    }

    this.globalState = {
      ...this.globalState,
      ...sanitized,
      updatedBy: actor,
      updatedAt: new Date().toISOString(),
    };
    return this.getState();
  }

  isPaymentsBlocked() {
    return this.globalState.halted || this.globalState.paymentsPaused;
  }
}

module.exports = new PlatformControlService();
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
