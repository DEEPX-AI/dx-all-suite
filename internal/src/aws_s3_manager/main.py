### WARNING ###
'''
이 코드를 사용하기 위해서는 aws_config.properties에 AWS_ACCESS_KEY 및 AWS_SECRET_KEY 값을 셋업하거나, 환경변수로 설정한 뒤에 사용가능합니다.
또한, --s3-path 및 --save-location 인자를 필수로 제공해야 합니다.
선택적으로 --include-pattern을 여러 번 사용하여 특정 파일 패턴만 다운로드할 수 있습니다 (예: `--include-pattern "**/*.onnx"`).
선택적으로 --exclude-pattern을 여러 번 사용하여 특정 파일 패턴을 다운로드에서 제외할 수 있습니다 
(예: `--exclude-pattern "**/*.tar.gz" --exclude-pattern "**/*.dxnn"`).
exclude-pattern은 include-pattern보다 우선순위가 높습니다.

공개 배포는 엄격히 금지됩니다.
'''
### WARNING ###

import boto3
import requests
import os
import argparse
import sys
import math # For human_readable_size and progress bar
import fnmatch # For pattern matching

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"

def colored_print(message, level="INFO"):
    """Prints a colored log message based on its level."""
    if level == "ERROR":
        sys.stderr.write(f"{COLOR_RED}{message}{COLOR_RESET}\n")
    elif level == "WARNING":
        sys.stdout.write(f"{COLOR_YELLOW}{message}{COLOR_RESET}\n")
    elif level == "INFO":
        sys.stdout.write(f"{COLOR_GREEN}{message}{COLOR_RESET}\n")
    elif level == "DEBUG": # For potential future use
        sys.stdout.write(f"{COLOR_BLUE}{message}{COLOR_RESET}\n")
    else:
        sys.stdout.write(f"{message}\n")
    sys.stdout.flush()
    sys.stderr.flush() # Ensure error messages are flushed

def human_readable_size(size_bytes):
    """Converts a size in bytes to a human-readable format (e.g., KB, MB, GB)."""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█', print_end = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end   - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix}{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write(print_end)
        sys.stdout.flush()


class AWSS3FileUploader:
    def __init__(self, aws_cfg):
        self.aws_access_key_id = aws_cfg.get('AWS_ACCESS_KEY')
        self.aws_secret_access_key = aws_cfg.get('AWS_SECRET_KEY')
        self.region_name = aws_cfg.get('REGION_NAME')
        self.s3_bucket = aws_cfg.get('BUCKET_NAME')

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    def upload_s3_path(
        self,
        local_path,
        s3_path,
        include_patterns=None,
        exclude_patterns=None
    ):
        """
        Uploads files from a local path (file or directory) to a given S3 path,
        with options to include and exclude files by multiple patterns.
        Exclude patterns take precedence over include patterns.
        """
        if not os.path.exists(local_path):
            colored_print(f"ERROR: Local path '{local_path}' not found.", "ERROR")
            return False

        if os.path.isfile(local_path):
            # --- Pattern Matching Logic (Include then Exclude) ---
            if include_patterns:
                is_included = False
                for pattern in include_patterns:
                    if fnmatch.fnmatch(os.path.relpath(local_file_path), os.path.relpath(pattern)):
                        is_included = True
                        break
                if not is_included:
                    colored_print(f"INFO: Skipping {local_path} because it does not match any include pattern.", "INFO")
                    return True  # Not an error, just skipped

            if exclude_patterns:
                is_excluded = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(os.path.relpath(local_file_path), os.path.relpath(pattern)):
                        is_excluded = True
                        break
                if is_excluded:
                    colored_print(f"INFO: Skipping {local_path} due to exclude pattern match.", "INFO")
                    return True  # Not an error, just skipped

            return self._upload_single_file(local_path, s3_path)

        elif os.path.isdir(local_path):
            success = True
            for root, _, filenames in os.walk(local_path):
                for filename in filenames:
                    local_file_path = os.path.join(root, filename)
                    relative_local_file_apth = os.path.relpath(local_file_path, local_path)
                    s3_key = os.path.join(s3_path, relative_local_file_apth).replace("\\", "/")

                    # --- Pattern Matching Logic (Include then Exclude) ---
                    if include_patterns:
                        is_included = False
                        for pattern in include_patterns:
                            if fnmatch.fnmatch(os.path.relpath(local_file_path), os.path.relpath(pattern)):
                                is_included = True
                                break
                        if not is_included:
                            colored_print(f"INFO: Skipping {local_file_path} because it does not match any include pattern.", "INFO")
                            continue

                    if exclude_patterns:
                        for pattern in exclude_patterns:
                            if fnmatch.fnmatch(os.path.relpath(local_file_path), os.path.relpath(pattern)):
                                colored_print(f"INFO: Skipping {local_file_path} due to exclude pattern match.", "INFO")
                                continue
                    if not self._upload_single_file(local_file_path, s3_key):
                        success = False
            return success

        else:
            colored_print(f"ERROR: Invalid upload location: '{local_path}'. Must be a file or directory.", "ERROR")
            return False

    def _upload_single_file(self, local_file_path, s3_key):
        """Uploads a single file to S3 with a progress bar."""
        try:
            file_size = os.path.getsize(local_file_path)
            colored_print(f"INFO: Uploading {local_file_path} ({human_readable_size(file_size)}) to s3://{self.s3_bucket}/{s3_key}...", "INFO")

            with open(local_file_path, "rb") as f:
                self.s3_client.upload_fileobj(
                    f,
                    self.s3_bucket,
                    s3_key,
                    Callback=ProgressPercentage(local_file_path)
                )
            colored_print(f"SUCCESS: Successfully uploaded {local_file_path} to S3.", "INFO")
            return True
        except Exception as e:
            colored_print(f"ERROR: Failed to upload {local_file_path} to S3: {e}", "ERROR")
            return False


