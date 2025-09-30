const AlphaToken = require('../models/AlphaToken');
const winston = require('winston');
const axios = require('axios');

class RiskAssessmentService {
  constructor() {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      defaultMeta: { service: 'risk-assessment-service' },
      transports: [
        new winston.transports.File({ filename: 'logs/risk-assessment.log' }),
        new winston.transports.Console(),
      ],
    });

    this.riskFactors = {
      team: { weight: 0.25, maxScore: 100 },
      technology: { weight: 0.2, maxScore: 100 },
      market: { weight: 0.15, maxScore: 100 },
      tokenomics: { weight: 0.15, maxScore: 100 },
      compliance: { weight: 0.1, maxScore: 100 },
      community: { weight: 0.1, maxScore: 100 },
      partnerships: { weight: 0.05, maxScore: 100 },
    };

    this.isInitialized = false;
  }

  async initialize() {
    if (this.isInitialized) return;

    try {
      this.logger.info('Initializing Risk Assessment Service...');

      // Load any external risk data sources
      await this.loadRiskDataSources();

      this.isInitialized = true;
      this.logger.info('Risk Assessment Service initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize Risk Assessment Service:', error);
      throw error;
    }
  }

  async loadRiskDataSources() {
    // Load external risk assessment data sources
    // This could include blockchain analysis APIs, security audit databases, etc.
    this.logger.info('Loading risk data sources...');
  }

  async assessTokenRisk(tokenData) {
    try {
      this.logger.info(`Assessing risk for token: ${tokenData.symbol}`);

      const riskAssessment = {
        team: await this.assessTeamRisk(tokenData),
        technology: await this.assessTechnologyRisk(tokenData),
        market: await this.assessMarketRisk(tokenData),
        tokenomics: await this.assessTokenomicsRisk(tokenData),
        compliance: await this.assessComplianceRisk(tokenData),
        community: await this.assessCommunityRisk(tokenData),
        partnerships: await this.assessPartnershipRisk(tokenData),
      };

      const overallScore = this.calculateOverallRiskScore(riskAssessment);
      const riskLevel = this.determineRiskLevel(overallScore);

      return {
        overallScore,
        riskLevel,
        factors: riskAssessment,
        recommendations: this.generateRecommendations(
          riskAssessment,
          overallScore
        ),
        assessedAt: new Date(),
      };
    } catch (error) {
      this.logger.error('Error assessing token risk:', error);
      throw error;
    }
  }

  async assessTeamRisk(tokenData) {
    let score = 100; // Start with perfect score and deduct points
    const factors = [];

    // Check team information completeness
    if (!tokenData.projectTeam || tokenData.projectTeam.length === 0) {
      score -= 40;
      factors.push({
        factor: 'No team information provided',
        impact: -40,
        description: 'Team transparency is crucial for project credibility',
      });
    } else {
      // Analyze team members
      const teamAnalysis = this.analyzeTeamMembers(tokenData.projectTeam);
      score -= teamAnalysis.deduction;
      factors.push(...teamAnalysis.factors);
    }

    // Check for previous project experience
    const experienceScore = this.assessTeamExperience(tokenData.projectTeam);
    score -= (100 - experienceScore) * 0.3;

    if (experienceScore < 70) {
      factors.push({
        factor: 'Limited team experience',
        impact: -(100 - experienceScore) * 0.3,
        description: 'Team lacks significant blockchain/crypto experience',
      });
    }

    return {
      score: Math.max(0, Math.min(100, score)),
      factors,
      weight: this.riskFactors.team.weight,
    };
  }

  analyzeTeamMembers(teamMembers) {
    let deduction = 0;
    const factors = [];

    teamMembers.forEach((member) => {
      if (!member.linkedin || member.linkedin.trim() === '') {
        deduction += 5;
      }

      if (!member.experience || member.experience.trim() === '') {
        deduction += 10;
      }
    });

    if (teamMembers.length < 3) {
      deduction += 20;
      factors.push({
        factor: 'Small team size',
        impact: -20,
        description:
          'Team has fewer than 3 members, which may indicate limited capacity',
      });
    }

    return { deduction, factors };
  }

  assessTeamExperience(teamMembers) {
    if (!teamMembers || teamMembers.length === 0) return 0;

    let totalExperience = 0;
    teamMembers.forEach((member) => {
      if (member.experience) {
        // Simple keyword-based experience assessment
        const keywords = [
          'blockchain',
          'crypto',
          'defi',
          'smart contract',
          'solidity',
          'ethereum',
        ];
        const experienceText = member.experience.toLowerCase();
        const keywordMatches = keywords.filter((keyword) =>
          experienceText.includes(keyword)
        ).length;
        totalExperience += Math.min(100, keywordMatches * 20);
      }
    });

    return totalExperience / teamMembers.length;
  }

  async assessTechnologyRisk(tokenData) {
    let score = 100;
    const factors = [];

    // Check whitepaper availability
    if (!tokenData.whitepaper || !tokenData.whitepaper.url) {
      score -= 30;
      factors.push({
        factor: 'No whitepaper provided',
        impact: -30,
        description:
          'Technical documentation is essential for understanding the project',
      });
    }

    // Check blockchain choice
    const blockchainRisk = this.assessBlockchainRisk(tokenData.blockchain);
    score -= blockchainRisk.deduction;
    if (blockchainRisk.deduction > 0) {
      factors.push(blockchainRisk.factor);
    }

    // Check smart contract audit status
    if (!tokenData.contractAddress) {
      score -= 20;
      factors.push({
        factor: 'No smart contract deployed',
        impact: -20,
        description: 'Contract not yet deployed increases technical risk',
      });
    }

    return {
      score: Math.max(0, Math.min(100, score)),
      factors,
      weight: this.riskFactors.technology.weight,
    };
  }

  assessBlockchainRisk(blockchain) {
    const blockchainRisks = {
      ethereum: { risk: 0, reason: 'Established and secure network' },
      bsc: { risk: 10, reason: 'Centralized consensus mechanism' },
      polygon: { risk: 5, reason: 'Layer 2 solution with good security' },
      arbitrum: { risk: 5, reason: 'Optimistic rollup with good security' },
      optimism: { risk: 5, reason: 'Optimistic rollup with good security' },
      avalanche: { risk: 10, reason: 'Newer network with less battle-testing' },
      fantom: { risk: 15, reason: 'Smaller ecosystem and validator set' },
      solana: { risk: 20, reason: 'Network stability concerns and outages' },
    };

    const riskData = blockchainRisks[blockchain] || {
      risk: 25,
      reason: 'Unknown or untested blockchain',
    };

    return {
      deduction: riskData.risk,
      factor:
        riskData.risk > 0
          ? {
              factor: `Blockchain choice: ${blockchain}`,
              impact: -riskData.risk,
              description: riskData.reason,
            }
          : null,
    };
  }

  async assessMarketRisk(tokenData) {
    let score = 100;
    const factors = [];

    // Check market timing
    const marketTiming = await this.assessMarketTiming();
    score -= marketTiming.deduction;
    if (marketTiming.deduction > 0) {
      factors.push(marketTiming.factor);
    }

    // Check competition analysis
    if (!tokenData.competitorAnalysis) {
      score -= 15;
      factors.push({
        factor: 'No competitor analysis',
        impact: -15,
        description: 'Understanding competitive landscape is important',
      });
    }

    // Check use case viability
    const useCaseScore = this.assessUseCaseViability(tokenData.description);
    score -= (100 - useCaseScore) * 0.2;

    return {
      score: Math.max(0, Math.min(100, score)),
      factors,
      weight: this.riskFactors.market.weight,
    };
  }

  async assessMarketTiming() {
    // This would typically involve checking market conditions, crypto market sentiment, etc.
    // For now, we'll use a simplified approach
    const currentDate = new Date();
    const marketConditions = 'neutral'; // This would come from external APIs

    let deduction = 0;
    let factor = null;

    if (marketConditions === 'bear') {
      deduction = 20;
      factor = {
        factor: 'Bear market conditions',
        impact: -20,
        description: 'Current market conditions may affect token performance',
      };
    } else if (marketConditions === 'volatile') {
      deduction = 10;
      factor = {
        factor: 'High market volatility',
        impact: -10,
        description: 'Market volatility increases investment risk',
      };
    }

    return { deduction, factor };
  }

  assessUseCaseViability(description) {
    if (!description) return 0;

    const viabilityKeywords = [
      'defi',
      'nft',
      'gaming',
      'metaverse',
      'dao',
      'yield farming',
      'staking',
      'governance',
      'utility',
      'payment',
      'infrastructure',
    ];

    const description_lower = description.toLowerCase();
    const keywordMatches = viabilityKeywords.filter((keyword) =>
      description_lower.includes(keyword)
    ).length;

    return Math.min(100, keywordMatches * 15 + 40);
  }

  async assessTokenomicsRisk(tokenData) {
    let score = 100;
    const factors = [];

    // Check vesting schedule
    if (!tokenData.vestingSchedule || tokenData.vestingSchedule.length === 0) {
      score -= 25;
      factors.push({
        factor: 'No vesting schedule',
        impact: -25,
        description: 'Lack of vesting schedule may lead to token dumping',
      });
    } else {
      const vestingAnalysis = this.analyzeVestingSchedule(
        tokenData.vestingSchedule
      );
      score -= vestingAnalysis.deduction;
      if (vestingAnalysis.factor) {
        factors.push(vestingAnalysis.factor);
      }
    }

    // Check token allocation
    const allocationRisk = this.assessTokenAllocation(tokenData);
    score -= allocationRisk.deduction;
    if (allocationRisk.factor) {
      factors.push(allocationRisk.factor);
    }

    return {
      score: Math.max(0, Math.min(100, score)),
      factors,
      weight: this.riskFactors.tokenomics.weight,
    };
  }

  analyzeVestingSchedule(vestingSchedule) {
    let deduction = 0;
    let factor = null;

    // Check if vesting is too short (less than 6 months)
    const totalVestingPeriod = this.calculateVestingPeriod(vestingSchedule);
    if (totalVestingPeriod < 6) {
      deduction = 15;
      factor = {
        factor: 'Short vesting period',
        impact: -15,
        description: 'Vesting period shorter than 6 months increases dump risk',
      };
    }

    // Check for cliff period
    const hasCliff = vestingSchedule.some(
      (vest) =>
        vest.description && vest.description.toLowerCase().includes('cliff')
    );

    if (!hasCliff) {
      deduction += 10;
      factor = {
        factor: 'No cliff period',
        impact: -10,
        description: 'Lack of cliff period may lead to immediate token selling',
      };
    }

    return { deduction, factor };
  }

  calculateVestingPeriod(vestingSchedule) {
    if (vestingSchedule.length === 0) return 0;

    const firstRelease = new Date(
      Math.min(...vestingSchedule.map((v) => new Date(v.releaseDate)))
    );
    const lastRelease = new Date(
      Math.max(...vestingSchedule.map((v) => new Date(v.releaseDate)))
    );

    return (lastRelease - firstRelease) / (1000 * 60 * 60 * 24 * 30); // months
  }

  assessTokenAllocation(tokenData) {
    let deduction = 0;
    let factor = null;

    const alphaPercentage =
      (tokenData.alphaAllocation / tokenData.totalSupply) * 100;

    if (alphaPercentage > 50) {
      deduction = 20;
      factor = {
        factor: 'High alpha allocation percentage',
        impact: -20,
        description: 'Alpha allocation exceeds 50% of total supply',
      };
    } else if (alphaPercentage < 5) {
      deduction = 10;
      factor = {
        factor: 'Very low alpha allocation',
        impact: -10,
        description: 'Alpha allocation is less than 5% of total supply',
      };
    }

    return { deduction, factor };
  }

  async assessComplianceRisk(tokenData) {
    let score = 100;
    const factors = [];

    // Check KYC requirements
    if (!tokenData.isKYCRequired) {
      score -= 30;
      factors.push({
        factor: 'No KYC requirement',
        impact: -30,
        description: 'Lack of KYC increases regulatory compliance risk',
      });
    }

    // Check jurisdiction
    const jurisdictionRisk = this.assessJurisdictionRisk(
      tokenData.jurisdiction
    );
    score -= jurisdictionRisk.deduction;
    if (jurisdictionRisk.factor) {
      factors.push(jurisdictionRisk.factor);
    }

    return {
      score: Math.max(0, Math.min(100, score)),
      factors,
      weight: this.riskFactors.compliance.weight,
    };
  }

  assessJurisdictionRisk(jurisdiction) {
    const jurisdictionRisks = {
      US: { risk: 0, reason: 'Clear regulatory framework' },
      EU: { risk: 0, reason: 'Established crypto regulations' },
      UK: { risk: 5, reason: 'Evolving regulatory landscape' },
      Singapore: { risk: 5, reason: 'Crypto-friendly but strict compliance' },
      Switzerland: { risk: 0, reason: 'Clear crypto regulations' },
      Unknown: {
        risk: 40,
        reason: 'Unknown jurisdiction increases compliance risk',
      },
    };

    const riskData =
      jurisdictionRisks[jurisdiction] || jurisdictionRisks['Unknown'];

    return {
      deduction: riskData.risk,
      factor:
        riskData.risk > 0
          ? {
              factor: `Jurisdiction: ${jurisdiction || 'Unknown'}`,
              impact: -riskData.risk,
              description: riskData.reason,
            }
          : null,
    };
  }

  async assessCommunityRisk(tokenData) {
    let score = 100;
    const factors = [];

    // Check social media presence
    const socialScore = this.assessSocialMediaPresence(tokenData.socialLinks);
    score -= (100 - socialScore) * 0.4;

    if (socialScore < 50) {
      factors.push({
        factor: 'Weak social media presence',
        impact: -(100 - socialScore) * 0.4,
        description:
          'Limited social media presence may indicate low community engagement',
      });
    }

    return {
      score: Math.max(0, Math.min(100, score)),
      factors,
      weight: this.riskFactors.community.weight,
    };
  }

  assessSocialMediaPresence(socialLinks) {
    if (!socialLinks) return 0;

    let score = 0;
    const platforms = ['twitter', 'telegram', 'discord', 'medium'];

    platforms.forEach((platform) => {
      if (socialLinks[platform] && socialLinks[platform].trim() !== '') {
        score += 25;
      }
    });

    return score;
  }

  async assessPartnershipRisk(tokenData) {
    let score = 100;
    const factors = [];

    // Check for strategic partnerships
    if (!tokenData.partnerships || tokenData.partnerships.length === 0) {
      score -= 20;
      factors.push({
        factor: 'No strategic partnerships',
        impact: -20,
        description: 'Lack of partnerships may limit project growth potential',
      });
    }

    return {
      score: Math.max(0, Math.min(100, score)),
      factors,
      weight: this.riskFactors.partnerships.weight,
    };
  }

  calculateOverallRiskScore(riskAssessment) {
    let weightedScore = 0;
    let totalWeight = 0;

    Object.keys(riskAssessment).forEach((factor) => {
      const assessment = riskAssessment[factor];
      weightedScore += assessment.score * assessment.weight;
      totalWeight += assessment.weight;
    });

    return Math.round(weightedScore / totalWeight);
  }

  determineRiskLevel(score) {
    if (score >= 80) return 'Low';
    if (score >= 60) return 'Medium';
    if (score >= 40) return 'High';
    return 'Very High';
  }

  generateRecommendations(riskAssessment, overallScore) {
    const recommendations = [];

    if (overallScore < 40) {
      recommendations.push(
        'Consider avoiding this investment due to very high risk'
      );
    } else if (overallScore < 60) {
      recommendations.push(
        'Proceed with extreme caution and only invest small amounts'
      );
    } else if (overallScore < 80) {
      recommendations.push(
        'Moderate risk investment - diversify your portfolio'
      );
    } else {
      recommendations.push(
        'Relatively low risk investment suitable for alpha trading'
      );
    }

    // Add specific recommendations based on risk factors
    Object.keys(riskAssessment).forEach((factor) => {
      const assessment = riskAssessment[factor];
      if (assessment.score < 50) {
        recommendations.push(`Address ${factor} concerns before investing`);
      }
    });

    return recommendations;
  }

  async updateTokenRiskScore(tokenId) {
    try {
      const token = await AlphaToken.findOne({ tokenId });
      if (!token) {
        throw new Error('Token not found');
      }

      const riskAssessment = await this.assessTokenRisk(token);

      token.riskScore = riskAssessment.overallScore;
      token.riskFactors = riskAssessment.factors.map((factor) => ({
        factor: factor.factor,
        score: factor.score,
        description: factor.description,
      }));

      await token.save();

      this.logger.info(
        `Updated risk score for token ${tokenId}: ${riskAssessment.overallScore}`
      );
      return riskAssessment;
    } catch (error) {
      this.logger.error(
        `Error updating risk score for token ${tokenId}:`,
        error
      );
      throw error;
    }
  }
}

module.exports = new RiskAssessmentService();
