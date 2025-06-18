// MacroPad RP2040 Top Cover
// Parametric design for Adafruit MacroPad RP2040 keyboard controller
// Author: Generated for CircuitPython EVM Controller project
// License: MIT

// =============================================================================
// PARAMETERS - Easy to modify for different requirements
// =============================================================================

// Overall cover dimensions
cover_length = 105;        // Total length of cover (mm)
cover_width = 70;          // Total width of cover (mm)  
cover_thickness = 3;       // Thickness of top plate (mm)
corner_radius = 4;         // Rounded corner radius (mm)

// Key switch parameters (Cherry MX compatible)
key_switch_size = 14;      // Square hole size for key switches (mm)
key_switch_spacing = 19.05; // Center-to-center spacing (0.75" standard)
key_rows = 4;              // Number of rows
key_cols = 3;              // Number of columns

// Key switch grid positioning (relative to cover center)
keys_offset_x = 0;         // X offset of key grid center
keys_offset_y = -8;        // Y offset of key grid center (negative = toward bottom)

// LCD/OLED display parameters
lcd_width = 28;            // Width of LCD cutout (mm)
lcd_height = 15;           // Height of LCD cutout (mm)
lcd_corner_radius = 2;     // Corner radius for LCD hole
lcd_offset_x = 0;          // X position relative to center
lcd_offset_y = 22;         // Y position relative to center (positive = toward top)

// Rotary encoder parameters
encoder_size = 12;         // Square hole size for encoder (mm)
encoder_corner_radius = 1; // Corner radius for encoder hole
encoder_offset_x = 35;     // X position relative to center
encoder_offset_y = 22;     // Y position relative to center

// Mounting and clearance
wall_thickness = 2;        // Wall thickness for sides (if adding later)
clearance = 0.2;           // General clearance for 3D printing (mm)

// =============================================================================
// MAIN OBJECT
// =============================================================================

difference() {
    // Base cover plate
    base_cover();
    
    // Cut out holes for key switches
    key_switch_holes();
    
    // Cut out hole for LCD/OLED
    lcd_hole();
    
    // Cut out hole for rotary encoder
    encoder_hole();
}

// Optional: Show key switch positions for reference (comment out for final print)
// %key_switch_positions(); // The % makes it transparent/reference only

// =============================================================================
// MODULES (Functions)
// =============================================================================

// Create the base cover plate with rounded corners
module base_cover() {
    // Using hull() with corner cylinders to create rounded rectangle
    hull() {
        // Four corner cylinders to create rounded rectangle
        translate([-(cover_length/2 - corner_radius), -(cover_width/2 - corner_radius), 0])
            cylinder(h = cover_thickness, r = corner_radius, $fn = 32);
        
        translate([+(cover_length/2 - corner_radius), -(cover_width/2 - corner_radius), 0])
            cylinder(h = cover_thickness, r = corner_radius, $fn = 32);
        
        translate([+(cover_length/2 - corner_radius), +(cover_width/2 - corner_radius), 0])
            cylinder(h = cover_thickness, r = corner_radius, $fn = 32);
        
        translate([-(cover_length/2 - corner_radius), +(cover_width/2 - corner_radius), 0])
            cylinder(h = cover_thickness, r = corner_radius, $fn = 32);
    }
}

// Create all key switch holes in a 3x4 matrix
module key_switch_holes() {
    // Calculate starting position for grid (top-left key)
    start_x = keys_offset_x - (key_switch_spacing * (key_cols - 1) / 2);
    start_y = keys_offset_y + (key_switch_spacing * (key_rows - 1) / 2);
    
    // Create grid of holes
    for (row = [0 : key_rows - 1]) {
        for (col = [0 : key_cols - 1]) {
            translate([
                start_x + (col * key_switch_spacing),
                start_y - (row * key_switch_spacing),
                -0.5  // Extend slightly below surface for clean cut
            ]) {
                // Square hole for key switch
                cube([
                    key_switch_size + clearance,
                    key_switch_size + clearance,
                    cover_thickness + 1
                ], center = true);
            }
        }
    }
}

