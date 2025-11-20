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

# --- Triangle plane (thin triangle, adjustable width) ---
def triangle_plane_controlled(O, L_start, length=20.0, width=5.5):
    v = L_start - O
    v = v / np.linalg.norm(v)

    tmp = np.array([0, 0, 1])
    if abs(np.dot(tmp, v)) > 0.9:
        tmp = np.array([0, 1, 0])

    w = np.cross(v, tmp)
    w = w / np.linalg.norm(w)

    A = O
    B = O + v * length
    C = O + v * length + w * width

    X = np.array([A[0], B[0], C[0]])
    Y = np.array([A[1], B[1], C[1]])
    Z = np.array([A[2], B[2], C[2]])

    return X, Y, Z

# --- Intersection of triangle with plane ---
def green_line_on_plane_dynamic(A, B, C, n_plane, P_plane):
    def intersect_edge(P1, P2):
        u = P2 - P1
        denom = np.dot(n_plane, u)
        if abs(denom) < 1e-12:
            return None
        t = np.dot(n_plane, P_plane - P1) / denom
        if 0 <= t <= 1:
            return P1 + t*u
        return None

    points = []
    for edge in [(A,B),(B,C),(C,A)]:
        p = intersect_edge(edge[0], edge[1])
        if p is not None:
            points.append(p)

    if len(points) >= 2:
        return points[0], points[1]
    return None, None

# --- Main animation ---
def plotly_planes_with_dynamic_green_lines():
    x = np.linspace(-5,5,50)
    y = np.linspace(-5,5,50)
    Xg, Yg = np.meshgrid(x, y)

    # Blue plane (rotates)
    a1, b1, c1 = 0.5, 0.3, 4.0
    # Red plane (fixed)
    a2, b2, c2 = 10, 4.0, 1.0

    Z1 = a1*Xg + b1*Yg + c1
    Z2 = a2*Xg + b2*Yg + c2

    # Fixed point O
    O = np.array([10.0, 1.0, -3.0])

    # Base line for triangle orientation
    L1_start = np.array([-3, -3, a1*(-3)+b1*(-3)+c1])
    L1_end   = np.array([ 3,  3, a1*(3)+b1*(3)+c1])
    line_pts = np.linspace(L1_start, L1_end, 20)

    # Static initial figure
    fig = go.Figure()

    fig.add_trace(go.Surface(x=Xg, y=Yg, z=Z1, colorscale='Blues', opacity=0.7, name='Π'))
    fig.add_trace(go.Surface(x=Xg, y=Yg, z=Z2, colorscale='Reds', opacity=0.7, name='Π₀'))

    fig.add_trace(go.Scatter3d(x=[O[0]], y=[O[1]], z=[O[2]],
                               mode="markers", marker=dict(size=6,color="black"), name="O"))

    fig.add_trace(go.Mesh3d(x=[0,0,0], y=[0,0,0], z=[0,0,0],
                            color='yellow', opacity=0.5, name='Yellow plane'))

    fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,0],
                               mode='lines', line=dict(color='green', width=5),
                               name='Intersection Blue'))

    fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,0],
                               mode='lines', line=dict(color='lime', width=5),
                               name='Intersection Red'))

    # Animation frames
    angles = np.linspace(0,180,20)
    frames = []

    for angle in angles:
        R = rotation_matrix_y(angle)

        # Rotated blue plane normal & point
        n_blue = np.array([-a1,-b1,1])
        n_blue_rot = R @ n_blue
        P_blue_rot = R @ np.array([0,0,c1])

        # Red plane normal & point (NOT rotating)
        n_red = np.array([-a2,-b2,1])
        P_red = np.array([0,0,c2])

        # Rotate blue plane surface
        X1_rot, Y1_rot, Z1_rot = rotate_points(Xg, Yg, Z1, R)
        # Red plane fixed
        X2_rot, Y2_rot, Z2_rot = Xg, Yg, Z2

        # Rotate direction line for triangle
        L_rot = np.array([R @ pt for pt in line_pts])
        L_start_rot = L_rot[0]

        # Yellow triangle
        X_y, Y_y, Z_y = triangle_plane_controlled(O, L_start_rot)
        A = np.array([X_y[0],Y_y[0],Z_y[0]])
        B = np.array([X_y[1],Y_y[1],Z_y[1]])
        C = np.array([X_y[2],Y_y[2],Z_y[2]])

        mesh_plane = go.Mesh3d(
            x=X_y, y=Y_y, z=Z_y,
            color='yellow', opacity=0.5,
            i=[0], j=[1], k=[2]
        )

        # Green line: intersection with BLUE plane
        P1b, P2b = green_line_on_plane_dynamic(A, B, C, n_blue_rot, P_blue_rot)
        if P1b is not None and P2b is not None:
            green_line_blue = go.Scatter3d(
                x=[P1b[0], P2b[0]], y=[P1b[1], P2b[1]], z=[P1b[2], P2b[2]],
                mode='lines', line=dict(color='green', width=5)
            )
        else:
            green_line_blue = go.Scatter3d(x=[0,0],y=[0,0],z=[0,0],mode='lines')

        # Green line: intersection with RED plane
        P1r, P2r = green_line_on_plane_dynamic(A, B, C, n_red, P_red)
        if P1r is not None and P2r is not None:
            green_line_red = go.Scatter3d(
                x=[P1r[0], P2r[0]], y=[P1r[1], P2r[1]], z=[P1r[2], P2r[2]],
                mode='lines', line=dict(color='lime', width=5)
            )
        else:
            green_line_red = go.Scatter3d(x=[0,0],y=[0,0],z=[0,0],mode='lines')

        frames.append(go.Frame(
            name=f"f-{angle:.1f}",
            data=[
                go.Surface(x=X1_rot, y=Y1_rot, z=Z1_rot, showscale=False, opacity=0.7),
                go.Surface(x=X2_rot, y=Y2_rot, z=Z2_rot, showscale=False, opacity=0.7),
                go.Scatter3d(x=[O[0]], y=[O[1]], z=[O[2]],
                             mode="markers", marker=dict(size=6,color="black")),
                mesh_plane,
                green_line_blue,
                green_line_red
            ]
        ))

    fig.frames = frames

    fig.update_layout(
        sliders=[dict(
            active=0,
            currentvalue={"prefix": "Rotation angle: "},
            steps=[dict(
                label=f"{a:.1f}",
                method="animate",
                args=[[f"f-{a:.1f}"],
                      {"frame":{"duration":0,"redraw":True}, "mode":"immediate"}]
            ) for a in angles]
        )],
        scene=dict(
            xaxis=dict(range=[-10,10]),
            yaxis=dict(range=[-10,10]),
            zaxis=dict(range=[-20,20]),
            aspectmode='cube'
        )
    )

    fig.show()

if __name__ == "__main__":
    plotly_planes_with_dynamic_green_lines()
