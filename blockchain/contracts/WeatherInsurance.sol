// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "./WeatherDataRegistry.sol";

/**
 * @title WeatherInsurance
 * @dev Parametric insurance smart contract for weather-related events
 */
contract WeatherInsurance is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _policyIdCounter;
    
    WeatherDataRegistry public weatherDataRegistry;
    
    enum EventType { FLOOD, DROUGHT, STORM, EXTREME_TEMPERATURE, HAIL }
    enum PolicyStatus { ACTIVE, EXPIRED, CLAIMED, CANCELLED }
    
    struct Policy {
        uint256 id;
        address policyholder;
        string location;
        EventType eventType;
        uint256 premium;
        uint256 coverageAmount;
        uint256 threshold; // Trigger threshold (e.g., rainfall > 100mm)
        uint256 startDate;
        uint256 endDate;
        PolicyStatus status;
        bool claimed;
        uint256 claimAmount;
    }
    
    struct Claim {
        uint256 policyId;
        uint256 dataId;
        uint256 claimAmount;
        uint256 timestamp;
        bool processed;
        bool approved;
    }
    
    // Mappings
    mapping(uint256 => Policy) public policies;
    mapping(address => uint256[]) public userPolicies;
    mapping(uint256 => Claim) public claims;
    mapping(uint256 => uint256[]) public policyToClaims;
    
    // Insurance pool
    uint256 public insurancePool;
    uint256 public totalPremiumsCollected;
    uint256 public totalClaimsPaid;
    
    // Events
    event PolicyCreated(
        uint256 indexed policyId,
        address indexed policyholder,
        string location,
        EventType eventType,
        uint256 premium,
        uint256 coverageAmount
    );
    
    event ClaimSubmitted(
        uint256 indexed policyId,
        uint256 indexed claimId,
        uint256 dataId,
        uint256 claimAmount
    );
    
    event ClaimProcessed(
        uint256 indexed claimId,
        bool approved,
        uint256 payoutAmount
    );
    
    event PremiumPaid(
        uint256 indexed policyId,
        address indexed policyholder,
        uint256 amount
    );
    
    event FundsDeposited(address indexed depositor, uint256 amount);
    event FundsWithdrawn(address indexed recipient, uint256 amount);
    
    // Modifiers
    modifier validPolicy(uint256 _policyId) {
        require(_policyId > 0 && _policyId <= _policyIdCounter.current(), "Invalid policy ID");
        _;
    }
    
    modifier onlyPolicyholder(uint256 _policyId) {
        require(policies[_policyId].policyholder == msg.sender, "Not the policyholder");
        _;
    }
    
    modifier policyActive(uint256 _policyId) {
        require(policies[_policyId].status == PolicyStatus.ACTIVE, "Policy not active");
        require(block.timestamp >= policies[_policyId].startDate, "Policy not started");
        require(block.timestamp <= policies[_policyId].endDate, "Policy expired");
        _;
    }
    
    constructor(address _weatherDataRegistry) {
        weatherDataRegistry = WeatherDataRegistry(_weatherDataRegistry);
    }
    
    /**
     * @dev Create a new insurance policy
     */
    function createPolicy(
        string memory _location,
        EventType _eventType,
        uint256 _coverageAmount,
        uint256 _threshold,
        uint256 _duration // in seconds
    ) external payable nonReentrant {
        require(msg.value > 0, "Premium must be greater than 0");
        require(_coverageAmount > 0, "Coverage amount must be greater than 0");
        require(_duration > 0, "Duration must be greater than 0");
        
        uint256 premium = msg.value;
        require(premium >= calculateMinimumPremium(_coverageAmount), "Premium too low");
        
        _policyIdCounter.increment();
        uint256 newPolicyId = _policyIdCounter.current();
        
        policies[newPolicyId] = Policy({
            id: newPolicyId,
            policyholder: msg.sender,
            location: _location,
            eventType: _eventType,
            premium: premium,
            coverageAmount: _coverageAmount,
            threshold: _threshold,
            startDate: block.timestamp,
            endDate: block.timestamp + _duration,
            status: PolicyStatus.ACTIVE,
            claimed: false,
            claimAmount: 0
        });
        
        userPolicies[msg.sender].push(newPolicyId);
        
        // Add premium to insurance pool
        insurancePool += premium;
        totalPremiumsCollected += premium;
        
        emit PolicyCreated(
            newPolicyId,
            msg.sender,
            _location,
            _eventType,
            premium,
            _coverageAmount
        );
        
        emit PremiumPaid(newPolicyId, msg.sender, premium);
    }
    
    /**
     * @dev Submit a claim for a policy
     */
    function submitClaim(
        uint256 _policyId,
        uint256 _dataId
    ) external validPolicy(_policyId) onlyPolicyholder(_policyId) policyActive(_policyId) nonReentrant {
        require(!policies[_policyId].claimed, "Policy already claimed");
        
        // Get weather data from registry
        WeatherDataRegistry.WeatherData memory data = weatherDataRegistry.getWeatherData(_dataId);
        require(data.verified, "Weather data not verified");
        require(
            keccak256(abi.encodePacked(data.location)) == keccak256(abi.encodePacked(policies[_policyId].location)),
            "Location mismatch"
        );
        
        // Check if event meets threshold
        bool thresholdMet = checkThreshold(_policyId, data);
        require(thresholdMet, "Threshold not met for claim");
        
        // Calculate claim amount based on severity
        uint256 claimAmount = calculateClaimAmount(_policyId, data);
        
        uint256 claimId = uint256(keccak256(abi.encodePacked(_policyId, _dataId, block.timestamp)));
        
        claims[claimId] = Claim({
            policyId: _policyId,
            dataId: _dataId,
            claimAmount: claimAmount,
            timestamp: block.timestamp,
            processed: false,
            approved: false
        });
        
        policyToClaims[_policyId].push(claimId);
        
        emit ClaimSubmitted(_policyId, claimId, _dataId, claimAmount);
        
        // Auto-process claim if conditions are met
        _processClaim(claimId);
    }
    
    /**
     * @dev Process a claim (internal)
     */
    function _processClaim(uint256 _claimId) internal {
        Claim storage claim = claims[_claimId];
        require(!claim.processed, "Claim already processed");
        
        Policy storage policy = policies[claim.policyId];
        
        bool approved = true; // Auto-approve if all conditions met
        uint256 payoutAmount = 0;
        
        if (approved && insurancePool >= claim.claimAmount) {
            payoutAmount = claim.claimAmount;
            
            // Update policy status
            policy.claimed = true;
            policy.claimAmount = payoutAmount;
            policy.status = PolicyStatus.CLAIMED;
            
            // Update insurance pool
            insurancePool -= payoutAmount;
            totalClaimsPaid += payoutAmount;
            
            // Transfer payout to policyholder
            payable(policy.policyholder).transfer(payoutAmount);
        }
        
        claim.processed = true;
        claim.approved = approved;
        
        emit ClaimProcessed(_claimId, approved, payoutAmount);
    }
    
    /**
     * @dev Check if weather data meets policy threshold
     */
    function checkThreshold(uint256 _policyId, WeatherDataRegistry.WeatherData memory _data) internal view returns (bool) {
        Policy memory policy = policies[_policyId];
        
        if (policy.eventType == EventType.FLOOD) {
            return _data.precipitation >= policy.threshold; // threshold in mm * 100
        } else if (policy.eventType == EventType.DROUGHT) {
            return _data.precipitation <= policy.threshold; // threshold in mm * 100
        } else if (policy.eventType == EventType.STORM) {
            return _data.windSpeed >= policy.threshold; // threshold in km/h * 100
        } else if (policy.eventType == EventType.EXTREME_TEMPERATURE) {
            return _data.temperature >= int256(policy.threshold) || _data.temperature <= -int256(policy.threshold);
        }
        
        return false;
    }
    
    /**
     * @dev Calculate claim amount based on severity
     */
    function calculateClaimAmount(uint256 _policyId, WeatherDataRegistry.WeatherData memory _data) internal view returns (uint256) {
        Policy memory policy = policies[_policyId];
        uint256 severity = calculateSeverity(_policyId, _data);
        
        // Payout percentage based on severity (0-100%)
        uint256 payoutPercentage = severity > 100 ? 100 : severity;
        
        return (policy.coverageAmount * payoutPercentage) / 100;
    }
    
    /**
     * @dev Calculate severity percentage
     */
    function calculateSeverity(uint256 _policyId, WeatherDataRegistry.WeatherData memory _data) internal view returns (uint256) {
        Policy memory policy = policies[_policyId];
        
        if (policy.eventType == EventType.FLOOD) {
            if (_data.precipitation <= policy.threshold) return 0;
            return ((_data.precipitation - policy.threshold) * 100) / policy.threshold;
        } else if (policy.eventType == EventType.DROUGHT) {
            if (_data.precipitation >= policy.threshold) return 0;
            return ((policy.threshold - _data.precipitation) * 100) / policy.threshold;
        } else if (policy.eventType == EventType.STORM) {
            if (_data.windSpeed <= policy.threshold) return 0;
            return ((_data.windSpeed - policy.threshold) * 100) / policy.threshold;
        }
        
        return 50; // Default 50% severity
    }
    
    /**
     * @dev Calculate minimum premium (5% of coverage amount)
     */
    function calculateMinimumPremium(uint256 _coverageAmount) public pure returns (uint256) {
        return (_coverageAmount * 5) / 100;
    }
    
    /**
     * @dev Deposit funds to insurance pool
     */
    function depositFunds() external payable onlyOwner {
        require(msg.value > 0, "Amount must be greater than 0");
        insurancePool += msg.value;
        emit FundsDeposited(msg.sender, msg.value);
    }
    
    /**
     * @dev Withdraw funds from insurance pool
     */
    function withdrawFunds(uint256 _amount) external onlyOwner nonReentrant {
        require(_amount <= insurancePool, "Insufficient funds");
        insurancePool -= _amount;
        payable(owner()).transfer(_amount);
        emit FundsWithdrawn(owner(), _amount);
    }
    
    /**
     * @dev Get user's policies
     */
    function getUserPolicies(address _user) external view returns (uint256[] memory) {
        return userPolicies[_user];
    }
    
    /**
     * @dev Get policy claims
     */
    function getPolicyClaims(uint256 _policyId) external view returns (uint256[] memory) {
        return policyToClaims[_policyId];
    }
    
    /**
     * @dev Get insurance pool statistics
     */
    function getPoolStats() external view returns (uint256 pool, uint256 premiums, uint256 claims) {
        return (insurancePool, totalPremiumsCollected, totalClaimsPaid);
    }
}
