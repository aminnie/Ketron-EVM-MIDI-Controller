
// RP2040 PCB parameters
pcb_length = 105;          // RP2040 PCB length (mm)
pcb_width = 60;            // RP2040 PCB width (mm)
pcb_thickness = 1.6;       // Standard PCB thickness (mm)
pcb_clearance = 1;         // Space around PCB (mm)
pcb_height_clearance = 8;  // Space above PCB for components (mm)

// Overall cover dimensions addinh Quad Encoder
qencoder_width = 25;      // Width of Quad Encoder (mm)
cover_length = 105 - 1;   // Total length of cover (mm)  
cover_width = 60 + qencoder_width;         // Total width of cover (mm)
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
//encoder_offset_x = 18.5 ;   // X position relative to center
encoder_offset_x = -48.5 - qencoder_width / 2;   // X position relative to center
encoder_offset_y = 38.5;   // Y position relative to center
encoder_shaft_z = 7;      // Encoder shaft height
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
            
    // Wrap the open encoder shaft
    quad_encoder_wrap();                        

    quad_encoder_hole();                       

    // Cut out encoder shaft hole
    encoder_round_hole();    
}


quad_encoder_offset_x = 0;
quad_encoder_offset_y = 0;

quad_encoder_z = 4;

wall_width = 2;
quad_encoder_size_x = 75/2 + wall_width;
quad_encoder_size_y = 13/2 + wall_width;

quad_encoder_hole_x = 75;
quad_encoder_hole_y = 13;

encoder_z = quad_encoder_z - shaft_wall_width;  // 2mm Shaft top cover


// Seperated: Create rotary encoder hole through cover base and shaft cibe
module quad_encoder_wrap() {
    
    translate([quad_encoder_offset_x, quad_encoder_offset_y, 0]) {
        // Square hole with slightly rounded corners for encoder
        hull() {
            // Four corner cylinders for rounded square
            translate([+(quad_encoder_size_x - shaft_corner_radius), -(quad_encoder_size_y - shaft_corner_radius), 0])
                cylinder(h = cover_thickness + quad_encoder_z, r = shaft_corner_radius, $fn = 32);
            
            translate([-(quad_encoder_size_x - shaft_corner_radius), -(quad_encoder_size_y - shaft_corner_radius), 0])
                cylinder(h = cover_thickness + quad_encoder_z, r = shaft_corner_radius, $fn = 32);
            
            translate([+(quad_encoder_size_x - shaft_corner_radius), (quad_encoder_size_y - shaft_corner_radius), 0])
                cylinder(h = cover_thickness + quad_encoder_z, r = shaft_corner_radius, $fn = 32);
            
            translate([-(quad_encoder_size_x - shaft_corner_radius), (quad_encoder_size_y - shaft_corner_radius), 0])
                cylinder(h = cover_thickness + quad_encoder_z, r = shaft_corner_radius, $fn = 32);
        }
    }
}

// Encoder hole in cover base
module quad_encoder_hole() {
    
    color("blue") translate([quad_encoder_offset_x, quad_encoder_offset_y, 5]) {
        // Square hole with slightly rounded corners for encoder
        cube([quad_encoder_hole_x, quad_encoder_hole_y, 7], center = true);
    }    
}


// Seperated: Create Encoder 6mm Shaft through hole
module encoder_round_hole() {

    encoder_count = 4;
    x_offset_start = 30;
    x_offset_incr = 18.5;
    
    for (row = [0 : encoder_count - 1]) {

        color("red") translate([x_offset_start - x_offset_incr * row, 0, -0.5]) {
            // Through hole for encoder shaft
            cylinder(
                h = encoder_shaft_z + 2, 
                d = encoder_shaft_diameter + 2, 
                $fn = 16
            );        
        }
        
    }
}
