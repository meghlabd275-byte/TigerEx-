// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title TigerToken
 * @dev TigerEx native utility token with governance, staking, and fee discount features
 */
contract TigerToken is 
    ERC20, 
    ERC20Burnable, 
    ERC20Pausable, 
    AccessControl, 
    ERC20Permit, 
    ERC20Votes,
    ReentrancyGuard 
{
    using SafeMath for uint256;

    // Roles
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");

    // Token Economics
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens
    uint256 public constant INITIAL_SUPPLY = 100_000_000 * 10**18; // 100 million tokens
    
    // Vesting and Distribution
    mapping(address => VestingSchedule) public vestingSchedules;
    mapping(address => uint256) public stakingBalances;
    mapping(address => uint256) public stakingRewards;
    mapping(address => uint256) public lastStakeTime;
    
    // Fee Discount Tiers
    mapping(address => uint256) public feeDiscountTier;
    uint256[] public tierThresholds = [1000 * 10**18, 10000 * 10**18, 100000 * 10**18, 1000000 * 10**18];
    uint256[] public discountRates = [5, 10, 15, 25]; // Percentage discounts
    
    // Staking Parameters
    uint256 public stakingAPY = 1200; // 12% APY (basis points)
    uint256 public constant SECONDS_PER_YEAR = 365 * 24 * 60 * 60;
    uint256 public minimumStakingPeriod = 7 days;
    
    // Events
    event TokensStaked(address indexed user, uint256 amount);
    event TokensUnstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);
    event VestingScheduleCreated(address indexed beneficiary, uint256 amount, uint256 duration);
    event FeeDiscountTierUpdated(address indexed user, uint256 tier);

    struct VestingSchedule {
        uint256 totalAmount;
        uint256 releasedAmount;
        uint256 startTime;
        uint256 duration;
        bool revocable;
        bool revoked;
    }

    constructor(
        address _admin,
        address _treasury
    ) 
        ERC20("TigerEx Token", "TIGER") 
        ERC20Permit("TigerEx Token")
    {
        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(MINTER_ROLE, _admin);
        _grantRole(PAUSER_ROLE, _admin);
        _grantRole(BURNER_ROLE, _admin);
        _grantRole(GOVERNANCE_ROLE, _admin);

        // Mint initial supply to treasury
        _mint(_treasury, INITIAL_SUPPLY);
        
        // Update fee discount tier for treasury
        _updateFeeDiscountTier(_treasury);
    }

    /**
     * @dev Mint new tokens (only by minter role)
     */
    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) {
        require(totalSupply().add(amount) <= MAX_SUPPLY, "TigerToken: Max supply exceeded");
        _mint(to, amount);
        _updateFeeDiscountTier(to);
    }

    /**
     * @dev Pause token transfers (only by pauser role)
     */
    function pause() public onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause token transfers (only by pauser role)
     */
    function unpause() public onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @dev Burn tokens from specific account (only by burner role)
     */
    function burnFrom(address account, uint256 amount) public override onlyRole(BURNER_ROLE) {
        super.burnFrom(account, amount);
        _updateFeeDiscountTier(account);
    }

    /**
     * @dev Stake tokens to earn rewards and governance power
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "TigerToken: Amount must be greater than 0");
        require(balanceOf(msg.sender) >= amount, "TigerToken: Insufficient balance");

        // Claim pending rewards before staking
        _claimStakingRewards(msg.sender);

        // Transfer tokens to contract
        _transfer(msg.sender, address(this), amount);
        
        // Update staking balance
        stakingBalances[msg.sender] = stakingBalances[msg.sender].add(amount);
        lastStakeTime[msg.sender] = block.timestamp;

        emit TokensStaked(msg.sender, amount);
    }

    /**
     * @dev Unstake tokens and claim rewards
     */
    function unstake(uint256 amount) external nonReentrant {
        require(amount > 0, "TigerToken: Amount must be greater than 0");
        require(stakingBalances[msg.sender] >= amount, "TigerToken: Insufficient staking balance");
        require(
            block.timestamp >= lastStakeTime[msg.sender].add(minimumStakingPeriod),
            "TigerToken: Minimum staking period not met"
        );

        // Claim pending rewards
        _claimStakingRewards(msg.sender);

        // Update staking balance
        stakingBalances[msg.sender] = stakingBalances[msg.sender].sub(amount);

        // Transfer tokens back to user
        _transfer(address(this), msg.sender, amount);
        
        // Update fee discount tier
        _updateFeeDiscountTier(msg.sender);

        emit TokensUnstaked(msg.sender, amount);
    }

    /**
     * @dev Claim staking rewards
     */
    function claimRewards() external nonReentrant {
        _claimStakingRewards(msg.sender);
    }

    /**
     * @dev Internal function to claim staking rewards
     */
    function _claimStakingRewards(address user) internal {
        uint256 rewards = calculateStakingRewards(user);
        if (rewards > 0) {
            stakingRewards[user] = 0;
            lastStakeTime[user] = block.timestamp;
            
            // Mint rewards (if within max supply)
            if (totalSupply().add(rewards) <= MAX_SUPPLY) {
                _mint(user, rewards);
                _updateFeeDiscountTier(user);
            }
            
            emit RewardsClaimed(user, rewards);
        }
    }

    /**
     * @dev Calculate pending staking rewards for a user
     */
    function calculateStakingRewards(address user) public view returns (uint256) {
        if (stakingBalances[user] == 0) {
            return stakingRewards[user];
        }

        uint256 stakingDuration = block.timestamp.sub(lastStakeTime[user]);
        uint256 annualReward = stakingBalances[user].mul(stakingAPY).div(10000);
        uint256 reward = annualReward.mul(stakingDuration).div(SECONDS_PER_YEAR);
        
        return stakingRewards[user].add(reward);
    }

    /**
     * @dev Create vesting schedule for token distribution
     */
    function createVestingSchedule(
        address beneficiary,
        uint256 amount,
        uint256 duration,
        bool revocable
    ) external onlyRole(GOVERNANCE_ROLE) {
        require(beneficiary != address(0), "TigerToken: Invalid beneficiary");
        require(amount > 0, "TigerToken: Amount must be greater than 0");
        require(duration > 0, "TigerToken: Duration must be greater than 0");
        require(vestingSchedules[beneficiary].totalAmount == 0, "TigerToken: Vesting schedule already exists");

        vestingSchedules[beneficiary] = VestingSchedule({
            totalAmount: amount,
            releasedAmount: 0,
            startTime: block.timestamp,
            duration: duration,
            revocable: revocable,
            revoked: false
        });

        // Transfer tokens to contract for vesting
        _transfer(msg.sender, address(this), amount);

        emit VestingScheduleCreated(beneficiary, amount, duration);
    }

    /**
     * @dev Release vested tokens to beneficiary
     */
    function releaseVestedTokens() external nonReentrant {
        VestingSchedule storage schedule = vestingSchedules[msg.sender];
        require(schedule.totalAmount > 0, "TigerToken: No vesting schedule");
        require(!schedule.revoked, "TigerToken: Vesting schedule revoked");

        uint256 releasableAmount = calculateReleasableAmount(msg.sender);
        require(releasableAmount > 0, "TigerToken: No tokens to release");

        schedule.releasedAmount = schedule.releasedAmount.add(releasableAmount);
        _transfer(address(this), msg.sender, releasableAmount);
        
        _updateFeeDiscountTier(msg.sender);
    }

    /**
     * @dev Calculate releasable vested tokens
     */
    function calculateReleasableAmount(address beneficiary) public view returns (uint256) {
        VestingSchedule memory schedule = vestingSchedules[beneficiary];
        
        if (schedule.totalAmount == 0 || schedule.revoked) {
            return 0;
        }

        uint256 elapsedTime = block.timestamp.sub(schedule.startTime);
        
        if (elapsedTime >= schedule.duration) {
            return schedule.totalAmount.sub(schedule.releasedAmount);
        } else {
            uint256 vestedAmount = schedule.totalAmount.mul(elapsedTime).div(schedule.duration);
            return vestedAmount.sub(schedule.releasedAmount);
        }
    }

    /**
     * @dev Get fee discount rate for user based on token holdings
     */
    function getFeeDiscountRate(address user) external view returns (uint256) {
        uint256 tier = feeDiscountTier[user];
        if (tier > 0 && tier <= discountRates.length) {
            return discountRates[tier - 1];
        }
        return 0;
    }

    /**
     * @dev Update fee discount tier based on token balance
     */
    function _updateFeeDiscountTier(address user) internal {
        uint256 balance = balanceOf(user).add(stakingBalances[user]);
        uint256 newTier = 0;

        for (uint256 i = 0; i < tierThresholds.length; i++) {
            if (balance >= tierThresholds[i]) {
                newTier = i + 1;
            } else {
                break;
            }
        }

        if (feeDiscountTier[user] != newTier) {
            feeDiscountTier[user] = newTier;
            emit FeeDiscountTierUpdated(user, newTier);
        }
    }

    /**
     * @dev Update staking APY (only governance)
     */
    function updateStakingAPY(uint256 newAPY) external onlyRole(GOVERNANCE_ROLE) {
        require(newAPY <= 5000, "TigerToken: APY too high"); // Max 50%
        stakingAPY = newAPY;
    }

    /**
     * @dev Update tier thresholds and discount rates (only governance)
     */
    function updateFeeDiscountTiers(
        uint256[] calldata newThresholds,
        uint256[] calldata newDiscountRates
    ) external onlyRole(GOVERNANCE_ROLE) {
        require(newThresholds.length == newDiscountRates.length, "TigerToken: Array length mismatch");
        
        tierThresholds = newThresholds;
        discountRates = newDiscountRates;
    }

    // Override functions for multiple inheritance
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Pausable) {
        super._beforeTokenTransfer(from, to, amount);
    }

    function _afterTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal override(ERC20, ERC20Votes) {
        super._afterTokenTransfer(from, to, amount);
        
        // Update fee discount tiers for both sender and receiver
        if (from != address(0)) {
            _updateFeeDiscountTier(from);
        }
        if (to != address(0)) {
            _updateFeeDiscountTier(to);
        }
    }

    function _mint(address to, uint256 amount) internal override(ERC20, ERC20Votes) {
        super._mint(to, amount);
    }

    function _burn(address account, uint256 amount) internal override(ERC20, ERC20Votes) {
        super._burn(account, amount);
    }
}