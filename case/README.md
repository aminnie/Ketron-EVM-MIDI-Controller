# Ketron EVM-Button-Controller Enclosure

More details and refinement of the OpenSCAD 3D (https://openscad.org/) design and code to follow.

The EVM HS13 AND HS13+ MacroPad controller enclosure consists of three components:
- Bottom case
  - The PCB and next two layers insert into the bottom case. 
  - The case has openings for the UCB connection as well as the Macropad reset.
- Top cover
  - Keys are inserted into the PCB using the top cover as guide. 
  - The top cover also hides the encoder main body with a seperately printed case (in a seperate file for the HS13)
- Filler layer
  - This layer is inserted in between the top cover laaer and the MacroPad PCB. This closes the gap between the top cover and the PCB and ensures that the latter remains correctly positions.

Assembly Instructions:
- 3D Print/order to print the three layers.
  - Check the opt cover encoder body part to ensure that it is clear of debris.
  - You may need a sharp knife or tool to clear our the encoder body, and a drill body to clean the 6mm shaft hole.
- Lay the top cover on filler layer. 
  - Note the filler layer has bigger openings for the keys than the top cover.
- Unscrew the encoder washer and nut.
- Place the filler layer, and top cover on the PCB, carefully placing the cover over the encoder main body.
  - Replace the encoder washer and nut you removed earlier and lightly tighten the it.
  - If you find that you are unable to get the nut to secure the top cover, then please revisit the step above and clear the top cover encoder body of extra print material.
  - Loosen the nut so that the cover top has a bit of play that helps with inserting the keyswitches
- Insert the 12 key switches into PCB going through the top cover.
  - The PCB has sockets for the keyswitches and no soldering is needed.
  - It will be a tight fir. Ensure you have a compatible key switch, that the pins are straight, and carefully position and insert the keys
  - I start with the middle row centers, followed by the outer corners.
- Insert the PCB assembly into the bottom case.
  - Ensure you have the USB connector aligned with the case USB opening!
  - Insert the PCB assembly at the LCD corner first so that Reset button goes into its respctive whole with out too much pressure
- Use 4 x 3mm screws to secure the bottom case to the PCB and the keyboard assembly.
  - To remobve the keyboard assembly, loosen all four screws, and remove the PCB out of the case by pushing the screws in.
- Insert the encoder knob onto the exposed shaft
  - Press the encoder button a few times and to ensure it is seated correctly.
  
  
