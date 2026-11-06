#!/usr/bin/env python3
"""V4-A/B: high-quality CC0 scanned bust + Blender volumetric fog, two sequential spots.
Only the opening shot. No fake anatomy, no slideshow or generated poster.
Run: blender -b -t 2 --python blender/v4_opening.py -- --asset assets/external/marble_bust_01.glb --output build/v4
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

FPS = 24
END = 150

def fr(t):
    return round(FPS*t) + 1

def kf(target, prop, times):
    for time, value in times:
        setattr(target, prop, value)
        target.keyframe_insert(data_path=prop, frame=fr(time))

def look_at(obj, point):
    obj.rotation_euler = (Vector(point)-obj.location).to_track_quat("-Z","Y").to_euler()

def attach_bust(filepath):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=filepath)
    imported = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in imported if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("The downloaded GLB contains no 3D mesh. Do not substitute primitive busts.")
    bpy.context.view_layer.update()
    coords = [obj.matrix_world @ Vector(c) for obj in meshes for c in obj.bound_box]
    lo = Vector(tuple(min(v[k] for v in coords) for k in range(3)))
    hi = Vector(tuple(max(v[k] for v in coords) for k in range(3)))
    height = hi.z - lo.z
    if height <= 0 or height > 1e4:
        raise RuntimeError("Impossible model dimensions: " + str(height))
    center = (lo+hi)*.5
    root = bpy.data.objects.new("CC0 Poly Haven bust | cinematic hero", None)
    bpy.context.collection.objects.link(root)
    # Parent imported root node(s), preserving model-local transforms.
    for obj in imported:
        if obj.parent not in imported:
            world = obj.matrix_world.copy()
            obj.parent = root
            obj.matrix_world = world
    scale = 2.72 / height
    root.scale = (scale,)*3
    root.location = (-center.x*scale, -center.y*scale, -lo.z*scale)
    # Hide each mesh independently; a parent Empty hide flag is not reliable
    # for all versions/import hierarchies.
    for obj in meshes:
        kf(obj, "hide_render", [(0,True),(3.32,True),(3.38,False),(6.25,False)])
    # Actual emerging spatial path, not a cut-in.
    p = root.location.copy()
    kf(root,"location",[
        (0,tuple(p+Vector((0,2.4,-.40)))),
        (3.35,tuple(p+Vector((0,2.4,-.40)))),
        (4.25,tuple(p+Vector((0,0.8,-.12)))),
        (5.32,tuple(p)),
        (6.25,tuple(p)),
    ])
    kf(root,"rotation_euler",[
        (0,(0,0,math.radians(28))),
        (3.38,(0,0,math.radians(28))),
        (5.4,(0,0,math.radians(0))),
        (6.25,(0,0,0)),
    ])
    print(f"Imported Poly Haven CC0 3D mesh: {len(meshes)} meshes; dims {tuple(hi-lo)}; 3D scale={scale:.4f}")
    return root, meshes

def fog():
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, .6, 1.37))
    obj=bpy.context.object
    obj.name="Volume fog | physical 3-D density, no 2-D fog cards"
    obj.scale=(3.65,2.75,2.05)
    m=bpy.data.materials.new("Smoke / cool monochrome procedural 4D")
    m.use_nodes=True
    nodes=m.node_tree.nodes
    nodes.clear()
    out=nodes.new("ShaderNodeOutputMaterial")
    vol=nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value=(.72,.72,.72,1)
    vol.inputs["Anisotropy"].default_value=.42
    noise=nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions="4D"
    noise.inputs["Scale"].default_value=2.4
    noise.inputs["Detail"].default_value=5.0
    kf(noise.inputs["W"],"default_value",[(0,.12),(6.25,1.0)])
    ramp=nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position=.48
    ramp.color_ramp.elements[1].position=.81
    mult=nodes.new("ShaderNodeMath")
    mult.operation="MULTIPLY"
    mult.inputs[1].default_value=.038
    links=m.node_tree.links
    links.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"],mult.inputs[0])
    links.new(mult.outputs[0],vol.inputs["Density"])
    links.new(vol.outputs["Volume"],out.inputs["Volume"])
    obj.data.materials.append(m)

def spot(name, xyz, target, color, times):
    data=bpy.data.lights.new(name,"SPOT")
    data.energy=0
    data.color=color
    data.spot_size=math.radians(31)
    data.spot_blend=.48
    data.shadow_soft_size=.15
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location=xyz
    look_at(obj,target)
    kf(data,"energy",times)
    return obj

def spotlight_scattering_volume(name, lamp_xyz, target_xyz, cone_angle, visibility):
    """Closed 3-D cone of *actual* volume-scattering medium aligned with a spot.

    The old fog box ended at z=3.42 but lamps were at z=5.4. Most of
    each lamp cone passed through a vacuum. Keep a local true volumetric
    medium along the complete shaft; the lamp still provides all the light.
    The cone is NOT a glowing surface or flat overlay.
    """
    a, b = Vector(lamp_xyz), Vector(target_xyz)
    axis = a - b
    length = axis.length
    # Slightly smaller than spot outer edge, so softened beam tails remain
    # volumetric while rays outside the lamp stay black.
    outer = (length * math.tan(cone_angle * .5)) * .82
    bpy.ops.mesh.primitive_cone_add(
        vertices=64, radius1=outer, radius2=.045, depth=length,
        location=(a+b)*.5,
    )
    ob = bpy.context.object
    ob.name = name
    ob.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()

    m = bpy.data.materials.new(name + " | actual Cycles volume scattering")
    m.use_nodes = True
    n = m.node_tree.nodes
    n.clear()
    output = n.new("ShaderNodeOutputMaterial")
    volume = n.new("ShaderNodeVolumePrincipled")
    volume.inputs["Color"].default_value = (.79,.79,.77,1)
    volume.inputs["Anisotropy"].default_value = .12
    noise = n.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "4D"
    noise.inputs["Scale"].default_value = 2.3
    noise.inputs["Detail"].default_value = 3.0
    kf(noise.inputs["W"],"default_value",[(0,.0),(6.25,.27)])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .26
    ramp.color_ramp.elements[1].position = .75
    mul = n.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = .29

    # Feather the scattering medium spatially to zero at the *real* cone
    # boundary; otherwise a hard-edged geometric wedge is visible on camera.
    coords = n.new("ShaderNodeTexCoord")
    xyz = n.new("ShaderNodeSeparateXYZ")
    dx = n.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = .5
    dy = n.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = .5
    sx = n.new("ShaderNodeMath"); sx.operation = "MULTIPLY"
    sy = n.new("ShaderNodeMath"); sy.operation = "MULTIPLY"
    sumsq = n.new("ShaderNodeMath"); sumsq.operation = "ADD"
    radial = n.new("ShaderNodeMath"); radial.operation = "SQRT"
    one_minus_z = n.new("ShaderNodeMath"); one_minus_z.operation = "SUBTRACT"
    one_minus_z.inputs[0].default_value = 1.0
    maxrad = n.new("ShaderNodeMath"); maxrad.operation = "MULTIPLY"
    maxrad.inputs[1].default_value = .5
    safe_rad = n.new("ShaderNodeMath"); safe_rad.operation = "MAXIMUM"
    safe_rad.inputs[1].default_value = .025
    relative_radius = n.new("ShaderNodeMath"); relative_radius.operation = "DIVIDE"
    feather = n.new("ShaderNodeValToRGB")
    feather.color_ramp.interpolation = "EASE"
    feather.color_ramp.elements[0].position = .48
    feather.color_ramp.elements[0].color = (1,1,1,1)
    feather.color_ramp.elements[1].position = .96
    feather.color_ramp.elements[1].color = (0,0,0,1)
    feathered_density = n.new("ShaderNodeMath")
    feathered_density.operation = "MULTIPLY"

    link = m.node_tree.links
    link.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    link.new(ramp.outputs["Color"],mul.inputs[0])
    link.new(coords.outputs["Generated"],xyz.inputs["Vector"])
    link.new(xyz.outputs["X"],dx.inputs[0])
    link.new(xyz.outputs["Y"],dy.inputs[0])
    link.new(dx.outputs[0],sx.inputs[0]); link.new(dx.outputs[0],sx.inputs[1])
    link.new(dy.outputs[0],sy.inputs[0]); link.new(dy.outputs[0],sy.inputs[1])
    link.new(sx.outputs[0],sumsq.inputs[0])
    link.new(sy.outputs[0],sumsq.inputs[1])
    link.new(sumsq.outputs[0],radial.inputs[0])
    link.new(xyz.outputs["Z"],one_minus_z.inputs[1])
    link.new(one_minus_z.outputs[0],maxrad.inputs[0])
    link.new(maxrad.outputs[0],safe_rad.inputs[0])
    link.new(radial.outputs[0],relative_radius.inputs[0])
    link.new(safe_rad.outputs[0],relative_radius.inputs[1])
    link.new(relative_radius.outputs[0],feather.inputs["Fac"])
    link.new(mul.outputs[0],feathered_density.inputs[0])
    link.new(feather.outputs["Color"],feathered_density.inputs[1])
    link.new(feathered_density.outputs[0],volume.inputs["Density"])
    link.new(volume.outputs["Volume"],output.inputs["Volume"])
    ob.data.materials.append(m)
    kf(ob,"hide_render",visibility)
    return ob


def softbox(name, xyz, power, start):
    data=bpy.data.lights.new(name,"AREA")
    data.energy=0
    data.shape="DISK"
    data.size=4
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location=xyz
    look_at(obj,(0,0,1.45))
    kf(data,"energy",[(0,0),(start,0),(start+.55,power),(6.25,power)])
    return obj

def build(asset, output):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.samples=40
    scene.cycles.use_denoising=False
    bpy.context.view_layer.cycles.use_denoising=False
    scene.render.film_transparent=False
    scene.world.color=(0,0,0)
    # A black "world.color" does NOT override a node-based world background.
    # Set both explicitly; previous smoke frames rendered uniformly gray.
    scene.world.use_nodes=True
    world_background=scene.world.node_tree.nodes.get("Background")
    if world_background:
        world_background.inputs["Color"].default_value=(0,0,0,1)
        world_background.inputs["Strength"].default_value=0.0
    scene.render.resolution_x=1920
    scene.render.resolution_y=1080
    scene.render.resolution_percentage=50
    scene.render.pixel_aspect_x=1
    scene.render.pixel_aspect_y=1
    scene.render.fps=FPS
    scene.frame_start=1
    scene.frame_end=END
    scene.view_settings.view_transform="Standard"
    scene.view_settings.exposure=-0.55
    # No floor plane, no fake horizon line.
    fog()
    # LEFT beam fully extinguished before RIGHT beam starts.
    # The lamps are ABOVE the main diffuse fog: add narrow local volumes
    # following their actual 3-D light paths. In alternate frames only
    # one shaft can receive light; energy zero + hide_render at the gap.
    beam_angle = math.radians(31)
    spot("BEAM 01 LEFT",(-4.8,-2.7,5.4),(0,.4,1.25),(1,.95,.87),[
        (0,0),(.74,0),(1.04,3400),(1.62,3400),(1.94,0),(6.25,0)])
    spot("BEAM 02 RIGHT",(4.8,-2.7,5.4),(0,.4,1.25),(.86,.91,1),[
        (0,0),(2.12,0),(2.42,3400),(2.83,3400),(3.12,0),(6.25,0)])
    spotlight_scattering_volume(
        "LEFT independent 3D scattering shaft",(-4.8,-2.7,5.4),
        (0,.4,1.25), beam_angle,
        [(0,True),(.74,False),(1.94,True),(6.25,True)])
    spotlight_scattering_volume(
        "RIGHT independent 3D scattering shaft",(4.8,-2.7,5.4),
        (0,.4,1.25), beam_angle,
        [(0,True),(2.12,False),(3.12,True),(6.25,True)])
    # Separate softbox only after both opening beams switch off.
    softbox("MOVIE portrait key",(-2.5,-4.6,5.0),470,3.40)
    softbox("MOVIE portrait rim",(3.1,1.0,4.3),600,3.45)
    # Small fog-only fill to reveal smoke in the dark without showing a figure.
    fill=bpy.data.lights.new("Deep fog fill, not third spot","AREA")
    fill.energy=2.5
    fill.shape="DISK"
    fill.size=6
    fillobj=bpy.data.objects.new("Low contrast haze fill",fill)
    bpy.context.collection.objects.link(fillobj)
    fillobj.location=(.1,1.9,3.1)
    look_at(fillobj,(0,0,1.1))

    root,meshes=attach_bust(asset)
    camdata=bpy.data.cameras.new("Cinematic portrait | locked 16:9 safe crop")
    cam=bpy.data.objects.new("Camera",camdata)
    bpy.context.collection.objects.link(cam)
    scene.camera=cam
    camdata.lens=48
    camdata.clip_end=200
    for t,xyz in [(0,(0,-9.3,1.47)),(3.2,(0,-9.3,1.47)),(5.6,(0,-8.0,1.47)),(6.25,(0,-8.0,1.47))]:
        cam.location=xyz
        look_at(cam,(0,0,1.37))
        cam.keyframe_insert(data_path="location",frame=fr(t))
        cam.keyframe_insert(data_path="rotation_euler",frame=fr(t))
    # Save both mesh and packed textures for reproducibility.
    scene.frame_set(1)
    os.makedirs(output,exist_ok=True)
    bpy.ops.file.pack_all()
    scene.render.filepath=os.path.join(output,"shots","frame_")
    scene.render.image_settings.file_format="PNG"
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(output,"BROKE_TRIO_V4_opening.blend"))
    return scene

if __name__=="__main__":
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p=argparse.ArgumentParser()
    p.add_argument("--asset",default="assets/external/marble_bust_01.glb")
    p.add_argument("--output",default="build/v4")
    p.add_argument("--render",action="store_true")
    args=p.parse_args(argv)
    sc=build(os.path.abspath(args.asset),os.path.abspath(args.output))
    if args.render:
        # PR smoke frames prioritize lighting/layout; .blend retains 40 samples.
        # 12-sample previews avoid paying full offline-quality cost per revision.
        sc.cycles.samples=12
        os.makedirs(sc.render.filepath.rsplit("/",1)[0],exist_ok=True)
        for f in (14,39,69,101,127):
            sc.frame_set(f)
            sc.render.filepath=os.path.join(os.path.abspath(args.output),"shots",f"frame_{f:04d}.png")
            bpy.ops.render.render(write_still=True)
