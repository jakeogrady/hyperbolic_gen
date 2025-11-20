import numpy as np
import plotly.graph_objects as go

# --- Rotation helpers ---
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

# --- Projective map f ---
def project_point_to_plane(O, X, n0, d0):
    direction = X - O
    denom = np.dot(n0, direction)
    if np.abs(denom) < 1e-12:
        return None
    t = (d0 - np.dot(n0, O)) / denom
    return O + t * direction

def line_on_plane_via_projection(O, line_pts, n0, d0):
    L0 = [project_point_to_plane(O, X, n0, d0) for X in line_pts]
    L0 = np.array([p if p is not None else [np.nan,np.nan,np.nan] for p in L0])
    return L0

# --- Triangle plane through line and point O ---
def triangle_plane_through_line_and_point(L_start, L_end, O):
    """
    Return three points forming a triangle plane through line (L_start,L_end) and point O
    Suitable for go.Mesh3d in Plotly.
    """
    X = np.array([L_start[0], L_end[0], O[0]])
    Y = np.array([L_start[1], L_end[1], O[1]])
    Z = np.array([L_start[2], L_end[2], O[2]])
    return X, Y, Z

# --- Main plotting ---
def plotly_planes_with_projective_map():
    # Grid for planes
    x = np.linspace(-5,5,50)
    y = np.linspace(-5,5,50)
    Xg, Yg = np.meshgrid(x, y)

    # Plane Π coefficients: z = a1*x + b1*y + c1 (flatter)
    a1, b1, c1 = 0.5, 0.3, 3.0
    # Plane Π0 coefficients
    a2, b2, c2 = -0.5, 1.0, 6.0

    Z1 = a1*Xg + b1*Yg + c1
    Z2 = a2*Xg + b2*Yg + c2

    # Fixed point O
    O = np.array([3.0, 1.0, 2.0])

    # Line L on Π (diagonal)
    L1_start = np.array([-3, -3, a1*(-3)+b1*(-3)+c1])
    L1_end   = np.array([ 3,  3, a1*(3)+b1*(3)+c1])
    line_pts = np.linspace(L1_start, L1_end, 20)

    # Plane Π0 normal and offset (z - a2*x - b2*y = c2)
    n0 = np.array([-a2,-b2,1])
    d0 = c2

    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Surface(x=Xg, y=Yg, z=Z1, colorscale='Blues', opacity=0.7, name='Π'))
    fig.add_trace(go.Surface(x=Xg, y=Yg, z=Z2, colorscale='Reds', opacity=0.7, name='Π₀'))
    fig.add_trace(go.Scatter3d(x=[O[0]], y=[O[1]], z=[O[2]],
                               mode="markers", marker=dict(size=6,color="black"), name="O"))

    # Placeholder for yellow triangle plane
    fig.add_trace(go.Mesh3d(x=[0,0,0], y=[0,0,0], z=[0,0,0],
                            color='yellow', opacity=0.5, name='Yellow plane'))

    # Animation frames
    angles = np.linspace(0,180,20)
    frames = []

    for angle in angles:
        R = rotation_matrix_y(angle)
        X1_rot, Y1_rot, Z1_rot = rotate_points(Xg, Yg, Z1, R)

        # Rotate line L
        L_rot = np.array([R @ pt for pt in line_pts])
        L_start_rot = L_rot[0]
        L_end_rot = L_rot[-1]

        # Yellow triangle plane through O and rotated L
        X_y, Y_y, Z_y = triangle_plane_through_line_and_point(L_start_rot, L_end_rot, O)

        mesh_plane = go.Mesh3d(
            x=X_y, y=Y_y, z=Z_y,
            color='yellow', opacity=0.5,
            i=[0], j=[1], k=[2],
            name='Yellow plane'
        )

        frames.append(go.Frame(name=f"f-{angle:.1f}",
                               data=[
                                   go.Surface(x=X1_rot, y=Y1_rot, z=Z1_rot, showscale=False, opacity=0.7),
                                   go.Surface(x=Xg, y=Yg, z=Z2, showscale=False, opacity=0.7),
                                   go.Scatter3d(x=[O[0]], y=[O[1]], z=[O[2]],
                                                mode="markers", marker=dict(size=6,color="black")),
                                   mesh_plane
                               ]))

    fig.frames = frames

    # Slider
    slider = dict(active=0, currentvalue={"prefix":"Rotation angle: "}, x=0.1, y=0.05, len=0.8,
                  steps=[dict(label=f"{a:.1f}", method="animate",
                              args=[[f"f-{a:.1f}"], {"frame":{"duration":0,"redraw":True},"mode":"immediate"}])
                         for a in angles])

    fig.update_layout(sliders=[slider],
                      scene=dict(xaxis=dict(range=[-10,10]),
                                 yaxis=dict(range=[-10,10]),
                                 zaxis=dict(range=[-20,20]),
                                 aspectmode='cube'))

    fig.show()

if __name__ == "__main__":
    plotly_planes_with_projective_map()
