/**
 * API Client for TrailSaga backend
 * Provides a centralized way to make API requests with error handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Get profile ID from localStorage
   */
  private getProfileId(): string | null {
    if (typeof window === 'undefined') return null;
    const profile = localStorage.getItem('trailsaga-profile');
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
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${this.baseURL}/${cleanEndpoint}`;
  }

  /**
   * Make HTTP request with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = this.buildUrl(endpoint);
    
    // Get profile ID for authenticated requests
    const profileId = this.getProfileId();
    
    // Set default headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add profile ID to headers if available (for demo purposes)
    if (profileId) {
      headers['X-Profile-Id'] = profileId;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        if (!response.ok) {
          throw new ApiError(
            `HTTP ${response.status}: ${response.statusText}`,
            response.status
          );
        }
        return {} as T;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new ApiError(
          data.detail || data.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          data
        );
      }

      return data as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Network or other errors
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new ApiError(
          'Network error: Could not connect to the server. Please check if the backend is running.',
          0
        );
      }
      
      throw new ApiError(
        error instanceof Error ? error.message : 'Unknown error occurred',
        0,
        error
      );
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'GET',
    });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'DELETE',
    });
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

