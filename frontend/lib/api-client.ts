/**
 * API Client for TrailSaga – Hogwarts Expedition Series backend
 * Provides a centralized way to make API requests with error handling
 *
 * See api-types.ts for TypeScript type definitions that match the backend schemas
 */

import { logger } from './logger';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number, public data?: unknown) {
    super(message);
    this.name = "ApiError";
  }
}

class ApiClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
    logger.info('API Client initialized', { baseURL: this.baseURL }, 'ApiClient', 'INIT');
  }

  /**
   * Get profile ID from localStorage
   */
  private getProfileId(): string | null {
    if (typeof window === "undefined") return null;
    const profile = localStorage.getItem("trailsaga-profile");
    if (profile) {
      try {
        const parsed = JSON.parse(profile);
        return parsed.id || null;
      } catch {
        return null;
      }
    }
    return null;
  }

  /**
   * Build full URL from endpoint
   */
  private buildUrl(endpoint: string): string {
    // Remove leading slash if present to avoid double slashes
    const cleanEndpoint = endpoint.startsWith("/")
      ? endpoint.slice(1)
      : endpoint;
    return `${this.baseURL}/${cleanEndpoint}`;
  }

  /**
   * Make HTTP request with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    timeoutMs: number = 60000  // Default 60 seconds for all requests
  ): Promise<T> {
    const url = this.buildUrl(endpoint);
    const method = options.method || 'GET';
    const startTime = performance.now();

    // Get profile ID for authenticated requests
    const profileId = this.getProfileId();

    // Set default headers
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    // Add profile ID to headers if available (for demo purposes)
    if (profileId) {
      headers["X-Profile-Id"] = profileId;
    }

    // Log request
    let requestData: any = undefined;
    try {
      requestData = options.body ? JSON.parse(options.body as string) : undefined;
    } catch (e) {
      requestData = options.body;
    }
    logger.logApiRequest(method, url, { data: requestData, profileId }, 'ApiClient');

    // Create AbortController for timeout
    // Use longer timeout for story generation (60 seconds)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      const duration = performance.now() - startTime;

      // Handle non-OK responses first
      if (!response.ok) {
        // Try to parse as JSON for error details
        const contentType = response.headers.get("content-type");
        let errorData: any = null;
        
        if (contentType?.includes("application/json")) {
          try {
            errorData = await response.json();
          } catch (e) {
            // If JSON parsing fails, use status text
          }
        } else {
          // For non-JSON responses, read as text
          try {
            const text = await response.text();
            errorData = { message: text };
          } catch (e) {
            // If reading fails, use status text
          }
        }
        
        // Log detailed error information
        const errorInfo = {
          status: response.status,
          statusText: response.statusText,
          errorData,
          url,
          method,
        };
        logger.logApiError(method, url, errorInfo, 'ApiClient');
        
        // Extract error message
        const errorMessage = errorData?.detail || 
                           errorData?.message || 
                           errorData?.error ||
                           `HTTP ${response.status}: ${response.statusText}`;
        
        throw new ApiError(
          errorMessage,
          response.status,
          errorData
        );
      }

      // Handle non-JSON responses for successful requests
      const contentType = response.headers.get("content-type");
      if (!contentType?.includes("application/json")) {
        logger.logApiResponse(method, url, response.status, duration, { contentType }, 'ApiClient');
        return {} as T;
      }

      const data = await response.json();
      logger.logApiResponse(method, url, response.status, duration, { dataSize: JSON.stringify(data).length }, 'ApiClient');
      return data as T;
    } catch (error) {
      clearTimeout(timeoutId);
      const duration = performance.now() - startTime;
      
      if (error instanceof ApiError) {
        logger.logApiError(method, url, { status: error.status, duration }, 'ApiClient');
        throw error;
      }

      // Handle timeout/abort
      if (error instanceof Error && error.name === "AbortError") {
        logger.logApiError(method, url, { error: 'timeout', duration, timeoutMs }, 'ApiClient');
        throw new ApiError(
          "Request timeout: The server took too long to respond. This might be due to AI generation taking longer than expected.",
          0
        );
      }

      // Network or other errors
      if (error instanceof TypeError && error.message === "Failed to fetch") {
        logger.logApiError(method, url, { 
          error: 'network', 
          duration,
          errorMessage: error.message,
          errorName: error.name,
          stack: error.stack
        }, 'ApiClient');
        throw new ApiError(
          "Network error: Could not connect to the server. Please check if the backend is running on http://localhost:8000",
          0,
          { networkError: true, originalError: error.message }
        );
      }

      // Log all error details
      const errorDetails = {
        error: 'unknown',
        duration,
        errorMessage: error instanceof Error ? error.message : 'Unknown',
        errorName: error instanceof Error ? error.name : 'Unknown',
        errorType: typeof error,
        stack: error instanceof Error ? error.stack : undefined,
        fullError: String(error)
      };
      logger.logApiError(method, url, errorDetails, 'ApiClient');
      throw new ApiError(
        error instanceof Error ? error.message : "Unknown error occurred",
        0,
        error
      );
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, options?: RequestInit, timeoutMs?: number): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "GET",
    }, timeoutMs);
  }

  /**
   * POST request
   */
  async post<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestInit,
    timeoutMs?: number
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }, timeoutMs);
  }

  /**
   * PUT request
   */
  async put<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestInit
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "DELETE",
    });
  }

  /**
   * PATCH request
   */
  async patch<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestInit
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * Create a souvenir by completing a route
   */
  async createSouvenir(
    profileId: number,
    routeId: number,
    completedQuestIds: number[]
  ): Promise<RouteCompleteResponse> {
    return this.post<RouteCompleteResponse>(
      `api/profiles/${profileId}/souvenirs`,
      {
        route_id: routeId,
        completed_quest_ids: completedQuestIds,
      }
    );
  }

  /**
   * Get all souvenirs for a profile
   */
  async getSouvenirs(
    profileId: number,
    options?: {
      limit?: number;
      offset?: number;
      sort?: "newest" | "oldest" | "xp_high" | "xp_low";
    }
  ): Promise<SouvenirListResponse> {
    const params = new URLSearchParams();
    if (options?.limit) params.append("limit", String(options.limit));
    if (options?.offset) params.append("offset", String(options.offset));
    if (options?.sort) params.append("sort", options.sort);

    const queryString = params.toString();
    const endpoint = `api/profiles/${profileId}/souvenirs${queryString ? `?${queryString}` : ""}`;
    return this.get<SouvenirListResponse>(endpoint);
  }

  /**
   * Get a single souvenir by ID
   */
  async getSouvenir(
    profileId: number,
    souvenirId: number
  ): Promise<ApiSouvenir> {
    return this.get<ApiSouvenir>(
      `api/profiles/${profileId}/souvenirs/${souvenirId}`
    );
  }

  /**
   * Get profile details including user preferences
   */
  async getProfile(profileId: number): Promise<ApiProfile> {
    return this.get<ApiProfile>(
      `api/profiles/${profileId}`
    );
  }

  /**
   * Get aggregated statistics for a profile
   */
  async getProfileStatistics(profileId: number): Promise<ApiProfileStatistics> {
    return this.get<ApiProfileStatistics>(
      `api/profiles/${profileId}/statistics`
    );
  }

  /**
   * Submit negative feedback for a route recommendation
   */
  async submitFeedback(
    profileId: number,
    routeId: number,
    reason: string
  ): Promise<FeedbackResponse> {
    return this.post<FeedbackResponse>(
      `api/profiles/${profileId}/feedback`,
      {
        route_id: routeId,
        reason: reason,
      }
    );
  }

  /**
   * Get all achievement definitions
   */
  async getAchievements(): Promise<ApiAchievement[]> {
    return this.get<ApiAchievement[]>("api/achievements");
  }

  /**
   * Get user's achievements with unlock status
   */
  async getProfileAchievements(profileId: number): Promise<ApiProfileAchievement[]> {
    return this.get<ApiProfileAchievement[]>(`api/achievements/profiles/${profileId}`);
  }

  /**
   * Check and unlock achievements for a user
   */
  async checkAchievements(profileId: number): Promise<ApiAchievement[]> {
    return this.post<ApiAchievement[]>(`api/achievements/profiles/${profileId}/check`);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Re-export API types for convenience
export * from "./api-types";
import type {
  FeedbackResponse,
  RouteCompleteResponse,
  SouvenirListResponse,
  ApiSouvenir,
  ApiAchievement,
  ApiProfileAchievement,
  ApiProfileStatistics,
  ApiProfile,
} from "./api-types";
