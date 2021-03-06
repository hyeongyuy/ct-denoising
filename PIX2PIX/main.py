# -*- coding: utf-8 -*-
"""
@author: yeohyeongyu
"""


import argparse
import os
import sys
import tensorflow as tf
os.chdir(os.getcwd())
sys.path.extend([os.path.abspath("."), os.path.abspath("./..")])
import inout_util as ut
from pix2pix_model import pix2Pix
from time import time
os.chdir(os.getcwd() + '/..')
print('pwd : {}'.format(os.getcwd()))

parser = argparse.ArgumentParser(description='')
#set load directory
parser.add_argument('--dcm_path', dest='dcm_path', default='/data/DICOM', help='dicom file directory')
parser.add_argument('--input_path', dest='input_path', default='LDCT', \
                    help='LDCT image folder name')
parser.add_argument('--target_path', dest='target_path', default='NDCT', \
                    help='NDCT image folder name')
parser.add_argument('--extension', dest='extension', default= 'npy', help='extension, [IMA, DCM]')
parser.add_argument('--train_ratio', dest='train_ratio', type=float, default=0.7, \
                    help='# of train samples')
parser.add_argument('--seed', dest='seed', type=int, default=0, \
                    help='ramdom sampling seed num(for train/test)')
#set save directory
parser.add_argument('--result', dest='result', default='/home/working/experiments/PIX2PIX', help='save result dir(check point, test, log, summary params)')
parser.add_argument('--checkpoint_dir', dest='checkpoint_dir', default='model', help='save dir : model checkpoint')
parser.add_argument('--inference_result', dest='inference_result', default='output', help='save dir : inference_result numpy file')
parser.add_argument('--log_dir', dest='log_dir', default='logs', help='save dir : tensorboard load')

#image info
parser.add_argument('--patch_size', dest='patch_size', type=int, default=256, help='image patch size, h=w')
parser.add_argument('--whole_size', dest='whole_size', type=int, default=512, help='image whole size, h=w')
parser.add_argument('--depth', dest='depth', type=int, default=1, help='image depth, 1')
parser.add_argument('--trun_max', dest='trun_max', type=int, default=2000, help='truncated image max value')
parser.add_argument('--trun_min', dest='trun_min', type=int, default=-1000, help='runcated image min value')
 
#train, test
parser.add_argument('--phase', dest='phase', default='train', help='train or test')

#train detail
parser.add_argument('--augument', dest='augument',type=ut.ParseBoolean, default=False, help='augumentation')
parser.add_argument('--norm', dest='norm', default='n-11', help='normalization range, n-11: -1 ~ 1, n01 : 0 ~ 1')
parser.add_argument('--is_unpair', dest='is_unpair', type=ut.ParseBoolean, default=False, help='unpaired image: True|False')
parser.add_argument('--end_epoch', dest = 'end_epoch', type=int, default = 10, help = 'iterations')
parser.add_argument('--lr', dest='lr', type=float, default=0.0002, help='learning rate')
parser.add_argument('--batch_size', dest='batch_size', type=int, default=10, help='batch size')
parser.add_argument('--ngf', dest='ngf', type=int, default=64, \
                    help='# of gen filters in first conv layer')
parser.add_argument('--ndf', dest='ndf', type=int, default=64, \
                    help='# of discri filters in first conv layer')
parser.add_argument("--separable_conv", dest='separable_conv',type=ut.ParseBoolean, default=False, \
                        help="use separable convolutions in the generator")

parser.add_argument("--beta1", type=float, default=0.5, help="momentum term of adam")
parser.add_argument("--beta2", type=float, default=0.999, help="momentum term of adam")
parser.add_argument("--l1_weight", type=float, default=100.0, help="weight on L1 term for generator gradient")
parser.add_argument("--gan_weight", type=float, default=1.0, help="weight on GAN term for generator gradient")

#others
parser.add_argument('--save_freq', dest='save_freq', type=int, default=-1, \
                    help='save a model every save_freq (iteration)// -1 : epoch')
parser.add_argument('--print_freq', dest='print_freq', type=int, default=500, \
                    help='print_freq (iterations)')
parser.add_argument('--print_sample_freq', dest='print_sample_freq', type=int, default=2000, \
                    help='print_sample_freq (iterations)')
parser.add_argument('--continue_train', dest='continue_train', type=ut.ParseBoolean, default=True, help='load the latest model: true, false')
parser.add_argument('--gpu_no', dest='gpu_no', type=int, default=0, help='gpu no')
parser.add_argument('--prefetch_buffer', dest='prefetch_buffer', type=int, default=200, help='prefetch buffer size ')
parser.add_argument('--num_parallel_calls', dest='num_parallel_calls', type=int, default=6, help='num parallel calls')
parser.add_argument('--raw_output', dest='raw_output', type=ut.ParseBoolean, \
                     default=False, help='True : outpu raw image')

# -------------------------------------
args = parser.parse_args()
print(args)

os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_no)

tf.reset_default_graph()
tfconfig = tf.ConfigProto(allow_soft_placement=True)
tfconfig.gpu_options.allow_growth = True
sess = tf.Session(config=tfconfig)


print('train/test start!!')
t_start  = time()

model = pix2Pix(sess, args)
model.train(args) if args.phase == 'train' else model.inference(args)

if args.phase == 'train':
    params_summary = '{} complete!!, \ntime : {}\nset params : \n{}'.\
    format(args.phase, time() - t_start, args)
    print(params_summary)
    with open(os.path.join(args.result, "parameter_summary.txt"), "w") as text_file:
        text_file.write(params_summary)
sess.close()