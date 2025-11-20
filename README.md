# Perspective Visualizer

This program provides an interactive 3D visualization of perspectivity between two planes.
The construction involves a fixed point O, a rotating plane Π (blue), and a fixed reference plane Π′ (red).
As the blue plane rotates, the lines of intersection between the projection rays from O and each plane change dynamically.
By applying rotation matrices, we can rotate Π to explore the variety of perspective projections that arise between just two planes.

The visualization demonstrates how a line in one plane corresponds to a different line in another plane.
It reflects the geometric concept illustrated in Lecture 19, where the set of lines connecting O to points on a line 
in Π forms a plane that intersects Π′ in a line L′, which is the perspectivity image of L.

This also highlights an important property: if either plane becomes parallel to the plane defined by rays from O,
no intersection line can be formed, demonstrating the limitations of the perspectivity mapping.

# Benefits
Provides an intuitive, visual understanding of how perspective projections depend on the relative orientation of planes and viewpoint.

Allows observation of how rotation of a plane or viewpoint affects the resulting intersection lines.

Clearly demonstrates cases where the perspectivity mapping is undefined, offering insight into degenerate configurations.

# Example of the Visualizer

![visualizer](visualizer.gif)