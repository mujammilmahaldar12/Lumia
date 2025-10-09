"""
Convert all markdown files in blackbook folder to plain text files
Removes all HTML tags and converts markdown formatting to plain text
"""
import os
import re
from bs4 import BeautifulSoup

def remove_html_tags(text):
    """Remove HTML tags using BeautifulSoup"""
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

def clean_markdown(text):
    """Clean markdown syntax and convert to plain text"""
    # Remove HTML tags first
    text = remove_html_tags(text)
    
    # Remove markdown bold (**text**)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # Remove markdown italic (*text* or _text_)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove markdown headers (# ## ###)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # Remove markdown code blocks (```code```)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remove markdown links [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove markdown images ![alt](url)
    text = re.sub(r'!\[.*?\]\(.+?\)', '', text)
    
    # Clean up multiple empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove excessive whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def convert_md_to_txt(blackbook_dir, output_dir):
    """Convert all .md files to .txt files"""
    
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all markdown files
    md_files = sorted([f for f in os.listdir(blackbook_dir) if f.endswith('.md')])
    
    print(f"Found {len(md_files)} markdown files to convert")
    
    for md_file in md_files:
        md_path = os.path.join(blackbook_dir, md_file)
        txt_file = md_file.replace('.md', '.txt')
        txt_path = os.path.join(output_dir, txt_file)
        
        print(f"Converting {md_file} to {txt_file}...")
        
        try:
            # Read markdown file
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean content
            clean_content = clean_markdown(content)
            
            # Write to text file
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            
            print(f"  ✓ Successfully converted {md_file}")
            
        except Exception as e:
            print(f"  ✗ Error converting {md_file}: {str(e)}")
    
    print(f"\nAll files converted and saved to: {output_dir}")

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Output directory for text files
    output_dir = os.path.join(script_dir, 'txt_files')
    
    print("=" * 60)
    print("Converting Markdown Files to Plain Text")
    print("=" * 60)
    
    convert_md_to_txt(script_dir, output_dir)
    
    print("\n" + "=" * 60)
    print("Conversion Complete!")
    print("=" * 60)
