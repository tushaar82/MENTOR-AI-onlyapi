/**
 * AI Features Loading States and Error Handling
 * 
 * This utility provides centralized loading state management and error handling
 * for all AI features in the application. It includes retry logic,
 * timeout handling, and user-friendly error messages.
 * 
 * Author: Mentor AI Team
 * Version: 1.0.0
 */

import { useState, useCallback, useEffect, useRef } from 'react';

// Types
export interface LoadingState {
  isLoading: boolean;
  isRetrying: boolean;
  progress?: number;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  error: Error | null;
  message: string;
  code?: string;
  retryCount: number;
}

export interface AIRequestOptions {
  timeout?: number;
  maxRetries?: number;
  retryDelay?: number;
  onProgress?: (progress: number) => void;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  showRetry?: boolean;
  customErrorMessage?: string;
}

export interface AIRequestResult<T = any> {
  data: T | null;
  loading: LoadingState;
  error: ErrorState;
  execute: () => Promise<T | null>;
  reset: () => void;
  retry: () => Promise<T | null>;
}

// Default configuration
const DEFAULT_CONFIG = {
  timeout: 30000, // 30 seconds
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  retryBackoffMultiplier: 2,
};

// Error messages
const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network connection error. Please check your internet connection.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  SERVER_ERROR: 'Server error occurred. Please try again later.',
  AUTH_ERROR: 'Authentication error. Please log in again.',
  RATE_LIMIT_ERROR: 'Too many requests. Please wait a moment and try again.',
  AI_SERVICE_ERROR: 'AI service is temporarily unavailable. Please try again later.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
};

// Error code to message mapping
const getErrorMessage = (error: any): string => {
  if (!error) return ERROR_MESSAGES.UNKNOWN_ERROR;
  
  if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
    return ERROR_MESSAGES.NETWORK_ERROR;
  }
  
  if (error.code === 'TIMEOUT' || error.message?.includes('timeout')) {
    return ERROR_MESSAGES.TIMEOUT_ERROR;
  }
  
  if (error.code === 'ECONNABORTED') {
    return ERROR_MESSAGES.TIMEOUT_ERROR;
  }
  
  if (error.response?.status === 401 || error.code === 'AUTH_ERROR') {
    return ERROR_MESSAGES.AUTH_ERROR;
  }
  
  if (error.response?.status === 429) {
    return ERROR_MESSAGES.RATE_LIMIT_ERROR;
  }
  
  if (error.response?.status >= 500) {
    return ERROR_MESSAGES.SERVER_ERROR;
  }
  
  if (error.response?.status >= 400 && error.response?.status < 500) {
    return error.response?.data?.error?.message || error.message || ERROR_MESSAGES.UNKNOWN_ERROR;
  }
  
  // Check for AI service specific errors
  if (error.message?.includes('AI') || error.message?.includes('Gemini')) {
    return ERROR_MESSAGES.AI_SERVICE_ERROR;
  }
  
  return error.message || ERROR_MESSAGES.UNKNOWN_ERROR;
};

// Retry logic with exponential backoff
const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

const executeWithRetry = async <T>(
  requestFn: () => Promise<T>,
  options: AIRequestOptions
): Promise<T> => {
  const {
    maxRetries = DEFAULT_CONFIG.maxRetries,
    retryDelay = DEFAULT_CONFIG.retryDelay,
    timeout = DEFAULT_CONFIG.timeout,
  } = options;
  
  let lastError: Error;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Create timeout promise
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), timeout);
      });
      
      // Race between request and timeout
      const result = await Promise.race([requestFn(), timeoutPromise]);
      
      // If successful, return result
      return result;
      
    } catch (error: any) {
      lastError = error;
      
      // Don't retry on authentication errors
      if (error.response?.status === 401 || error.code === 'AUTH_ERROR') {
        throw error;
      }
      
      // Don't retry on the last attempt
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Calculate delay with exponential backoff
      const delay = retryDelay * Math.pow(DEFAULT_CONFIG.retryBackoffMultiplier, attempt);
      await sleep(delay);
    }
  }
  
  throw lastError!;
};

