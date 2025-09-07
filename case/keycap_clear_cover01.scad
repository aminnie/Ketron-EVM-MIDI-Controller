/*
This module provides models of single Cherry profile keycaps
in R1 to R4 profile and sizes 1u, 1.25u, 1.5u, 1.75u, 2u, 2.25u, 2.75u and 6.25u

The actual models are taken from the ConstantinoSchillebeeckx/cherry-mx-keycaps repository
(https://github.com/ConstantinoSchillebeeckx/cherry-mx-keycaps/tree/thick-wall).
All credit for the models goes to the original author.
*/

//import("C:/Users/a_min/Ketron-EVM-Button-Controller/case/transparent_keycap_insert.stl");

//difference() {
//    cube([17,17,7.5], center = true);
//    color("red")
//        translate([0,0,-1])
//        cube([14.8,14.8,7.5], center = true);
//}


// A tapering cube using hull()
module tapered_cube(bottom_size, top_size, height) {
    hull() {
        // Bottom cube
        cube(bottom_size, center = true);

        // Top cube (translated up)
        translate([0, 0, height]) {
            cube(top_size, center = true);
        }
    }
}

// Example: Create a tapering cube with hull()
//tapered_cube(bottom_size = [40, 30, 0.1], top_size = [20, 15, 0.1], height = 20);
rotate([180,180,0])
    translate([0, 0, -7.5]) {

    difference() {
        // Example: Create a tapering cube with hull()
        tapered_cube(bottom_size = [17, 17, 0.1], top_size = [16, 16, 0.1], height = 7.5);

        color("red")
            translate([0, 0, -1])
            tapered_cube(bottom_size = [15, 15, 0.1], top_size = [14.5, 14.5, 0.1], height = 6.5);
    }
}
