from PIL import Image 
from PIL.Image import branches

# Define a function to calculate and print branch coverage


def calculate_branch_coverage():
    num_branches = len(branches)
    branch_covered = {key: value for key, value in branches.items() if value is True}
    sum_branches = len(branch_covered)
    coverage = (sum_branches/num_branches) * 100
    print(f"Branches covered: {sum_branches}")
    print(f"Total branches: {num_branches}")
    print("\nBRANCH COVERAGE:", coverage, "%\n")

R = Image.new('L', (100, 100), color=255)
G = Image.new('L', (100, 100), color=128)  
B = Image.new('L', (100, 100), color=0)
merged_image = Image.merge('RGB', (R, G, B))
merged_image.save('merged_image.png')

calculate_branch_coverage()