class ProgressPercentage(object):
    """A callback class that implements the progress bar for uploads."""
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._num_updates = 0  # Counter for updates

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        percentage = (self._seen_so_far / self._size) * 100
        if (self._num_updates % 100 == 0) or (self._seen_so_far == self._size):  # Update every 100 calls
            print_progress_bar(self._seen_so_far, self._size, prefix=f'Uploading {os.path.basename(self._filename)}:', suffix=f'({human_readable_size(self._seen_so_far)}/{human_readable_size(self._size)})', length=50)
        self._num_updates += 1


class AWSS3FileDownloader:
    def __init__(self, aws_cfg):
        # Initialize AWS credentials and other configurations from the provided dictionary
        self.aws_access_key_id = aws_cfg.get('AWS_ACCESS_KEY')
        self.aws_secret_access_key = aws_cfg.get('AWS_SECRET_KEY')
        self.region_name = aws_cfg.get('REGION_NAME')
        self.s3_bucket = aws_cfg.get('BUCKET_NAME')
        self.cloudfront_domain = aws_cfg.get('CLOUDFRONT_DOMAIN')

        # Initialize the boto3 S3 client with explicit credentials
        # This ensures the provided credentials take precedence over default AWS CLI configs or environment variables
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    def _download_single_file(self, s3_key, local_file_path):
        """
        Downloads a single file from CloudFront URL to a local path with progress bar.
        Returns True on success, False on failure.
        """
        download_url = f"https://{self.cloudfront_domain}/{s3_key}" 
        
        # Create any necessary local subdirectories for the file
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        colored_print(f"INFO: Downloading {download_url} to {local_file_path}...", "INFO")
        try:
            # Send a GET request to the CloudFront URL
            response = requests.get(download_url, stream=True)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            total_size = int(response.headers.get('content-length', 0))
            downloaded_bytes = 0

            # Initialize progress bar
            if total_size > 0:
                print_progress_bar(0, total_size, prefix='Progress:', suffix=f'({human_readable_size(0)}/{human_readable_size(total_size)})', length=50)
            else:
                sys.stdout.write(f'\rProgress: 0 B downloaded...')
                sys.stdout.flush()

            # Write the downloaded content to the local file
            with open(local_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk: # Filter out keep-alive new chunks
                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        if total_size > 0:
                            print_progress_bar(downloaded_bytes, total_size, prefix='Progress:', suffix=f'({human_readable_size(downloaded_bytes)}/{human_readable_size(total_size)})', length=50)
                        else:
                            sys.stdout.write(f'\rProgress: {human_readable_size(downloaded_bytes)} downloaded...')
                            sys.stdout.flush()
            
            # Final progress bar update and newline
            if total_size > 0:
                print_progress_bar(total_size, total_size, prefix='Progress:', suffix=f'({human_readable_size(total_size)}/{human_readable_size(total_size)})', length=50, print_end='\n')
            else:
                sys.stdout.write('\n')
                sys.stdout.flush()

            final_downloaded_size = os.path.getsize(local_file_path)

            if final_downloaded_size == 0:
                colored_print(f"ERROR: Downloaded file '{local_file_path}' is empty. This often indicates a server-side error or incorrect URL.", "ERROR")
                os.remove(local_file_path) # Remove empty file
                return False
            elif total_size > 0 and final_downloaded_size < total_size:
                colored_print(f"WARNING: Downloaded file size ({human_readable_size(final_downloaded_size)}) is less than expected ({human_readable_size(total_size)}). File might be incomplete.", "WARNING")
                os.remove(local_file_path)
                return False
            else:
                colored_print(f"SUCCESS: File successfully downloaded and saved to '{local_file_path}'. Size: {human_readable_size(final_downloaded_size)}.", "INFO")
                return True

        except requests.exceptions.RequestException as e:
            colored_print(f"ERROR: An HTTP/network error occurred during file download for {s3_key}: {e}", "ERROR")
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                colored_print(f"INFO: Removed incomplete file at '{local_file_path}'.", "INFO")
            return False
        except IOError as e:
            colored_print(f"ERROR: An error occurred while saving file {s3_key} to disk: {e}", "ERROR")
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                colored_print(f"INFO: Removed incomplete file at '{local_file_path}'.", "INFO")
            return False
        except Exception as e:
            colored_print(f"ERROR: An unexpected error occurred during download of {s3_key}: {e}", "ERROR")
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                colored_print(f"INFO: Removed incomplete file at '{local_file_path}'.", "INFO")
            return False

    def download_s3_path_via_cloudfront(
        self,
        s3_path, # Can be a prefix (folder) or a specific key (file)
        save_location,
        force,
        include_patterns=None, # New parameter for inclusion patterns
        exclude_patterns=None  # Existing parameter for exclusion patterns
    ):
        """
        Downloads files from a given S3 path (either a folder or a single file)
        via CloudFront URL, with options to include and exclude files by multiple patterns.
        Exclude patterns take precedence over include patterns.
        """

        # Ensure the save directory exists
        try:
            os.makedirs(save_location, exist_ok=True)
            colored_print(f"INFO: Created local download directory: {save_location}", "INFO")
        except OSError as e:
            colored_print(f"ERROR: Could not create save directory '{save_location}': {e}", "ERROR")
            return

        # --- Determine if s3_path is a file or a directory ---
        is_directory = False
        
        # Try to list objects starting with s3_path to determine its type
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.s3_bucket, Prefix=s3_path, MaxKeys=2)
            
            if 'Contents' not in response or not response['Contents']:
                # No objects found with this prefix/key
                colored_print(f"ERROR: S3 path '{s3_path}' not found in bucket '{self.s3_bucket}'.", "ERROR")
                sys.exit(1)
            
            # If there's only one item and its key exactly matches s3_path, it's a single file.
            # Otherwise, it's a directory (prefix for multiple files)
            if len(response['Contents']) == 1 and response['Contents'][0]['Key'] == s3_path:
                is_directory = False # It's a single file
            else:
                is_directory = True # It's a directory (prefix for one or more files)

        except Exception as e:
            colored_print(f"ERROR: Error determining S3 path type for '{s3_path}': {e}", "ERROR")
            sys.exit(1)
        
        if is_directory:
            # Ensure the prefix ends with a slash for listing contents correctly
            if not s3_path.endswith('/'):
                s3_path += '/'
                colored_print(f"INFO: Appended trailing slash to S3 path, treating as directory: '{s3_path}'", "INFO")
            
            colored_print(f"INFO: Detected S3 path '{s3_path}' as a directory. Downloading all contents.", "INFO")
            try:
                # List all objects under the given prefix
                response = self.s3_client.list_objects_v2(Bucket=self.s3_bucket, Prefix=s3_path)
            except Exception as e:
                colored_print(f"ERROR: Error listing objects in S3 bucket {self.s3_bucket} with prefix {s3_path}: {e}", "ERROR")
                sys.exit(1)

            if 'Contents' not in response or not response['Contents']:
                colored_print(f"WARNING: No files found in s3://{self.s3_bucket}/{s3_path}", "WARNING")
                return

            colored_print(f"INFO: Found {len(response['Contents'])} objects under s3://{self.s3_bucket}/{s3_path}", "INFO")

            for obj in response['Contents']:
                s3_key = obj['Key'] 
                
                # Skip the directory marker itself (e.g., 'res/onnx/')
                if s3_key == s3_path:
                    colored_print(f"DEBUG: Skipping directory marker: {s3_key}", "DEBUG")
                    continue

                # Local file path: use os.path.basename to get only the filename from s3_key
                s3_key_basename = os.path.basename(s3_key)

                if s3_key_basename == '': # Ensure it's not an empty string (e.g., if s3_key was "folder/")
                    colored_print(f"DEBUG: Skipping empty filename for S3 key: {s3_key}", "DEBUG")
                    continue

                local_file_path = os.path.join(save_location, s3_key.replace(s3_path, "", 1))
                
                # --- Pattern Matching Logic (Include then Exclude) ---
                # 1. Check include patterns first
                if include_patterns:
                    is_included = False
                    for pattern in include_patterns:
                        if fnmatch.fnmatch(s3_key, pattern):
                            is_included = True
                            break
                    if not is_included:
                        colored_print(f"INFO: Skipping {s3_key} because it does not match any include pattern.", "INFO")
                        continue # Skip this file if it's not explicitly included

                # 2. Check exclude patterns (higher priority)
                if exclude_patterns:
                    is_excluded = False
                    for pattern in exclude_patterns:
                        if fnmatch.fnmatch(s3_key, pattern):
                            is_excluded = True
                            break
                    if is_excluded:
                        colored_print(f"INFO: Skipping {s3_key} due to exclude pattern match.", "INFO")
                        continue # Skip this file if it's excluded

                # Check if the file exists and handle overwrite based on --force flag
                if os.path.exists(local_file_path):
                    if force:
                        colored_print(f"WARNING: File '{local_file_path}' already exists. Overwriting due to --force option.", "WARNING")
                        self._download_single_file(s3_key, local_file_path)
                    else:
                        colored_print(f"WARNING: File '{local_file_path}' already exists. Skipping download. Use --force to overwrite.", "WARNING")
                else:
                    self._download_single_file(s3_key, local_file_path)

        else: # It's a single file
            colored_print(f"INFO: Detected S3 path '{s3_path}' as a single file. Downloading.", "INFO")
            
            # Local file path: use os.path.basename to get only the filename from s3_path
            s3_key = response['Contents'][0]['Key']
            local_file_path = os.path.join(save_location, s3_key.replace(os.path.dirname(s3_key) + os.path.sep, "", 1))
            
            # --- Pattern Matching Logic (Include then Exclude) ---
            # 1. Check include patterns first
            if include_patterns:
                is_included = False
                for pattern in include_patterns:
                    if fnmatch.fnmatch(s3_path, pattern):
                        is_included = True
                        break
                if not is_included:
                    colored_print(f"INFO: Skipping {s3_path} because it does not match any include pattern.", "INFO")
                    return # Skip download and exit function

            # 2. Check exclude patterns (higher priority)
            if exclude_patterns:
                is_excluded = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(s3_path, pattern):
                        is_excluded = True
                        break
                if is_excluded:
                    colored_print(f"INFO: Skipping {s3_path} due to exclude pattern match.", "INFO")
                    return # Skip download and exit function

            # Check if the file exists and handle overwrite based on --force flag
            if os.path.exists(local_file_path):
                if force:
                    colored_print(f"WARNING: File '{local_file_path}' already exists. Overwriting due to --force option.", "WARNING")
                    self._download_single_file(s3_key, local_file_path)
                else:
                    colored_print(f"WARNING: File '{local_file_path}' already exists. Skipping download. Use --force to overwrite.", "WARNING")
            else:
                self._download_single_file(s3_key, local_file_path)


