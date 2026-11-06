#!/usr/bin/env python3
"""BROKE TRIO: original, deterministic 3-D cinematic intro for Blender 3.6+.
No borrowed sculpture mesh, footage, fonts, or images are required.
Usage: blender -b -t 2 --python blender/scene.py -- --mode preview --output build
"""
import argparse
import math
import os
import random
import sys

import bpy
from mathutils import Vector

R = random.Random(20261106)
FPS = 24
END = 240


def frame(seconds):
    return round(seconds * FPS) + 1


def animate(obj, prop, samples):
    for seconds, value in samples:
        setattr(obj, prop, value)
        obj.keyframe_insert(data_path=prop, frame=frame(seconds))


def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def stone_material(name, base=(0.66, 0.655, 0.625, 1)):
    m = bpy.data.materials.new(name)
    m.diffuse_color = base
    m.use_nodes = True
    nodes = m.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = 0.88
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 95
    noise.inputs["Detail"].default_value = 4
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.015
    m.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    m.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def plain_material(name, color, roughness=0.9):
    m = bpy.data.materials.new(name)
    m.diffuse_color = color
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = roughness
    return m


def uv(name, pos, scale, mat, root=None, seg=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=pos)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(mat)
    for poly in o.data.polygons:
        poly.use_smooth = True
    if root:
        o.parent = root
    return o


def cylinder(name, a, b, radius, mat, root=None, vertices=16):
    diff = Vector(b) - Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=diff.length,
        location=(Vector(a) + Vector(b)) / 2,
    )
    o = bpy.context.object
    o.name = name
    o.rotation_euler = diff.to_track_quat("Z", "Y").to_euler()
    o.data.materials.append(mat)
    for poly in o.data.polygons:
        poly.use_smooth = True
    if root:
        o.parent = root
    return o


def drapery(name, mat, root):
    # Curved, folded marble cloth across the front of the bust.
    verts, faces = [], []
    for i in range(25):
        u = (i / 24) * 2 - 1
        for j in range(7):
            v = j / 6
            x = 1.15 * u
            y = -0.32 - 0.22 * v - 0.10 * math.sin(9 * u + 4 * v)
            z = 1.02 - 0.64 * v + 0.16 * math.sin(3.2 * u + 5.8 * v)
            verts.append((x, y, z))
    for i in range(24):
        for j in range(6):
            a = i * 7 + j
            faces.append((a, a + 7, a + 8, a + 1))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    o.parent = root
    mesh.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True
    modifier = o.modifiers.new("Softened cloth folds", "SOLIDIFY")
    modifier.thickness = 0.037
    return o


def bust(name, stone, position=(0, 0, 0), size=1, yaw=0):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.location = position
    root.rotation_euler.z = yaw
    root.scale = (size,) * 3

    uv(name + ".torso", (0, 0.06, 0.82), (1.08, 0.44, 0.67), stone, root)
    uv(name + ".shoulders", (0, 0.08, 1.02), (1.45, 0.39, 0.28), stone, root)
    cylinder(name + ".neck", (0, 0, 1.04), (0, 0, 1.72), 0.30, stone, root)
    uv(name + ".head", (0, 0, 2.02), (0.54, 0.46, 0.70), stone, root, 32, 24)
    uv(name + ".chin", (0, -0.12, 1.61), (0.33, 0.33, 0.18), stone, root)
    uv(name + ".nose", (0, -0.52, 2.02), (0.12, 0.20, 0.27), stone, root)
    for s in (-1, 1):
        uv(name + ".cheek", (s * 0.28, -0.36, 1.94), (0.25, 0.15, 0.22), stone, root)
        uv(name + ".brow", (s * 0.23, -0.435, 2.25), (0.19, 0.074, 0.046), stone, root)
        uv(name + ".lid", (s * 0.22, -0.457, 2.17), (0.175, 0.035, 0.043), stone, root)
        uv(name + ".ear", (s * 0.54, -0.02, 2.07), (0.12, 0.12, 0.22), stone, root)
        cylinder(name + ".arm", (s * 1.05, 0, 0.98), (s * 1.58, -0.20, 0.72), 0.23, stone, root)
    uv(name + ".lips", (0, -0.505, 1.77), (0.24, 0.045, 0.05), stone, root)
    # Independent, original curls: no stock mesh or borrowed sculpt.
    for i in range(42):
        angle = 2 * math.pi * (i / 21)
        layer = i // 21
        x = 0.48 * math.cos(angle)
        y = 0.39 * math.sin(angle)
        z = 2.50 + layer * 0.23 + 0.095 * math.sin(3 * angle + layer)
        uv(name + ".curl", (x, y, z), (.16, .16, .15), stone, root, 12, 8)
    drapery(name + ".drapery", stone, root)
    return root


