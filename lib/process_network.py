#mport tensorflow as tf
import time
from datetime import timedelta
#from time import sleep
#from sklearn.metrics import confusion_matrix
from tqdm import tqdm
#from tqdm import tqdm_notebook as tqdm
import numpy as np
"""
DESCRIPTION:
    TF - Manager "codenamed: process_network"
    
CURRENT WORK:
    feedback redoubts 
    
TODO:
    complete load / save / cue transfer
"""
CURSOR_UP="\033[F"
CLEAR_LINE="\033[K"
""" TEST SET """
def backup_print_less(msg):
    return "{}{}{}{}".format(CURSOR_UP,CLEAR_LINE,CURSOR_UP,msg) 
                
def backup_print(msg):
    return "{}{}{}{}".format(CURSOR_UP,CLEAR_LINE,CURSOR_UP,msg)
    
def extend_string(s, l):
    return (s*l)[:l]

def clear_screen():
    print(extend_string(backup_print("DummyScript.com"),55))

    
    
""" real Deal """
class Process_Network(object):
    """ This class handles Opimization / Visualization for TF Models """
    def __init__(self, network, ipy=None):
        self.werk_done = 0
        self.ipy = ipy   
        self.network = network
        
        # get dataset from network
        self.dataset = network.dataset
        # get options from network
        self.options = network.options
        # get verbose
        self.verbose = self.options.verbose
        
        # this is extreme... use patience
        #if self.verbose:
        #    from pprint import pprint
        #    pprint (vars(self.dataset))
        #    pprint (vars(self.network))
        # setup a better output
        self.progress = tqdm
        
    
    def end(self):
        """ This is run at the end of a TF script session"""
        self.network.session.close() 
        
    def run(self, epochs=5):
        """ This will perform the optimize function"""
        
        # BOOLEAN HACK...
        is_running = True
        
        # always run a .. .run timer... its in the name
        start_time = time.time() 
        start_readout = time.strftime("%a, %d %b %Y %H:%M:%S\n\n", time.gmtime())
        self.current_epoch = self.dataset._epochs_completed
        goal_train = self.current_epoch + epochs
        print("Start Time: {}\nTraining {} epochs...".format(start_readout,goal_train))
        #while self.current_epoch < goal_train:
        while is_running:
            batch = self.dataset.next_batch(self.options.batch_size)
            current_epoch = batch[2]
            print(backup_print("##\tEpoch: {}\n##\tIter: {}".format(current_epoch,self.werk_done)))
            
            if len(batch[0]) is len(batch[1]):
                # setup up a dict
                Dict = {self.network.Input_Tensor_Images: batch[0], self.network.Input_Tensor_Labels: batch[1], self.network.keep_prob: 0.8}
                
                # This is the optimize function
                #self.network.session.run(self.network.optimizer2, feed_dict=Dict)
                self.network.session.run(self.network.optimizer, feed_dict=Dict)
                self.werk_done += 1
            else:
                clear_screen()
            
            # dont run again !
            if current_epoch is goal_train:
                is_running = False
                print("Duck out of loop")
        print("Finished Training... Waiting on some Info...")
        batch = self.dataset.next_batch(self.options.batch_size)
        self.feedback(batch)
        end_time = time.time()             # AND STOP THE CLOCK...
        time_dif = end_time - start_time   # do the math
        time_msg = "Time usage: " + str(timedelta(seconds=int(round(time_dif))))   # boom and done.
        print(time_msg, ", Iters Complete: %s" % self.werk_done)
   
    def feedback(self,training_batch=False):
        """WORKING THROUGH THE FEEDBACK DEBUGS!! 2_23_17  * finished same day... BOOM..."""
        
        """This will do a test for acc and loss"""
        testing_start = 110 # should be randowm less than the _num examples
        msg = "Feedback: \n"
        msg += "Total Epochs Complete: {}\n".format(self.dataset._epochs_completed)
        msg += "Total Optimizations Complete: {}\n".format(self.werk_done)
        Testing_set_images = self.dataset.train_images[testing_start:(testing_start+self.options.batch_size)]
        Testing_set_labels = self.dataset.train_labels[testing_start:(testing_start+self.options.batch_size)]
        test_dict = {self.network.Input_Tensor_Images: Testing_set_images, self.network.Input_Tensor_Labels: Testing_set_labels, self.network.keep_prob: 1.0}
        
        # this is the get_loss function
        test_loss = self.network.loss.eval(feed_dict=test_dict)
        msg += "Test Loss: {:.1%}\n".format(test_loss)
            
        # this is the print acc funtion
        test_acc = self.network.session.run(self.network.accuracy, feed_dict=test_dict)
        msg += "Test Acc: {:1%}\n".format(test_acc)
        
        if training_batch:
            training_dict = {self.network.Input_Tensor_Images: training_batch[0], self.network.Input_Tensor_Labels: training_batch[1], self.network.keep_prob: 1.0}
            train_loss = self.network.loss.eval(feed_dict=training_dict)
            msg += "Train Loss: {:.1%}\n".format(train_loss)
            train_acc = self.network.session.run(self.network.accuracy, feed_dict=training_dict)
            msg += "Train Acc: {:1%}\n".format(train_acc)
        if self.verbose: print(msg)
        print(msg)
        
    """ RECLAMATION YARD """

    def BATCH_VERIFY(self, input_tensor, labels, cls_true):
        batch_size = self.options.batch_size
        num_images = len(input_tensor)
        cls_pred = np.zeros(shape=num_images, dtype=np.int)
        i = 0
        while i < num_images:
            j = min(i + batch_size, num_images) # j is remade frest every loop...
            #feed_dict = self.network.feed_dictionary(test=False,x_batch=input_tensor, y_true_batch=labels)
            feed_dict = {self.network.Input_Tensor_Images: input_tensor[i:j, :], self.network.Input_Tensor_Labels: labels[i:j, :]}
            cls_pred[i:j] = self.network.session.run(self.network.y_pred_cls, feed_dict=feed_dict)
            i = j
        correct = (cls_true == cls_pred)   
        return correct, cls_pred   
        
    def run_test(self):
        return self.BATCH_VERIFY(input_tensor = self.dataset.test_images,
                                 labels       = self.dataset.test_labels,
                                 cls_true     = self.dataset.test_cls)
    # NOT IMPLEMENTED YET...  
    def run_valid(self):
        return self.BATCH_VERIFY(input_tensor = self.dataset.valid_images,
                                 labels       = self.dataset.valid_labels,
                                 cls_true     = self.dataset.valid_cls)
        
    def run_train(self,):
        x = self.network.session.run(self.network.accuracy, feed_dict=self.feed_train)                   ## TRAINING ACCURACY   
        return x
        
    def challenge(self,):
        #train_acc   = self.run_train()
        test, _     = self.run_test()
        #valid, _    = self.run_valid()
        test_sum    = test.sum()
        #valid_sum   = valid.sum()
        
        test_acc    = float(test_sum) / len(test)
        #valid_acc   = float(valid_sum) / len(valid)
        return train_acc, test_acc#, valid_acc
        


