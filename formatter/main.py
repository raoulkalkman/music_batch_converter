'''Python script for changing extension type of files
For now this is only used for .flac -> .wav

@author Raoul Kalkman
@date 30-05-2025

'''

import click
import ffmpeg
import logging
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.command()
@click.option('-f', type=str, default=None, help='Path to the folder containing music files. If not provided, user will be prompted.')
def cli(f: str | None = None):
    '''Command line interface for changing file extensions in a given folder.
    Places new files in a subfolder called 'converted'.
    If the folder does not exist, it will be created.
    Args:
        music_folder (str): The path to the folder containing music files.
                            If None, the user will be prompted to enter a folder path.
    '''
    main(f)






def main(music_folder: str | None = None):
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
    
    # Get desired folder from user
    if music_folder is None:
        music_folder = input('Enter the path to the folder containing music files: ')
    if not os.path.exists(music_folder):
        raise FileNotFoundError(f'The folder {music_folder} does not exist.')
    if not os.path.isdir(music_folder):
        raise ValueError(f'The path {music_folder} is not a valid directory.')
    
    # Create a subfolder for converted files
    converted_folder = os.path.join(music_folder, 'wav')
    if not os.path.exists(converted_folder):
        os.makedirs(converted_folder)

    # Iterate through files in the folder
    checked_count = 0
    converter_count = 0
    skipped_count = 0
    error_count = 0
    error_files = []

    for filename in os.listdir(music_folder):
        if filename.endswith('.flac'):
            checked_count += 1
            file_path = os.path.join(music_folder, filename)

            # Check if converted file already exists
            if os.path.exists(os.path.join(converted_folder, filename.replace('.flac', '.wav'))):
                skipped_count += 1
                logger.info(f'Skipping {filename}, already converted.')
                continue

            # Convert the file from .flac to .wav
            try:
                ffmpeg.input(
                    file_path
                    ).output(
                        os.path.join(converted_folder, filename.replace('.flac', '.wav'))
                            ).run(overwrite_output=True)
                converter_count += 1
                logger.info(f'Converted {filename} to {filename.replace(".flac", ".wav")}')
            except ffmpeg.Error as e:
                error_count += 1
                error_files.append(filename)
                logger.error(f'Error converting {filename}: {e}')                    
                continue

    # Log summary of operations
    logger.info(f'Checked {checked_count} files.')
    logger.info(f'Converted {converter_count} files.')
    logger.info(f'Skipped {skipped_count} files (already converted).')
    logger.info(f'Encountered {error_count} errors during conversion.')
    if error_count > 0:
        logger.error(f'Files with errors: {", ".join(error_files)}')


    return 0

if __name__ == '__main__':
    cli()