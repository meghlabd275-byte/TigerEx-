// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title TigerNFT
 * @dev NFT contract for TigerEx marketplace
 */
contract TigerNFT is ERC721, ERC721URIStorage, ERC721Burnable, AccessControl, ReentrancyGuard {
    using Counters for Counters.Counter;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    Counters.Counter private _tokenIdCounter;

    uint256 public mintingFee = 0.01 ether;
    uint256 public royaltyPercentage = 250; // 2.5% in basis points
    
    mapping(uint256 => address) public creators;
    mapping(uint256 => uint256) public royalties;
    mapping(address => bool) public verifiedCreators;

    event NFTMinted(uint256 indexed tokenId, address indexed creator, string tokenURI);
    event RoyaltyPaid(uint256 indexed tokenId, address indexed recipient, uint256 amount);
    event CreatorVerified(address indexed creator);

    constructor() ERC721("TigerEx NFT", "TNFT") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
    }

    function mint(address to, string memory uri) public payable nonReentrant returns (uint256) {
        require(msg.value >= mintingFee, "Insufficient minting fee");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        
        creators[tokenId] = to;
        royalties[tokenId] = royaltyPercentage;
        
        emit NFTMinted(tokenId, to, uri);
        
        return tokenId;
    }

    function batchMint(address to, string[] memory uris) external payable nonReentrant returns (uint256[] memory) {
        require(msg.value >= mintingFee * uris.length, "Insufficient minting fee");
        
        uint256[] memory tokenIds = new uint256[](uris.length);
        
        for (uint256 i = 0; i < uris.length; i++) {
            uint256 tokenId = _tokenIdCounter.current();
            _tokenIdCounter.increment();
            
            _safeMint(to, tokenId);
            _setTokenURI(tokenId, uris[i]);
            
            creators[tokenId] = to;
            royalties[tokenId] = royaltyPercentage;
            
            tokenIds[i] = tokenId;
            
            emit NFTMinted(tokenId, to, uris[i]);
        }
        
        return tokenIds;
    }

    function setMintingFee(uint256 _fee) external onlyRole(DEFAULT_ADMIN_ROLE) {
        mintingFee = _fee;
    }

    function setRoyaltyPercentage(uint256 _percentage) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_percentage <= 1000, "Royalty too high"); // Max 10%
        royaltyPercentage = _percentage;
    }

    function verifyCreator(address creator) external onlyRole(DEFAULT_ADMIN_ROLE) {
        verifiedCreators[creator] = true;
        emit CreatorVerified(creator);
    }

    function getCreator(uint256 tokenId) external view returns (address) {
        return creators[tokenId];
    }

    function getRoyalty(uint256 tokenId) external view returns (uint256) {
        return royalties[tokenId];
    }

    function withdraw() external onlyRole(DEFAULT_ADMIN_ROLE) {
        uint256 balance = address(this).balance;
        payable(msg.sender).transfer(balance);
    }

    // Override functions
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}