// Create LCD/OLED display hole
module lcd_hole() {
    translate([lcd_offset_x, lcd_offset_y, -0.5]) {
        // Rounded rectangle hole for LCD
        hull() {
            // Four corner cylinders for rounded rectangle
            translate([-(lcd_width/2 - lcd_corner_radius), -(lcd_height/2 - lcd_corner_radius), 0])
                cylinder(h = cover_thickness + 1, r = lcd_corner_radius, $fn = 16);
            
            translate([+(lcd_width/2 - lcd_corner_radius), -(lcd_height/2 - lcd_corner_radius), 0])
                cylinder(h = cover_thickness + 1, r = lcd_corner_radius, $fn = 16);
            
            translate([+(lcd_width/2 - lcd_corner_radius), +(lcd_height/2 - lcd_corner_radius), 0])
                cylinder(h = cover_thickness + 1, r = lcd_corner_radius, $fn = 16);
            
            translate([-(lcd_width/2 - lcd_corner_radius), +(lcd_height/2 - lcd_corner_radius), 0])
                cylinder(h = cover_thickness + 1, r = lcd_corner_radius, $fn = 16);
        }
    }
}

// Create rotary encoder hole
module encoder_hole() {
    translate([encoder_offset_x, encoder_offset_y, -0.5]) {
        // Square hole with slightly rounded corners for encoder
        hull() {
            // Four corner cylinders for rounded square
            translate([-(encoder_size/2 - encoder_corner_radius), -(encoder_size/2 - encoder_corner_radius), 0])
                cylinder(h = cover_thickness + 1, r = encoder_corner_radius, $fn = 16);
            
            translate([+(encoder_size/2 - encoder_corner_radius), -(encoder_size/2 - encoder_corner_radius), 0])
                cylinder(h = cover_thickness + 1, r = encoder_corner_radius, $fn = 16);
            
            translate([+(encoder_size/2 - encoder_corner_radius), +(encoder_size/2 - encoder_corner_radius), 0])
                cylinder(h = cover_thickness + 1, r = encoder_corner_radius, $fn = 16);
            
            translate([-(encoder_size/2 - encoder_corner_radius), +(encoder_size/2 - encoder_corner_radius), 0])
                cylinder(h = cover_thickness + 1, r = encoder_corner_radius, $fn = 16);
        }
    }
}

// Reference module to show key switch positions (for design verification)
module key_switch_positions() {
    // Calculate starting position for grid
    start_x = keys_offset_x - (key_switch_spacing * (key_cols - 1) / 2);
    start_y = keys_offset_y + (key_switch_spacing * (key_rows - 1) / 2);
    
    // Show key positions with small cylinders
    for (row = [0 : key_rows - 1]) {
        for (col = [0 : key_cols - 1]) {
            translate([
                start_x + (col * key_switch_spacing),
                start_y - (row * key_switch_spacing),
                cover_thickness
            ]) {
                cylinder(h = 2, r = 1, $fn = 8);
                
                // Optional: Add text labels for key numbers
                translate([0, 0, 2]) {
                    linear_extrude(height = 0.5) {
                        text(
                            str(row * key_cols + col), 
                            size = 3, 
                            halign = "center", 
                            valign = "center"
                        );
                    }
                }
            }
        }
    }
}

// =============================================================================
// CUSTOMIZATION EXAMPLES
// =============================================================================

/* 
To customize this design, modify the parameters at the top:

1. DIFFERENT KEY SPACING:
   - Change key_switch_spacing for different layouts
   - Standard Cherry MX: 19.05mm
   - Compact layouts: 15-17mm

2. DIFFERENT LCD SIZE:
   - Adjust lcd_width and lcd_height for your display
   - Common OLED sizes: 
     * 0.96": ~27x15mm viewing area
     * 1.3": ~30x16mm viewing area

3. ENCODER OPTIONS:
   - For round hole: replace encoder_hole() with cylinder
   - For different size: change encoder_size

4. BOARD FITMENT:
   - Adjust cover_length and cover_width to match your PCB
   - Use clearance parameter for tight/loose fit

5. 3D PRINTING:
   - Increase clearance for loose fit: 0.3-0.4mm
   - Decrease for tight fit: 0.1-0.15mm
   - Adjust cover_thickness for strength vs material usage
*/

// =============================================================================
// ASSEMBLY NOTES
// =============================================================================

/*
PRINTING TIPS:
- Print with holes facing up (as designed)
- No supports needed for this top cover
- Recommended layer height: 0.2-0.3mm
- Infill: 15-25% is sufficient for keyboard cover

ASSEMBLY:
- Key switches press-fit into 14mm holes
- LCD/OLED typically mounts from below with screws or clips
- Rotary encoder usually has threaded shaft with nut

MEASUREMENTS TO VERIFY:
1. Measure your actual MacroPad PCB dimensions
2. Check key switch center-to-center spacing
3. Measure LCD module size (not just screen size)
4. Verify encoder mounting requirements

Use the reference key positions (uncomment %key_switch_positions())
to verify layout before printing!
*/