// Hook for managing AI request state
export const useAIRequest = <T = any>(
  requestFn: () => Promise<T>,
  options: AIRequestOptions = {}
): AIRequestResult<T> => {
  const [loading, setLoading] = useState<LoadingState>({
    isLoading: false,
    isRetrying: false,
  });
  
  const [error, setError] = useState<ErrorState>({
    hasError: false,
    error: null,
    message: '',
    retryCount: 0,
  });
  
  const [data, setData] = useState<T | null>(null);
  
  const requestRef = useRef(requestFn);
  const optionsRef = useRef(options);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // Update refs when dependencies change
  useEffect(() => {
    requestRef.current = requestFn;
    optionsRef.current = options;
  });
  
  const execute = useCallback(async (): Promise<T | null> => {
    try {
      // Cancel previous request if still running
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      // Create new abort controller
      abortControllerRef.current = new AbortController();
      
      // Reset state
      setLoading(prev => ({
        ...prev,
        isLoading: true,
        isRetrying: error.retryCount > 0,
        message: optionsRef.current.onProgress ? 'Processing...' : undefined,
      }));
      
      setError({
        hasError: false,
        error: null,
        message: '',
        retryCount: 0,
      });
      
      // Execute request with retry logic
      const result = await executeWithRetry(requestRef.current, {
        ...optionsRef.current,
        onProgress: (progress) => {
          setLoading(prev => ({
            ...prev,
            progress,
            message: optionsRef.current.onProgress ? `Processing... ${progress}%` : undefined,
          }));
          optionsRef.current.onProgress?.(progress);
        },
      });
      
      // Success
      setData(result);
      setLoading({
        isLoading: false,
        isRetrying: false,
      });
      
      optionsRef.current.onSuccess?.(result);
      
      return result;
      
    } catch (err: any) {
      // Handle error
      const errorMessage = optionsRef.current.customErrorMessage || getErrorMessage(err);
      
      setError({
        hasError: true,
        error: err,
        message: errorMessage,
        code: err.code,
        retryCount: error.retryCount + 1,
      });
      
      setLoading({
        isLoading: false,
        isRetrying: false,
      });
      
      optionsRef.current.onError?.(err);
      
      return null;
    }
  }, [error.retryCount]);
  
  const retry = useCallback(async (): Promise<T | null> => {
    return execute();
  }, [execute]);
  
  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    setLoading({
      isLoading: false,
      isRetrying: false,
    });
    
    setError({
      hasError: false,
      error: null,
      message: '',
      retryCount: 0,
    });
    
    setData(null);
  }, []);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);
  
  return {
    data,
    loading,
    error,
    execute,
    reset,
    retry,
  };
};

// Hook for managing multiple AI requests
export const useMultiAIRequest = <T = any>(
  requests: Array<{ key: string; fn: () => Promise<T>; options?: AIRequestOptions }>
) => {
  const [states, setStates] = useState<Record<string, AIRequestResult<T>>>({});
  const [overallLoading, setOverallLoading] = useState(false);
  const [hasAnyError, setHasAnyError] = useState(false);
  
  const executeAll = useCallback(async () => {
    setOverallLoading(true);
    setHasAnyError(false);
    
    const results: Record<string, T | null> = {};
    const newStates: Record<string, AIRequestResult<T>> = {};
    
    try {
      // Execute all requests in parallel
      const promises = requests.map(async ({ key, fn, options }) => {
        try {
          const result = await executeWithRetry(fn, options || {});
          results[key] = result;
          return { key, result, error: null };
        } catch (error) {
          results[key] = null;
          return { key, result: null, error };
        }
      });
      
      const responses = await Promise.all(promises);
      
      // Update states
      responses.forEach(({ key, result, error }) => {
        newStates[key] = {
          data: result,
          loading: { isLoading: false, isRetrying: false },
          error: {
            hasError: !!error,
            error: error as Error,
            message: error ? getErrorMessage(error) : '',
            retryCount: 0,
          },
          execute: async () => result,
          reset: () => {},
          retry: async () => result,
        };
      });
      
      setStates(newStates);
      setHasAnyError(responses.some(r => r.error));
      
    } catch (error) {
      console.error('Error in multi-request execution:', error);
      setHasAnyError(true);
    } finally {
      setOverallLoading(false);
    }
    
    return results;
  }, [requests]);
  
  return {
    states,
    overallLoading,
    hasAnyError,
    executeAll,
  };
};

// Utility functions
export const createAIRequest = <T>(
  requestFn: () => Promise<T>,
  options: AIRequestOptions = {}
) => {
  return executeWithRetry(requestFn, options);
};

export const isRetriableError = (error: any): boolean => {
  if (!error) return false;
  
  // Don't retry on authentication errors
  if (error.response?.status === 401 || error.code === 'AUTH_ERROR') {
    return false;
  }
  
  // Don't retry on client errors (4xx)
  if (error.response?.status >= 400 && error.response?.status < 500) {
    return false;
  }
  
  // Retry on network errors, timeouts, and server errors
  return true;
};

export const formatRetryMessage = (retryCount: number, maxRetries: number): string => {
  if (retryCount === 0) return '';
  if (retryCount >= maxRetries) return 'Max retries reached. Please try again later.';
  return `Retrying... (${retryCount}/${maxRetries})`;
};

// Export constants
export const AI_LOADING_CONFIG = DEFAULT_CONFIG;
export const AI_ERROR_MESSAGES = ERROR_MESSAGES;