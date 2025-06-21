# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 17:55:35 2025

@author: m
"""

import zipfile
import tarfile
import gzip
import os
from pathlib import Path
from typing import Generator, List, Optional

class CompressedFileReader:
    """Simple reader for ZIP, TAR.GZ, and GZ files."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.compression_type = self._detect_compression()
        self.is_folder = self._is_compressed_folder()
    
    def _detect_compression(self) -> str:
        """Detect compression type from file extension."""
        file_path_lower = self.file_path.lower()
        
        if file_path_lower.endswith('.zip'):
            return 'zip'
        elif file_path_lower.endswith('.tar.gz') or file_path_lower.endswith('.tgz'):
            return 'tar.gz'
        elif file_path_lower.endswith('.gz'):
            return 'gz'
        else:
            raise ValueError(f"Unsupported file type: {self.file_path}")
    
    def _is_compressed_folder(self) -> bool:
        """Check if compressed file contains multiple files (folder) or single file."""
        if self.compression_type == 'zip':
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                files = [f for f in zf.namelist() if not f.endswith('/')]
                return len(files) > 1
        
        elif self.compression_type == 'tar.gz':
            with tarfile.open(self.file_path, 'r:gz') as tf:
                files = [f for f in tf.getnames() if tf.getmember(f).isfile()]
                return len(files) > 1
        
        elif self.compression_type == 'gz':
            # .gz files typically contain single files
            return False
        
        return False
    
    def list_files(self) -> List[str]:
        """List all files in the compressed archive."""
        files = []
        
        if self.compression_type == 'zip':
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                files = [f for f in zf.namelist() if not f.endswith('/')]
        
        elif self.compression_type == 'tar.gz':
            with tarfile.open(self.file_path, 'r:gz') as tf:
                files = [f for f in tf.getnames() if tf.getmember(f).isfile()]
        
        elif self.compression_type == 'gz':
            # For .gz, use the filename without .gz extension
            base_name = os.path.basename(self.file_path)
            if base_name.endswith('.gz'):
                files = [base_name[:-3]]  # Remove .gz extension
        
        return files
    
    def iter_files(self, file_pattern: str = None) -> Generator[tuple, None, None]:
        """
        Iterate through files in the compressed archive.
        
        Args:
            file_pattern: Filter files by extension (e.g., '.txt', '.tsv')
        
        Yields:
            tuple: (file_path, file_content_as_bytes)
        """
        if self.compression_type == 'zip':
            yield from self._iter_zip_files(file_pattern)
        elif self.compression_type == 'tar.gz':
            yield from self._iter_tarball_files(file_pattern)
        elif self.compression_type == 'gz':
            yield from self._iter_gz_file(file_pattern)
    
    def _iter_zip_files(self, file_pattern: str = None):
        """Iterate through ZIP files."""
        with zipfile.ZipFile(self.file_path, 'r') as zf:
            for file_path in zf.namelist():
                # Skip directories
                if file_path.endswith('/'):
                    continue
                
                # Filter by pattern
                if file_pattern and not file_path.endswith(file_pattern):
                    continue
                
                try:
                    with zf.open(file_path) as file_obj:
                        content = file_obj.read()
                        yield file_path, content
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    def _iter_tarball_files(self, file_pattern: str = None):
        """Iterate through TAR.GZ files."""
        with tarfile.open(self.file_path, 'r:gz') as tf:
            for member in tf.getmembers():
                # Skip directories
                if not member.isfile():
                    continue
                
                file_path = member.name
                
                # Filter by pattern
                if file_pattern and not file_path.endswith(file_pattern):
                    continue
                
                try:
                    file_obj = tf.extractfile(member)
                    if file_obj:
                        content = file_obj.read()
                        yield file_path, content
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    def _iter_gz_file(self, file_pattern: str = None):
        """Iterate through GZ file (single file)."""
        base_name = os.path.basename(self.file_path)
        if base_name.endswith('.gz'):
            file_name = base_name[:-3]  # Remove .gz extension
        else:
            file_name = base_name
        
        # Filter by pattern
        if file_pattern and not file_name.endswith(file_pattern):
            return
        
        try:
            with gzip.open(self.file_path, 'rb') as gz_file:
                content = gz_file.read()
                yield file_name, content
        except Exception as e:
            print(f"Error reading {file_name}: {e}")
    
    def read_file(self, file_path: str) -> bytes:
        """Read a specific file from the archive."""
        if self.compression_type == 'zip':
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                with zf.open(file_path) as file_obj:
                    return file_obj.read()
        
        elif self.compression_type == 'tar.gz':
            with tarfile.open(self.file_path, 'r:gz') as tf:
                file_obj = tf.extractfile(file_path)
                if file_obj:
                    return file_obj.read()
        
        elif self.compression_type == 'gz':
            with gzip.open(self.file_path, 'rb') as gz_file:
                return gz_file.read()
        
        raise FileNotFoundError(f"File {file_path} not found in archive")
    
    def read_single_file(self, encoding: str = 'utf-8') -> str:
        """
        Read content if it's a single file archive.
        Returns the content as string.
        """
        if self.is_folder:
            raise ValueError("This is a multi-file archive. Use iter_files() instead.")
        
        # Get the single file
        for file_path, content in self.iter_files():
            return content.decode(encoding)
        
        raise ValueError("No files found in archive")
    
    def read_single_file_as_bytes(self) -> bytes:
        """
        Read content if it's a single file archive.
        Returns raw bytes.
        """
        if self.is_folder:
            raise ValueError("This is a multi-file archive. Use iter_files() instead.")
        
        # Get the single file
        for file_path, content in self.iter_files():
            return content
        
        raise ValueError("No files found in archive")
    
    def get_single_filename(self) -> str:
        """Get the filename of the single file in archive."""
        if self.is_folder:
            raise ValueError("This is a multi-file archive.")
        
        files = self.list_files()
        if files:
            return files[0]
        else:
            raise ValueError("No files found in archive")
    
    def get_info(self) -> dict:
        """Get basic information about the compressed file."""
        files = self.list_files()
        return {
            'file_path': self.file_path,
            'compression_type': self.compression_type,
            'is_folder': self.is_folder,
            'file_count': len(files),
            'files': files[:10]  # Show first 10 files
        }

