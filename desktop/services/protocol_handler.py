"""
Protocol Handler Service

Parses oceanml:// URLs and extracts video ID and auth token.
"""

from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict


class ProtocolHandler:
    """Handles oceanml:// protocol URLs"""

    def __init__(self, protocol: str = "oceanml"):
        self.protocol = protocol

    def parse_url(self, url: str) -> Dict[str, Optional[str]]:
        """
        Parse oceanml:// URL and extract parameters.

        Args:
            url: Protocol URL (e.g., oceanml://annotate?video=123&token=abc)

        Returns:
            Dictionary with action, video_id, and token

        Raises:
            ValueError: If URL format is invalid

        Example:
            >>> handler = ProtocolHandler()
            >>> result = handler.parse_url("oceanml://annotate?video=123&token=abc")
            >>> result
            {'action': 'annotate', 'video_id': '123', 'token': 'abc'}
        """
        try:
            parsed = urlparse(url)

            # Check protocol
            if parsed.scheme != self.protocol:
                raise ValueError(
                    f"Invalid protocol. Expected '{self.protocol}://', got '{parsed.scheme}://'"
                )

            # Extract action (netloc part)
            action = parsed.netloc or parsed.path.split("/")[0]

            # Extract query parameters
            params = parse_qs(parsed.query)

            # Get video ID
            video_id = params.get("video", [None])[0]

            # Get auth token
            token = params.get("token", [None])[0]

            return {
                "action": action,
                "video_id": video_id,
                "token": token
            }

        except Exception as e:
            raise ValueError(f"Failed to parse URL: {e}")

    def validate_token(self, token: str) -> bool:
        """
        Basic JWT token format validation.

        Args:
            token: JWT token string

        Returns:
            True if token appears valid (has 3 parts), False otherwise
        """
        if not token:
            return False

        parts = token.split(".")
        return len(parts) == 3  # JWT has header.payload.signature

    def validate_params(self, params: Dict[str, Optional[str]]) -> bool:
        """
        Validate that required parameters are present.

        Args:
            params: Dictionary from parse_url()

        Returns:
            True if all required params present and valid
        """
        # Check action
        if not params.get("action"):
            print("❌ Missing action")
            return False

        # Check video ID
        if not params.get("video_id"):
            print("❌ Missing video_id")
            return False

        # Check token
        if not params.get("token"):
            print("❌ Missing token")
            return False

        if not self.validate_token(params["token"]):
            print("❌ Invalid token format")
            return False

        return True


def test_protocol_handler():
    """Test function for protocol handler"""
    handler = ProtocolHandler()

    # Test valid URL
    print("Test 1: Valid URL")
    try:
        result = handler.parse_url("oceanml://annotate?video=123&token=eyJ0.eyJ1.sig")
        print(f"  Result: {result}")
        print(f"  Valid: {handler.validate_params(result)}")
    except Exception as e:
        print(f"  Error: {e}")

    print()

    # Test URL with missing parameter
    print("Test 2: Missing token")
    try:
        result = handler.parse_url("oceanml://annotate?video=123")
        print(f"  Result: {result}")
        print(f"  Valid: {handler.validate_params(result)}")
    except Exception as e:
        print(f"  Error: {e}")

    print()

    # Test invalid protocol
    print("Test 3: Invalid protocol")
    try:
        result = handler.parse_url("http://example.com")
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    test_protocol_handler()
