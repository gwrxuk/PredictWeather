// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title EmergencyResourceAllocation
 * @dev Smart contract for transparent allocation of emergency resources during weather disasters
 */
contract EmergencyResourceAllocation is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _requestIdCounter;
    Counters.Counter private _allocationIdCounter;
    
    enum ResourceType { FOOD, WATER, MEDICAL, SHELTER, EVACUATION, EQUIPMENT }
    enum RequestStatus { PENDING, APPROVED, REJECTED, FULFILLED }
    enum Priority { LOW, MEDIUM, HIGH, CRITICAL }
    
    struct ResourceRequest {
        uint256 id;
        address requester;
        string location;
        ResourceType resourceType;
        uint256 quantity;
        Priority priority;
        string description;
        uint256 timestamp;
        RequestStatus status;
        uint256 approvedQuantity;
        string rejectionReason;
    }
    
    struct ResourceAllocation {
        uint256 id;
        uint256 requestId;
        address supplier;
        uint256 allocatedQuantity;
        uint256 cost;
        uint256 timestamp;
        bool delivered;
        string trackingInfo;
    }
    
    struct EmergencyEvent {
        uint256 id;
        string eventType;
        string location;
        Priority severity;
        uint256 startTime;
        uint256 endTime;
        bool active;
        uint256 totalBudget;
        uint256 usedBudget;
    }
    
    struct AuthorizedResponder {
        address responderAddress;
        string name;
        string organization;
        bool isActive;
        uint256 authorizationLevel; // 1-5, higher = more authority
    }
    
    // Mappings
    mapping(uint256 => ResourceRequest) public resourceRequests;
    mapping(uint256 => ResourceAllocation) public resourceAllocations;
    mapping(uint256 => EmergencyEvent) public emergencyEvents;
    mapping(address => AuthorizedResponder) public authorizedResponders;
    mapping(string => uint256[]) public locationToRequests;
    mapping(uint256 => uint256[]) public eventToRequests;
    mapping(address => uint256[]) public userRequests;
    
    // Resource inventory
    mapping(ResourceType => uint256) public availableResources;
    mapping(ResourceType => uint256) public reservedResources;
    
    // Emergency fund
    uint256 public emergencyFund;
    
    // Events
    event ResourceRequested(
        uint256 indexed requestId,
        address indexed requester,
        string location,
        ResourceType resourceType,
        uint256 quantity,
        Priority priority
    );
    
    event RequestApproved(
        uint256 indexed requestId,
        uint256 approvedQuantity,
        address indexed approver
    );
    
    event RequestRejected(
        uint256 indexed requestId,
        string reason,
        address indexed approver
    );
    
    event ResourceAllocated(
        uint256 indexed allocationId,
        uint256 indexed requestId,
        address indexed supplier,
        uint256 quantity,
        uint256 cost
    );
    
    event ResourceDelivered(
        uint256 indexed allocationId,
        string trackingInfo
    );
    
    event EmergencyEventCreated(
        uint256 indexed eventId,
        string eventType,
        string location,
        Priority severity
    );
    
    event ResponderAuthorized(
        address indexed responder,
        string name,
        string organization,
        uint256 authorizationLevel
    );
    
    event FundsDeposited(address indexed depositor, uint256 amount);
    
    // Modifiers
    modifier onlyAuthorizedResponder() {
        require(authorizedResponders[msg.sender].responderAddress != address(0), "Not an authorized responder");
        require(authorizedResponders[msg.sender].isActive, "Responder not active");
        _;
    }
    
    modifier validRequest(uint256 _requestId) {
        require(_requestId > 0 && _requestId <= _requestIdCounter.current(), "Invalid request ID");
        _;
    }
    
    modifier validAllocation(uint256 _allocationId) {
        require(_allocationId > 0 && _allocationId <= _allocationIdCounter.current(), "Invalid allocation ID");
        _;
    }
    
    modifier sufficientAuthorization(uint256 _level) {
        require(authorizedResponders[msg.sender].authorizationLevel >= _level, "Insufficient authorization level");
        _;
    }
    
    /**
     * @dev Authorize a new emergency responder
     */
    function authorizeResponder(
        address _responder,
        string memory _name,
        string memory _organization,
        uint256 _authorizationLevel
    ) external onlyOwner {
        require(_responder != address(0), "Invalid responder address");
        require(_authorizationLevel >= 1 && _authorizationLevel <= 5, "Invalid authorization level");
        
        authorizedResponders[_responder] = AuthorizedResponder({
            responderAddress: _responder,
            name: _name,
            organization: _organization,
            isActive: true,
            authorizationLevel: _authorizationLevel
        });
        
        emit ResponderAuthorized(_responder, _name, _organization, _authorizationLevel);
    }
    
    /**
     * @dev Create an emergency event
     */
    function createEmergencyEvent(
        string memory _eventType,
        string memory _location,
        Priority _severity,
        uint256 _budget
    ) external onlyAuthorizedResponder sufficientAuthorization(3) {
        uint256 eventId = uint256(keccak256(abi.encodePacked(_eventType, _location, block.timestamp)));
        
        emergencyEvents[eventId] = EmergencyEvent({
            id: eventId,
            eventType: _eventType,
            location: _location,
            severity: _severity,
            startTime: block.timestamp,
            endTime: 0,
            active: true,
            totalBudget: _budget,
            usedBudget: 0
        });
        
        emit EmergencyEventCreated(eventId, _eventType, _location, _severity);
    }
    
    /**
     * @dev Request emergency resources
     */
    function requestResources(
        string memory _location,
        ResourceType _resourceType,
        uint256 _quantity,
        Priority _priority,
        string memory _description
    ) external nonReentrant {
        require(_quantity > 0, "Quantity must be greater than 0");
        
        _requestIdCounter.increment();
        uint256 newRequestId = _requestIdCounter.current();
        
        resourceRequests[newRequestId] = ResourceRequest({
            id: newRequestId,
            requester: msg.sender,
            location: _location,
            resourceType: _resourceType,
            quantity: _quantity,
            priority: _priority,
            description: _description,
            timestamp: block.timestamp,
            status: RequestStatus.PENDING,
            approvedQuantity: 0,
            rejectionReason: ""
        });
        
        locationToRequests[_location].push(newRequestId);
        userRequests[msg.sender].push(newRequestId);
        
        emit ResourceRequested(
            newRequestId,
            msg.sender,
            _location,
            _resourceType,
            _quantity,
            _priority
        );
    }
    
    /**
     * @dev Approve a resource request
     */
    function approveRequest(
        uint256 _requestId,
        uint256 _approvedQuantity
    ) external onlyAuthorizedResponder validRequest(_requestId) {
        ResourceRequest storage request = resourceRequests[_requestId];
        require(request.status == RequestStatus.PENDING, "Request not pending");
        require(_approvedQuantity <= request.quantity, "Approved quantity exceeds requested");
        
        // Check if we have enough resources
        require(
            availableResources[request.resourceType] >= _approvedQuantity,
            "Insufficient available resources"
        );
        
        request.status = RequestStatus.APPROVED;
        request.approvedQuantity = _approvedQuantity;
        
        // Reserve the resources
        availableResources[request.resourceType] -= _approvedQuantity;
        reservedResources[request.resourceType] += _approvedQuantity;
        
        emit RequestApproved(_requestId, _approvedQuantity, msg.sender);
    }
    
    /**
     * @dev Reject a resource request
     */
    function rejectRequest(
        uint256 _requestId,
        string memory _reason
    ) external onlyAuthorizedResponder validRequest(_requestId) {
        ResourceRequest storage request = resourceRequests[_requestId];
        require(request.status == RequestStatus.PENDING, "Request not pending");
        
        request.status = RequestStatus.REJECTED;
        request.rejectionReason = _reason;
        
        emit RequestRejected(_requestId, _reason, msg.sender);
    }
    
    /**
     * @dev Allocate resources to approved request
     */
    function allocateResources(
        uint256 _requestId,
        address _supplier,
        uint256 _cost,
        string memory _trackingInfo
    ) external onlyAuthorizedResponder validRequest(_requestId) sufficientAuthorization(2) nonReentrant {
        ResourceRequest storage request = resourceRequests[_requestId];
        require(request.status == RequestStatus.APPROVED, "Request not approved");
        require(_cost <= emergencyFund, "Insufficient emergency fund");
        
        _allocationIdCounter.increment();
        uint256 newAllocationId = _allocationIdCounter.current();
        
        resourceAllocations[newAllocationId] = ResourceAllocation({
            id: newAllocationId,
            requestId: _requestId,
            supplier: _supplier,
            allocatedQuantity: request.approvedQuantity,
            cost: _cost,
            timestamp: block.timestamp,
            delivered: false,
            trackingInfo: _trackingInfo
        });
        
        // Update request status
        request.status = RequestStatus.FULFILLED;
        
        // Update emergency fund
        emergencyFund -= _cost;
        
        // Update reserved resources
        reservedResources[request.resourceType] -= request.approvedQuantity;
        
        emit ResourceAllocated(
            newAllocationId,
            _requestId,
            _supplier,
            request.approvedQuantity,
            _cost
        );
    }
    
    /**
     * @dev Mark resources as delivered
     */
    function markDelivered(
        uint256 _allocationId,
        string memory _deliveryProof
    ) external onlyAuthorizedResponder validAllocation(_allocationId) {
        ResourceAllocation storage allocation = resourceAllocations[_allocationId];
        require(!allocation.delivered, "Already marked as delivered");
        
        allocation.delivered = true;
        allocation.trackingInfo = _deliveryProof;
        
        emit ResourceDelivered(_allocationId, _deliveryProof);
    }
    
    /**
     * @dev Add resources to inventory
     */
    function addResources(
        ResourceType _resourceType,
        uint256 _quantity
    ) external onlyAuthorizedResponder sufficientAuthorization(2) {
        availableResources[_resourceType] += _quantity;
    }
    
    /**
     * @dev Deposit funds to emergency fund
     */
    function depositEmergencyFund() external payable {
        require(msg.value > 0, "Amount must be greater than 0");
        emergencyFund += msg.value;
        emit FundsDeposited(msg.sender, msg.value);
    }
    
    /**
     * @dev Get requests by location
     */
    function getRequestsByLocation(string memory _location) external view returns (uint256[] memory) {
        return locationToRequests[_location];
    }
    
    /**
     * @dev Get user's requests
     */
    function getUserRequests(address _user) external view returns (uint256[] memory) {
        return userRequests[_user];
    }
    
    /**
     * @dev Get pending requests by priority
     */
    function getPendingRequestsByPriority(Priority _priority) external view returns (uint256[] memory) {
        uint256[] memory pendingRequests = new uint256[](_requestIdCounter.current());
        uint256 count = 0;
        
        for (uint256 i = 1; i <= _requestIdCounter.current(); i++) {
            if (resourceRequests[i].status == RequestStatus.PENDING && 
                resourceRequests[i].priority == _priority) {
                pendingRequests[count] = i;
                count++;
            }
        }
        
        // Resize array
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = pendingRequests[i];
        }
        
        return result;
    }
    
    /**
     * @dev Get resource inventory
     */
    function getResourceInventory() external view returns (
        uint256[6] memory available,
        uint256[6] memory reserved
    ) {
        for (uint256 i = 0; i < 6; i++) {
            available[i] = availableResources[ResourceType(i)];
            reserved[i] = reservedResources[ResourceType(i)];
        }
    }
    
    /**
     * @dev Toggle responder status
     */
    function toggleResponderStatus(address _responder) external onlyOwner {
        require(authorizedResponders[_responder].responderAddress != address(0), "Responder not found");
        authorizedResponders[_responder].isActive = !authorizedResponders[_responder].isActive;
    }
}
