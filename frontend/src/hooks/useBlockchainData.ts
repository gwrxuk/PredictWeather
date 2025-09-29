import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import { useWeb3 } from '../contexts/Web3Context';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface BlockchainStatus {
  connected: boolean;
  network: string;
  account: string | null;
  balance: number;
  contracts: {
    weather_data_registry: boolean;
    weather_insurance: boolean;
    emergency_resource: boolean;
  };
}

interface WeatherDataSubmission {
  location: string;
  temperature: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  precipitation: number;
  weather_type: string;
  ipfs_hash?: string;
}

interface InsurancePolicy {
  location: string;
  event_type: number;
  coverage_amount: number;
  threshold: number;
  duration: number;
  premium: number;
}

interface ResourceRequest {
  location: string;
  resource_type: number;
  quantity: number;
  priority: number;
  description: string;
}

const fetchBlockchainStatus = async (): Promise<BlockchainStatus> => {
  const response = await axios.get(`${API_BASE_URL}/blockchain/status`);
  return response.data;
};

const fetchWeatherDataFromBlockchain = async (dataId: number) => {
  const response = await axios.get(`${API_BASE_URL}/blockchain/weather/${dataId}`);
  return response.data;
};

const fetchRecentWeatherData = async () => {
  const response = await axios.get(`${API_BASE_URL}/blockchain/weather/recent`);
  return response.data;
};

const fetchUserPolicies = async (userAddress: string) => {
  const response = await axios.get(`${API_BASE_URL}/blockchain/insurance/policies/${userAddress}`);
  return response.data;
};

const fetchResourceInventory = async () => {
  const response = await axios.get(`${API_BASE_URL}/blockchain/emergency/inventory`);
  return response.data;
};

const fetchPendingRequests = async (priority?: number) => {
  const response = await axios.get(`${API_BASE_URL}/blockchain/emergency/requests/pending`, {
    params: priority !== undefined ? { priority } : {}
  });
  return response.data;
};

export const useBlockchainData = () => {
  return useQuery(
    ['blockchain', 'status'],
    fetchBlockchainStatus,
    {
      refetchInterval: 30 * 1000, // Refetch every 30 seconds
      staleTime: 15 * 1000, // Consider data stale after 15 seconds
      onError: (error) => {
        console.error('Error fetching blockchain status:', error);
      }
    }
  );
};

export const useWeatherDataFromBlockchain = (dataId: number) => {
  return useQuery(
    ['blockchain', 'weather', dataId],
    () => fetchWeatherDataFromBlockchain(dataId),
    {
      enabled: !!dataId,
      staleTime: 5 * 60 * 1000, // Consider data stale after 5 minutes
      onError: (error) => {
        console.error('Error fetching weather data from blockchain:', error);
      }
    }
  );
};

export const useRecentWeatherData = () => {
  return useQuery(
    ['blockchain', 'weather', 'recent'],
    fetchRecentWeatherData,
    {
      refetchInterval: 2 * 60 * 1000, // Refetch every 2 minutes
      staleTime: 1 * 60 * 1000, // Consider data stale after 1 minute
      onError: (error) => {
        console.error('Error fetching recent weather data:', error);
      }
    }
  );
};

export const useUserPolicies = (userAddress?: string) => {
  return useQuery(
    ['blockchain', 'insurance', 'policies', userAddress],
    () => fetchUserPolicies(userAddress!),
    {
      enabled: !!userAddress,
      staleTime: 5 * 60 * 1000, // Consider data stale after 5 minutes
      onError: (error) => {
        console.error('Error fetching user policies:', error);
      }
    }
  );
};

export const useResourceInventory = () => {
  return useQuery(
    ['blockchain', 'emergency', 'inventory'],
    fetchResourceInventory,
    {
      refetchInterval: 1 * 60 * 1000, // Refetch every minute
      staleTime: 30 * 1000, // Consider data stale after 30 seconds
      onError: (error) => {
        console.error('Error fetching resource inventory:', error);
      }
    }
  );
};

export const usePendingRequests = (priority?: number) => {
  return useQuery(
    ['blockchain', 'emergency', 'requests', 'pending', priority],
    () => fetchPendingRequests(priority),
    {
      refetchInterval: 30 * 1000, // Refetch every 30 seconds
      staleTime: 15 * 1000, // Consider data stale after 15 seconds
      onError: (error) => {
        console.error('Error fetching pending requests:', error);
      }
    }
  );
};

// Mutation hooks for blockchain operations
export const useSubmitWeatherDataToBlockchain = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async (data: WeatherDataSubmission) => {
      const response = await axios.post(`${API_BASE_URL}/blockchain/weather/submit`, data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['blockchain', 'weather']);
      },
      onError: (error) => {
        console.error('Error submitting weather data to blockchain:', error);
      }
    }
  );
};

export const useVerifyWeatherData = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async (dataId: number) => {
      const response = await axios.post(`${API_BASE_URL}/blockchain/weather/${dataId}/verify`);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['blockchain', 'weather']);
      },
      onError: (error) => {
        console.error('Error verifying weather data:', error);
      }
    }
  );
};

export const useCreateInsurancePolicy = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async (policy: InsurancePolicy) => {
      const response = await axios.post(`${API_BASE_URL}/blockchain/insurance/policy`, policy);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['blockchain', 'insurance']);
      },
      onError: (error) => {
        console.error('Error creating insurance policy:', error);
      }
    }
  );
};

export const useSubmitInsuranceClaim = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async ({ policyId, dataId }: { policyId: number; dataId: number }) => {
      const response = await axios.post(`${API_BASE_URL}/blockchain/insurance/claim`, null, {
        params: { policy_id: policyId, data_id: dataId }
      });
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['blockchain', 'insurance']);
      },
      onError: (error) => {
        console.error('Error submitting insurance claim:', error);
      }
    }
  );
};

export const useRequestEmergencyResources = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async (request: ResourceRequest) => {
      const response = await axios.post(`${API_BASE_URL}/blockchain/emergency/request`, request);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['blockchain', 'emergency']);
      },
      onError: (error) => {
        console.error('Error requesting emergency resources:', error);
      }
    }
  );
};

export const useApproveResourceRequest = () => {
  const queryClient = useQueryClient();

  return useMutation(
    async ({ requestId, approvedQuantity }: { requestId: number; approvedQuantity: number }) => {
      const response = await axios.post(`${API_BASE_URL}/blockchain/emergency/approve/${requestId}`, null, {
        params: { approved_quantity: approvedQuantity }
      });
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['blockchain', 'emergency']);
      },
      onError: (error) => {
        console.error('Error approving resource request:', error);
      }
    }
  );
};

// Hook for contract addresses
export const useContractAddresses = () => {
  return useQuery(
    ['blockchain', 'contracts', 'addresses'],
    async () => {
      const response = await axios.get(`${API_BASE_URL}/blockchain/contracts/addresses`);
      return response.data;
    },
    {
      staleTime: Infinity, // Contract addresses don't change
      onError: (error) => {
        console.error('Error fetching contract addresses:', error);
      }
    }
  );
};