# Simple usage examples
def process_compressed_file(file_path: str):
    """Simple example of processing a compressed file."""
    
    # Initialize reader
    reader = CompressedFileReader(file_path)
    
    # Get basic info
    info = reader.get_info()
    print(f"File: {info['file_path']}")
    print(f"Type: {info['compression_type']}")
    print(f"Is folder: {info['is_folder']}")
    print(f"Contains {info['file_count']} files")
    
    # Process each file
    for file_path, content in reader.iter_files('.txt'):  # Only .txt files
        print(f"Processing: {file_path}")
        
        # Convert bytes to string
        text_content = content.decode('utf-8')
        print(f"  Length: {len(text_content)} characters")
        print(f"  First 100 chars: {text_content[:100]}...")

def read_single_file_example(file_path: str):
    """Example: Read a single compressed file."""
    reader = CompressedFileReader(file_path)
    
    # Check if it's a single file
    if reader.is_folder:
        print(f"{file_path} contains multiple files")
        files = reader.list_files()
        print(f"Files: {files}")
    else:
        print(f"{file_path} is a single file")
        
        # Get filename
        filename = reader.get_single_filename()
        print(f"Filename: {filename}")
        
        # Read content as string
        content = reader.read_single_file()
        print(f"Content length: {len(content)} characters")
        print(f"First 200 characters: {content[:200]}...")
        
        # Or read as bytes if needed
        raw_content = reader.read_single_file_as_bytes()
        print(f"Raw content length: {len(raw_content)} bytes")

def process_tsv_files(file_path: str):
    """Example: Process TSV files specifically."""
    import pandas as pd
    import io
    
    reader = CompressedFileReader(file_path)
    
    if not reader.is_folder:
        # Single TSV file
        if reader.get_single_filename().endswith('.tsv'):
            content = reader.read_single_file()
            df = pd.read_csv(io.StringIO(content), sep='\t')
            print(f"Single TSV Shape: {df.shape}")
    else:
        # Multiple files
        for file_path, content in reader.iter_files('.tsv'):
            print(f"Processing TSV: {file_path}")
            
            # Convert to DataFrame
            text_content = content.decode('utf-8')
            df = pd.read_csv(io.StringIO(text_content), sep='\t')
            
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            
            # Your processing here
            # analyze_dataframe(df)
            # save_processed_data(df, file_path)

if __name__ == "__main__":
    # Example usage
    compressed_files = [
        "data.zip",
        "archive.tar.gz", 
        "single_file.txt.gz"
    ]
    
    for file_path in compressed_files:
        try:
            print(f"\n=== Processing {file_path} ===")
            
            # Check if single file and read accordingly
            reader = CompressedFileReader(file_path)
            if reader.is_folder:
                process_compressed_file(file_path)  # Multiple files
            else:
                read_single_file_example(file_path)  # Single file
                
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    ## ==================================================
    """Simple example of processing a compressed file."""
    file_path = "txt.zip"
    # Initialize reader
    reader = CompressedFileReader(file_path)    
    
    if reader.is_folder: # Multiple files

        # Process each file
        for file_path, content in reader.iter_files('.txt'):  # Only .txt files
            print(f"Processing: {file_path}")
            
            # Convert bytes to string
            text_content = content.decode('utf-8')
            print(f"  Length: {len(text_content)} characters")
            print(f"  First 100 chars: {text_content[:100]}...")
      
    if not reader.is_folder:
        text_content = read_single_file_example(file_path)  # Single file

        
    def process_tsv_files(file_path: str):
        """Example: Process TSV files specifically."""
        import pandas as pd
        import io
        
        reader = CompressedFileReader(file_path)
        
        for file_path, content in reader.iter_files('.tsv'):
            print(f"Processing TSV: {file_path}")
            
            # Convert to DataFrame
            text_content = content.decode('utf-8')
            df = pd.read_csv(io.StringIO(text_content), sep='\t')
            
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            
            # Your processing here
            # analyze_dataframe(df)
            # save_processed_data(df, file_path)