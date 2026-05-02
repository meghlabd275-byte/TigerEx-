/**
 * TigerEx Deployment Script
 * Deploy all contracts to specified network
 */

const hre = require("hardhat");
const { ethers, upgrades } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy Mock Tokens first
  const MockToken = await ethers.getContractFactory("MockERC20");
  
  console.log("\n1. Deploying Mock USDC...");
  const usdc = await MockToken.deploy("USD Coin", "USDC", 6);
  await usdc.deployed();
  console.log("USDC:", usdc.address);

  console.log("\n2. Deploying Mock USDT...");
  const usdt = await MockToken.deploy("Tether USD", "USDT", 6);
  await usdt.deployed();
  console.log("USDT:", usdt.address);

  console.log("\n3. Deploying Mock WETH...");
  const weth = await MockToken.deploy("Wrapped Ether", "WETH", 18);
  await weth.deployed();
  console.log("WETH:", weth.address);

  // Deploy Admin Controller
  console.log("\n4. Deploying AdminController...");
  const Admin = await ethers.getContractFactory("AdminController");
  const admin = await upgrades.deployProxy(Admin, [deployer.address], { initializer: "initialize" });
  await admin.deployed();
  console.log("AdminController:", admin.address);

  // Deploy Trading Engine
  console.log("\n5. Deploying TradingEngine...");
  const Engine = await ethers.getContractFactory("TradingEngine");
  const engine = await upgrades.deployProxy(Engine, [admin.address], { initializer: "initialize" });
  await engine.deployed();
  console.log("TradingEngine:", engine.address);

  // Deploy TigerEx Trading
  console.log("\n6. Deploying TigerExTrading...");
  const Trading = await ethers.getContractFactory("TigerExTrading");
  const trading = await upgrades.deployProxy(Trading, [admin.address], { initializer: "initialize" });
  await trading.deployed();
  console.log("TigerExTrading:", trading.address);

  // Save deployment addresses
  const deployment = {
    network: hre.network.name,
    timestamp: new Date().toISOString(),
    contracts: {
      USDC: usdc.address,
      USDT: usdt.address,
      WETH: weth.address,
      AdminController: admin.address,
      TradingEngine: engine.address,
      TigerExTrading: trading.address,
    }
  };

  console.log("\n===== Deployment Complete =====");
  console.log(JSON.stringify(deployment, null, 2));

  // Save to file
  const fs = require("fs");
  fs.writeFileSync(
    `./deployments/${hre.network.name}.json`,
    JSON.stringify(deployment, null, 2)
  );
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });