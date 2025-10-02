// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract GovernanceV2 is Ownable, ReentrancyGuard {
    using SafeMath for uint256;
    
    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        string status; // pending, active, executed, defeated
        mapping(address => bool) hasVoted;
        mapping(address => uint256) votes;
    }
    
    struct TreasuryFund {
        uint256 id;
        string name;
        uint256 amount;
        address recipient;
        string purpose;
        uint256 proposalTime;
        bool isApproved;
        bool isExecuted;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => TreasuryFund) public treasuryFunds;
    
    uint256 public proposalCount = 0;
    uint256 public treasuryFundCount = 0;
    uint256 public votingPeriod = 7 days;
    uint256 public quorum = 1000000 * 10**18; // 1M tokens
    
    address public governanceToken;
    
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string title);
    event Voted(uint256 indexed proposalId, address indexed voter, uint256 votes, string support);
    event ProposalExecuted(uint256 indexed proposalId);
    event TreasuryFundCreated(uint256 indexed fundId, string name, uint256 amount);
    event TreasuryFundApproved(uint256 indexed fundId);
    event TreasuryFundExecuted(uint256 indexed fundId, address recipient, uint256 amount);
    
    constructor(address _governanceToken) {
        governanceToken = _governanceToken;
    }
    
    function createProposal(
        string memory title,
        string memory description,
        bytes memory targets,
        bytes memory values,
        bytes memory signatures,
        bytes memory calldatas
    ) external returns (uint256) {
        require(ERC20(governanceToken).balanceOf(msg.sender) >= 10000 * 10**18, "Insufficient voting power");
        
        proposalCount++;
        uint256 proposalId = proposalCount;
        
        proposals[proposalId] = Proposal({
            id: proposalId,
            proposer: msg.sender,
            title: title,
            description: description,
            startTime: block.timestamp,
            endTime: block.timestamp.add(votingPeriod),
            forVotes: 0,
            againstVotes: 0,
            abstainVotes: 0,
            status: "pending"
        });
        
        emit ProposalCreated(proposalId, msg.sender, title);
        return proposalId;
    }
    
    function vote(
        uint256 proposalId,
        string memory support,
        uint256 votes
    ) external {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id > 0, "Proposal does not exist");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        require(keccak256(bytes(proposal.status)) == keccak256(bytes("active")), "Proposal not active");
        require(block.timestamp < proposal.endTime, "Voting period ended");
        require(ERC20(governanceToken).balanceOf(msg.sender) >= votes, "Insufficient tokens");
        
        proposal.hasVoted[msg.sender] = true;
        proposal.votes[msg.sender] = votes;
        
        if (keccak256(bytes(support)) == keccak256(bytes("for"))) {
            proposal.forVotes = proposal.forVotes.add(votes);
            emit Voted(proposalId, msg.sender, votes, "for");
        } else if (keccak256(bytes(support)) == keccak256(bytes("against"))) {
            proposal.againstVotes = proposal.againstVotes.add(votes);
            emit Voted(proposalId, msg.sender, votes, "against");
        } else if (keccak256(bytes(support)) == keccak256(bytes("abstain"))) {
            proposal.abstainVotes = proposal.abstainVotes.add(votes);
            emit Voted(proposalId, msg.sender, votes, "abstain");
        }
    }
    
    function executeProposal(uint256 proposalId) external onlyOwner {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id > 0, "Proposal does not exist");
        require(block.timestamp > proposal.endTime, "Voting period not ended");
        require(keccak256(bytes(proposal.status)) == keccak256(bytes("active")), "Proposal not active");
        
        uint256 totalVotes = proposal.forVotes.add(proposal.againstVotes).add(proposal.abstainVotes);
        require(totalVotes >= quorum, "Quorum not reached");
        require(proposal.forVotes > proposal.againstVotes, "Proposal defeated");
        
        proposal.status = "executed";
        emit ProposalExecuted(proposalId);
    }
    
    function createTreasuryFund(
        string memory name,
        uint256 amount,
        address recipient,
        string memory purpose
    ) external onlyOwner returns (uint256) {
        treasuryFundCount++;
        uint256 fundId = treasuryFundCount;
        
        treasuryFunds[fundId] = TreasuryFund({
            id: fundId,
            name: name,
            amount: amount,
            recipient: recipient,
            purpose: purpose,
            proposalTime: block.timestamp,
            isApproved: false,
            isExecuted: false
        });
        
        emit TreasuryFundCreated(fundId, name, amount);
        return fundId;
    }
    
    function approveTreasuryFund(uint256 fundId) external onlyOwner {
        TreasuryFund storage fund = treasuryFunds[fundId];
        require(fund.id > 0, "Fund does not exist");
        require(!fund.isApproved, "Fund already approved");
        
        fund.isApproved = true;
        emit TreasuryFundApproved(fundId);
    }
    
    function executeTreasuryFund(uint256 fundId) external onlyOwner nonReentrant {
        TreasuryFund storage fund = treasuryFunds[fundId];
        require(fund.id > 0, "Fund does not exist");
        require(fund.isApproved, "Fund not approved");
        require(!fund.isExecuted, "Fund already executed");
        
        // Transfer funds to recipient
        // In a real implementation, this would involve actual token transfers
        
        fund.isExecuted = true;
        emit TreasuryFundExecuted(fundId, fund.recipient, fund.amount);
    }
    
    function getProposal(uint256 proposalId) external view returns (
        uint256 id,
        address proposer,
        string memory title,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        uint256 forVotes,
        uint256 againstVotes,
        uint256 abstainVotes,
        string memory status
    ) {
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.id,
            proposal.proposer,
            proposal.title,
            proposal.description,
            proposal.startTime,
            proposal.endTime,
            proposal.forVotes,
            proposal.againstVotes,
            proposal.abstainVotes,
            proposal.status
        );
    }
    
    function getTreasuryFund(uint256 fundId) external view returns (
        uint256 id,
        string memory name,
        uint256 amount,
        address recipient,
        string memory purpose,
        uint256 proposalTime,
        bool isApproved,
        bool isExecuted
    ) {
        TreasuryFund storage fund = treasuryFunds[fundId];
        return (
            fund.id,
            fund.name,
            fund.amount,
            fund.recipient,
            fund.purpose,
            fund.proposalTime,
            fund.isApproved,
            fund.isExecuted
        );
    }
    
    function setVotingPeriod(uint256 _votingPeriod) external onlyOwner {
        votingPeriod = _votingPeriod;
    }
    
    function setQuorum(uint256 _quorum) external onlyOwner {
        quorum = _quorum;
    }
}