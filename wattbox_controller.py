#!/usr/bin/env python3
"""
WattBox Controller - A simple tool to control WattBox outlets via HTTP
"""

import argparse
import os
import sys
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Suppress only the single InsecureRequestWarning from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def main():
    """Main function to control WattBox outlets"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Control WattBox outlets via HTTP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url http://172.16.19.184 --outlet 3 --action off
  %(prog)s -u http://172.16.19.184 -o 3 -a on --username admin --password pass
  
Environment Variables:
  WATTBOX_URL       Base URL of the WattBox (e.g., http://172.16.19.184)
  WATTBOX_USERNAME  Username for HTTP authentication
  WATTBOX_PASSWORD  Password for HTTP authentication
  WATTBOX_OUTLET    Default outlet number
  WATTBOX_ACTION    Default action (on/off/reset)
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        default=os.environ.get('WATTBOX_URL', 'http://172.16.19.184'),
        help='Base URL of the WattBox (default: %(default)s or WATTBOX_URL env var)'
    )
    
    parser.add_argument(
        '--username',
        default=os.environ.get('WATTBOX_USERNAME', 'wattbox'),
        help='Username for HTTP authentication (default: %(default)s or WATTBOX_USERNAME env var)'
    )
    
    parser.add_argument(
        '--password',
        default=os.environ.get('WATTBOX_PASSWORD', 'wattbox'),
        help='Password for HTTP authentication (default: %(default)s or WATTBOX_PASSWORD env var)'
    )
    
    parser.add_argument(
        '--outlet', '-o',
        type=int,
        default=os.environ.get('WATTBOX_OUTLET'),
        required=os.environ.get('WATTBOX_OUTLET') is None,
        help='Outlet number (required, or set WATTBOX_OUTLET env var)'
    )
    
    parser.add_argument(
        '--action', '-a',
        choices=['on', 'off', 'reset'],
        default=os.environ.get('WATTBOX_ACTION', 'off'),
        help='Action to perform on the outlet (default: %(default)s or WATTBOX_ACTION env var)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Remove trailing slash from URL if present
    base_url = args.url.rstrip('/')
    
    try:
        session = requests.Session()
        
        # Try to detect if we need HTTPS by making an initial request
        if args.verbose:
            print(f"Connecting to {base_url}...")
        
        # Make initial request without auth to detect protocol and auth type
        test_response = session.get(
            f"{base_url}/main",
            allow_redirects=False,
            verify=False,
            timeout=10
        )
        
        # If we get a redirect, check if it's to HTTPS
        if test_response.status_code in (301, 302, 303, 307, 308):
            redirect_url = test_response.headers.get('Location', '')
            if args.verbose:
                print(f"Detected redirect to: {redirect_url}")
            
            # If redirecting to HTTPS, update base_url
            if redirect_url.startswith('https://'):
                # Extract the base URL from the redirect
                from urllib.parse import urlparse
                parsed = urlparse(redirect_url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"
                if args.verbose:
                    print(f"Switching to HTTPS: {base_url}")
                
                # Make another test request to the HTTPS endpoint
                test_response = session.get(
                    f"{base_url}/main",
                    allow_redirects=False,
                    verify=False,
                    timeout=10
                )
        
        # Detect authentication type from WWW-Authenticate header
        www_auth = test_response.headers.get('WWW-Authenticate', '').lower()
        
        if 'digest' in www_auth:
            if args.verbose:
                print(f"Using Digest authentication")
            auth = HTTPDigestAuth(args.username, args.password)
        else:
            if args.verbose:
                print(f"Using Basic authentication")
            auth = HTTPBasicAuth(args.username, args.password)
        
        # Now authenticate with the correct protocol and auth type
        if args.verbose:
            print(f"Authenticating to {base_url}/main...")
        
        response = session.get(
            f"{base_url}/main",
            auth=auth,
            allow_redirects=True,
            verify=False,  # Ignore SSL certificate errors
            timeout=10
        )
        response.raise_for_status()
        
        if args.verbose:
            print(f"Authentication successful (Status: {response.status_code})")
            print(f"Final URL: {response.url}")
        
        # Send the outlet control command
        action_url = f"{base_url}/outlet/{args.action}?o={args.outlet}"
        
        if args.verbose:
            print(f"Sending command to {action_url}...")
        
        response = session.get(
            action_url,
            auth=auth,
            allow_redirects=True,
            verify=False,  # Ignore SSL certificate errors
            timeout=10
        )
        response.raise_for_status()
        
        if args.verbose:
            print(f"Command successful (Status: {response.status_code})")
        
        print(f"✓ Successfully executed '{args.action}' on outlet {args.outlet}")
        return 0
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}", file=sys.stderr)
        if args.verbose and hasattr(e.response, 'text'):
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        return 1
        
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection Error: Could not connect to {base_url}", file=sys.stderr)
        if args.verbose:
            print(f"Details: {e}", file=sys.stderr)
        return 1
        
    except requests.exceptions.Timeout as e:
        print(f"✗ Timeout Error: Request timed out", file=sys.stderr)
        return 1
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Request Error: {e}", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"✗ Unexpected Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())


