# tropical fruit identifier

A web application which can recognize photos of Oranges, Lemons, Papayas and Cocoa and collect them for addition to a tropical fruits. 
It contains three combined parts: 
   1. A Yolo image annotation tool 
   2. A PyTorch implementation of Yolov3 
   3. A frontend application with persistence for image collection. 
### Installation
##### Clone and install requirements
    clone github.com/Totally-Random-Productions/tropical_fruit_identifier
    cd src
    pip3 install -r requirements.txt

###Preparing the Dataset
##### Annotate fruit images  
1. Add images to data/custom/images 
2. Edit classes.names to include the categories or classes of images being annotated 
3. Run annotate.py:
   
        python annotate.py
4. Enter 'images' in the Image Dir field and select 'load'
5. For each image and for each type of fruit in the image:
    1. Select the class of the image
    2. Draw the bounding box where it appears
6. Click next
7. Exit the program when all images have been annotated 

##### Create the Test and Train sets 
    python an_process.py
    
### Training Yolov3 using the existing configuration 
Training the model generates the weights that will be used for detection.

- Edit the number of classes in config/custom.data to reflect the current number.
            
      python custom_train.py 
 
 The last created checkpoint or set of weights created are evaluated at the end of each epoch therefore the average precision can be viewed at end. 
    
    
### Test
Evaluates the model.
Below the weights entered are from the last training of this model, it should be replaced when the model is retrained. 

    python custom_test.py --weights_path checkpoints/yolov3_ckpt_9.pth

### Independent Detection
Uses our pretrained weights to make predictions on images. 

    python custom_detect.py

The detection program is currently triggered by the upload function of the web application. 
It can be run independently by editing the image folder it reads from by adding the argument below:
        
    --image_folder root/images
     
The weights used for detection can be changed using the addition of the following argument:
    
    --weights_path root/weight.pth 
    
There are also lines at the end of the custom_detect.py file which would have to be altered, they have been marked with comments. 


## The Frontend
Launches the web application server. 

    python wsgi.py 
    
Uploading an image allows it to be detected, verified then added to the database. 
Another page also always admins to access and check user submissions in the database. 



## Credit / References

Yolov3 Code using Pytorch: [PyTorch Yolov3](https://github.com/eriklindernoren/PyTorch-YOLOv3)

Yolo Annotation Tool: [New Yolo Annotation Tool](https://github.com/ManivannanMurugavel/Yolo-Annotation-Tool-New-)

The Original Yolo and Darknet Framework: [The Original Darknet](https://github.com/pjreddie/darknet)

