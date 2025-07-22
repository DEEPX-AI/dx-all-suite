import pytest
from unittest.mock import patch, MagicMock, mock_open
import requests
from aws_s3_manager.main import AWSS3FileUploader, AWSS3FileDownloader

@pytest.fixture
def mock_aws_config():
    return {
        'AWS_ACCESS_KEY': 'test_access_key',
        'AWS_SECRET_KEY': 'test_secret_key',
        'REGION_NAME': 'us-west-2',
        'BUCKET_NAME': 'test-bucket',
        'CLOUDFRONT_DOMAIN': 'sdk.deepx.ai'
    }


@pytest.fixture
def uploader(mock_aws_config):
    return AWSS3FileUploader(mock_aws_config)


def test_upload_directory_not_found(uploader):
    """Test case where the local directory does not exist."""
    with patch('os.path.exists', return_value=False):
        result = uploader.upload_s3_path('nonexistent_dir', 's3_prefix') 
        assert result is False  # Assert upload fails for nonexistent directory


# You can add more tests here, for example:


# - Test for ProgressPercentage class
# - Test for pattern matching logic in upload_s3_path


@pytest.fixture
def downloader(mock_aws_config):
    return AWSS3FileDownloader(mock_aws_config)


def test_download_single_file_success(downloader):
    """Test successful single file download."""
    with patch('requests.get') as mock_get, \
            patch('os.makedirs'), \
            patch('os.path.getsize') as mock_getsize, \
            patch('aws_s3_manager.main.print_progress_bar'), \
            patch('builtins.open', mock_open()):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'chunk']
        mock_get.return_value = mock_response
        mock_getsize.return_value = 1024

        result = downloader._download_single_file('s3_path/test_file.txt', 'local_path/test_file.txt')
        assert result is True
        mock_get.assert_called_once_with('https://sdk.deepx.ai/s3_path/test_file.txt', stream=True)


def test_download_single_file_not_found(downloader):
    """Test file download failure due to file not found."""
    with patch('requests.get') as mock_get, \
            patch('os.makedirs'):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_get.return_value = mock_response

        result = downloader._download_single_file('s3_path/test_file.txt', 'local_path/test_file.txt')
        assert result is False
        mock_get.assert_called_once_with('https://sdk.deepx.ai/s3_path/test_file.txt', stream=True)


def test_download_s3_path_via_cloudfront_single_file(downloader):
    """Test downloading a single file using download_s3_path_via_cloudfront."""
    with patch.object(downloader.s3_client, 'list_objects_v2') as mock_list_objects, \
            patch.object(downloader, '_download_single_file') as mock_download_file, \
            patch('os.makedirs'):
        mock_list_objects.return_value = {'Contents': [{'Key': 's3_path/test_file.txt'}]}
        mock_download_file.return_value = True

        downloader.download_s3_path_via_cloudfront('s3_path/test_file.txt', 'local_dir', False)
        mock_list_objects.assert_called_once_with(Bucket='test-bucket', Prefix='s3_path/test_file.txt', MaxKeys=2)
        mock_download_file.assert_called_once_with('s3_path/test_file.txt', 'local_dir/test_file.txt')

def test_download_s3_path_via_cloudfront_single_file2(downloader):
    """Test downloading a single file using download_s3_path_via_cloudfront."""
    with patch.object(downloader.s3_client, 'list_objects_v2') as mock_list_objects, \
            patch.object(downloader, '_download_single_file') as mock_download_file, \
            patch('os.makedirs'):
        mock_list_objects.return_value = {'Contents': [{'Key': 's3_path/sub_dir/test_file.txt'}]}
        mock_download_file.return_value = True

        downloader.download_s3_path_via_cloudfront('s3_path/sub_dir/test_file.txt', 'local_dir', False)
        mock_list_objects.assert_called_once_with(Bucket='test-bucket', Prefix='s3_path/sub_dir/test_file.txt', MaxKeys=2)
        mock_download_file.assert_called_once_with('s3_path/sub_dir/test_file.txt', 'local_dir/test_file.txt')