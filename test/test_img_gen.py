from src.img_gen import generate_hr_diagram

# Basic diagram
generate_hr_diagram("test_basic")

# With a red dot (red giant zone)
generate_hr_diagram("test_dot", dot=(4000, 50))

# With highlighted region
generate_hr_diagram("test_highlight_main", highlight_region="main_sequence")
generate_hr_diagram("test_highlight_giants", highlight_region="red_giants")
generate_hr_diagram("test_highlight_supergiants", highlight_region="supergiants")
generate_hr_diagram("test_highlight_wd", highlight_region="white_dwarfs")

# Dot + highlight together
generate_hr_diagram("test_dot_and_highlight", dot=(4000, 50), highlight_region="red_giants")

print("Images saved to database/imgs/")
