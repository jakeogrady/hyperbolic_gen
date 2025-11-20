import numpy as np
import plotly.graph_objects as go

def rotate_points(X, Y, Z, R):
    pts = np.vstack([X.ravel(), Y.ravel(), Z.ravel()])
    pts_rot = R @ pts
    X_rot = pts_rot[0,:].reshape(X.shape)
    Y_rot = pts_rot[1,:].reshape(Y.shape)
    Z_rot = pts_rot[2,:].reshape(Z.shape)
    return X_rot, Y_rot, Z_rot

def rotation_matrix_y(theta_deg):
    theta = np.radians(theta_deg)
    return np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])

def plane_plane_intersection_segment(n1, d1, n2, d2, length=10):
    """
    Returns two points forming a finite line segment where two planes intersect.
    Returns None if planes are parallel (no intersection).
    """
    v = np.cross(n1, n2)
    norm_v = np.linalg.norm(v)
    if norm_v < 1e-12:
        return None
    v /= norm_v
    idx = np.argmax(np.abs(v))
    idxs = [i for i in range(3) if i != idx]
    A2 = np.array([[n1[idxs[0]], n1[idxs[1]]],
                   [n2[idxs[0]], n2[idxs[1]]]])
    b2 = np.array([d1, d2])
    try:
        sol = np.linalg.solve(A2, b2)
    except np.linalg.LinAlgError:
        return None
    X0 = np.zeros(3)
    X0[idx] = 0
    X0[idxs[0]] = sol[0]
    X0[idxs[1]] = sol[1]
    return X0 - v*length/2, X0 + v*length/2

def plotly_planes_with_flush_lines():
    # Grid for planes
    x = np.linspace(-5,5,50)
    y = np.linspace(-5,5,50)
    Xg, Yg = np.meshgrid(x, y)

    # Plane coefficients
    a1, b1, c1 = 1.0, 2.0, 3.0
    a2, b2, c2 = -0.5, 1.0, 6.0
    Z1 = a1*Xg + b1*Yg + c1
    Z2 = a2*Xg + b2*Yg + c2

    # Fixed point O
    O = np.array([3.0, 1.0, 2.0])

    # Line L on Π before forming the perspective plane
    L1_start = np.array([-3, -3, a1*(-3)+b1*(-3)+c1])
    L1_end   = np.array([ 3,  3, a1*(3)+b1*(3)+c1])

    # Plane through O and line L (perspective plane)
    v1 = L1_end - L1_start
    v2 = O - L1_start
    n_persp = np.cross(v1, v2)
    d_persp = np.dot(n_persp, L1_start)

    # Create figure
    fig = go.Figure()
    # Plane surfaces
    fig.add_trace(go.Surface(x=Xg, y=Yg, z=Z1, colorscale='Blues', opacity=0.7, name='Π'))
    fig.add_trace(go.Surface(x=Xg, y=Yg, z=Z2, colorscale='Reds', opacity=0.7, name='Π₀'))
    # Black line from O to origin
    fig.add_trace(go.Scatter3d(
        x=[O[0]], y=[O[1]], z=[O[2]],
        mode="markers",
        marker=dict(size=6, color="black"),
        name="O"
    ))
    # Placeholders for yellow and green lines
    fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,0], mode="lines", line=dict(color='gold', width=6), name='Yellow Π'))
    fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,0], mode="lines", line=dict(color='green', width=6), name='Green Π₀'))

    # Rotation angles
    angles = np.linspace(0,180,20)
    frames = []

    for angle1 in angles:
        R1 = rotation_matrix_y(angle1)
        X1_rot, Y1_rot, Z1_rot = rotate_points(Xg, Yg, Z1, R1)
        n1_rot = R1 @ np.array([-a1,-b1,1])
        d1_rot = c1
        for angle2 in angles:
            R2 = rotation_matrix_y(angle2)
            X2_rot, Y2_rot, Z2_rot = rotate_points(Xg, Yg, Z2, R2)
            n2_rot = R2 @ np.array([-a2,-b2,1])
            d2_rot = c2

            # --- Yellow line on Π: intersection of Π and perspective plane ---
            yellow_seg = plane_plane_intersection_segment(n1_rot, d1_rot, n_persp, d_persp)
            if yellow_seg is None:
                x_y, y_y, z_y = [np.nan,np.nan],[np.nan,np.nan],[np.nan,np.nan]
                x_g, y_g, z_g = [np.nan,np.nan],[np.nan,np.nan],[np.nan,np.nan]
            else:
                y_start, y_end = yellow_seg
                x_y, y_y, z_y = [y_start[0], y_end[0]], [y_start[1], y_end[1]], [y_start[2], y_end[2]]
                # --- Green line on Π₀: intersection of Π₀ and same perspective plane ---
                green_seg = plane_plane_intersection_segment(n2_rot, d2_rot, n_persp, d_persp)
                if green_seg is None:
                    x_g, y_g, z_g = [np.nan,np.nan],[np.nan,np.nan],[np.nan,np.nan]
                else:
                    g_start, g_end = green_seg
                    x_g, y_g, z_g = [g_start[0], g_end[0]], [g_start[1], g_end[1]], [g_start[2], g_end[2]]

            # Compose frame
            frames.append(go.Frame(name=f"f-{angle1:.1f}-{angle2:.1f}",
                                   data=[
                                       go.Surface(x=X1_rot, y=Y1_rot, z=Z1_rot, showscale=False, opacity=0.7),
                                       go.Surface(x=X2_rot, y=Y2_rot, z=Z2_rot, showscale=False, opacity=0.7),
                                       go.Scatter3d(
                                           x=[O[0]], y=[O[1]], z=[O[2]],
                                           mode="markers",
                                           marker=dict(size=6, color="black"),
                                           name="O"
                                       ),
                                       go.Scatter3d(x=x_y, y=y_y, z=z_y, mode="lines", line=dict(color='gold', width=6)),
                                       go.Scatter3d(x=x_g, y=y_g, z=z_g, mode="lines", line=dict(color='green', width=6))
                                   ]))

    fig.frames = frames

    # Sliders
    slider1 = dict(active=0, currentvalue={"prefix":"Plane Π angle: "}, x=0.1, y=0.05, len=0.8,
                   steps=[dict(label=f"{a:.1f}", method="animate",
                               args=[[f"f-{a:.1f}-0.0"], {"frame":{"duration":0,"redraw":True},"mode":"immediate"}]) for a in angles])
    slider2 = dict(active=0, currentvalue={"prefix":"Plane Π₀ angle: "}, x=0.1, y=0, len=0.8,
                   steps=[dict(label=f"{a:.1f}", method="animate",
                               args=[[f"f-0.0-{a:.1f}"], {"frame":{"duration":0,"redraw":True},"mode":"immediate"}]) for a in angles])

    fig.update_layout(sliders=[slider1,slider2],
                      scene=dict(xaxis=dict(range=[-10,10]),
                                 yaxis=dict(range=[-10,10]),
                                 zaxis=dict(range=[-20,20]),
                                 aspectmode='cube'))
    fig.show()

if __name__ == "__main__":
    plotly_planes_with_flush_lines()
