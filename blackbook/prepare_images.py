import base64
import os

# Create images directory
blackbook_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(blackbook_dir, 'images')
os.makedirs(images_dir, exist_ok=True)

print(f"Images directory ready at: {images_dir}")
print("\nTo complete the setup:")
print("1. Save the Gantt Chart as 'gantt_chart.png'")
print("2. Save the Use Case Diagram as 'use_case.png'")
print("3. Save the Database Schema as 'schema.png'")
print("4. Save the Component Architecture as 'component_architecture.png'")
print("5. Save the Sequence Diagram as 'sequence_diagram.png'")
print("\nAll images should be saved to:", images_dir)