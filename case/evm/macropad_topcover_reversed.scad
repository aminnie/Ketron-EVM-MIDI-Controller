// MacroPad RP2040 Top Cover
// Parametric design for Adafruit MacroPad RP2040 keyboard controller
// Author: Generated for CircuitPython EVM Controller project
// License: MIT

// Cheatsheet: https://openscad.org/cheatsheet/index.html?version=2021.01

// This file is the design for the top cover of a case designed to enclose the 
// Adafruit MacroPad RP2040 hardware module. Tve cover comtains 12 holes for the 
// key switches. The holes are sized to enssure a tight fit for the keys switches
// Key swiicthes are carefully inserted through the top cover holes, the looser
// fitting filler layer in to the keys switches sockes that Adafruit has soldered
// into the board. The cover also completely encloses the Encoder on the PCB.
// The encoder nut and washer is to be removed during assembly and added back
// on top of the shaft cover and used to secure the top cover to the PCB board. 

// =============================================================================
// PARAMETERS
// =============================================================================

// RP2040 PCB parameters
pcb_length = 105;          // RP2040 PCB length (mm)
pcb_width = 60;            // RP2040 PCB width (mm)
pcb_thickness = 1.6;       // Standard PCB thickness (mm)
pcb_clearance = 1;         // Space around PCB (mm)
pcb_height_clearance = 8;  // Space above PCB for components (mm)

// Overall cover dimensions
cover_length = 105 - 1;   // Total length of cover (mm)  
cover_width = 60;         // Total width of cover (mm)
cover_thickness = 2;       // Thickness of top plate (mm)
corner_radius = 1;         // Rounded corner radius (mm)

// Key switch parameters (Cherry MX compatible)
key_switch_size = 14;      // Square hole size for key switches (mm)
key_switch_spacing = 19.05; // Center-to-center spacing (0.75" standard)
key_rows = 4;              // Number of rows
key_cols = 3;              // Number of columns

// Key switch grid positioning (relative to cover center)
keys_offset_x = 0;         // X offset of key grid center
keys_offset_y = -13;     // Y offset of key grid center (negative = toward bottom)

// LCD/OLED display parameters
lcd_width = 31;            // Width of LCD cutout (mm)
lcd_height = 17;           // Height of LCD cutout (mm)
lcd_corner_radius = 1;     // Corner radius for LCD hole
//lcd_offset_x = -11;        // X position relative to center
lcd_offset_x = 11;        // X position relative to center
lcd_offset_y = 41;         // Y position relative to center (positive = toward top)

// Cover base Encoder hole
encoder_hole_size = 13;         // Square hole size for encoder + 1 mm space(mm)
encoder_hole_offset_x = -18.5;   // Hole X position relative to center
encoder_hole_offset_y = 38.5;   // Hole Y position relative to center
encoder_hole_z = 5;             // Hole encoder shaft height

// Rotary encoder parameters and relative to shaft center
encoder_shaft_diameter = 6;
encoder_size = 13;         // Square hole size for encoder + 1 mm space(mm)
//encoder_offset_x = 18.5;   // X position relative to center
encoder_offset_x = -48.5;   // X position relative to center
encoder_offset_y = 38.5;   // Y position relative to center
encoder_shaft_z = 8;      // Encoder shaft height
encoder_shaft_clearance = 2; // General clearance for 3D printing (mm)

shaft_wall_width= 2;       // 
shaft_corner_radius = 1;   // Corner radius for encoder hole

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
    
    base_encoder_hole();

    // Cut out hole for rotary encoder
    encoder_shaft_hole();                        

    // Cut out encoder shaft hole
    encoder_round_hole();
        
}

// Optional: Show key switch positions for reference (comment out for final print)
// %key_switch_positions(); // The % makes it transparent/reference only

// =============================================================================
// MODULES (Functions)
// =============================================================================

// Create the base cover plate with rounded corners
module base_cover() {
    
    union() {
        // Using hull() with corner cylinders to create rounded rectangle
        hull() {
            // Four corner cylinders to create rounded rectangle
            translate([-(cover_width/2 - corner_radius), -(cover_length/2 - corner_radius), 0])
                cylinder(h = cover_thickness, r = corner_radius, $fn = 32);
            
            translate([+(cover_width/2 - corner_radius), -(cover_length/2 - corner_radius), 0])
                cylinder(h = cover_thickness, r = corner_radius, $fn = 32);
            
            translate([+(cover_width/2 - corner_radius), +(cover_length/2 - corner_radius), 0])
                cylinder(h = cover_thickness, r = corner_radius, $fn = 32);
            
            translate([-(cover_width/2 - corner_radius), +(cover_length/2 - corner_radius), 0])
                cylinder(h = cover_thickness, r = corner_radius, $fn = 32);
        }
        
        // Wrap the open encoder shaft
        encoder_shaft_wrap();                        
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
                    cover_thickness + 5
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

// Encoder hole in cover base
module base_encoder_hole() {
    
    color("blue") translate([encoder_hole_offset_x, encoder_hole_offset_y, -0.5]) {
        // Square hole with slightly rounded corners for encoder
        rotate(45) 
        cube([encoder_hole_size,encoder_hole_size, 10],center = true);
    }    
}



// Seperated: Create rotary encoder hole through cover base and shaft cibe
module encoder_shaft_wrap() {
    
    encoder_z = encoder_shaft_z - shaft_wall_width;  // 2mm Shaft top cover
    
    translate([encoder_offset_x, encoder_offset_y, 0]) {
        // Square hole with slightly rounded corners for encoder
        hull() {
            // Four corner cylinders for rounded square
            translate([+(encoder_size/2 + shaft_wall_width - shaft_corner_radius), -(encoder_size/2 + shaft_wall_width - shaft_corner_radius), 0])
                cylinder(h = cover_thickness + encoder_z, r = shaft_corner_radius, $fn = 32);
            
            translate([-(encoder_size/2 + shaft_wall_width - shaft_corner_radius), -(encoder_size/2 + shaft_wall_width - shaft_corner_radius), 0])
                cylinder(h = cover_thickness + encoder_z, r = shaft_corner_radius, $fn = 32);
            
            translate([+(encoder_size/2 + shaft_wall_width - shaft_corner_radius), (encoder_size/2 + shaft_wall_width - shaft_corner_radius), 0])
                cylinder(h = cover_thickness + encoder_z, r = shaft_corner_radius, $fn = 32);
            
            translate([-(encoder_size/2 + shaft_wall_width - shaft_corner_radius), (encoder_size/2 + shaft_wall_width - shaft_corner_radius), 0])
                cylinder(h = cover_thickness + encoder_z, r = shaft_corner_radius, $fn = 32);
        }
    }
}


// Seperated: Create a wrapper around encoder sides starting at cover height
module encoder_shaft_hole() {
    encoder_z = encoder_shaft_z + shaft_wall_width;  // 2mm Shaft top cover
    
    color("red") translate([encoder_offset_x, encoder_offset_y, encoder_z / 2 + 2]) {
        // Square hole with slightly rounded corners for encoder 
        cube([encoder_size,encoder_size, encoder_z],center = true);
    }    
}

// Seperated: Create Encoder 6mm Shaft through hole
module encoder_round_hole() {
    color("blue") translate([encoder_offset_x, encoder_offset_y, -0.5]) {
        // Through hole for encoder shaft
        cylinder(
            h = encoder_shaft_z + 2, 
            d = encoder_shaft_diameter + encoder_shaft_clearance, 
            $fn = 16
        );        
    }
}