def volume_smoke():
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0.2, 1.7))
    obj = bpy.context.object
    obj.name = "TRUE 3D: procedural heterogeneous fog volume"
    obj.scale = (5.7, 3.8, 2.9)
    volume = bpy.data.materials.new("Animated volumetric smoke")
    volume.use_nodes = True
    nodes = volume.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    vol = nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (.70, .71, .72, 1)
    vol.inputs["Anisotropy"].default_value = 0.35
    noise = nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "4D"
    noise.inputs["Scale"].default_value = 1.8
    noise.inputs["Detail"].default_value = 4
    animate(noise.inputs["W"], "default_value", [(0, 0.3), (10, 1.5)])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.40
    ramp.color_ramp.elements[1].position = 0.77
    density = nodes.new("ShaderNodeMath")
    density.operation = "MULTIPLY"
    density.inputs[1].default_value = 0.105
    links = volume.node_tree.links
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], density.inputs[0])
    links.new(density.outputs[0], vol.inputs["Density"])
    links.new(vol.outputs["Volume"], out.inputs["Volume"])
    obj.data.materials.append(volume)


def spotlight(name, loc, target, color):
    data = bpy.data.lights.new(name, type="SPOT")
    data.energy = 0
    data.color = color
    data.spot_size = math.radians(36)
    data.spot_blend = 0.52
    data.shadow_soft_size = 0.13
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    o.location = loc
    aim(o, target)
    return data


def shatter_and_reform(stone):
    # Deterministic, ballistic 3D particles: NOT a baked rigid-body simulation.
    shard_mat = plain_material("Stone debris", (.58, .58, .56, 1))
    for i in range(115):
        theta = R.random() * 2 * math.pi
        h = R.uniform(1.55, 2.75)
        rr = math.sqrt(max(0.08, 1 - ((h - 2.02) / .77) ** 2))
        p0 = Vector((.54 * rr * math.cos(theta), -.30 - .17 * R.random(), h))
        speed = R.uniform(1.0, 4.1)
        vel = Vector((math.cos(theta) * speed, -R.uniform(.15, 1.6), R.uniform(.2, 2.8)))
        rad = R.uniform(.025, .10)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=0, radius=rad, location=p0)
        p = bpy.context.object
        p.name = "Fracture fragment"
        p.data.materials.append(shard_mat)
        animate(p, "scale", [(0, (0, 0, 0)), (5.63, (0, 0, 0)),
                             (5.79, (1, 1, 1)), (6.95, (.33, .33, .33)),
                             (7.25, (0, 0, 0))])
        for sec in (5.7, 5.9, 6.25, 6.7, 7.23):
            t = max(0, sec - 5.72)
            pos = p0 + vel * t + Vector((0, 0, -3.2 * t * t))
            p.location = pos
            p.rotation_euler = (3 * t, t * (i % 7), t * 4)
            p.keyframe_insert(data_path="location", frame=frame(sec))
            p.keyframe_insert(data_path="rotation_euler", frame=frame(sec))
    for i in range(190):
        target_col = (i % 3) - 1
        tx = target_col * 1.73
        centerz = 1.86 if target_col else 2.06
        a = R.uniform(0, math.tau)
        z = R.uniform(-.66, .82)
        radius = R.uniform(.20, .52)
        target = (tx + radius * math.cos(a), .1 + radius * math.sin(a), centerz + z)
        spawn = (R.uniform(-2.4, 2.4), R.uniform(-1.5, 1), R.uniform(3.4, 5.3))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=0,
                                               radius=R.uniform(.01, .038), location=spawn)
        p = bpy.context.object
        p.name = "Reassembly dust"
        p.data.materials.append(shard_mat)
        animate(p, "scale", [(0, (0, 0, 0)), (7.04, (0, 0, 0)),
                             (7.19, (1, 1, 1)), (8.52, (.15, .15, .15)),
                             (8.73, (0, 0, 0))])
        animate(p, "location", [(7.16, spawn), (7.82, (target[0] * .5, -.7, 2.6)),
                               (8.55, target)])


