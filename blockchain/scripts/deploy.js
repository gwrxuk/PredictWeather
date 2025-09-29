const { ethers } = require("hardhat");

async function main() {
  console.log("Starting deployment of WeatherGuard contracts...");
  
  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy WeatherDataRegistry
  console.log("\n1. Deploying WeatherDataRegistry...");
  const WeatherDataRegistry = await ethers.getContractFactory("WeatherDataRegistry");
  const weatherDataRegistry = await WeatherDataRegistry.deploy();
  await weatherDataRegistry.deployed();
  console.log("WeatherDataRegistry deployed to:", weatherDataRegistry.address);

  // Deploy WeatherInsurance
  console.log("\n2. Deploying WeatherInsurance...");
  const WeatherInsurance = await ethers.getContractFactory("WeatherInsurance");
  const weatherInsurance = await WeatherInsurance.deploy(weatherDataRegistry.address);
  await weatherInsurance.deployed();
  console.log("WeatherInsurance deployed to:", weatherInsurance.address);

  // Deploy EmergencyResourceAllocation
  console.log("\n3. Deploying EmergencyResourceAllocation...");
  const EmergencyResourceAllocation = await ethers.getContractFactory("EmergencyResourceAllocation");
  const emergencyResourceAllocation = await EmergencyResourceAllocation.deploy();
  await emergencyResourceAllocation.deployed();
  console.log("EmergencyResourceAllocation deployed to:", emergencyResourceAllocation.address);

  // Initialize contracts with some sample data
  console.log("\n4. Initializing contracts...");
  
  // Register a sample weather station
  console.log("Registering sample weather station...");
  await weatherDataRegistry.registerWeatherStation(
    deployer.address,
    "Main Weather Station",
    "New York, NY"
  );
  
  // Authorize deployer as emergency responder
  console.log("Authorizing emergency responder...");
  await emergencyResourceAllocation.authorizeResponder(
    deployer.address,
    "Emergency Coordinator",
    "WeatherGuard Emergency Response",
    5 // Maximum authorization level
  );
  
  // Add some initial resources
  console.log("Adding initial emergency resources...");
  await emergencyResourceAllocation.addResources(0, 1000); // FOOD
  await emergencyResourceAllocation.addResources(1, 2000); // WATER
  await emergencyResourceAllocation.addResources(2, 500);  // MEDICAL
  await emergencyResourceAllocation.addResources(3, 100);  // SHELTER
  
  // Deposit initial funds to insurance pool
  console.log("Depositing initial funds to insurance pool...");
  await weatherInsurance.depositFunds({ value: ethers.utils.parseEther("10.0") });
  
  // Deposit initial emergency fund
  console.log("Depositing initial emergency fund...");
  await emergencyResourceAllocation.depositEmergencyFund({ value: ethers.utils.parseEther("5.0") });

  console.log("\n✅ Deployment completed successfully!");
  console.log("\n📋 Contract Addresses:");
  console.log("WeatherDataRegistry:", weatherDataRegistry.address);
  console.log("WeatherInsurance:", weatherInsurance.address);
  console.log("EmergencyResourceAllocation:", emergencyResourceAllocation.address);
  
  console.log("\n📝 Save these addresses to your .env file:");
  console.log(`WEATHER_DATA_REGISTRY_ADDRESS=${weatherDataRegistry.address}`);
  console.log(`WEATHER_INSURANCE_ADDRESS=${weatherInsurance.address}`);
  console.log(`EMERGENCY_RESOURCE_ADDRESS=${emergencyResourceAllocation.address}`);

  // Verify contracts on Etherscan (if not local network)
  if (network.name !== "localhost" && network.name !== "hardhat") {
    console.log("\n🔍 Verifying contracts on Etherscan...");
    
    try {
      await hre.run("verify:verify", {
        address: weatherDataRegistry.address,
        constructorArguments: [],
      });
      console.log("WeatherDataRegistry verified");
    } catch (error) {
      console.log("WeatherDataRegistry verification failed:", error.message);
    }

    try {
      await hre.run("verify:verify", {
        address: weatherInsurance.address,
        constructorArguments: [weatherDataRegistry.address],
      });
      console.log("WeatherInsurance verified");
    } catch (error) {
      console.log("WeatherInsurance verification failed:", error.message);
    }

    try {
      await hre.run("verify:verify", {
        address: emergencyResourceAllocation.address,
        constructorArguments: [],
      });
      console.log("EmergencyResourceAllocation verified");
    } catch (error) {
      console.log("EmergencyResourceAllocation verification failed:", error.message);
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });
