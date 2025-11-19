import numpy as np
import plotly.graph_objects as go

def rotate_points(X, Y, Z, R):
    """
    Rotate points using a 3x3 rotation matrix R.
    X, Y, Z: grids of points
    """
    pts = np.vstack([X.ravel(), Y.ravel(), Z.ravel()])
    pts_rot = R @ pts
    X_rot = pts_rot[0,:].reshape(X.shape)
    Y_rot = pts_rot[1,:].reshape(Y.shape)
    Z_rot = pts_rot[2,:].reshape(Z.shape)
    return X_rot, Y_rot, Z_rot

def rotation_matrix_y(theta_deg):
    """
    Rotation matrix around Y axis by theta degrees
    """
    theta = np.radians(theta_deg)
    R = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])
    return R

def plotly_rotating_planes():
    # Grid
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)

    # Plane definitions (z = a*x + b*y + c)
    a1, b1, c1 = 1, 8, 3
    a2, b2, c2 = -7, 3, 1

    Z1 = a1*X + b1*Y + c1
    Z2 = a2*X + b2*Y + c2

    # Intersection point for the normal (fixed point on plane 1)
    P_intersect = np.array([0, 0, c1])

    # Normal vector to plane 1
    normal = np.array([a1, b1, -1])
    normal = normal / np.linalg.norm(normal)
    scale = 10  # length of the normal line

    # Create figure
    fig = go.Figure()

    # Initial traces
    fig.add_trace(go.Surface(x=X, y=Y, z=Z1, colorscale='Blues', opacity=0.7))  # plane 1
    fig.add_trace(go.Surface(x=X, y=Y, z=Z2, colorscale='Reds', opacity=0.7))   # plane 2

    # Add initial normal line
    P0_line = P_intersect - 0.5 * scale * normal
    P1_line = P_intersect + 0.5 * scale * normal
    fig.add_trace(go.Scatter3d(
        x=[P0_line[0], P1_line[0]],
        y=[P0_line[1], P1_line[1]],
        z=[P0_line[2], P1_line[2]],
        mode="lines",
        line=dict(color="black", width=8),
        name="Normal Vector"
    ))

    # Rotation angles
    angles = np.linspace(0, 180, 20)

    frames = []

    for angle1 in angles:      # Plane 1 rotation
        R1 = rotation_matrix_y(angle1)
        X1_rot, Y1_rot, Z1_rot = rotate_points(X, Y, Z1, R1)

        # Rotate normal vector using same rotation
        normal_rot = R1 @ normal
        P0_line_rot = P_intersect - 0.5*scale*normal_rot
        P1_line_rot = P_intersect + 0.5*scale*normal_rot

        for angle2 in angles:  # Plane 2 rotation
            R2 = rotation_matrix_y(angle2)
            X2_rot, Y2_rot, Z2_rot = rotate_points(X, Y, Z2, R2)

            frames.append(go.Frame(
                name=f"f-{angle1:.1f}-{angle2:.1f}",
                data=[
                    go.Surface(x=X1_rot, y=Y1_rot, z=Z1_rot),  # plane 1
                    go.Surface(x=X2_rot, y=Y2_rot, z=Z2_rot),  # plane 2
                    go.Scatter3d(
                        x=[P0_line_rot[0], P1_line_rot[0]],
                        y=[P0_line_rot[1], P1_line_rot[1]],
                        z=[P0_line_rot[2], P1_line_rot[2]],
                        mode="lines",
                        line=dict(color="black", width=8)
                    )
                ]
            ))

    fig.frames = frames

    # Slider for Plane 1
    slider1 = dict(
        active=0,
        currentvalue={"prefix": "Plane 1 angle: "},
        x=0.1, y=0.05,
        len=0.8,
        steps=[dict(
            label=f"{angle:.1f}",
            method="animate",
            args=[[f"f-{angle:.1f}-{0:.1f}"], {"frame": {"duration":0,"redraw":True}, "mode":"immediate"}]
        ) for angle in angles]
    )

    # Slider for Plane 2
    slider2 = dict(
        active=0,
        currentvalue={"prefix": "Plane 2 angle: "},
        x=0.1, y=0,
        len=0.8,
        steps=[dict(
            label=f"{angle:.1f}",
            method="animate",
            args=[[f"f-{0:.1f}-{angle:.1f}"], {"frame": {"duration":0,"redraw":True}, "mode":"immediate"}]
        ) for angle in angles]
    )

    fig.update_layout(
        sliders=[slider1, slider2],
        scene=dict(
            xaxis=dict(range=[-10,10]),
            yaxis=dict(range=[-10,10]),
            zaxis=dict(range=[-20,20]),
            aspectmode='cube'
        )
    )

    fig.show()


if __name__ == "__main__":
    plotly_rotating_planes()
