/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

const express = require('express');
const router = express.Router();
const UnifiedListing = require('../models/UnifiedListing');
const { authenticateAdmin } = require('../middleware/auth');

// Get all listings
router.get('/', authenticateAdmin, async (req, res) => {
  try {
    const { status, listingType, blockchain, page = 1, limit = 20 } = req.query;
    
    const query = {};
    if (status) query.overallStatus = status;
    if (listingType) query.listingType = listingType;
    if (blockchain) query.blockchain = blockchain;
    
    const listings = await UnifiedListing.find(query)
      .sort({ createdAt: -1 })
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .exec();
    
    const count = await UnifiedListing.countDocuments(query);
    
    res.json({
      listings,
      totalPages: Math.ceil(count / limit),
      currentPage: page,
      total: count
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get single listing
router.get('/:id', authenticateAdmin, async (req, res) => {
  try {
    const listing = await UnifiedListing.findById(req.params.id);
    if (!listing) {
      return res.status(404).json({ error: 'Listing not found' });
    }
    res.json(listing);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create new listing
router.post('/', authenticateAdmin, async (req, res) => {
  try {
    const listing = new UnifiedListing(req.body);
    listing.submittedAt = new Date();
    listing.overallStatus = 'SUBMITTED';
    
    await listing.save();
    res.status(201).json(listing);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Update listing
router.put('/:id', authenticateAdmin, async (req, res) => {
  try {
    const listing = await UnifiedListing.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    
    if (!listing) {
      return res.status(404).json({ error: 'Listing not found' });
    }
    
    res.json(listing);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Approve listing for CEX
router.post('/:id/approve-cex', authenticateAdmin, async (req, res) => {
  try {
    const listing = await UnifiedListing.findById(req.params.id);
    
    if (!listing) {
      return res.status(404).json({ error: 'Listing not found' });
    }
    
    listing.cexConfig.status = 'APPROVED';
    listing.cexConfig.enabled = true;
    listing.adminActions.push({
      action: 'CEX_APPROVED',
      reason: req.body.reason,
      adminId: req.admin.id,
      timestamp: new Date()
    });
    
    // Update overall status
    if (listing.listingType === 'CEX_ONLY' || 
        (listing.listingType === 'HYBRID' && listing.dexConfig.status === 'APPROVED')) {
      listing.overallStatus = 'APPROVED';
      listing.approvedAt = new Date();
    }
    
    await listing.save();
    res.json(listing);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Approve listing for DEX
router.post('/:id/approve-dex', authenticateAdmin, async (req, res) => {
  try {
    const listing = await UnifiedListing.findById(req.params.id);
    
    if (!listing) {
      return res.status(404).json({ error: 'Listing not found' });
    }
    
    listing.dexConfig.status = 'APPROVED';
    listing.dexConfig.enabled = true;
    listing.adminActions.push({
      action: 'DEX_APPROVED',
      reason: req.body.reason,
      adminId: req.admin.id,
      timestamp: new Date()
    });
    
    // Update overall status
    if (listing.listingType === 'DEX_ONLY' || 
        (listing.listingType === 'HYBRID' && listing.cexConfig.status === 'APPROVED')) {
      listing.overallStatus = 'APPROVED';
      listing.approvedAt = new Date();
    }
    
    await listing.save();
    res.json(listing);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Reject listing
router.post('/:id/reject', authenticateAdmin, async (req, res) => {
  try {
    const listing = await UnifiedListing.findById(req.params.id);
    
    if (!listing) {
      return res.status(404).json({ error: 'Listing not found' });
    }
    
    listing.overallStatus = 'REJECTED';
    listing.adminActions.push({
      action: 'REJECTED',
      reason: req.body.reason,
      adminId: req.admin.id,
      timestamp: new Date()
    });
    
    await listing.save();
    res.json(listing);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Activate listing (make it live)
router.post('/:id/activate', authenticateAdmin, async (req, res) => {
  try {
    const listing = await UnifiedListing.findById(req.params.id);
    
    if (!listing) {
      return res.status(404).json({ error: 'Listing not found' });
    }
    
    if (listing.overallStatus !== 'APPROVED') {
      return res.status(400).json({ error: 'Listing must be approved first' });
    }
    
    listing.overallStatus = 'ACTIVE';
    listing.listedAt = new Date();
    
    if (listing.cexConfig.enabled) {
      listing.cexConfig.status = 'ACTIVE';
    }
    
    if (listing.dexConfig.enabled) {
      listing.dexConfig.status = 'ACTIVE';
    }
    
    listing.adminActions.push({
      action: 'ACTIVATED',
      reason: req.body.reason,
      adminId: req.admin.id,
      timestamp: new Date()
    });
    
    await listing.save();
    res.json(listing);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Suspend listing
router.post('/:id/suspend', authenticateAdmin, async (req, res) => {
  try {
    const listing = await UnifiedListing.findById(req.params.id);
    
    if (!listing) {
      return res.status(404).json({ error: 'Listing not found' });
    }
    
    listing.overallStatus = 'SUSPENDED';
    listing.cexConfig.status = 'SUSPENDED';
    listing.dexConfig.status = 'SUSPENDED';
    
    listing.adminActions.push({
      action: 'SUSPENDED',
      reason: req.body.reason,
      adminId: req.admin.id,
      timestamp: new Date()
    });
    
    await listing.save();
    res.json(listing);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete listing
router.delete('/:id', authenticateAdmin, async (req, res) => {
  try {
    const listing = await UnifiedListing.findByIdAndDelete(req.params.id);
    
    if (!listing) {
      return res.status(404).json({ error: 'Listing not found' });
    }
    
    res.json({ message: 'Listing deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;