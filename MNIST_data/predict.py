import sys
import tensorflow as tf
from PIL import Image, ImageFilter

import matplotlib.pyplot as plt


def predictint(imvalue):
    """
    This function returns the predicted integer.
    The imput is the pixel values from the imageprepare() function.
    """
    
    # Define the model (same as when creating the model file)
    # x = tf.placeholder(tf.float32, [None, 784])
    # W = tf.Variable(tf.zeros([784, 10]))
    # b = tf.Variable(tf.zeros([10]))
    tf.reset_default_graph()
    def init_weights(shape):
        init_random_dist = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(init_random_dist)
    
    def init_bias(shape):
        init_bias_vals = tf.constant(0.1, shape=shape)
        return tf.Variable(init_bias_vals)
       
    def conv2d(x, W):
        return tf.nn.conv2d(x, W, strides=[1,1,1,1], padding='SAME')
    
    def max_pool_2by2(x):
        return tf.nn.max_pool(x, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
   
    def convolutional_layer(input_x, shape):
        W = init_weights(shape)
        b = init_bias([shape[3]])
        return tf.nn.relu(conv2d(input_x, W) + b)
   
    def normal_full_layer(input_layer, size):
        input_size = int(input_layer.get_shape()[1])
        W = init_weights([input_size, size])
        b = init_bias([size])
        return tf.matmul(input_layer, W) + b
    
    x = tf.placeholder(tf.float32,shape=[None,784])

    y_true = tf.placeholder(tf.float32,shape=[None,10])

    x_image = tf.reshape(x,[-1,28,28,1])

    convo_1 = convolutional_layer(x_image,shape=[6,6,1,32])
    convo_1_pooling = max_pool_2by2(convo_1)

    convo_2 = convolutional_layer(convo_1_pooling,shape=[6,6,32,64])
    convo_2_pooling = max_pool_2by2(convo_2)

    convo_2_flat = tf.reshape(convo_2_pooling,[-1,7*7*64])
    full_layer_one = tf.nn.relu(normal_full_layer(convo_2_flat,1024))

    hold_prob = tf.placeholder(tf.float32)
    full_one_dropout = tf.nn.dropout(full_layer_one,keep_prob=hold_prob)

    y_pred = normal_full_layer(full_one_dropout,10)

    init_op = tf.global_variables_initializer()
    saver = tf.train.Saver()

    with tf.Session() as sess:
        sess.run(init_op)
        saver.restore(sess, "model1.ckpt")
        print ("Model restored.")

        prediction=tf.argmax(y_pred, 1)
        return prediction.eval(feed_dict={x: [imvalue],hold_prob: 1.0}, session=sess)


def imageprepare(argv):
    """
    This function returns the pixel values.
    The imput is a png file location.
    """
    im = Image.open(argv).convert('L')
    width = float(im.size[0])
    height = float(im.size[1])
    newImage = Image.new('L', (28, 28), (255)) #creates white canvas of 28x28 pixels
    
    if width > height: #check which dimension is bigger
        #Width is bigger. Width becomes 20 pixels.
        nheight = int(round((20.0/width*height),0)) #resize height according to ratio width
        if (nheight == 0): #rare case but minimum is 1 pixel
            nheight = 1  
        # resize and sharpen
        img = im.resize((20,nheight), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wtop = int(round(((28 - nheight)/2),0)) #caculate horizontal pozition
        newImage.paste(img, (4, wtop)) #paste resized image on white canvas
    else:
        #Height is bigger. Heigth becomes 20 pixels. 
        nwidth = int(round((20.0/height*width),0)) #resize width according to ratio height
        if (nwidth == 0): #rare case but minimum is 1 pixel
            nwidth = 1
         # resize and sharpen
        img = im.resize((nwidth,20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wleft = int(round(((28 - nwidth)/2),0)) #caculate vertical pozition
        newImage.paste(img, (wleft, 4)) #paste resized image on white canvas
    
    #newImage.save("sample.png")

    tv = list(newImage.getdata()) #get pixel values
    
    #normalize pixels to 0 and 1. 0 is pure white, 1 is pure black.
    tva = [ (255-x)*1.0/255.0 for x in tv]
   # plt.imshow(tva.reshape(28, 28))
    return tva
    #print(tva)

def predict(argv):
    """
    Main function.
    """
    imvalue = imageprepare(argv)
    predint = predictint(imvalue)
    print (predint[0]) #first value in list
    return predint[0]

# if __name__ == "__main__":
#     main(sys.argv[1])