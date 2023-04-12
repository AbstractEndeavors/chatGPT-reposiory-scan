# chatGPT-reposiory-scan
This Python script is designed to process and modify text files within a given directory. It leverages the OpenAI API to send the content of the files, with a specific focus on GPT-3.5-turbo. The script will analyze and process the text files, allowing users to make revisions, provide general feedback, or indicate whether a file requires reassessment.

## Features

- Analyze and process text files within a given directory
- Send file content to the OpenAI API for processing
- Handle revisions and reassessments based on user input
- Ignore image files during processing
- Create a replica of the target directory with modified content

## Installation

1. Clone this repository
2. Install the required Python packages by running `pip install -r requirements.txt`
3. Set up your OpenAI API Key (obtain it from the OpenAI website) and add it to your `.env` file as `OPENAI_API_KEY=your_key_here`

## Usage

1. Open a terminal and navigate to the project directory
2. Run `python main.py`
3. When prompted, enter the path to the folder you'd like to process
4. Follow the interactive prompts to provide input and receive processed text

## Requirements

- Python 3.6 or higher
- openai
- imghdr
- python-dotenv
- requests