"""Graveyard... some things need rework..."""
#    # RETURNING w for IPY.plot_weights 
#    def get_weights(self):
#        """This should still work"""
#        x = self.network.session.run(self.network.weights)
#        return x
#        
#    # RETURNING ConfusionMatrix and NumClasses for IPY.plot_confused 
#    def get_confused(self): pass
#    """
#    def get_confused(self):
#        #get num_classes
#        num_classes = self.model.num_classes
#        # Get the true classifications for the test-set.
#        cls_true = self.model.test_cls
#        # Get the predicted classifications for the test-set.
#        cls_pred = self.network.session.run(self.network.y_pred_cls, feed_dict=self.network.feed_test)
#        cm = confusion_matrix(y_true=cls_true, y_pred=cls_pred)
#        if self.options.verbose: print(cm);
#        return cm, num_classes
#    """
#    # RETURNING IMAGES, CLS_TRUE, CLS_PRED for IPY.SIMPLE_PLOT
#    def get_example_errors(self):
#        """This should still work"""
#        self.print_acc()
#        correct, cls_pred = self.network.session.run([self.network.correct_prediction, self.network.y_pred_cls],
#                                                     feed_dict=self.network.feed_test)
#        incorrect = (correct == False)
#        images = self.dataset.images_test[incorrect]
#        cls_pred = cls_pred[incorrect]
#        cls_true = self.dataset.cls_true[incorrect]
#        n = min(9, len(images))       
#        return images[0:n], cls_true[0:n], cls_pred[0:n]
#    
#    # This is A Verbose Output of All Available Sources
#    def show_Verbose(self):
#       ## GET SOME DATAS
#       cm, num_classes = self.get_confused()
#       img, cls_t,cls_p = self.get_example_errors()
#       ## Bring in IPY
#       self.ipy.plot_confused(cm,num_classes)
#       self.ipy.simple_plot(images=img, cls_true=cls_t, cls_pred=cls_p)
#    
#    def print_samples(self):
#        """This should tell you if you have congruent img:labels"""
#        x = self.dataset.train_images[0:9]
#        y = self.dataset.train_labels[0:9]
#        index = 0
#        for i in x:
#            print("img {} label = {}".format(i,y[index]))
#            index += 1