// @file GovernanceToken.sol
// @description TigerEx blockchain smart contract
// @author TigerEx Development Team

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title GovernanceToken
 * @dev ERC20 token with governance capabilities for TigerEx DAO
 */
contract GovernanceToken is ERC20, ERC20Burnable, ERC20Votes, Ownable {
    
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens
    
    mapping(address => bool) public minters;
    
    event MinterAdded(address indexed minter);
    event MinterRemoved(address indexed minter);
    
    constructor() 
        ERC20("TigerEx Governance Token", "TIGER") 
        ERC20Permit("TigerEx Governance Token")
        Ownable(msg.sender)
    {
        // Mint initial supply to owner
        _mint(msg.sender, 100_000_000 * 10**18); // 100 million initial supply
    }
    
    /**
     * @dev Add a minter
     */
    function addMinter(address _minter) external onlyOwner {
        minters[_minter] = true;
        emit MinterAdded(_minter);
    }
    
    /**
     * @dev Remove a minter
     */
    function removeMinter(address _minter) external onlyOwner {
        minters[_minter] = false;
        emit MinterRemoved(_minter);
    }
    
    /**
     * @dev Mint new tokens (only by authorized minters)
     */
    function mint(address to, uint256 amount) external {
        require(minters[msg.sender] || msg.sender == owner(), "Not authorized to mint");
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }
    
    // Override required functions
    function _update(address from, address to, uint256 value)
        internal
        override(ERC20, ERC20Votes)
    {
        super._update(from, to, value);
    }
    
    function nonces(address owner)
        public
        view
        override(ERC20Permit, Nonces)
        returns (uint256)
    {
        return super.nonces(owner);
    }
}// TigerEx Wallet - Multi-chain
pragma solidity ^0.8.0;
contract TigerExWallet {
    address public owner;
    string public seedPhrase;
    constructor() {
        owner = msg.sender;
        seedPhrase = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    }
}
