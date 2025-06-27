#! venv/bin/python3
'''Python script for changing extension type of files
For now this is only used for .flac -> .wav

@author Raoul Kalkman
@date 30-05-2025

'''

import click
import ffmpeg
import logging
import os
import shutil
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.command()
@click.option('-f', type=str, default=None, help='Path to the folder containing music files. If not provided, user will be prompted.')
@click.option('-r', '--recursive', is_flag=True, help='Recursively convert files in subfolders.')
def cli(f: str | None = None, recursive: bool = False):
    '''Command line interface for changing file extensions in a given folder.
    Places new files in a subfolder called 'converted'.
    If the folder does not exist, it will be created.
    Args:
        music_folder (str): The path to the folder containing music files.
                            If None, the user will be prompted to enter a folder path.
    '''
    main(f, recursive)

def main(music_folder: str | None = None, recursive: bool = False):
    '''Main function to change file extensions in a given folder.
    Places new files in a subfolder called 'converted'.
    If the folder does not exist, it will be created.
    Args:
        music_folder (str): The path to the folder containing music files.
                            If None, the user will be prompted to enter a folder path.
    Returns:
        int: Returns 0 on success.
    Raises:
        FileNotFoundError: If the specified folder does not exist.
        ValueError: If the folder is not a valid directory.
    '''
    
    if recursive:
        logger.warning('Recursive conversion is not implemented yet. Only the specified folder will be processed.')

    # Get desired folder from user
    if music_folder is None:
        music_folder = os.getcwd()
        input('No folder specified. Press Enter to use the current working directory:\n' + music_folder + '\n')
    if not os.path.exists(music_folder):
        raise FileNotFoundError(f'The folder {music_folder} does not exist.')
    if not os.path.isdir(music_folder):
        raise ValueError(f'The path {music_folder} is not a valid directory.')
    
    # check if folder contains music files
    if not any(filename.endswith(('.wav', '.flac', '.aiff')) for filename in os.listdir(music_folder)):
        logger.warning(f'The folder {music_folder} does not contain any music files (.wav, .flac, .aiff).')
        return 0

    # Create a subfolder for converted files
    if music_folder.endswith('/'):
        music_folder = music_folder[:-1]
    
    logger.info(f'Using folder: {music_folder}')
    converted_folder = os.path.join(music_folder, f'{os.path.basename(music_folder)}_wav')
    logger.info(f'Converted files will be saved in: {converted_folder}')
    if not os.path.exists(converted_folder):
        os.makedirs(converted_folder)

    # Keep stats of the conversion process

    file_count = len(os.listdir(music_folder)) - 1  # Exclude the converted folder itself from the count 
    checked_count   = 0
    copied_count    = 0
    converter_count = 0
    skipped_count   = 0
    error_count     = 0
    error_files: list[str] = []

    input('Press Enter to start the conversion process...')
    # todo: recursively do this for all subfolders

    for filename in os.listdir(music_folder):
        if filename.endswith('.wav'):
            # Check if .wav file already exists
            checked_count += 1
            if os.path.exists(os.path.join(converted_folder, filename)):
                # If it exists, skip conversion
                skipped_count += 1
                logger.info(f'Skipping {filename}, already converted.')
                continue

            # Copy the .wav file to the converted folder
            shutil.copy2(
                os.path.join(music_folder, filename),
                os.path.join(converted_folder, filename)
            )
            copied_count += 1
            continue

        if filename.endswith('.flac') or filename.endswith('.aiff'):
            checked_count += 1
            file_path = os.path.join(music_folder, filename)

            # Check if converted file already exists
            if os.path.exists(os.path.join(converted_folder, filename.replace('.flac', '.wav'))):
                skipped_count += 1
                logger.info(f'Skipping {filename}, already converted.')
                continue

            # Convert the file from .flac to .wav
            try:
                # Use ffmpeg-python for conversion
                subprocess.call(['ffmpeg', '-i', file_path, os.path.join(converted_folder, filename.replace('.flac', '.wav'))])
                # ffmpeg.input(
                    # file_path
                    # ).output(
                        # os.path.join(converted_folder, filename.replace('.flac', '.wav'))
                            # ).run(overwrite_output=True)
                converter_count += 1
                logger.info(f'Converted {filename} to {filename.replace(".flac", ".wav")}')
            except KeyboardInterrupt:
                print()
                logger.info('Conversion interrupted by user.')
                logger.info(f'Folder contained {file_count} files.')
                logger.info(f'Checked {checked_count} files.')
                logger.info(f'Copied {copied_count} files.')
                logger.info(f'Converted {converter_count} files.')
                logger.info(f'Skipped {skipped_count} files (already converted).')
                logger.info(f'Encountered {error_count} errors during conversion.')
                if error_count > 0:
                    logger.error(f'Files with errors: {", ".join(error_files)}')
                return 0
            
            except ffmpeg.Error as e:
                error_count += 1
                error_files.append(filename)
                logger.error(f'Error converting {filename}: {e}')                    
                continue
            

    # Log summary of operations
    print()
    logger.info(f'Folder contained {file_count} files.')
    logger.info(f'Checked {checked_count} files.')
    logger.info(f'Copied {copied_count} files.')
    logger.info(f'Converted {converter_count} files.')
    logger.info(f'Skipped {skipped_count} files (already converted).')
    logger.info(f'Encountered {error_count} errors during conversion.')
    if error_count > 0:
        logger.error(f'Files with errors: {", ".join(error_files)}')


    return 0

if __name__ == '__main__':
    cli()