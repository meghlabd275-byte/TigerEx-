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
