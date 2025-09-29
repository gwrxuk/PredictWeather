// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title WeatherDataRegistry
 * @dev Smart contract for storing and verifying weather data on blockchain
 */
contract WeatherDataRegistry is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _dataIdCounter;
    
    struct WeatherData {
        uint256 id;
        string location;
        int256 temperature; // in Celsius * 100 (to handle decimals)
        uint256 humidity; // percentage
        uint256 pressure; // in hPa
        uint256 windSpeed; // in km/h * 100
        uint256 precipitation; // in mm * 100
        string weatherType; // "sunny", "rainy", "stormy", etc.
        uint256 timestamp;
        address reporter;
        bool verified;
        uint256 verificationCount;
        string ipfsHash; // for storing additional data
    }
    
    struct WeatherStation {
        address stationAddress;
        string name;
        string location;
        bool isActive;
        uint256 reputationScore;
        uint256 totalReports;
    }
    
    // Mappings
    mapping(uint256 => WeatherData) public weatherData;
    mapping(address => WeatherStation) public weatherStations;
    mapping(uint256 => mapping(address => bool)) public hasVerified;
    mapping(string => uint256[]) public locationToDataIds;
    
    // Arrays
    address[] public registeredStations;
    uint256[] public allDataIds;
    
    // Events
    event WeatherDataSubmitted(
        uint256 indexed dataId,
        string location,
        address indexed reporter,
        uint256 timestamp
    );
    
    event WeatherDataVerified(
        uint256 indexed dataId,
        address indexed verifier,
        uint256 verificationCount
    );
    
    event WeatherStationRegistered(
        address indexed stationAddress,
        string name,
        string location
    );
    
    event WeatherStationStatusChanged(
        address indexed stationAddress,
        bool isActive
    );
    
    // Modifiers
    modifier onlyRegisteredStation() {
        require(weatherStations[msg.sender].stationAddress != address(0), "Not a registered weather station");
        require(weatherStations[msg.sender].isActive, "Weather station is not active");
        _;
    }
    
    modifier validDataId(uint256 _dataId) {
        require(_dataId > 0 && _dataId <= _dataIdCounter.current(), "Invalid data ID");
        _;
    }
    
    /**
     * @dev Register a new weather station
     */
    function registerWeatherStation(
        address _stationAddress,
        string memory _name,
        string memory _location
    ) external onlyOwner {
        require(_stationAddress != address(0), "Invalid station address");
        require(weatherStations[_stationAddress].stationAddress == address(0), "Station already registered");
        
        weatherStations[_stationAddress] = WeatherStation({
            stationAddress: _stationAddress,
            name: _name,
            location: _location,
            isActive: true,
            reputationScore: 100,
            totalReports: 0
        });
        
        registeredStations.push(_stationAddress);
        
        emit WeatherStationRegistered(_stationAddress, _name, _location);
    }
    
    /**
     * @dev Submit weather data
     */
    function submitWeatherData(
        string memory _location,
        int256 _temperature,
        uint256 _humidity,
        uint256 _pressure,
        uint256 _windSpeed,
        uint256 _precipitation,
        string memory _weatherType,
        string memory _ipfsHash
    ) external onlyRegisteredStation nonReentrant {
        _dataIdCounter.increment();
        uint256 newDataId = _dataIdCounter.current();
        
        weatherData[newDataId] = WeatherData({
            id: newDataId,
            location: _location,
            temperature: _temperature,
            humidity: _humidity,
            pressure: _pressure,
            windSpeed: _windSpeed,
            precipitation: _precipitation,
            weatherType: _weatherType,
            timestamp: block.timestamp,
            reporter: msg.sender,
            verified: false,
            verificationCount: 0,
            ipfsHash: _ipfsHash
        });
        
        allDataIds.push(newDataId);
        locationToDataIds[_location].push(newDataId);
        
        // Update station stats
        weatherStations[msg.sender].totalReports++;
        
        emit WeatherDataSubmitted(newDataId, _location, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Verify weather data
     */
    function verifyWeatherData(uint256 _dataId) external onlyRegisteredStation validDataId(_dataId) {
        require(!hasVerified[_dataId][msg.sender], "Already verified by this station");
        require(weatherData[_dataId].reporter != msg.sender, "Cannot verify own data");
        
        hasVerified[_dataId][msg.sender] = true;
        weatherData[_dataId].verificationCount++;
        
        // Auto-verify if enough verifications (3 or more)
        if (weatherData[_dataId].verificationCount >= 3) {
            weatherData[_dataId].verified = true;
            
            // Increase reputation of original reporter
            weatherStations[weatherData[_dataId].reporter].reputationScore += 10;
        }
        
        emit WeatherDataVerified(_dataId, msg.sender, weatherData[_dataId].verificationCount);
    }
    
    /**
     * @dev Get weather data by ID
     */
    function getWeatherData(uint256 _dataId) external view validDataId(_dataId) returns (WeatherData memory) {
        return weatherData[_dataId];
    }
    
    /**
     * @dev Get weather data by location
     */
    function getWeatherDataByLocation(string memory _location) external view returns (uint256[] memory) {
        return locationToDataIds[_location];
    }
    
    /**
     * @dev Get recent weather data (last 24 hours)
     */
    function getRecentWeatherData() external view returns (uint256[] memory) {
        uint256[] memory recentData = new uint256[](allDataIds.length);
        uint256 count = 0;
        uint256 oneDayAgo = block.timestamp - 86400; // 24 hours
        
        for (uint256 i = allDataIds.length; i > 0; i--) {
            uint256 dataId = allDataIds[i - 1];
            if (weatherData[dataId].timestamp >= oneDayAgo) {
                recentData[count] = dataId;
                count++;
            } else {
                break; // Data is ordered by time, so we can break here
            }
        }
        
        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = recentData[i];
        }
        
        return result;
    }
    
    /**
     * @dev Toggle weather station status
     */
    function toggleStationStatus(address _stationAddress) external onlyOwner {
        require(weatherStations[_stationAddress].stationAddress != address(0), "Station not registered");
        
        weatherStations[_stationAddress].isActive = !weatherStations[_stationAddress].isActive;
        
        emit WeatherStationStatusChanged(_stationAddress, weatherStations[_stationAddress].isActive);
    }
    
    /**
     * @dev Get total number of data entries
     */
    function getTotalDataCount() external view returns (uint256) {
        return _dataIdCounter.current();
    }
    
    /**
     * @dev Get all registered stations
     */
    function getAllStations() external view returns (address[] memory) {
        return registeredStations;
    }
}
