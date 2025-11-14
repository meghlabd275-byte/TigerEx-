const mongoose = require('mongoose');
const TradingContract = require('../models/TradingContract');
const MarketMakerBot = require('../models/MarketMakerBot');
const User = require('../models/User');
const LiquidityPool = require('../models/LiquidityPool');
const OrderBook = require('../models/OrderBook');
const TradeExecution = require('../models/TradeExecution');
const CustomToken = require('../models/CustomToken');
const IOU = require('../models/IOU');
const BlockchainDeployment = require('../models/BlockchainDeployment');
const AuditLog = require('../models/AuditLog');
const { validationResult } = require('express-validator');

class AdminTradingController {
  // SPOT TRADING MANAGEMENT
  async createSpotContract(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        symbol,
        baseAsset,
        quoteAsset,
        baseAssetPrecision,
        quoteAssetPrecision,
        minNotional,
        minQty,
        maxQty,
        tickSize,
        stepSize,
        isActive,
        description,
        tradingRules
      } = req.body;

      // Check if contract already exists
      const existingContract = await TradingContract.findOne({
        symbol,
        type: 'spot',
        isDeleted: false
      });

      if (existingContract) {
        return res.status(400).json({
          success: false,
          message: 'Spot contract already exists'
        });
      }

      const contract = new TradingContract({
        symbol,
        type: 'spot',
        baseAsset,
        quoteAsset,
        baseAssetPrecision,
        quoteAssetPrecision,
        minNotional,
        minQty,
        maxQty,
        tickSize,
        stepSize,
        isActive: isActive !== undefined ? isActive : true,
        description,
        tradingRules,
        createdBy: req.user.id
      });

      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_spot_contract',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol, baseAsset, quoteAsset },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Spot contract created successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error creating spot contract:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async pauseSpotTrading(req, res) {
    try {
      const { contractId } = req.params;

      const contract = await TradingContract.findOne({
        _id: contractId,
        type: 'spot',
        isDeleted: false
      });

      if (!contract) {
        return res.status(404).json({
          success: false,
          message: 'Spot contract not found'
        });
      }

      contract.isActive = false;
      contract.status = 'paused';
      contract.updatedBy = req.user.id;
      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'pause_spot_trading',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol: contract.symbol },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Spot trading paused successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error pausing spot trading:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async resumeSpotTrading(req, res) {
    try {
      const { contractId } = req.params;

      const contract = await TradingContract.findOne({
        _id: contractId,
        type: 'spot',
        isDeleted: false
      });

      if (!contract) {
        return res.status(404).json({
          success: false,
          message: 'Spot contract not found'
        });
      }

      contract.isActive = true;
      contract.status = 'active';
      contract.updatedBy = req.user.id;
      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'resume_spot_trading',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol: contract.symbol },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Spot trading resumed successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error resuming spot trading:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async deleteSpotContract(req, res) {
    try {
      const { contractId } = req.params;

      const contract = await TradingContract.findOne({
        _id: contractId,
        type: 'spot',
        isDeleted: false
      });

      if (!contract) {
        return res.status(404).json({
          success: false,
          message: 'Spot contract not found'
        });
      }

      contract.isDeleted = true;
      contract.isActive = false;
      contract.status = 'deleted';
      contract.deletedAt = new Date();
      contract.updatedBy = req.user.id;
      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'delete_spot_contract',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol: contract.symbol },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Spot contract deleted successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error deleting spot contract:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // FUTURES TRADING MANAGEMENT
  async createFuturesContract(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        symbol,
        baseAsset,
        quoteAsset,
        contractType, // 'perpetual' or 'cross'
        contractSize,
        settlementType,
        maxLeverage,
        minLeverage,
        maintenanceMarginRatio,
        initialMarginRatio,
        fundingRateInterval,
        baseAssetPrecision,
        quoteAssetPrecision,
        minNotional,
        minQty,
        maxQty,
        tickSize,
        stepSize,
        isActive,
        description,
        tradingRules
      } = req.body;

      // Check if contract already exists
      const existingContract = await TradingContract.findOne({
        symbol,
        type: 'futures',
        contractType,
        isDeleted: false
      });

      if (existingContract) {
        return res.status(400).json({
          success: false,
          message: 'Futures contract already exists'
        });
      }

      const contract = new TradingContract({
        symbol,
        type: 'futures',
        contractType,
        baseAsset,
        quoteAsset,
        contractSize,
        settlementType,
        maxLeverage,
        minLeverage,
        maintenanceMarginRatio,
        initialMarginRatio,
        fundingRateInterval,
        baseAssetPrecision,
        quoteAssetPrecision,
        minNotional,
        minQty,
        maxQty,
        tickSize,
        stepSize,
        isActive: isActive !== undefined ? isActive : true,
        description,
        tradingRules,
        createdBy: req.user.id
      });

      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_futures_contract',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol, contractType, baseAsset, quoteAsset },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Futures contract created successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error creating futures contract:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async createPerpetualContract(req, res) {
    try {
      const contractData = {
        ...req.body,
        contractType: 'perpetual',
        settlementType: 'linear'
      };

      return await this.createFuturesContract({ ...req, body: contractData }, res);

    } catch (error) {
      console.error('Error creating perpetual contract:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async createCrossFuturesContract(req, res) {
    try {
      const contractData = {
        ...req.body,
        contractType: 'cross',
        settlementType: 'inverse'
      };

      return await this.createFuturesContract({ ...req, body: contractData }, res);

    } catch (error) {
      console.error('Error creating cross futures contract:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // MARGIN TRADING MANAGEMENT
  async createMarginContract(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        symbol,
        baseAsset,
        quoteAsset,
        marginType, // 'isolated' or 'cross'
        maxLeverage,
        minLeverage,
        interestRate,
        marginRatio,
        liquidationThreshold,
        baseAssetPrecision,
        quoteAssetPrecision,
        minNotional,
        minQty,
        maxQty,
        tickSize,
        stepSize,
        isActive,
        description,
        tradingRules
      } = req.body;

      // Check if contract already exists
      const existingContract = await TradingContract.findOne({
        symbol,
        type: 'margin',
        marginType,
        isDeleted: false
      });

      if (existingContract) {
        return res.status(400).json({
          success: false,
          message: 'Margin contract already exists'
        });
      }

      const contract = new TradingContract({
        symbol,
        type: 'margin',
        marginType,
        baseAsset,
        quoteAsset,
        maxLeverage,
        minLeverage,
        interestRate,
        marginRatio,
        liquidationThreshold,
        baseAssetPrecision,
        quoteAssetPrecision,
        minNotional,
        minQty,
        maxQty,
        tickSize,
        stepSize,
        isActive: isActive !== undefined ? isActive : true,
        description,
        tradingRules,
        createdBy: req.user.id
      });

      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_margin_contract',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol, marginType, baseAsset, quoteAsset },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Margin contract created successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error creating margin contract:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // OPTIONS TRADING MANAGEMENT
  async createOptionsContract(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        symbol,
        underlyingAsset,
        optionType, // 'call' or 'put'
        strikePrice,
        expirationDate,
        contractSize,
        settlementType,
        exerciseType, // 'european' or 'american'
        baseAssetPrecision,
        quoteAssetPrecision,
        minNotional,
        minQty,
        maxQty,
        tickSize,
        stepSize,
        isActive,
        description,
        tradingRules
      } = req.body;

      // Check if contract already exists
      const existingContract = await TradingContract.findOne({
        symbol,
        type: 'options',
        optionType,
        strikePrice,
        expirationDate,
        isDeleted: false
      });

      if (existingContract) {
        return res.status(400).json({
          success: false,
          message: 'Options contract already exists'
        });
      }

      const contract = new TradingContract({
        symbol,
        type: 'options',
        underlyingAsset,
        optionType,
        strikePrice,
        expirationDate: new Date(expirationDate),
        contractSize,
        settlementType,
        exerciseType,
        baseAssetPrecision,
        quoteAssetPrecision,
        minNotional,
        minQty,
        maxQty,
        tickSize,
        stepSize,
        isActive: isActive !== undefined ? isActive : true,
        description,
        tradingRules,
        createdBy: req.user.id
      });

      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_options_contract',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol, optionType, strikePrice, expirationDate },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Options contract created successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error creating options contract:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // GRID TRADING MANAGEMENT
  async createGridTradingBot(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        name,
        symbol,
        strategy,
        gridCount,
        upperPrice,
        lowerPrice,
        investmentAmount,
        orderType,
        isActive,
        description,
        settings
      } = req.body;

      const bot = new MarketMakerBot({
        name,
        type: 'grid',
        symbol,
        strategy,
        gridCount,
        upperPrice,
        lowerPrice,
        investmentAmount,
        orderType,
        isActive: isActive !== undefined ? isActive : true,
        description,
        settings,
        createdBy: req.user.id
      });

      await bot.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_grid_bot',
        targetId: bot._id,
        targetType: 'MarketMakerBot',
        details: { name, symbol, strategy },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Grid trading bot created successfully',
        data: bot
      });

    } catch (error) {
      console.error('Error creating grid trading bot:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // COPY TRADING MANAGEMENT
  async createCopyTradingSystem(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        name,
        description,
        minFollowAmount,
        maxFollowAmount,
        feeRate,
        profitShare,
        riskLevel,
        isActive,
        settings
      } = req.body;

      // Create copy trading system configuration
      const copyTradingConfig = {
        name,
        type: 'copy_trading',
        description,
        minFollowAmount,
        maxFollowAmount,
        feeRate,
        profitShare,
        riskLevel,
        isActive: isActive !== undefined ? isActive : true,
        settings,
        createdBy: req.user.id
      };

      // Save to database (you might want to create a specific model for this)
      const system = await TradingContract.create({
        ...copyTradingConfig,
        symbol: 'COPY_TRADING',
        baseAsset: 'VARIOUS',
        quoteAsset: 'USDT',
        type: 'copy_trading'
      });

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_copy_trading_system',
        targetId: system._id,
        targetType: 'TradingContract',
        details: { name, minFollowAmount, feeRate },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Copy trading system created successfully',
        data: system
      });

    } catch (error) {
      console.error('Error creating copy trading system:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // MARKET MAKING BOT MANAGEMENT
  async createMarketMakerBot(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        name,
        symbol,
        strategy,
        orderBookDepth,
        spreadPercentage,
        inventoryTarget,
        maxOrderSize,
        minOrderSize,
        rebalanceThreshold,
        isActive,
        description,
        settings
      } = req.body;

      const bot = new MarketMakerBot({
        name,
        type: 'market_maker',
        symbol,
        strategy,
        orderBookDepth,
        spreadPercentage,
        inventoryTarget,
        maxOrderSize,
        minOrderSize,
        rebalanceThreshold,
        isActive: isActive !== undefined ? isActive : true,
        description,
        settings,
        createdBy: req.user.id
      });

      await bot.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_market_maker_bot',
        targetId: bot._id,
        targetType: 'MarketMakerBot',
        details: { name, symbol, strategy },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Market maker bot created successfully',
        data: bot
      });

    } catch (error) {
      console.error('Error creating market maker bot:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async pauseMarketMakerBot(req, res) {
    try {
      const { botId } = req.params;

      const bot = await MarketMakerBot.findById(botId);
      if (!bot) {
        return res.status(404).json({
          success: false,
          message: 'Market maker bot not found'
        });
      }

      bot.isActive = false;
      bot.status = 'paused';
      bot.updatedBy = req.user.id;
      await bot.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'pause_market_maker_bot',
        targetId: bot._id,
        targetType: 'MarketMakerBot',
        details: { name: bot.name, symbol: bot.symbol },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Market maker bot paused successfully',
        data: bot
      });

    } catch (error) {
      console.error('Error pausing market maker bot:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async resumeMarketMakerBot(req, res) {
    try {
      const { botId } = req.params;

      const bot = await MarketMakerBot.findById(botId);
      if (!bot) {
        return res.status(404).json({
          success: false,
          message: 'Market maker bot not found'
        });
      }

      bot.isActive = true;
      bot.status = 'active';
      bot.updatedBy = req.user.id;
      await bot.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'resume_market_maker_bot',
        targetId: bot._id,
        targetType: 'MarketMakerBot',
        details: { name: bot.name, symbol: bot.symbol },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Market maker bot resumed successfully',
        data: bot
      });

    } catch (error) {
      console.error('Error resuming market maker bot:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async deleteMarketMakerBot(req, res) {
    try {
      const { botId } = req.params;

      const bot = await MarketMakerBot.findById(botId);
      if (!bot) {
        return res.status(404).json({
          success: false,
          message: 'Market maker bot not found'
        });
      }

      bot.isDeleted = true;
      bot.isActive = false;
      bot.status = 'deleted';
      bot.deletedAt = new Date();
      bot.updatedBy = req.user.id;
      await bot.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'delete_market_maker_bot',
        targetId: bot._id,
        targetType: 'MarketMakerBot',
        details: { name: bot.name, symbol: bot.symbol },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Market maker bot deleted successfully',
        data: bot
      });

    } catch (error) {
      console.error('Error deleting market maker bot:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // IOU SYSTEM MANAGEMENT
  async createIOU(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        issuerId,
        holderId,
        amount,
        currency,
        description,
        maturityDate,
        interestRate,
        collateral,
        isActive
      } = req.body;

      const iou = new IOU({
        issuerId,
        holderId,
        amount,
        currency,
        description,
        maturityDate: maturityDate ? new Date(maturityDate) : null,
        interestRate,
        collateral,
        isActive: isActive !== undefined ? isActive : true,
        createdBy: req.user.id
      });

      await iou.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_iou',
        targetId: iou._id,
        targetType: 'IOU',
        details: { issuerId, holderId, amount, currency },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'IOU created successfully',
        data: iou
      });

    } catch (error) {
      console.error('Error creating IOU:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async pauseIOU(req, res) {
    try {
      const { iouId } = req.params;

      const iou = await IOU.findById(iouId);
      if (!iou) {
        return res.status(404).json({
          success: false,
          message: 'IOU not found'
        });
      }

      iou.isActive = false;
      iou.status = 'paused';
      iou.updatedBy = req.user.id;
      await iou.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'pause_iou',
        targetId: iou._id,
        targetType: 'IOU',
        details: { issuerId: iou.issuerId, amount: iou.amount },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'IOU paused successfully',
        data: iou
      });

    } catch (error) {
      console.error('Error pausing IOU:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async resumeIOU(req, res) {
    try {
      const { iouId } = req.params;

      const iou = await IOU.findById(iouId);
      if (!iou) {
        return res.status(404).json({
          success: false,
          message: 'IOU not found'
        });
      }

      iou.isActive = true;
      iou.status = 'active';
      iou.updatedBy = req.user.id;
      await iou.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'resume_iou',
        targetId: iou._id,
        targetType: 'IOU',
        details: { issuerId: iou.issuerId, amount: iou.amount },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'IOU resumed successfully',
        data: iou
      });

    } catch (error) {
      console.error('Error resuming IOU:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async deleteIOU(req, res) {
    try {
      const { iouId } = req.params;

      const iou = await IOU.findById(iouId);
      if (!iou) {
        return res.status(404).json({
          success: false,
          message: 'IOU not found'
        });
      }

      iou.isDeleted = true;
      iou.isActive = false;
      iou.status = 'deleted';
      iou.deletedAt = new Date();
      iou.updatedBy = req.user.id;
      await iou.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'delete_iou',
        targetId: iou._id,
        targetType: 'IOU',
        details: { issuerId: iou.issuerId, amount: iou.amount },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'IOU deleted successfully',
        data: iou
      });

    } catch (error) {
      console.error('Error deleting IOU:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // BLOCKCHAIN DEPLOYMENT MANAGEMENT
  async createEVMBlockchainDeployment(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        name,
        networkName,
        chainId,
        rpcUrl,
        wsUrl,
        blockExplorerUrl,
        gasPrice,
        gasLimit,
        contractAddress,
        abi,
        bytecode,
        deploymentTxHash,
        isActive,
        description
      } = req.body;

      const deployment = new BlockchainDeployment({
        name,
        blockchainType: 'evm',
        networkName,
        chainId,
        rpcUrl,
        wsUrl,
        blockExplorerUrl,
        gasPrice,
        gasLimit,
        contractAddress,
        abi,
        bytecode,
        deploymentTxHash,
        isActive: isActive !== undefined ? isActive : true,
        description,
        createdBy: req.user.id
      });

      await deployment.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_evm_blockchain_deployment',
        targetId: deployment._id,
        targetType: 'BlockchainDeployment',
        details: { name, networkName, chainId },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'EVM blockchain deployment created successfully',
        data: deployment
      });

    } catch (error) {
      console.error('Error creating EVM blockchain deployment:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async createNonEVMBlockchainDeployment(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        name,
        blockchainType,
        networkName,
        rpcUrl,
        wsUrl,
        blockExplorerUrl,
        nodeUrl,
        nativeCurrency,
        decimals,
        isActive,
        description
      } = req.body;

      const deployment = new BlockchainDeployment({
        name,
        blockchainType,
        networkName,
        rpcUrl,
        wsUrl,
        blockExplorerUrl,
        nodeUrl,
        nativeCurrency,
        decimals,
        isActive: isActive !== undefined ? isActive : true,
        description,
        createdBy: req.user.id
      });

      await deployment.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_non_evm_blockchain_deployment',
        targetId: deployment._id,
        targetType: 'BlockchainDeployment',
        details: { name, blockchainType, networkName },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Non-EVM blockchain deployment created successfully',
        data: deployment
      });

    } catch (error) {
      console.error('Error creating non-EVM blockchain deployment:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // CUSTOM TOKEN MANAGEMENT
  async createCustomToken(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        name,
        symbol,
        contractAddress,
        blockchainType,
        networkName,
        totalSupply,
        decimals,
        logoUrl,
        description,
        isActive,
        features
      } = req.body;

      const token = new CustomToken({
        name,
        symbol,
        contractAddress,
        blockchainType,
        networkName,
        totalSupply,
        decimals,
        logoUrl,
        description,
        isActive: isActive !== undefined ? isActive : true,
        features,
        createdBy: req.user.id
      });

      await token.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_custom_token',
        targetId: token._id,
        targetType: 'CustomToken',
        details: { name, symbol, contractAddress, blockchainType },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Custom token created successfully',
        data: token
      });

    } catch (error) {
      console.error('Error creating custom token:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async createTradingPair(req, res) {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation errors',
          errors: errors.array()
        });
      }

      const {
        baseTokenId,
        quoteTokenId,
        symbol,
        minPrice,
        maxPrice,
        tickSize,
        stepSize,
        minQty,
        maxQty,
        isActive,
        tradingRules
      } = req.body;

      // Check if trading pair already exists
      const existingPair = await TradingContract.findOne({
        symbol,
        type: 'trading_pair',
        isDeleted: false
      });

      if (existingPair) {
        return res.status(400).json({
          success: false,
          message: 'Trading pair already exists'
        });
      }

      const tradingPair = new TradingContract({
        symbol,
        type: 'trading_pair',
        baseTokenId,
        quoteTokenId,
        minPrice,
        maxPrice,
        tickSize,
        stepSize,
        minQty,
        maxQty,
        isActive: isActive !== undefined ? isActive : true,
        tradingRules,
        createdBy: req.user.id
      });

      await tradingPair.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'create_trading_pair',
        targetId: tradingPair._id,
        targetType: 'TradingContract',
        details: { symbol, baseTokenId, quoteTokenId },
        timestamp: new Date()
      });

      res.status(201).json({
        success: true,
        message: 'Trading pair created successfully',
        data: tradingPair
      });

    } catch (error) {
      console.error('Error creating trading pair:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async pauseTrading(req, res) {
    try {
      const { contractId } = req.params;

      const contract = await TradingContract.findById(contractId);
      if (!contract) {
        return res.status(404).json({
          success: false,
          message: 'Contract not found'
        });
      }

      contract.isActive = false;
      contract.status = 'paused';
      contract.updatedBy = req.user.id;
      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'pause_trading',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol: contract.symbol, type: contract.type },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Trading paused successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error pausing trading:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async resumeTrading(req, res) {
    try {
      const { contractId } = req.params;

      const contract = await TradingContract.findById(contractId);
      if (!contract) {
        return res.status(404).json({
          success: false,
          message: 'Contract not found'
        });
      }

      contract.isActive = true;
      contract.status = 'active';
      contract.updatedBy = req.user.id;
      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'resume_trading',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol: contract.symbol, type: contract.type },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Trading resumed successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error resuming trading:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async suspendTrading(req, res) {
    try {
      const { contractId } = req.params;

      const contract = await TradingContract.findById(contractId);
      if (!contract) {
        return res.status(404).json({
          success: false,
          message: 'Contract not found'
        });
      }

      contract.isActive = false;
      contract.status = 'suspended';
      contract.updatedBy = req.user.id;
      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'suspend_trading',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol: contract.symbol, type: contract.type },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Trading suspended successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error suspending trading:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async deleteTrading(req, res) {
    try {
      const { contractId } = req.params;

      const contract = await TradingContract.findById(contractId);
      if (!contract) {
        return res.status(404).json({
          success: false,
          message: 'Contract not found'
        });
      }

      contract.isDeleted = true;
      contract.isActive = false;
      contract.status = 'deleted';
      contract.deletedAt = new Date();
      contract.updatedBy = req.user.id;
      await contract.save();

      // Log audit
      await AuditLog.create({
        userId: req.user.id,
        action: 'delete_trading',
        targetId: contract._id,
        targetType: 'TradingContract',
        details: { symbol: contract.symbol, type: contract.type },
        timestamp: new Date()
      });

      res.json({
        success: true,
        message: 'Trading deleted successfully',
        data: contract
      });

    } catch (error) {
      console.error('Error deleting trading:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  // GET ALL CONTRACTS BY TYPE
  async getAllSpotContracts(req, res) {
    try {
      const { page = 1, limit = 20, status } = req.query;
      const query = { type: 'spot', isDeleted: false };
      
      if (status) {
        query.status = status;
      }

      const contracts = await TradingContract.find(query)
        .sort({ createdAt: -1 })
        .limit(limit * 1)
        .skip((page - 1) * limit)
        .populate('createdBy', 'username email')
        .populate('updatedBy', 'username email');

      const total = await TradingContract.countDocuments(query);

      res.json({
        success: true,
        data: contracts,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit)
        }
      });

    } catch (error) {
      console.error('Error getting spot contracts:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async getAllFuturesContracts(req, res) {
    try {
      const { page = 1, limit = 20, contractType, status } = req.query;
      const query = { type: 'futures', isDeleted: false };
      
      if (contractType) {
        query.contractType = contractType;
      }
      
      if (status) {
        query.status = status;
      }

      const contracts = await TradingContract.find(query)
        .sort({ createdAt: -1 })
        .limit(limit * 1)
        .skip((page - 1) * limit)
        .populate('createdBy', 'username email')
        .populate('updatedBy', 'username email');

      const total = await TradingContract.countDocuments(query);

      res.json({
        success: true,
        data: contracts,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit)
        }
      });

    } catch (error) {
      console.error('Error getting futures contracts:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async getAllMarginContracts(req, res) {
    try {
      const { page = 1, limit = 20, marginType, status } = req.query;
      const query = { type: 'margin', isDeleted: false };
      
      if (marginType) {
        query.marginType = marginType;
      }
      
      if (status) {
        query.status = status;
      }

      const contracts = await TradingContract.find(query)
        .sort({ createdAt: -1 })
        .limit(limit * 1)
        .skip((page - 1) * limit)
        .populate('createdBy', 'username email')
        .populate('updatedBy', 'username email');

      const total = await TradingContract.countDocuments(query);

      res.json({
        success: true,
        data: contracts,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit)
        }
      });

    } catch (error) {
      console.error('Error getting margin contracts:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async getAllOptionsContracts(req, res) {
    try {
      const { page = 1, limit = 20, optionType, status } = req.query;
      const query = { type: 'options', isDeleted: false };
      
      if (optionType) {
        query.optionType = optionType;
      }
      
      if (status) {
        query.status = status;
      }

      const contracts = await TradingContract.find(query)
        .sort({ createdAt: -1 })
        .limit(limit * 1)
        .skip((page - 1) * limit)
        .populate('createdBy', 'username email')
        .populate('updatedBy', 'username email');

      const total = await TradingContract.countDocuments(query);

      res.json({
        success: true,
        data: contracts,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit)
        }
      });

    } catch (error) {
      console.error('Error getting options contracts:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async getAllTradingPairs(req, res) {
    try {
      const { page = 1, limit = 20, status } = req.query;
      const query = { type: 'trading_pair', isDeleted: false };
      
      if (status) {
        query.status = status;
      }

      const pairs = await TradingContract.find(query)
        .sort({ createdAt: -1 })
        .limit(limit * 1)
        .skip((page - 1) * limit)
        .populate('createdBy', 'username email')
        .populate('updatedBy', 'username email')
        .populate('baseTokenId', 'symbol name')
        .populate('quoteTokenId', 'symbol name');

      const total = await TradingContract.countDocuments(query);

      res.json({
        success: true,
        data: pairs,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / limit)
        }
      });

    } catch (error) {
      console.error('Error getting trading pairs:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }

  async getSystemOverview(req, res) {
    try {
      const [
        spotCount,
        futuresCount,
        marginCount,
        optionsCount,
        pairsCount,
        activeContracts,
        pausedContracts,
        suspendedContracts,
        botsCount,
        activeBots,
        iouCount,
        deploymentsCount,
        tokensCount
      ] = await Promise.all([
        TradingContract.countDocuments({ type: 'spot', isDeleted: false }),
        TradingContract.countDocuments({ type: 'futures', isDeleted: false }),
        TradingContract.countDocuments({ type: 'margin', isDeleted: false }),
        TradingContract.countDocuments({ type: 'options', isDeleted: false }),
        TradingContract.countDocuments({ type: 'trading_pair', isDeleted: false }),
        TradingContract.countDocuments({ isActive: true, isDeleted: false }),
        TradingContract.countDocuments({ status: 'paused', isDeleted: false }),
        TradingContract.countDocuments({ status: 'suspended', isDeleted: false }),
        MarketMakerBot.countDocuments({ isDeleted: false }),
        MarketMakerBot.countDocuments({ isActive: true, isDeleted: false }),
        IOU.countDocuments({ isDeleted: false }),
        BlockchainDeployment.countDocuments({ isDeleted: false }),
        CustomToken.countDocuments({ isDeleted: false })
      ]);

      res.json({
        success: true,
        data: {
          contracts: {
            spot: spotCount,
            futures: futuresCount,
            margin: marginCount,
            options: optionsCount,
            pairs: pairsCount,
            total: spotCount + futuresCount + marginCount + optionsCount + pairsCount
          },
          status: {
            active: activeContracts,
            paused: pausedContracts,
            suspended: suspendedContracts,
            total: activeContracts + pausedContracts + suspendedContracts
          },
          bots: {
            total: botsCount,
            active: activeBots
          },
          ious: iouCount,
          deployments: deploymentsCount,
          tokens: tokensCount
        }
      });

    } catch (error) {
      console.error('Error getting system overview:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error',
        error: error.message
      });
    }
  }
}

module.exports = new AdminTradingController();