import axios from 'axios'

const API_BASE_URL = '/api/moA'

class ApiService {
  private static instance: ApiService
  private client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  private constructor() {
    this.setupInterceptors()
  }

  private setupInterceptors() {
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error)
        throw error
      }
    )
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService()
    }
    return ApiService.instance
  }

  public async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<T>(url, { params })
    return response.data
  }

  public async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data)
    return response.data
  }

  public async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data)
    return response.data
  }

  public async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url)
    return response.data
  }
}

export const apiService = ApiService.getInstance()