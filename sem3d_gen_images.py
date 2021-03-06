import numpy as np
import os
import scipy.misc



# load the configuration file and define variables
print("Loading configuration file")
import argparse
import json
parser = argparse.ArgumentParser(description='Semantic3D')
parser.add_argument('--config', type=str, default="config.json", metavar='N',
help='config file')
args = parser.parse_args()
json_data=open(args.config).read()
config = json.loads(json_data)

if config["training"]:
    input_dir = config["train_input_dir"]
    directory = config["train_results_root_dir"]
    cam_number = config["train_cam_number"]
    create_mesh = config["train_create_mesh"]
    create_views = config["train_create_views"]
    create_images = config["train_create_images"]
else:
    input_dir = config["test_input_dir"]
    directory = config["test_results_root_dir"]
    cam_number = config["test_cam_number"]
    create_mesh = config["test_create_mesh"]
    create_views = config["test_create_views"]
    create_images = config["test_create_images"]

voxels_directory = os.path.join(directory,"voxels")
image_directory = os.path.join(directory,config["images_dir"])
voxel_size = config["voxel_size"]
imsize = config["imsize"]


# create directories if not already existing
if not os.path.exists(directory):
    os.makedirs(directory)
if not os.path.exists(voxels_directory):
    os.makedirs(voxels_directory)
if not os.path.exists(image_directory):
    os.makedirs(image_directory)

if(config["training"]):
    # training filenames
    filenames = [
        "bildstein_station1_xyz_intensity_rgb",
        # "bildstein_station3_xyz_intensity_rgb",
        # "bildstein_station5_xyz_intensity_rgb",
        # "domfountain_station1_xyz_intensity_rgb",
        # "domfountain_station2_xyz_intensity_rgb",
        # "domfountain_station3_xyz_intensity_rgb",
        # "neugasse_station1_xyz_intensity_rgb",
        # "sg27_station1_intensity_rgb",
        # "sg27_station2_intensity_rgb",
         #"sg27_station4_intensity_rgb",
         #"sg27_station5_intensity_rgb",
         #"sg27_station9_intensity_rgb",
         #"sg28_station4_intensity_rgb",
         #"untermaederbrunnen_station1_xyz_intensity_rgb",
         #"untermaederbrunnen_station3_xyz_intensity_rgb"
        ]
else: # testing filename
    filenames = [
        "sg27_station4_intensity_rgb",
        "sg27_station5_intensity_rgb",
        "sg27_station9_intensity_rgb",
        "sg28_station4_intensity_rgb",
        "untermaederbrunnen_station1_xyz_intensity_rgb",
        "untermaederbrunnen_station3_xyz_intensity_rgb"
        # "birdfountain_station1_xyz_intensity_rgb",
        # "castleblatten_station1_intensity_rgb",
        # "castleblatten_station5_xyz_intensity_rgb",
        # "marketplacefeldkirch_station1_intensity_rgb",
        # "marketplacefeldkirch_station4_intensity_rgb",
        # "marketplacefeldkirch_station7_intensity_rgb",
        # "sg27_station10_intensity_rgb",
        # "sg27_station3_intensity_rgb",
        # "sg27_station6_intensity_rgb",
        # "sg27_station8_intensity_rgb",
        # "sg28_station2_intensity_rgb",
        # "sg28_station5_xyz_intensity_rgb",
        # "stgallencathedral_station1_intensity_rgb",
        # "stgallencathedral_station3_intensity_rgb",
        # "stgallencathedral_station6_intensity_rgb"
    ]


