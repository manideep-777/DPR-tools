/**
 * Authentication utility functions
 */

/**
 * Decode JWT token to check expiration
 */
export function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expirationTime = payload.exp * 1000; // Convert to milliseconds
    return Date.now() >= expirationTime;
  } catch (error) {
    console.error("Error decoding token:", error);
    return true; // Treat invalid tokens as expired
  }
}

/**
 * Get valid token or redirect to login
 * Note: The app stores token with key "access_token" in localStorage
 */
export function getValidToken(): string | null {
  const token = localStorage.getItem("access_token");
  
  if (!token) {
    return null;
  }
  
  if (isTokenExpired(token)) {
    localStorage.removeItem("access_token");
    return null;
  }
  
  return token;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getValidToken() !== null;
}
