/**
 * TigerEx Trading Tests
 * Test suite for TigerExTrading smart contract
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TigerExTrading", function () {
  let owner, trader1, trader2;
  let mockTokenA, mockTokenB;
  let trading;

  before(async function () {
    [owner, trader1, trader2] = await ethers.getSigners();

    // Deploy mock ERC20 tokens
    const MockToken = await ethers.getContractFactory("MockERC20");
    mockTokenA = await MockToken.deploy("Mock Token A", "MTA", 18);
    mockTokenB = await MockToken.deploy("Mock Token B", "MTB", 18);

    // Deploy trading contract
    const Trading = await ethers.getContractFactory("TigerExTrading");
    trading = await Trading.deploy();
  });

  describe("Order Management", function () {
    it("should create an order", async function () {
      await mockTokenA.connect(trader1).approve(trading.address, 1000);
      
      const tx = await trading.createOrder(
        mockTokenA.address,
        mockTokenB.address,
        100,
        200,
        true
      );
      
      const receipt = await tx.wait();
      expect(receipt.status).to.equal(1);
    });

    it("should fill an order", async function () {
      const orderId = 1;
      await mockTokenB.connect(trader2).approve(trading.address, 200);
      
      const tx = await trading.fillOrder(orderId, 100);
      const receipt = await tx.wait();
      
      expect(receipt.status).to.equal(1);
    });

    it("should cancel an order", async function () {
      const tx = await trading.cancelOrder(1);
      const receipt = await tx.wait();
      
      expect(receipt.status).to.equal(1);
    });
  });

  describe("Trading", function () {
    it("should execute a trade", async function () {
      await trading.createOrder(mockTokenA.address, mockTokenB.address, 50, 100, true);
      await trading.createOrder(mockTokenB.address, mockTokenA.address, 100, 50, false);
      
      const tx = await trading.executeTrade(2);
      const receipt = await tx.wait();
      
      expect(receipt.status).to.equal(1);
    });
  });

  describe("Liquidity", function () {
    it("should add liquidity", async function () {
      await mockTokenA.connect(trader1).approve(trading.address, 1000);
      
      const tx = await trading.addLiquidity(mockTokenA.address, mockTokenB.address, 500);
      const receipt = await tx.wait();
      
      expect(receipt.status).to.equal(1);
    });

    it("should remove liquidity", async function () {
      const tx = await trading.removeLiquidity(mockTokenA.address, mockTokenB.address, 100);
      const receipt = await tx.wait();
      
      expect(receipt.status).to.equal(1);
    });
  });
});

describe("AdminController", function () {
  let owner, user;
  let admin;

  before(async function () {
    [owner, user] = await ethers.getSigners();
    const Admin = await ethers.getContractFactory("AdminController");
    admin = await Admin.deploy();
  });

  it("should set fee tier", async function () {
    await admin.setFeeTier(user.address, 2);
    expect(await admin.feeTiers(user.address)).to.equal(2);
  });

  it("should pause contract", async function () {
    await admin.pause();
    expect(await admin.paused()).to.equal(true);
  });

  it("should unpause contract", async function () {
    await admin.unpause();
    expect(await admin.paused()).to.equal(false);
  });
});

describe("TradingEngine", function () {
  let owner, user;
  let engine;

  before(async function () {
    [owner, user] = await ethers.getSigners();
    const Engine = await ethers.getContractFactory("TradingEngine");
    engine = await Engine.deploy();
  });

  it("should process order", async function () {
    const orderData = {
      trader: user.address,
      tokenIn: ethers.constants.AddressZero,
      tokenOut: ethers.constants.AddressZero,
      amountIn: 1000,
      amountOutMin: 900
    };

    const tx = await engine.processOrder(orderData);
    const receipt = await tx.wait();
    
    expect(receipt.status).to.equal(1);
  });

  it("should set max slippage", async function () {
    await engine.setMaxSlippage(500); // 5%
    expect(await engine.maxSlippage()).to.equal(500);
  });
});export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