if create_mesh:

    import pointcloud_tools.lib.python.PcTools as PcTls
    for filename in filenames:
        print(filename)


        # create the mesher
        semantizer = PcTls.Semantic3D()
        semantizer.set_voxel_size(voxel_size)

        #loading data and voxelization
        print("  -- loading data")
        if config["training"]:
            semantizer.load_Sem3D_labels(os.path.join(input_dir,filename+".txt").encode('utf_8'),
                os.path.join(input_dir,filename+".labels").encode('utf-8'))
        else:
            semantizer.load_Sem3D(os.path.join(input_dir,filename+".txt").encode('utf-8'))

        # estimate normals
        print("  -- estimating normals")
        semantizer.estimate_normals_regression(100)

        print("  -- estimating noise")
        semantizer.estimate_noise_radius(1.)

        print("  -- estimating Z orient")
        semantizer.estimate_z_orient()

        #save points and labels
        print("  -- saving plys")
        semantizer.savePLYFile(os.path.join(voxels_directory,filename+"_points.ply").encode('utf-8'))
        semantizer.savePLYFile_composite(os.path.join(voxels_directory,filename+"_composite.ply").encode('utf-8'))
        if config["training"]:
            semantizer.savePLYFile_labels(os.path.join(voxels_directory,filename+"_labels.ply").encode('utf-8'))

        print("  -- building mesh")
        semantizer.build_mesh(False)
        semantizer.save_mesh(os.path.join(voxels_directory,filename+"_mesh.ply").encode('utf-8'))
        semantizer.save_mesh_composite(os.path.join(voxels_directory,filename+"_mesh_composite.ply").encode('utf-8'))
        if config["training"]:
            semantizer.save_mesh_labels(os.path.join(voxels_directory,filename+"_mesh_labels.ply").encode('utf-8'))

        print("  -- extracting vertices")
        vertices = semantizer.get_vertices_numpy()
        np.savez(os.path.join(voxels_directory,filename+"_vertices").encode('utf_8'), vertices)
        print("  -- extracting normals")
        normals = semantizer.get_normals_numpy()
        np.savez(os.path.join(voxels_directory,filename+"_normals").encode('utf_8'), normals)
        print("  -- extracting faces")
        faces = semantizer.get_faces_numpy()
        np.savez(os.path.join(voxels_directory,filename+"_faces").encode('utf_8'), faces)
        print("  -- extracting colors")
        colors = semantizer.get_colors_numpy()
        np.savez(os.path.join(voxels_directory,filename+"_colors").encode('utf_8'), colors)
        print("  -- extracting composite")
        composite = semantizer.get_composite_numpy()
        np.savez(os.path.join(voxels_directory,filename+"_composite").encode('utf_8'), composite)
        if config["training"]:
            print("  -- extracting labels")
            labels = semantizer.get_labels_numpy()
            np.savez(os.path.join(voxels_directory,filename+"_labels").encode('utf_8'), labels)
            print("  -- extracting labels colors")
            labelsColors = semantizer.get_labelsColors_numpy()
            np.savez(os.path.join(voxels_directory,filename+"_labelsColors").encode('utf_8'), labelsColors)

# """ commented out ViewGeneratorLauncher """
# if create_views:
#
#     # from python.viewGenerator import ViewGeneratorLauncher
#     from python.viewGenerator import ViewGeneratorNoDisplay as ViewGenerator
#
#     # launcher = ViewGeneratorLauncher()
#
#     for filename in filenames:
#         print(filename)
#         view_gen = ViewGenerator()
#         view_gen.initialize_acquisition(
#                 directory,
#                 image_directory,
#                 filename
#             )
#         view_gen.set_camera_generator(ViewGenerator.cam_generator_random_vertical_cone)
#         view_gen.opts["imsize"]= imsize
#         view_gen.generate_cameras_scales(cam_number, distances=[5,10,20])
#         view_gen.paintGL()
#         # launcher.launch(view_gen)

if create_views:

    from python.viewGenerator import ViewGeneratorLauncher
    from python.viewGenerator import ViewGeneratorNoDisplay as ViewGenerator

    launcher = ViewGeneratorLauncher()

    for filename in filenames:
        print(filename)
        view_gen = ViewGenerator()
        view_gen.initialize_acquisition(
                directory,
                image_directory,
                filename
            )
        view_gen.set_camera_generator(ViewGenerator.cam_generator_random_vertical_cone)
        view_gen.opts["imsize"]= imsize
        view_gen.generate_cameras_scales(cam_number, distances=[5,10,20])
        view_gen.init()
        launcher.launch(view_gen)

if create_images:
    from python.imageGenerator import ImageGenerator
    for filename in filenames:
        print(filename)
        # generate images
        print("  -- generating images")
        im_gen = ImageGenerator()
        if config["training"]:
            im_gen.set_isTraining(True)
        im_gen.initialize_acquisition(
                voxels_directory,
                image_directory,
                filename
            )
        im_gen.generate_images()
