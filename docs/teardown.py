#!/usr/bin/env python3
"""
FoundryIQ Teardown Script

Cleans up all Azure resources and local files created by the FoundryIQ demo.
Use this to remove everything when you're done with the demo.

Usage:
    python teardown.py                    # Interactive mode (recommended)
    python teardown.py --all              # Remove everything without prompts
    python teardown.py --local-only       # Only remove local files
    python teardown.py --azure-only       # Only remove Azure resources
    python teardown.py --dry-run          # Show what would be deleted
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.RED}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_warning(text: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_success(text: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print an info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def confirm(prompt: str, default: bool = False) -> bool:
    """Get yes/no confirmation from user."""
    default_str = "y/N" if not default else "Y/n"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    return response in ('y', 'yes')


def run_command(cmd: str, dry_run: bool = False, capture: bool = False) -> tuple:
    """Run a shell command."""
    if dry_run:
        print(f"  [DRY RUN] Would run: {cmd}")
        return (0, "", "")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        return (result.returncode, result.stdout, result.stderr)
    except Exception as e:
        return (1, "", str(e))


def load_env_file(project_path: str) -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    env_file = Path(project_path) / ".env"
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars


class TeardownManager:
    """Manages the teardown of FoundryIQ resources."""
    
    def __init__(self, project_path: str, dry_run: bool = False):
        self.project_path = Path(project_path)
        self.dry_run = dry_run
        self.env_vars = load_env_file(project_path)
        
    def get_azure_resources(self) -> dict:
        """Detect Azure resources from .env file."""
        resources = {
            'search_endpoint': self.env_vars.get('AZURE_SEARCH_ENDPOINT', ''),
            'search_index': self.env_vars.get('AZURE_SEARCH_INDEX_NAME', 'foundryiq-documents'),
            'openai_endpoint': self.env_vars.get('AZURE_OPENAI_ENDPOINT', ''),
        }
        
        # Extract service names from endpoints
        if resources['search_endpoint']:
            # https://myservice.search.windows.net -> myservice
            try:
                resources['search_service'] = resources['search_endpoint'].split('//')[1].split('.')[0]
            except:
                resources['search_service'] = ''
        else:
            resources['search_service'] = ''
            
        return resources
        
    def delete_search_index(self) -> bool:
        """Delete the Azure AI Search index."""
        resources = self.get_azure_resources()
        
        if not resources['search_endpoint']:
            print_warning("No Azure Search endpoint found in .env")
            return False
            
        index_name = resources['search_index']
        api_key = self.env_vars.get('AZURE_SEARCH_API_KEY', '')
        
        if not api_key:
            print_warning("No Azure Search API key found in .env")
            return False
            
        print_info(f"Deleting search index: {index_name}")
        
        cmd = f'''curl -s -X DELETE "{resources['search_endpoint']}/indexes/{index_name}?api-version=2023-11-01" -H "api-key: {api_key}"'''
        
        code, stdout, stderr = run_command(cmd, self.dry_run)
        
        if code == 0:
            print_success(f"Deleted search index: {index_name}")
            return True
        else:
            print_error(f"Failed to delete search index: {stderr}")
            return False
            
    def delete_container_app(self) -> bool:
        """Delete Azure Container App deployment."""
        print_info("Checking for Container Apps deployment...")
        
        # Try to find container app
        cmd = "az containerapp list --query \"[?contains(name, 'foundryiq')].{name:name, resourceGroup:resourceGroup}\" -o json 2>/dev/null"
        code, stdout, stderr = run_command(cmd, capture=True)
        
        if code != 0 or not stdout.strip() or stdout.strip() == '[]':
            print_info("No Container Apps deployment found")
            return True
            
        try:
            import json
            apps = json.loads(stdout)
            
            for app in apps:
                app_name = app.get('name', '')
                rg = app.get('resourceGroup', '')
                
                if app_name and rg:
                    print_info(f"Deleting Container App: {app_name}")
                    del_cmd = f"az containerapp delete --name {app_name} --resource-group {rg} --yes"
                    code, _, stderr = run_command(del_cmd, self.dry_run)
                    
                    if code == 0:
                        print_success(f"Deleted Container App: {app_name}")
                    else:
                        print_error(f"Failed to delete {app_name}: {stderr}")
                        
        except Exception as e:
            print_error(f"Error parsing Container Apps: {e}")
            return False
            
        return True
        
    def delete_container_environment(self) -> bool:
        """Delete Azure Container Apps environment."""
        print_info("Checking for Container Apps environment...")
        
        cmd = "az containerapp env list --query \"[?contains(name, 'foundryiq')].{name:name, resourceGroup:resourceGroup}\" -o json 2>/dev/null"
        code, stdout, stderr = run_command(cmd, capture=True)
        
        if code != 0 or not stdout.strip() or stdout.strip() == '[]':
            print_info("No Container Apps environment found")
            return True
            
        try:
            import json
            envs = json.loads(stdout)
            
            for env in envs:
                env_name = env.get('name', '')
                rg = env.get('resourceGroup', '')
                
                if env_name and rg:
                    print_info(f"Deleting Container Apps environment: {env_name}")
                    del_cmd = f"az containerapp env delete --name {env_name} --resource-group {rg} --yes"
                    code, _, stderr = run_command(del_cmd, self.dry_run)
                    
                    if code == 0:
                        print_success(f"Deleted environment: {env_name}")
                    else:
                        print_error(f"Failed to delete {env_name}: {stderr}")
                        
        except Exception as e:
            print_error(f"Error parsing environments: {e}")
            return False
            
        return True
        
    def delete_blob_storage(self) -> bool:
        """Delete blob storage container with uploaded documents."""
        print_info("Checking for blob storage...")
        
        # Look for storage account in .env or common patterns
        cmd = "az storage account list --query \"[?contains(name, 'foundryiq')].{name:name, resourceGroup:resourceGroup}\" -o json 2>/dev/null"
        code, stdout, stderr = run_command(cmd, capture=True)
        
        if code != 0 or not stdout.strip() or stdout.strip() == '[]':
            print_info("No FoundryIQ blob storage found")
            return True
            
        try:
            import json
            accounts = json.loads(stdout)
            
            for account in accounts:
                account_name = account.get('name', '')
                
                if account_name:
                    if confirm(f"Delete storage account '{account_name}'?"):
                        rg = account.get('resourceGroup', '')
                        del_cmd = f"az storage account delete --name {account_name} --resource-group {rg} --yes"
                        code, _, stderr = run_command(del_cmd, self.dry_run)
                        
                        if code == 0:
                            print_success(f"Deleted storage account: {account_name}")
                        else:
                            print_error(f"Failed to delete {account_name}: {stderr}")
                            
        except Exception as e:
            print_error(f"Error with storage accounts: {e}")
            return False
            
        return True
        
    def clean_local_files(self) -> bool:
        """Clean up local project files."""
        print_info("Cleaning local files...")
        
        items_to_clean = [
            ('files/', 'Uploaded documents'),
            ('frontend/node_modules/', 'Frontend dependencies'),
            ('frontend/dist/', 'Frontend build'),
            ('.venv/', 'Python virtual environment'),
            ('__pycache__/', 'Python cache'),
            ('src/__pycache__/', 'Source cache'),
            ('.env', 'Environment file (contains secrets)'),
        ]
        
        for item, description in items_to_clean:
            item_path = self.project_path / item
            
            if item_path.exists():
                if self.dry_run:
                    print(f"  [DRY RUN] Would delete: {item} ({description})")
                else:
                    try:
                        if item_path.is_dir():
                            shutil.rmtree(item_path)
                        else:
                            item_path.unlink()
                        print_success(f"Deleted: {item}")
                    except Exception as e:
                        print_error(f"Failed to delete {item}: {e}")
                        
        return True
        
    def stop_local_services(self) -> bool:
        """Stop any running local services."""
        print_info("Stopping local services...")
        
        # Kill Python/uvicorn processes on port 8000
        run_command("pkill -f 'uvicorn.*8000' 2>/dev/null", self.dry_run)
        
        # Kill Vite dev server on port 5173
        run_command("pkill -f 'vite.*5173' 2>/dev/null", self.dry_run)
        run_command("pkill -f 'node.*5173' 2>/dev/null", self.dry_run)
        
        # Kill any http.server on common ports
        run_command("pkill -f 'http.server' 2>/dev/null", self.dry_run)
        
        print_success("Stopped local services")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="FoundryIQ Teardown - Clean up demo resources"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Remove everything without prompts"
    )
    parser.add_argument(
        "--local-only", "-l",
        action="store_true",
        help="Only remove local files and stop services"
    )
    parser.add_argument(
        "--azure-only", "-z",
        action="store_true",
        help="Only remove Azure resources"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--project-path", "-p",
        default=os.getcwd(),
        help="Path to the FoundryIQ project"
    )
    
    args = parser.parse_args()
    
    print_header("FoundryIQ Teardown")
    
    if args.dry_run:
        print_warning("DRY RUN MODE - No changes will be made\n")
    
    manager = TeardownManager(args.project_path, args.dry_run)
    
    # Determine what to clean
    clean_azure = not args.local_only
    clean_local = not args.azure_only
    
    if not args.all and not args.dry_run:
        print("This script will help you clean up FoundryIQ resources.\n")
        
        if clean_azure:
            print(f"{Colors.BOLD}Azure resources that may be deleted:{Colors.END}")
            print("  • Azure AI Search index (foundryiq-documents)")
            print("  • Azure Container Apps deployment")
            print("  • Azure Container Apps environment")
            print("  • Blob storage (if created for documents)")
            print()
            
        if clean_local:
            print(f"{Colors.BOLD}Local items that may be deleted:{Colors.END}")
            print("  • /files folder (uploaded documents)")
            print("  • /frontend/node_modules")
            print("  • /.venv (virtual environment)")
            print("  • .env file (contains secrets)")
            print("  • Running services (API, frontend)")
            print()
        
        if not confirm("Do you want to proceed with teardown?"):
            print("\nTeardown cancelled.")
            return
    
    print()
    
    # Stop local services first
    if clean_local:
        print(f"\n{Colors.BOLD}[1/5] Stopping Local Services{Colors.END}")
        manager.stop_local_services()
    
    # Clean Azure resources
    if clean_azure:
        print(f"\n{Colors.BOLD}[2/5] Deleting Azure AI Search Index{Colors.END}")
        if args.all or confirm("Delete the Azure AI Search index?"):
            manager.delete_search_index()
        else:
            print_info("Skipping search index deletion")
            
        print(f"\n{Colors.BOLD}[3/5] Deleting Azure Container Apps{Colors.END}")
        if args.all or confirm("Delete Azure Container Apps deployment?"):
            manager.delete_container_app()
            manager.delete_container_environment()
        else:
            print_info("Skipping Container Apps deletion")
            
        print(f"\n{Colors.BOLD}[4/5] Checking Blob Storage{Colors.END}")
        if args.all or confirm("Check for and delete blob storage?"):
            manager.delete_blob_storage()
        else:
            print_info("Skipping blob storage")
    
    # Clean local files
    if clean_local:
        print(f"\n{Colors.BOLD}[5/5] Cleaning Local Files{Colors.END}")
        if args.all or confirm("Delete local files (node_modules, .venv, files/, .env)?"):
            manager.clean_local_files()
        else:
            print_info("Skipping local file cleanup")
    
    # Summary
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}Teardown complete!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    
    if not args.dry_run:
        print(f"""
{Colors.BOLD}What was cleaned:{Colors.END}
  • Stopped local API and frontend services
  • Deleted Azure AI Search index
  • Deleted Container Apps deployment (if any)
  • Removed local files and caches

{Colors.BOLD}Not deleted (manual cleanup may be needed):{Colors.END}
  • Azure OpenAI / AI Foundry resource (shared resource)
  • Azure AI Search service itself (only the index was deleted)
  • Azure resource group

{Colors.YELLOW}To completely remove Azure resources, delete the resource group:{Colors.END}
  az group delete --name <your-resource-group> --yes
""")


if __name__ == "__main__":
    main()
