// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract NFTLaunchpad is ERC721Enumerable, Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _projectIds;
    
    struct NFTProject {
        uint256 id;
        string name;
        string description;
        address creator;
        uint256 totalSupply;
        uint256 mintPrice;
        uint256 maxMintPerWallet;
        uint256 whitelistStart;
        uint256 publicSaleStart;
        uint256 launchDate;
        string metadataURI;
        string imageURI;
        uint256 royaltyPercentage;
        bool isFeatured;
        bool isVerified;
        string status; // upcoming, whitelist, public, sold_out, ended
    }
    
    struct WhitelistEntry {
        address wallet;
        uint256 allocation;
        uint256 mintedCount;
        bool isActive;
    }
    
    mapping(uint256 => NFTProject) public projects;
    mapping(uint256 => mapping(address => WhitelistEntry)) public whitelist;
    mapping(uint256 => mapping(uint256 => address)) public tokenToCreator;
    mapping(uint256 => mapping(uint256 => uint256)) public royaltyAmounts;
    
    event ProjectCreated(uint256 indexed projectId, address indexed creator, string name);
    event WhitelistAdded(uint256 indexed projectId, address indexed wallet, uint256 allocation);
    event NFTMinted(uint256 indexed projectId, uint256 indexed tokenId, address indexed minter);
    event RoyaltyPaid(uint256 indexed projectId, uint256 indexed tokenId, address creator, uint256 amount);
    
    constructor() ERC721("TigerEx NFT Launchpad", "TXLP") {}
    
    function createProject(
        string memory name,
        string memory description,
        uint256 totalSupply,
        uint256 mintPrice,
        uint256 maxMintPerWallet,
        uint256 whitelistStart,
        uint256 publicSaleStart,
        uint256 launchDate,
        string memory metadataURI,
        string memory imageURI,
        uint256 royaltyPercentage
    ) external onlyOwner returns (uint256) {
        _projectIds.increment();
        uint256 projectId = _projectIds.current();
        
        projects[projectId] = NFTProject({
            id: projectId,
            name: name,
            description: description,
            creator: msg.sender,
            totalSupply: totalSupply,
            mintPrice: mintPrice,
            maxMintPerWallet: maxMintPerWallet,
            whitelistStart: whitelistStart,
            publicSaleStart: publicSaleStart,
            launchDate: launchDate,
            metadataURI: metadataURI,
            imageURI: imageURI,
            royaltyPercentage: royaltyPercentage,
            isFeatured: false,
            isVerified: false,
            status: "upcoming"
        });
        
        emit ProjectCreated(projectId, msg.sender, name);
        return projectId;
    }
    
    function addToWhitelist(
        uint256 projectId,
        address wallet,
        uint256 allocation
    ) external onlyOwner {
        require(projectId > 0 && projectId <= _projectIds.current(), "Invalid project ID");
        
        whitelist[projectId][wallet] = WhitelistEntry({
            wallet: wallet,
            allocation: allocation,
            mintedCount: 0,
            isActive: true
        });
        
        emit WhitelistAdded(projectId, wallet, allocation);
    }
    
    function mintNFT(
        uint256 projectId,
        uint256 tokenId,
        string memory tokenURI
    ) external payable nonReentrant {
        NFTProject memory project = projects[projectId];
        require(project.id > 0, "Project does not exist");
        
        uint256 currentTime = block.timestamp;
        
        // Check project status and timing
        if (keccak256(bytes(project.status)) == keccak256(bytes("upcoming"))) {
            require(currentTime >= project.launchDate, "Project not launched yet");
            projects[projectId].status = "whitelist";
        }
        
        if (keccak256(bytes(project.status)) == keccak256(bytes("whitelist"))) {
            require(currentTime >= project.whitelistStart, "Whitelist phase not started");
            WhitelistEntry memory entry = whitelist[projectId][msg.sender];
            require(entry.isActive, "Not whitelisted");
            require(entry.mintedCount < entry.allocation, "Exceeds whitelist allocation");
            whitelist[projectId][msg.sender].mintedCount++;
        }
        
        if (keccak256(bytes(project.status)) == keccak256(bytes("public"))) {
            require(currentTime >= project.publicSaleStart, "Public sale not started");
        }
        
        require(msg.value >= project.mintPrice, "Insufficient payment");
        require(tokenId <= project.totalSupply, "Exceeds total supply");
        
        // Mint the NFT
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, tokenURI);
        
        // Set creator for royalty tracking
        tokenToCreator[projectId][tokenId] = project.creator;
        
        emit NFTMinted(projectId, tokenId, msg.sender);
    }
    
    function payRoyalty(
        uint256 projectId,
        uint256 tokenId,
        uint256 salePrice
    ) external payable nonReentrant {
        address creator = tokenToCreator[projectId][tokenId];
        require(creator != address(0), "Creator not found");
        
        uint256 royaltyAmount = (salePrice * projects[projectId].royaltyPercentage) / 100;
        royaltyAmounts[projectId][tokenId] += royaltyAmount;
        
        (bool success, ) = payable(creator).call{value: royaltyAmount}("");
        require(success, "Royalty payment failed");
        
        emit RoyaltyPaid(projectId, tokenId, creator, royaltyAmount);
    }
    
    function getProject(uint256 projectId) external view returns (NFTProject memory) {
        return projects[projectId];
    }
    
    function isWhitelisted(uint256 projectId, address wallet) external view returns (bool) {
        return whitelist[projectId][wallet].isActive;
    }
    
    function getWhitelistEntry(uint256 projectId, address wallet) external view returns (WhitelistEntry memory) {
        return whitelist[projectId][wallet];
    }
    
    function getRoyaltyAmount(uint256 projectId, uint256 tokenId) external view returns (uint256) {
        return royaltyAmounts[projectId][tokenId];
    }
}