def _read_properties_file(filepath):
    """
    Reads key=value pairs from a properties file.
    Skips empty lines and lines starting with '#'.
    """
    properties = {}
    if not os.path.exists(filepath):
        return properties # Return empty if file not found

    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue # Skip empty lines and comments

                if '=' in line:
                    key, value = line.split('=', 1) # Split only on the first '='
                    properties[key.strip()] = value.strip()
    except Exception as e:
        colored_print(f"ERROR: Could not read properties file '{filepath}': {e}", "ERROR")
        return {} # Return empty properties on error
    return properties


def load_config_and_args():
    """
    Loads configuration settings with the following priority:
    CLI Arguments > Environment Variables > .properties File.
    The .properties file is read from the same directory as the script.
    """
    parser = argparse.ArgumentParser(description="Download files from AWS S3 via CloudFront.")
    subparsers = parser.add_subparsers(title='commands', dest='command', help='Available commands')

    # Download command
    download_parser = subparsers.add_parser('download', help='Download files from S3 via CloudFront')
    download_parser.add_argument('--s3-path', type=str, required=True,
                                 help='S3 path to download (e.g., "res/onnx/", or "res/onnx/AlexNet-1.onnx").')
    download_parser.add_argument('--save-location', type=str, required=True,
                                 help='Local directory to save the downloaded files.')

    # Optional arguments for download command
    download_parser.add_argument('--include-pattern', type=str, action='append', nargs='*',
                                 help='Optional: Glob-style pattern to INCLUDE files. Can be used multiple times (e.g., "--include-pattern **/*.onnx"). If specified, only files matching these patterns will be considered.')
    download_parser.add_argument('--exclude-pattern', type=str, action='append', nargs='*',
                                 help='Optional: Glob-style pattern to EXCLUDE files. Can be used multiple times (e.g., "--exclude-pattern **/*.tar.gz --exclude-pattern **/*.dxnn"). Exclude patterns take precedence over include patterns.')
    download_parser.add_argument('--force', action='store_true', help='Force overwrite existing files')

    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload files to S3')
    upload_parser.add_argument('--s3-path', type=str, required=True, help='S3 path to upload to (e.g., "uploads/").')
    upload_parser.add_argument('--local-path', type=str, required=True, help='Local directory or file to upload.')

        # Optional arguments for upload command
    upload_parser.add_argument('--include-pattern', type=str, action='append', nargs='*',
                              help='Optional: Glob-style pattern to INCLUDE files. Can be used multiple times (e.g., "--include-pattern **/*.onnx"). If specified, only files matching these patterns will be considered.')
    upload_parser.add_argument('--exclude-pattern', type=str, action='append', nargs='*',
                              help='Optional: Glob-style pattern to EXCLUDE files. Can be used multiple times (e.g., "--exclude-pattern **/*.tar.gz --exclude-pattern **/*.dxnn"). Exclude patterns take precedence over include patterns.')

    # Global optional arguments (apply to both download and upload)
    parser.add_argument('--config-file-path', type=str, help='AWS Config file path')
    parser.add_argument('--aws-access-key', type=str, help='AWS Access Key ID')
    parser.add_argument('--aws-secret-key', type=str, help='AWS Secret Access Key')
    parser.add_argument('--bucket-name', type=str, help='S3 Bucket Name')
    parser.add_argument('--region-name', type=str, help='AWS Region Name (e.g., ap-northeast-2)')
    parser.add_argument('--cloudfront-domain', type=str, help='CloudFront Domain (e.g., sdk.deepx.ai)')

    args = parser.parse_args()

    # 1. Load base configuration from .properties file
    if args.config_file_path:
        aws_cfg = _read_properties_file(args.config_file_path)
        if not aws_cfg:
            colored_print(f"ERROR: Configuration file '{args.config_file_path}' not found or empty. Relying on environment variables or CLI arguments for AWS credentials.", "WARNING")
            sys.exit(1)
    
    # If neither CLI options for credentials nor config file path are provided, check environment variables.
    if not any([args.aws_access_key, args.aws_secret_key, args.config_file_path]):
        if not all([os.environ.get('AWS_ACCESS_KEY'), os.environ.get('AWS_SECRET_KEY')]):
            colored_print("ERROR: Missing AWS credentials. Provide them via --aws-access-key, --aws-secret-key, a configuration file with --config-file-path, or set AWS_ACCESS_KEY and AWS_SECRET_KEY environment variables.", "ERROR")
            parser.print_help()
            sys.exit(1)

    # 2. Override with Environment Variables
    aws_cfg['AWS_ACCESS_KEY'] = os.environ.get('AWS_ACCESS_KEY', aws_cfg.get('AWS_ACCESS_KEY'))
    aws_cfg['AWS_SECRET_KEY'] = os.environ.get('AWS_SECRET_KEY', aws_cfg.get('AWS_SECRET_KEY'))
    aws_cfg['BUCKET_NAME'] = os.environ.get('BUCKET_NAME', aws_cfg.get('BUCKET_NAME'))
    aws_cfg['REGION_NAME'] = os.environ.get('REGION_NAME', aws_cfg.get('REGION_NAME'))
    aws_cfg['CLOUDFRONT_DOMAIN'] = os.environ.get('CLOUDFRONT_DOMAIN', aws_cfg.get('CLOUDFRONT_DOMAIN'))

    # 3. Override with CLI Arguments (highest priority)
    # Note: argparse stores arguments with hyphens as attributes with underscores (e.g., args.aws_access_key)
    if args.aws_access_key:
        aws_cfg['AWS_ACCESS_KEY'] = args.aws_access_key
    if args.aws_secret_key:
        aws_cfg['AWS_SECRET_KEY'] = args.aws_secret_key
    if args.bucket_name:
        aws_cfg['BUCKET_NAME'] = args.bucket_name
    if args.region_name:
        aws_cfg['REGION_NAME'] = args.region_name
    if args.cloudfront_domain:
        aws_cfg['CLOUDFRONT_DOMAIN'] = args.cloudfront_domain

    # Validate that all required AWS configuration values are present
    required_aws_keys = ['AWS_ACCESS_KEY', 'AWS_SECRET_KEY', 'BUCKET_NAME', 'REGION_NAME', 'CLOUDFRONT_DOMAIN']
    for key in required_aws_keys:
        if not aws_cfg.get(key):
            colored_print(f"ERROR: Missing required AWS configuration value for '{key}'.", "ERROR")
            colored_print("Please provide it via aws_config.properties, environment variables, or CLI arguments.", "ERROR")
            parser.print_help() 
            sys.exit(1)

    # Return both the AWS config dictionary and the parsed arguments
    return aws_cfg, args


