"""
Email Security Breach Checker v2.0 - Cliente API HIBP

Autor: 686f6c61
Repositorio: https://github.com/686f6c61/email-security-breach-checker
Versión: 2.0
Fecha: 2025-11-20
Descripción: Módulo que proporciona una interfaz limpia para la API HIBP 
para verificar brechas de emails con manejo apropiado de errores y rate limiting.

Dirigido a: Comunidad de desarrolladores y profesionales de seguridad
Idioma: Español
Licencia: MIT
"""

import time
from typing import List, Dict, Any, Optional

import httpx

from config.settings import settings
from utils.exceptions import APIError, RateLimitError, AuthenticationError
from utils.logger import logger
from utils.cache import cache_manager


class HIBPClient:
    """Cliente para la API Have I Been Pwned."""
    
    def __init__(self):
        """Inicializar cliente HIBP con configuración."""
        self.base_url = settings.hibp_base_url
        self.api_key = settings.hibp_api_key
        self.rate_limit_delay = settings.hibp_rate_limit_delay
        self.timeout = settings.request_timeout
        self.last_request_time = 0
        
        # Configuración del cliente HTTP
        self.client = httpx.Client(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "hibp-api-key": self.api_key,
                "user-agent": f"{settings.app_name}/{settings.app_version}"
            }
        )
    
    def _rate_limit_wait(self) -> None:
        """Esperar si es necesario para respetar los límites de rate."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limiting: esperando {wait_time:.2f} segundos")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _handle_response(self, response: httpx.Response, email: str) -> List[Dict[str, Any]]:
        """
        Handle API response and return appropriate data or raise exceptions.
        
        Args:
            response: HTTP response from API
            email: Email being checked (for error messages)
            
        Returns:
            List of breach data or empty list if no breaches found
            
        Raises:
            APIError: For various API errors
            RateLimitError: When rate limit is exceeded
            AuthenticationError: When authentication fails
        """
        logger.debug(f"HIBP API response for {email}: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            # No breaches found - this is normal
            logger.info(f"No breaches found for {email}")
            return []
        elif response.status_code == 401:
            logger.error("HIBP API authentication failed")
            raise AuthenticationError("Invalid HIBP API key")
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', self.rate_limit_delay))
            logger.warning(f"Rate limit exceeded for {email}. Retry after {retry_after}s")
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {retry_after} seconds",
                retry_after=retry_after
            )
        elif response.status_code == 400:
            logger.error(f"Bad request for {email}: {response.text}")
            raise APIError(f"Bad request: {response.text}", response.status_code)
        elif response.status_code >= 500:
            logger.error(f"Server error for {email}: {response.status_code}")
            raise APIError(f"Server error: {response.status_code}", response.status_code)
        else:
            logger.error(f"Unexpected response for {email}: {response.status_code}")
            raise APIError(
                f"Unexpected response: {response.status_code}",
                response.status_code,
                {"response": response.text}
            )
    
    def check_email(self, email: str, use_cache: bool = True, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Check if email has been involved in any breaches.

        Args:
            email: Email address to check
            use_cache: Whether to use cached results if available
            max_retries: Maximum number of retries on rate limit (default: 3)

        Returns:
            List of breach data (empty if no breaches found)

        Raises:
            ValidationError: If email format is invalid
            APIError: For API-related errors
            RateLimitError: When rate limit is exceeded after all retries
            AuthenticationError: When authentication fails
        """
        logger.info(f"Checking breaches for email: {email}")

        # Check cache first
        if use_cache:
            cached_result = cache_manager.get(email)
            if cached_result is not None:
                logger.info(f"Using cached result for {email}")
                return cached_result

        # Retry logic for rate limiting
        for attempt in range(max_retries):
            # Respect rate limits
            self._rate_limit_wait()

            try:
                url = f"{self.base_url}/breachedaccount/{email}"
                params = {"truncateResponse": "false"}  # Get full breach details

                logger.debug(f"Making request to: {url} (attempt {attempt + 1}/{max_retries})")
                response = self.client.get(url, params=params)
                breaches = self._handle_response(response, email)

                # Cache the result
                if use_cache:
                    cache_manager.set(email, breaches)
                    logger.debug(f"Cached result for {email}")

                if breaches:
                    logger.info(f"Found {len(breaches)} breaches for {email}")
                else:
                    logger.info(f"No breaches found for {email}")

                return breaches

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    # Wait the requested time and retry
                    wait_time = e.retry_after if e.retry_after else self.rate_limit_delay
                    logger.info(f"Rate limit hit for {email}. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}")
                    time.sleep(wait_time)
                else:
                    # Max retries reached, raise the error
                    logger.error(f"Max retries reached for {email} after rate limiting")
                    raise
            except httpx.RequestError as e:
                logger.error(f"Request error for {email}: {str(e)}")
                raise APIError(f"Request failed: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error checking {email}: {str(e)}")
                raise

        # Should never reach here, but just in case
        raise APIError(f"Failed to check {email} after {max_retries} attempts")
    
    def check_multiple_emails(
        self, 
        emails: List[str], 
        use_cache: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check multiple emails for breaches.
        
        Args:
            emails: List of email addresses to check
            use_cache: Whether to use cached results if available
            
        Returns:
            Dictionary mapping emails to their breach data
        """
        logger.info(f"Checking {len(emails)} emails for breaches")
        results = {}
        
        for i, email in enumerate(emails, 1):
            try:
                logger.info(f"Processing email {i}/{len(emails)}: {email}")
                results[email] = self.check_email(email, use_cache)
            except Exception as e:
                logger.error(f"Failed to check {email}: {str(e)}")
                results[email] = None  # Indicate failure
        
        successful_checks = sum(1 for v in results.values() if v is not None)
        logger.info(f"Successfully checked {successful_checks}/{len(emails)} emails")
        
        return results
    
    def get_breach_details(self, breach_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific breach.
        
        Args:
            breach_name: Name of the breach to get details for
            
        Returns:
            Detailed breach information
        """
        logger.info(f"Getting details for breach: {breach_name}")
        
        self._rate_limit_wait()
        
        try:
            url = f"{self.base_url}/breach/{breach_name}"
            response = self.client.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise APIError(f"Breach not found: {breach_name}", 404)
            else:
                self._handle_response(response, breach_name)
                
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def close(self) -> None:
        """Close the HTTP client."""
        if hasattr(self.client, 'close'):
            self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()