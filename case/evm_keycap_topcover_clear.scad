// More information: https://danielupshaw.com/openscad-rounded-corners/

module roundedcube_simple(size = [1, 1, 1], center = false, radius = 0.5) {
	// If single value, convert to [x, y, z] vector
	size = (size[0] == undef) ? [size, size, size] : size;

	translate = (center == false) ?
		[radius, radius, radius] :
		[
			radius - (size[0] / 2),
			radius - (size[1] / 2),
			radius - (size[2] / 2)
	];

	translate(v = translate)
	minkowski() {
		cube(size = [
			size[0] - (radius * 2),
			size[1] - (radius * 2),
			size[2] - (radius * 2)
		]);
		sphere(r = radius);
	}
}

module roundedcube_tapered(size = [1, 1, 1], center = false, radius = 0.5) {
	// If single value, convert to [x, y, z] vector
	size = (size[0] == undef) ? [size, size, size] : size;

	translate = (center == false) ?
		[radius, radius, radius] :
		[
			radius - (size[0] / 2),
			radius - (size[1] / 2),
			radius - (size[2] / 2)
	];

	translate(v = translate)

    hull() {

        minkowski() {
            cube(size = [
                size[0] - (radius * 2),
                size[1] - (radius * 2),
                0.1 //size[2] - (radius * 2)
            ]);
            sphere(r = radius);
        }

        translate([+1, +1, size[2]]) {
            minkowski() {
                cube(size = [
                    size[0] - 2 - (radius * 2),
                    size[1] - 2 - (radius * 2),
                    0.1 //size[2] - 2 - (radius * 2)
                ]);
                sphere(r = radius);
            }
        }
    }
}


// Module: Create tapering cube
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
    
//translate(v = [2.5, -0.5, 5])
//translate(v = [0, 0, 0])
//color("Yellow")
//roundedcube_simple([14, 14, 7], false, 0.5);

rotate([0, 180, 0])
translate([0, 0, -6])
difference() {

    color("Yellow")
        translate(v = [0, 0, 0])
        roundedcube_tapered([18, 18, 8.5], true, 1);

    // Create a tapering cube hole on inside
    color("red")
        translate([0, 0, -5])
        tapered_cube(bottom_size = [15.65, 15.65, 0.1], top_size = [14.75, 14.75, 0.1], height = 10);
}