def camera_text(camera, content, name, y, fill_ratio, material, start, end):
    crv = bpy.data.curves.new(name, "FONT")
    crv.body = content
    crv.align_x = "CENTER"
    crv.align_y = "CENTER"
    crv.space_character = 1.11
    for fontpath in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
    ):
        if os.path.exists(fontpath):
            crv.font = bpy.data.fonts.load(fontpath)
            break
    o = bpy.data.objects.new(name, crv)
    bpy.context.collection.objects.link(o)
    crv.materials.append(material)
    o.parent = camera
    o.location = (0, y, -4)
    bpy.context.view_layer.update()
    camera_width_at_depth = 4 * camera.data.sensor_width / camera.data.lens
    target_width = camera_width_at_depth * fill_ratio
    size = target_width / max(o.dimensions.x, 1e-6)
    animate(o, "scale", [(0, (0, 0, 0)), (start, (0, 0, 0)),
                          (end, (size, size, size))])
    return o


def stage():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 12
    # The Ubuntu distribution build of Blender/Cycles may not include
    # OpenImageDenoise. Explicitly disable denoise for both scene and view layer;
    # otherwise a valid scene renders with "Build without OpenImageDenoiser".
    scene.cycles.use_denoising = False
    bpy.context.view_layer.cycles.use_denoising = False
    scene.render.film_transparent = False
    scene.world.color = (0, 0, 0)

    black = plain_material("Black stage", (.003, .003, .004, 1))
    marble = stone_material("Original procedural ivory marble")
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.12))
    floor = bpy.context.object
    floor.name = "Black floor"
    floor.data.materials.append(black)

    camera_data = bpy.data.cameras.new("Cinema lens")
    camera = bpy.data.objects.new("Camera: locked safe frame", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    camera_data.lens = 55
    animate(camera, "location", [(0, (0, -10.6, 3.0)), (3.4, (0, -10.6, 3.0)),
                                 (4.8, (0, -7.1, 2.65)), (5.55, (0, -4.55, 2.34)),
                                 (6.25, (0, -4.55, 2.34)), (7.60, (0, -10.6, 3.0))])
    # Animate aim by explicit, interpolable Euler keyframes.
    for sec, point in ((0, (0, 0, 1.84)), (3.4, (0, 0, 1.84)),
                       (4.8, (0, 0, 2.00)), (5.55, (0, 0, 2.10)),
                       (6.25, (0, 0, 2.10)), (7.6, (0, 0, 1.84))):
        camera.location = Vector((0, -10.6, 3.0)) if sec <= 3.4 else (
            Vector((0, -7.1, 2.65)) if sec == 4.8 else (
            Vector((0, -4.55, 2.34)) if sec <= 6.25 else Vector((0, -10.6, 3.0))))
        aim(camera, point)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame(sec))
    camera_data.dof.use_dof = True
    camera_data.dof.focus_distance = 10
    camera_data.dof.aperture_fstop = 8
    animate(camera_data, "lens", [(0, 55), (4.8, 55), (5.55, 68), (6.25, 68), (7.6, 55)])

    volume_smoke()
    left = spotlight("01 - LEFT sequential beam", (-5.2, -3.5, 6.0), (0, 0, 1.5), (1, .96, .87))
    right = spotlight("02 - RIGHT sequential beam", (5.2, -3.5, 6.0), (0, 0, 1.5), (.83, .88, 1))
    # NEVER overlap beams: left reaches zero BEFORE right begins.
    animate(left, "energy", [(0, 0), (.85, 0), (1.15, 2200),
                             (1.62, 2200), (1.96, 0), (10, 0)])
    animate(right, "energy", [(0, 0), (2.15, 0), (2.47, 2350),
                              (2.88, 2350), (3.22, 0), (10, 0)])
    soft = bpy.data.lights.new("Post-beam stone sculpture softbox", "AREA")
    soft.energy = 0
    soft.shape = "DISK"
    soft.size = 5
    ob = bpy.data.objects.new("Cinematic key after emergence", soft)
    bpy.context.collection.objects.link(ob)
    ob.location = (-2, -4.4, 5.2)
    aim(ob, (0, 0, 1.8))
    animate(soft, "energy", [(0, 0), (3.25, 0), (3.65, 520),
                             (6.5, 520), (7.5, 700), (10, 700)])
    rim = bpy.data.lights.new("Stone rim", "AREA")
    rim.energy = 0
    rim.size = 3.5
    ob = bpy.data.objects.new("Back rim", rim)
    bpy.context.collection.objects.link(ob)
    ob.location = (3.8, 2.7, 4.2)
    aim(ob, (0, 0, 2))
    animate(rim, "energy", [(0, 0), (3.3, 0), (4.0, 750), (10, 750)])

    hero = bust("ONE original marble figure", marble)
    animate(hero, "location", [(0, (0, 2.7, -2.8)), (3.3, (0, 2.7, -2.8)),
                               (4.2, (0, .75, -.6)), (4.8, (0, 0, 0)),
                               (5.7, (0, 0, 0))])
    animate(hero, "rotation_euler", [(0, (0, 0, math.radians(45))),
                                    (3.35, (0, 0, math.radians(45))),
                                    (4.8, (0, 0, 0))])
    animate(hero, "scale", [(0, (.95, .95, .95)), (5.7, (1, 1, 1)),
                            (5.88, (.93, .93, .93)), (6.14, (0, 0, 0))])

    final_busts = [
        bust("TRIO LEFT", marble, (-1.73, .5, -.2), .73, math.radians(-26)),
        bust("TRIO CENTER", marble, (0, .26, 0), .91, 0),
        bust("TRIO RIGHT", marble, (1.73, .5, -.2), .73, math.radians(26)),
    ]
    for idx, root in enumerate(final_busts):
        base = (.73, .91, .73)[idx]
        animate(root, "scale", [(0, (0, 0, 0)), (7.66, (0, 0, 0)),
                                (8.36, (base * .88,) * 3), (8.78, (base,) * 3)])

    raymat = plain_material("Subtle pale metal starburst", (.48, .47, .43, 1))
    for j in range(46):
        a = math.pi * j / 45
        p1 = (2.05 * math.cos(a), 1.12, 2.06 + 0.95 * math.sin(a))
        p2 = (2.62 * math.cos(a), 1.12, 2.06 + 1.28 * math.sin(a))
        o = cylinder("Halo radial filament", p1, p2, .009, raymat, vertices=6)
        animate(o, "scale", [(0, (0, 0, 0)), (7.8, (0, 0, 0)),
                             (8.7, (1, 1, 1))])
    shatter_and_reform(marble)

    ivory = plain_material("Ivory titles", (.9, .87, .8, 1))
    # Camera-parented typography means position remains stable at every render size.
    camera_text(camera, "BROKE TRIO", "SAFE 70% width TITLE", -.24, .68, ivory, 8.43, 8.84)
    camera_text(camera, "N O   M O N E Y   ·   N O   T I M E   ·   N O   9 - T O - 5",
                "SAFE 70% width TAGLINE", -.47, .60, ivory, 8.79, 9.09)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1
    scene.render.pixel_aspect_y = 1
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = END
    valid_transforms = {item.identifier for item in scene.view_settings.bl_rna.properties["view_transform"].enum_items}
    scene.view_settings.view_transform = "AgX" if "AgX" in valid_transforms else "Standard"
    scene.camera.data.lens = 55
    # Blender offline compositor: restrained bloom, retaining title contrast.
    scene.use_nodes = True
    comp = scene.node_tree
    comp.nodes.clear()
    layer = comp.nodes.new("CompositorNodeRLayers")
    glow = comp.nodes.new("CompositorNodeGlare")
    glow.glare_type = "FOG_GLOW"
    glow.quality = "HIGH"
    glow.threshold = 1.2
    glow.mix = -0.88
    output = comp.nodes.new("CompositorNodeComposite")
    comp.links.new(layer.outputs["Image"], glow.inputs["Image"])
    comp.links.new(glow.outputs["Image"], output.inputs["Image"])
    return scene


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("preview", "final"), default="preview")
    ap.add_argument("--output", default="build")
    ap.add_argument("--scene-only", action="store_true")
    args = ap.parse_args(argv)
    out = os.path.abspath(args.output)
    os.makedirs(os.path.join(out, "renders"), exist_ok=True)
    sc = stage()
    sc.render.filepath = os.path.join(out, "renders", "frame_")
    sc.render.image_settings.file_format = "PNG"
    if args.mode == "preview":
        sc.render.resolution_percentage = 50  # 960x540, EXACT same 16:9 layout
        sc.frame_step = 2                      # 12 displayed frames/second
        sc.cycles.samples = 8
    else:
        sc.render.resolution_percentage = 100
        sc.frame_step = 1
        sc.cycles.samples = 24
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "BROKE_TRIO.blend"))
    if not args.scene_only:
        bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
