from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import os.path
import shutil
import tensorflow as tf


# mnist = tf.contrib.learn.datasets.load_dataset("mnist")
# train_data = mnist.train.images  # Returns np.array
# train_labels = np.asarray(mnist.train.labels, dtype=np.int32)
# eval_data = mnist.test.images  # Returns np.array
# eval_labels = np.asarray(mnist.test.labels, dtype=np.int32)



LOGDIR = "/tmp/mnist_tutorial/"
#LABELS = os.path.join(os.getcwd(), "labels_1024.tsv")
#SPRITES = os.path.join(os.getcwd(), "sprite_1024.png")

mnist = tf.contrib.learn.datasets.mnist.read_data_sets(train_dir=LOGDIR + "data", one_hot=True)


def conv_layer(input, size_in, size_out, name="conv"):
  with tf.name_scope(name):
    w = tf.Variable(tf.truncated_normal([5, 5, size_in, size_out], stddev=0.1), name="W")
    b = tf.Variable(tf.constant(0.1, shape=[size_out]), name="B")
    conv = tf.nn.conv2d(input, w, strides=[1, 1, 1, 1], padding="SAME")
    act = tf.nn.relu(conv + b)
    #tf.summary.histogram("weights", w)
    #tf.summary.histogram("biases", b)
    #tf.summary.histogram("activations", act)
    return tf.nn.max_pool(act, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")


def conv_layer_2(input, size_in, size_out, name="conv"):
  with tf.name_scope(name):
    w = tf.Variable(tf.truncated_normal([5, 5, size_in, size_out], stddev=0.1), name="W")
    b = tf.Variable(tf.constant(0.1, shape=[size_out]), name="B")
    conv = tf.nn.conv2d(input, w, strides=[1, 1, 1, 1], padding="SAME")
    act = tf.nn.relu(conv + b)
    #tf.summary.histogram("weights", w)
    #tf.summary.histogram("biases", b)
    #tf.summary.histogram("activations", act)
    return act

def fc_layer(input, size_in, size_out, name="fc"):
  with tf.name_scope(name):
    w = tf.Variable(tf.truncated_normal([size_in, size_out], stddev=0.1), name="W")
    b = tf.Variable(tf.constant(0.1, shape=[size_out]), name="B")
    act = tf.matmul(input, w) + b
    #tf.summary.histogram("weights", w)
    #tf.summary.histogram("biases", b)
    #tf.summary.histogram("activations", act)
    return act


def mnist_model(learning_rate, use_two_fc, use_two_conv, hparam):
  tf.reset_default_graph()
  sess = tf.Session()

  # Setup placeholders, and reshape the data
  x = tf.placeholder(tf.float32, shape=[None, 784], name="x")
  x_image = tf.reshape(x, [-1, 28, 28, 1])
  tf.summary.image('input', x_image, 3)
  y = tf.placeholder(tf.float32, shape=[None, 10], name="labels")

  if use_two_conv:
    conv1 = conv_layer(x_image, 1, 32, "conv1")
    conv_out = conv_layer(conv1, 32, 64, "conv2")
  else:
    conv_out = conv_layer(x_image, 1, 16, "conv")

  flattened = tf.reshape(conv_out, [-1, 7 * 7 * 64])


  if use_two_fc:
    fc1 = fc_layer(flattened, 7 * 7 * 64, 1024, "fc1")
    relu = tf.nn.relu(fc1)
    embedding_input = relu
    tf.summary.histogram("fc1/relu", relu)
    embedding_size = 1024
    logits = fc_layer(relu, 1024, 10, "fc2")
  else:
    embedding_input = flattened
    embedding_size = 7*7*64
    logits = fc_layer(flattened, 7*7*64, 10, "fc")

  with tf.name_scope("xent"):
    xent = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(
            logits=logits, labels=y), name="xent")
    tf.summary.scalar("xent", xent)

  with tf.name_scope("train"):
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(xent)

  with tf.name_scope("accuracy"):
    correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    tf.summary.scalar("accuracy", accuracy)

  summ = tf.summary.merge_all()

  #embedding = tf.Variable(tf.zeros([1024, embedding_size]), name="test_embedding")
  #assignment = embedding.assign(embedding_input)
  #saver = tf.train.Saver()
  #config = tf.contrib.tensorboard.plugins.projector.ProjectorConfig()
  #embedding_config = config.embeddings.add()
  #embedding_config.tensor_name = embedding.name
  #embedding_config.sprite.image_path = SPRITES
  #embedding_config.metadata_path = LABELS
  # Specify the width and height of a single thumbnail.
  #embedding_config.sprite.single_image_dim.extend([28, 28])
  #tf.contrib.tensorboard.plugins.projector.visualize_embeddings(writer, config)

  sess.run(tf.global_variables_initializer())
  trainWriter = tf.summary.FileWriter('C:/Users/naikg/PycharmProjects/AML-HW10/writer/' + 'train')
  trainWriter.add_graph(sess.graph)
  testWriter = tf.summary.FileWriter('C:/Users/naikg/PycharmProjects/AML-HW10/writer/' + 'test')


  for i in range(10001):
    batch = mnist.train.next_batch(100)
    if i % 100 == 0:

      [testSummary, testAccuracy] = sess.run([summ, accuracy], feed_dict={x: mnist.test.images[:1024], y: mnist.test.labels[:1024]})
      testWriter.add_summary(testSummary, i)
      print("step %d, testing_accuracy %g" % (i, testAccuracy))

      [trainSummary] = sess.run([summ], feed_dict={x: batch[0], y: batch[1]})
      trainWriter.add_summary(trainSummary, i)

    if i % 500 == 0:
      [train_acc] = sess.run([accuracy], feed_dict={x: batch[0], y: batch[1]})
      print("step %d, training_accuracy %g" % (i,train_acc))
      #sess.run(assignment, feed_dict={x: mnist.test.images[:1024], y: mnist.test.labels[:1024]})
      #saver.save(sess, os.path.join(LOGDIR, "model.ckpt"), i)
    sess.run(train_step, feed_dict={x: batch[0], y: batch[1]})

def make_hparam_string(learning_rate, use_two_fc, use_two_conv):
  conv_param = "conv=2" if use_two_conv else "conv=1"
  fc_param = "fc=2" if use_two_fc else "fc=1"
  return "lr_%.0E,%s,%s" % (learning_rate, conv_param, fc_param)

def main():
  # You can try adding some more learning rates
  for learning_rate in [1E-3]:

    # Include "False" as a value to try different model architectures
    for use_two_fc in [True]:
      for use_two_conv in [True]:
        # Construct a hyperparameter string for each one (example: "lr_1E-3,fc=2,conv=2")
        hparam = make_hparam_string(learning_rate, use_two_fc, use_two_conv)
        print('Starting run for %s' % hparam)

        # Actually run with the new settings
        mnist_model(learning_rate, use_two_fc, use_two_conv, hparam)
  print('Done training!')
  print('Run `tensorboard --logdir=%s` to see the results.' % LOGDIR)
  print('Running on mac? If you want to get rid of the dialogue asking to give '
        'network permissions to TensorBoard, you can provide this flag: '
        '--host=localhost')

if __name__ == '__main__':
  main()


#tensorboard --logdir=/tmp/mnist_tutorial/lr_1E-03,conv=2,fc=2