def process_download(downloader: AWSS3FileDownloader, args):
    colored_print(f"--- Processing S3 path: {args.s3_path} and saving to: {args.save_location} ---", "INFO")
    include_patterns = None
    exclude_patterns = None

    if args.include_pattern:
        include_patterns=sum(args.include_pattern, [])
        colored_print(f"--- Only files matching any of these include patterns will be considered: {', '.join(include_patterns)} ---", "INFO")
    if args.exclude_pattern:
        exclude_patterns=sum(args.exclude_pattern, [])
        colored_print(f"--- Files matching any of these exclude patterns will be excluded (high priority): {', '.join(exclude_patterns)} ---", "INFO")

    downloader.download_s3_path_via_cloudfront(
        s3_path=args.s3_path,
        save_location=args.save_location,
        force=args.force,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns
    )


def process_upload(uploader: AWSS3FileUploader, args):
    colored_print(f"--- Uploading from: {args.local_path} to S3 path: {args.s3_path} ---", "INFO")
    include_patterns=None 
    exclude_patterns=None

    if args.include_pattern:
        include_patterns = sum(args.include_pattern, [])
        colored_print(f"--- Only files matching any of these include patterns will be considered: {', '.join(sum(args.include_pattern, []))} ---", "INFO")
    if args.exclude_pattern:
        exclude_patterns = sum(args.exclude_pattern, [])
        colored_print(f"--- Files matching any of these exclude patterns will be excluded (high priority): {', '.join(sum(args.exclude_pattern, []))} ---", "INFO")


    if uploader.upload_s3_path(local_path=args.local_path, s3_path=args.s3_path, include_patterns=include_patterns, exclude_patterns=exclude_patterns):
        if os.path.isdir(args.local_path):
            colored_print(f"--- Successfully uploaded directory '{args.local_path}' to 's3://{uploader.s3_bucket}/{args.s3_path}' ---", "INFO")
        else:
            colored_print(f"--- Successfully uploaded file '{args.local_path}' to 's3://{uploader.s3_bucket}/{args.s3_path}' ---", "INFO")
    else:
        if os.path.isdir(args.local_path):
            colored_print(f"--- Failed to upload directory '{args.local_path}' ---", "ERROR")
        else:
            colored_print(f"--- Failed to upload file '{args.local_path}' ---", "ERROR")

def main():
    # Load configuration and parse arguments
    aws_cfg, args = load_config_and_args()

    if args.command == 'download':
        downloader = AWSS3FileDownloader(aws_cfg=aws_cfg)
        process_download(downloader, args)
        colored_print("\n--- Download process completed ---", "INFO")

    elif args.command == 'upload':
        uploader = AWSS3FileUploader(aws_cfg=aws_cfg)
        process_upload(uploader, args)
        colored_print("\n--- Upload process completed ---", "INFO")

    else:
        colored_print("ERROR: Please specify a command ('download' or 'upload').", "ERROR")

if __name__ == "__main__":
    main()
