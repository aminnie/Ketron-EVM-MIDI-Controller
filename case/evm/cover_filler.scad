// MacroPad RP2040 Top Interim Layer
// Design for Adafruit MacroPad RP2040 keyboard controller
// Author: Generated for CircuitPython EVM Controller project
// License: MIT

// Cheatsheet: https://openscad.org/cheatsheet/index.html?version=2021.01

// The cover filler is a loose fitting template that is placed underneath the
// Macropad cover to secure the cover. The cover
// layer goes on top of this later, and key switches are inserted into the 
// PCB board through the tight fitting cover layer amd the cover filler.
// Please considerer using the newer covver filler support later that also
// wraps around the LCD screen and then encoder shaft to better support the
// top cover.

// =============================================================================
// PARAMETERS
// =============================================================================

// Adafruit Macropad RP2040 PCB parameters
pcb_length = 105;          // RP2040 PCB length (mm)
pcb_width = 60;            // RP2040 PCB width (mm)
pcb_thickness = 1.6;       // Standard PCB thickness (mm)
pcb_clearance = 1;         // Space around PCB (mm)
pcb_height_clearance = 8;  // Space above PCB for components (mm)

// Overall cover dimensions
cover_length = 78;          // Total width of cover (mm)  
cover_width = 58;         // Total length of cover (mm)
cover_thickness = 1.5;       // Thickness of top plate (mm)
corner_radius = 1;         // Rounded corner radius (mm)

// Key switch parameters (Cherry MX compatible) + some space
key_switch_size = 14 + 2;   // Square hole size for key switches (mm)
key_switch_spacing = 19.05; // Center-to-center spacing (0.75" standard)
key_rows = 4;              // Number of rows
key_cols = 3;              // Number of columns

// Key switch grid positioning (relative to cover center)
keys_offset_x = 0;         // X offset of key grid center
keys_offset_y = 0;       // Y offset of key grid center (negative = toward bottom)

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
    
}

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

