import requests
from bs4 import BeautifulSoup
import html2text
import sys
from typing import Optional
from pathlib import Path

def extract_main_content(html: str) -> Optional[str]:
    """Extract the main content from an HTML page, excluding navigation and sidebars."""
    soup = BeautifulSoup(html, 'html.parser')

    # Try to find main content using common HTML5 semantic tags
    main_content = None
    for selector in ['main', 'article', '[role="main"]', '#main-content', '.main-content']:
        main_content = soup.select_one(selector)
        if main_content:
            break

    # If no semantic markers found, try to find the largest content block
    if not main_content:
        # Remove common non-content elements
        for element in soup.select('nav, header, footer, sidebar, .sidebar, #sidebar'):
            element.decompose()

        # Find the div with the most text content
        divs = soup.find_all('div')
        if divs:
            main_content = max(divs, key=lambda x: len(x.get_text()))

    return str(main_content) if main_content else None

def url_to_markdown(url: str) -> Optional[str]:
    """Convert a URL's main content to markdown."""
    try:
        # Fetch the webpage
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        # Extract main content
        main_content = extract_main_content(response.text)
        if not main_content:
            print(f"Could not find main content for {url}")
            return None

        # Convert to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # Don't wrap text

        return h.handle(main_content)

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def process_url_file(input_file: str, output_dir: str = "markdown_output"):
    """Process a file containing URLs and save markdown versions."""
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Read and process URLs
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        print(f"Processing {url}...")
        markdown = url_to_markdown(url)

        if markdown:
            # Create a filename from the URL
            filename = url.split('/')[-1]
            if not filename:
                filename = url.split('/')[-2]
            filename = filename.replace('.html', '').replace('.htm', '')
            output_file = output_path / f"{filename}.md"

            # Save markdown content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"Saved markdown to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python url_to_markdown.py <url_file>")
        sys.exit(1)

    process_url_file(sys.argv[1])